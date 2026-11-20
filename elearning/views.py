from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404
from .models import Training, Module, StudentProgress, Quiz, Question, Choice, QuizSubmission, Certificate
from .utils import generate_pdf_certificate
from analytics.utils import log_page_view

def training_list(request):
    log_page_view(request, "Catalogue E-learning")
    trainings = Training.objects.all()

    # Enrich training list with user progress if logged in
    trainings_with_progress = []
    for t in trainings:
        progress = t.get_progress_for_user(request.user) if request.user.is_authenticated else 0
        trainings_with_progress.append({
            'obj': t,
            'progress': progress
        })

    return render(request, "elearning/training_list.html", {"trainings": trainings_with_progress})


def training_detail(request, training_id):
    log_page_view(request, f"Détails Formation {training_id}")
    training = get_object_or_404(Training, id=training_id)
    modules = training.modules.all().order_by("order")

    user_progress = {}
    has_certificate = False
    cert_obj = None

    if request.user.is_authenticated:
        # Get completion status for all modules in this training
        progress_records = StudentProgress.objects.filter(student=request.user, module__training=training)
        user_progress = {record.module_id: record.completed for record in progress_records}

        # Check if user has completed all modules
        total_modules = modules.count()
        completed_modules = sum(1 for m in modules if user_progress.get(m.id, False))

        if total_modules > 0 and completed_modules == total_modules:
            # Auto-issue certificate if not exists
            cert_obj, created = Certificate.objects.get_or_create(
                student=request.user,
                training=training
            )
            if created:
                from core.models import Notification
                Notification.objects.create(
                    type='CERTIFICATE',
                    title="Nouveau certificat généré",
                    message=f"L'étudiant {request.user.get_full_name() or request.user.username} a validé la formation '{training.title}' et obtenu son certificat."
                )

                # Send email notification
                from django.core.mail import send_mail
                from django.conf import settings
                try:
                    send_mail(
                        subject=f"Félicitations ! Votre certificat pour '{training.title}' est disponible",
                        message=f"Bonjour {request.user.get_full_name() or request.user.username},\n\nFélicitations ! Vous avez complété avec succès tous les modules de la formation '{training.title}'.\n\nVotre certificat de réussite a été généré automatiquement et est désormais disponible en téléchargement depuis votre espace étudiant.\n\nCordialement,\nL'administration.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[request.user.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass
            has_certificate = True

        elif Certificate.objects.filter(student=request.user, training=training).exists():
            cert_obj = Certificate.objects.get(student=request.user, training=training)
            has_certificate = True

    # Attach completion status directly to modules for rendering
    modules_list = []
    for m in modules:
        modules_list.append({
            'obj': m,
            'completed': user_progress.get(m.id, False),
            'has_quiz': hasattr(m, 'quiz')
        })

    context = {
        "training": training,
        "modules": modules_list,
        "progress_percent": training.get_progress_for_user(request.user) if request.user.is_authenticated else 0,
        "has_certificate": has_certificate,
        "certificate": cert_obj,
    }
    return render(request, "elearning/training_detail.html", context)


@login_required
def module_detail(request, module_id):
    log_page_view(request, f"Module {module_id}")
    module = get_object_or_404(Module, id=module_id)
    training = module.training

    # Get completion status
    progress, created = StudentProgress.objects.get_or_create(student=request.user, module=module)

    # Find next module for navigation
    next_module = training.modules.filter(order__gt=module.order).order_by("order").first()

    context = {
        "module": module,
        "training": training,
        "completed": progress.completed,
        "next_module": next_module,
        "has_quiz": hasattr(module, 'quiz'),
    }
    return render(request, "elearning/module_detail.html", context)


@login_required
def complete_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    # Check if module has a quiz. If it does, user cannot bypass it manually
    if hasattr(module, 'quiz'):
        messages.error(request, "Ce module nécessite la réussite d'un quiz pour être validé.")
        return redirect("module_detail", module_id=module.id)

    progress, created = StudentProgress.objects.get_or_create(student=request.user, module=module)
    progress.completed = True
    progress.save()
    messages.success(request, f"Module « {module.title} » marqué comme complété !")

    # Redirect to next module or back to training
    next_module = module.training.modules.filter(order__gt=module.order).order_by("order").first()
    if next_module:
        return redirect("module_detail", module_id=next_module.id)
    return redirect("training_detail", training_id=module.training.id)


@login_required
def take_quiz(request, quiz_id):
    log_page_view(request, f"Quiz {quiz_id}")
    quiz = get_object_or_404(Quiz, id=quiz_id)
    module = quiz.module
    questions = quiz.questions.prefetch_related("choices").all()

    if request.method == "POST":
        # Process answers
        total_questions = questions.count()
        if total_questions == 0:
            return redirect("module_detail", module_id=module.id)

        correct_count = 0

        # Check answer for each question
        for question in questions:
            choice_id_str = request.POST.get(f"question_{question.id}")
            if choice_id_str:
                try:
                    choice = Choice.objects.get(id=int(choice_id_str), question=question)
                    if choice.is_correct:
                        correct_count += 1
                except Choice.DoesNotExist:
                    pass

        # Grade quiz
        score = int((correct_count / total_questions) * 100)
        passed = score >= quiz.passing_score

        # Save submission
        QuizSubmission.objects.create(
            student=request.user,
            quiz=quiz,
            score=score,
            passed=passed
        )

        from core.models import Notification
        Notification.objects.create(
            type='QUIZ',
            title="Quiz complété",
            message=f"L'étudiant {request.user.get_full_name() or request.user.username} a complété le quiz '{quiz.title}' pour le module '{module.title}' (Score: {score}%, {'Réussi' if passed else 'Échoué'})."
        )

        if passed:
            # Mark module as completed
            progress, created = StudentProgress.objects.get_or_create(student=request.user, module=module)
            progress.completed = True
            progress.save()
            messages.success(request, f"Félicitations ! Vous avez réussi le quiz « {quiz.title} » avec un score de {score}% !")
        else:
            messages.error(request, f"Dommage ! Votre score est de {score}%. Il vous faut au moins {quiz.passing_score}% pour réussir.")

        context = {
            "quiz": quiz,
            "module": module,
            "score": score,
            "passed": passed,
            "correct_count": correct_count,
            "total_questions": total_questions,
        }
        return render(request, "elearning/quiz_results.html", context)

    return render(request, "elearning/take_quiz.html", {"quiz": quiz, "module": module, "questions": questions})


@login_required
def download_certificate(request, certificate_id):
    cert = get_object_or_404(Certificate, id=certificate_id, student=request.user)

    # Retrieve student's full name or fallback to username
    student_name = f"{request.user.first_name} {request.user.last_name}".strip()
    if not student_name:
        student_name = request.user.username

    issue_date = cert.issued_at.strftime("%d/%m/%Y")

    pdf_bytes = generate_pdf_certificate(
        student_name=student_name,
        training_title=cert.training.title,
        issue_date=issue_date,
        certificate_code=cert.code
    )

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Certificat_{cert.training.title.replace(" ", "_")}.pdf"'
    return response


@login_required
def student_dashboard(request):
    log_page_view(request, "Dashboard Étudiant")

    # Get all trainings the student has started progress on or has completed
    progress_records = StudentProgress.objects.filter(student=request.user)
    started_training_ids = progress_records.values_list('module__training_id', flat=True).distinct()

    # Or simply fetch all trainings
    trainings = Training.objects.all()

    enrolled_trainings = []
    for t in trainings:
        progress = t.get_progress_for_user(request.user)
        # We consider enrolled if they have progressed or training list is open
        enrolled_trainings.append({
            'obj': t,
            'progress': progress
        })

    # Get quiz submissions
    submissions = QuizSubmission.objects.filter(student=request.user).order_by("-submitted_at")

    # Get certificates
    certificates = Certificate.objects.filter(student=request.user)

    context = {
        "enrolled_trainings": enrolled_trainings,
        "submissions": submissions,
        "certificates": certificates,
    }
    return render(request, "elearning/dashboard.html", context)
