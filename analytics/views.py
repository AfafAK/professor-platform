import base64
import io
import csv
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Count, Avg, Q
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.core.paginator import Paginator

import matplotlib
matplotlib.use('Agg')  # Headless backend for web server rendering
import matplotlib.pyplot as plt

from core.models import ContactMessage, ProfessorProfile, News, NewsAttachment, Comment, Notification
from courses.models import Subject, CourseResource
from elearning.models import Training, Module, StudentProgress, Quiz, Question, Choice, QuizSubmission, Certificate
from scheduler.models import AppointmentSlot
from research.models import Publication
from .models import PageView, DownloadTracker

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from .forms import (
    NewsForm, PublicationForm, SubjectForm, CourseResourceForm,
    TrainingForm, ModuleForm, QuizForm, QuestionForm, ChoiceForm,
    ProfessorProfileForm, UserProfileForm
)

def generate_visits_chart(labels, counts):
    if not labels or not counts:
        return None
    fig, ax = plt.subplots(figsize=(5, 3.5), facecolor='none')
    colors_palette = ['#3b82f6', '#6366f1', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6']
    bars = ax.bar(labels, counts, color=colors_palette[:len(labels)], edgecolor='none', width=0.55)

    ax.tick_params(colors='#e2e8f0', labelsize=8)
    ax.set_facecolor('none')
    for spine in ax.spines.values():
        spine.set_visible(False)
    plt.xticks(rotation=15, ha='right')

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', color='#ffffff', fontsize=8, fontweight='bold')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=150)
    buf.seek(0)
    string = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return f"data:image/png;base64,{string}"

def generate_downloads_chart(labels, counts):
    if not labels or not counts:
        return None
    fig, ax = plt.subplots(figsize=(5, 3.5), facecolor='none')
    short_labels = [l[:15] + '...' if len(l) > 15 else l for l in labels]
    ax.plot(short_labels, counts, color='#6366f1', marker='o', linewidth=2.5, markersize=5)
    ax.fill_between(short_labels, counts, color='#6366f1', alpha=0.15)

    ax.tick_params(colors='#e2e8f0', labelsize=8)
    ax.set_facecolor('none')
    for spine in ax.spines.values():
        spine.set_visible(False)
    plt.xticks(rotation=15, ha='right')

    for i, txt in enumerate(counts):
        ax.annotate(f'{int(txt)}', (short_labels[i], counts[i]),
                    textcoords="offset points", xytext=(0, 6),
                    ha='center', color='#ffffff', fontsize=8, fontweight='bold')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=150)
    buf.seek(0)
    string = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return f"data:image/png;base64,{string}"

@user_passes_test(lambda u: u.is_staff)
def professor_dashboard(request):
    # Counts
    total_students = User.objects.filter(is_staff=False).count()
    total_courses = Subject.objects.count()
    total_trainings = Training.objects.count()
    total_publications = News.objects.count() + Publication.objects.count()
    total_downloads = DownloadTracker.objects.count()
    total_certificates = Certificate.objects.count()

    # Upcoming appointments
    upcoming_appointments = AppointmentSlot.objects.filter(is_booked=True).order_by('start_time')[:5]

    # Recent notifications
    recent_notifications = Notification.objects.all().order_by('-created_at')[:5]

    # Generate Chart Data: Page Views by section
    page_stats = PageView.objects.values('page_name').annotate(count=Count('id')).order_by('-count')
    chart_visits_labels = [item['page_name'] for item in page_stats]
    chart_visits_counts = [item['count'] for item in page_stats]

    # Generate Chart Data: Downloads by resource
    dl_stats = DownloadTracker.objects.values('resource__title').annotate(count=Count('id')).order_by('-count')[:5]
    chart_downloads_labels = [item['resource__title'] for item in dl_stats]
    chart_downloads_counts = [item['count'] for item in dl_stats]

    # Generate Activity Stream
    activities = []
    # 1. New registrations
    for u in User.objects.filter(is_staff=False).order_by('-date_joined')[:5]:
        activities.append({
            'time': u.date_joined,
            'icon': 'fa-user-plus text-primary',
            'text': f"Nouvel étudiant inscrit : {u.get_full_name() or u.username}"
        })
    # 2. Downloads
    for dl in DownloadTracker.objects.all().order_by('-timestamp')[:5]:
        activities.append({
            'time': dl.timestamp,
            'icon': 'fa-download text-success',
            'text': f"Ressource « {dl.resource.title} » téléchargée par {dl.user.username if dl.user else 'Anonyme'}"
        })
    # 3. Quiz submissions
    for sub in QuizSubmission.objects.all().order_by('-submitted_at')[:5]:
        activities.append({
            'time': sub.submitted_at,
            'icon': 'fa-circle-question text-warning',
            'text': f"Quiz '{sub.quiz.title}' soumis par {sub.student.username} (Score: {sub.score}%)"
        })

    # Sort activities by time descending
    activities.sort(key=lambda x: x['time'], reverse=True)
    activities = activities[:8]

    # Generate Matplotlib charts in base64
    visits_chart_base64 = generate_visits_chart(chart_visits_labels, chart_visits_counts)
    downloads_chart_base64 = generate_downloads_chart(chart_downloads_labels, chart_downloads_counts)

    context = {
        'total_students': total_students,
        'total_courses': total_courses,
        'total_trainings': total_trainings,
        'total_publications': total_publications,
        'total_downloads': total_downloads,
        'total_certificates': total_certificates,
        'upcoming_appointments': upcoming_appointments,
        'recent_notifications': recent_notifications,
        'visits_chart_base64': visits_chart_base64,
        'downloads_chart_base64': downloads_chart_base64,
        'activities': activities
    }
    return render(request, 'analytics/prof/overview.html', context)

@user_passes_test(lambda u: u.is_staff)
def toggle_student_status(request, user_id):
    student = get_object_or_404(User, id=user_id, is_staff=False)
    student.is_active = not student.is_active
    student.save()
    status_str = "activé" if student.is_active else "désactivé"
    messages.success(request, f"Le compte de l'étudiant {student.get_full_name() or student.username} a été {status_str} avec succès.")
    return redirect(request.META.get('HTTP_REFERER', 'professor_dashboard'))

@user_passes_test(lambda u: u.is_staff)
def reset_student_progress(request, user_id):
    student = get_object_or_404(User, id=user_id, is_staff=False)
    progress_count = StudentProgress.objects.filter(student=student).delete()[0]
    quiz_count = QuizSubmission.objects.filter(student=student).delete()[0]
    cert_count = Certificate.objects.filter(student=student).delete()[0]
    messages.success(
        request,
        f"Progression réinitialisée pour {student.get_full_name() or student.username}. "
        f"({progress_count} modules réinitialisés, {quiz_count} tentatives de quiz et {cert_count} certificats supprimés)."
    )
    return redirect(request.META.get('HTTP_REFERER', 'professor_dashboard'))

@user_passes_test(lambda u: u.is_staff)
def export_csv_report(request, report_type):
    response = HttpResponse(content_type='text/csv; charset=utf-8')

    if report_type == 'students':
        response['Content-Disposition'] = 'attachment; filename="rapport_etudiants.csv"'
        writer = csv.writer(response)
        writer.writerow(['Nom Complet', 'Nom d\'utilisateur', 'E-mail', 'Date d\'inscription', 'Statut', 'Tentatives Quiz', 'Certificats obtenus', 'Formations & Progrès'])

        students = User.objects.filter(is_staff=False).order_by("-date_joined")
        for s in students:
            progress_parts = []
            for t in Training.objects.all():
                prog = t.get_progress_for_user(s)
                if prog > 0:
                    progress_parts.append(f"{t.title}: {prog}%")
            progress_str = " | ".join(progress_parts) if progress_parts else "Aucun"

            status = "Actif" if s.is_active else "Inactif"
            quiz_count = QuizSubmission.objects.filter(student=s).count()
            cert_count = Certificate.objects.filter(student=s).count()

            writer.writerow([
                s.get_full_name() or f"{s.first_name} {s.last_name}".strip() or s.username,
                s.username,
                s.email,
                s.date_joined.strftime('%d/%m/%Y %H:%M'),
                status,
                quiz_count,
                cert_count,
                progress_str
            ])

    elif report_type == 'downloads':
        response['Content-Disposition'] = 'attachment; filename="rapport_telechargements.csv"'
        writer = csv.writer(response)
        writer.writerow(['Ressource', 'Matière', 'Utilisateur', 'Date & Heure'])

        downloads = DownloadTracker.objects.all().order_by("-timestamp")
        for dl in downloads:
            user_str = dl.user.username if dl.user else "Anonyme"
            writer.writerow([
                dl.resource.title,
                dl.resource.subject.name,
                user_str,
                dl.timestamp.strftime('%d/%m/%Y %H:%M')
            ])

    elif report_type == 'visits':
        response['Content-Disposition'] = 'attachment; filename="rapport_visites.csv"'
        writer = csv.writer(response)
        writer.writerow(['Section/Page', 'Utilisateur', 'Date & Heure'])

        visits = PageView.objects.all().order_by("-timestamp")
        for v in visits:
            user_str = v.user.username if v.user else "Anonyme"
            writer.writerow([
                v.page_name,
                user_str,
                v.timestamp.strftime('%d/%m/%Y %H:%M')
            ])
    else:
        return HttpResponse("Type de rapport invalide", status=400)

    return response

@user_passes_test(lambda u: u.is_staff)
def export_pdf_report(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="rapport_statistiques.pdf"'

    total_students = User.objects.filter(is_staff=False).count()
    total_active_students = User.objects.filter(is_staff=False, is_active=True).count()
    total_courses = CourseResource.objects.count()
    total_trainings = Training.objects.count()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0b0f19'),
        spaceAfter=5
    )

    subtitle_style = ParagraphStyle(
        'ReportSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=20
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=15,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155'),
    )

    th_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white,
    )

    metric_val_style = ParagraphStyle(
        'MetricVal',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=16,
        textColor=colors.HexColor('#3b82f6'),
        alignment=1
    )

    metric_lbl_style = ParagraphStyle(
        'MetricLbl',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#475569'),
        alignment=1
    )

    story = []

    header_data = [
        [
            Paragraph("<b>UNIVERSITÉ ACADEMIX</b><br/><font color='#6366f1'>Portail Académique du Professeur</font>", ParagraphStyle('H1', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=15, leading=18, textColor=colors.HexColor('#1e3a8a'))),
            Paragraph(f"Rapport d'activité<br/>Généré le: <b>{timezone.now().strftime('%d/%m/%Y %H:%M')}</b>", ParagraphStyle('H2', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#475569'), alignment=2))
        ]
    ]
    header_table = Table(header_data, colWidths=[330, 200])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("RAPPORT STATISTIQUE DE LA PLATEFORME", title_style))
    story.append(Paragraph("Ce document présente un résumé des activités d'apprentissage en ligne, des ressources partagées et du suivi des étudiants.", subtitle_style))

    metrics_data = [
        [
            Paragraph(str(total_students), metric_val_style),
            Paragraph(str(total_active_students), metric_val_style),
            Paragraph(str(total_courses), metric_val_style),
            Paragraph(str(total_trainings), metric_val_style),
        ],
        [
            Paragraph("Étudiants Inscrits", metric_lbl_style),
            Paragraph("Étudiants Actifs", metric_lbl_style),
            Paragraph("Supports de Cours", metric_lbl_style),
            Paragraph("Formations", metric_lbl_style),
        ]
    ]
    metrics_table = Table(metrics_data, colWidths=[132, 132, 132, 132])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 2),
        ('TOPPADDING', (0,1), (-1,1), 2),
        ('BOTTOMPADDING', (0,1), (-1,1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Top 5 des Téléchargements de Ressources", section_heading))
    dl_stats = DownloadTracker.objects.values('resource__title', 'resource__resource_type', 'resource__subject__code').annotate(count=Count('id')).order_by('-count')[:5]

    if dl_stats:
        dl_table_data = [[
            Paragraph("Code", th_style),
            Paragraph("Ressource", th_style),
            Paragraph("Type", th_style),
            Paragraph("Téléchargements", th_style)
        ]]
        for item in dl_stats:
            type_display = dict(CourseResource.RESOURCE_TYPES).get(item['resource__resource_type'], item['resource__resource_type'])
            dl_table_data.append([
                Paragraph(item['resource__subject__code'], body_style),
                Paragraph(item['resource__title'], body_style),
                Paragraph(type_display, body_style),
                Paragraph(str(item['count']), ParagraphStyle('CountCol', parent=body_style, alignment=1))
            ])

        dl_table = Table(dl_table_data, colWidths=[70, 270, 110, 80])
        dl_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ]))
        story.append(dl_table)
    else:
        story.append(Paragraph("Aucun téléchargement enregistré pour le moment.", body_style))

    story.append(Spacer(1, 15))

    story.append(Paragraph("Liste des Étudiants Actifs & Progression", section_heading))
    active_students = User.objects.filter(is_staff=False, is_active=True).order_by("-date_joined")

    if active_students:
        stud_table_data = [[
            Paragraph("Nom complet", th_style),
            Paragraph("E-mail", th_style),
            Paragraph("Formations commencées", th_style),
            Paragraph("Quiz réussis / Certificats", th_style)
        ]]
        for s in active_students:
            progress_parts = []
            for t in Training.objects.all():
                prog = t.get_progress_for_user(s)
                if prog > 0:
                    progress_parts.append(f"{t.title} ({prog}%)")
            progress_str = ", ".join(progress_parts) if progress_parts else "Aucune formation commencée"

            quiz_passed = QuizSubmission.objects.filter(student=s, passed=True).count()
            cert_count = Certificate.objects.filter(student=s).count()
            results_str = f"{quiz_passed} quiz réussi(s) / {cert_count} cert."

            stud_table_data.append([
                Paragraph(s.get_full_name() or s.username, body_style),
                Paragraph(s.email, body_style),
                Paragraph(progress_str, body_style),
                Paragraph(results_str, body_style)
            ])

        stud_table = Table(stud_table_data, colWidths=[120, 130, 170, 110])
        stud_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ]))
        story.append(stud_table)
    else:
        story.append(Paragraph("Aucun étudiant actif inscrit pour le moment.", body_style))

    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()

    response.write(pdf_data)
    return response


# ==========================================
# 1. PUBLICATIONS MANAGEMENT (News & Research)
# ==========================================

@user_passes_test(lambda u: u.is_staff)
def manage_publications(request):
    tab = request.GET.get('tab', 'news')
    search_query = request.GET.get('search', '').strip()
    sort_by = request.GET.get('sort', '-created_at')

    if tab == 'research':
        queryset = Publication.objects.all()
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(authors__icontains=search_query) |
                Q(journal_or_book__icontains=search_query)
            )
        # Handle research publications sorting
        if sort_by not in ['year', '-year', 'title', '-title']:
            sort_by = '-year'
        queryset = queryset.order_by(sort_by)
        paginator = Paginator(queryset, 10)
        page_obj = paginator.get_page(request.GET.get('page'))
        context = {'page_obj': page_obj, 'tab': tab, 'search': search_query, 'sort': sort_by}
        return render(request, 'analytics/prof/publications.html', context)

    else: # news
        queryset = News.objects.all()
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
            )
        # Handle news sorting
        if sort_by not in ['created_at', '-created_at', 'title', '-title', 'views_count', '-views_count']:
            sort_by = '-created_at'
        queryset = queryset.order_by(sort_by)
        paginator = Paginator(queryset, 10)
        page_obj = paginator.get_page(request.GET.get('page'))
        context = {'page_obj': page_obj, 'tab': tab, 'search': search_query, 'sort': sort_by}
        return render(request, 'analytics/prof/publications.html', context)


@user_passes_test(lambda u: u.is_staff)
def create_news(request):
    if request.method == "POST":
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            if news.is_published and not news.published_at:
                news.published_at = timezone.now()
            news.save()

            # Handle multiple file uploads
            files = request.FILES.getlist('attachments')
            for f in files:
                NewsAttachment.objects.create(news=news, file=f)

            messages.success(request, f"Actualité « {news.title} » créée avec succès.")
            return redirect('manage_publications')
    else:
        form = NewsForm()
    return render(request, 'analytics/prof/publication_form.html', {'form': form, 'title': 'Créer une actualité', 'type': 'news'})


@user_passes_test(lambda u: u.is_staff)
def edit_news(request, news_id):
    news = get_object_or_404(News, id=news_id)
    if request.method == "POST":
        form = NewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            news = form.save(commit=False)
            if news.is_published and not news.published_at:
                news.published_at = timezone.now()
            news.save()

            # Handle multiple file uploads
            files = request.FILES.getlist('attachments')
            for f in files:
                NewsAttachment.objects.create(news=news, file=f)

            messages.success(request, f"Actualité « {news.title} » modifiée avec succès.")
            return redirect('manage_publications')
    else:
        form = NewsForm(instance=news)
    return render(request, 'analytics/prof/publication_form.html', {'form': form, 'news': news, 'title': 'Modifier l\'actualité', 'type': 'news'})


@user_passes_test(lambda u: u.is_staff)
def delete_news(request, news_id):
    news = get_object_or_404(News, id=news_id)
    title = news.title
    news.delete()
    messages.success(request, f"Actualité « {title} » supprimée.")
    return redirect('manage_publications')


@user_passes_test(lambda u: u.is_staff)
def toggle_news_publish(request, news_id):
    news = get_object_or_404(News, id=news_id)
    news.is_published = not news.is_published
    if news.is_published and not news.published_at:
        news.published_at = timezone.now()
    news.save()
    status = "publiée" if news.is_published else "masquée"
    messages.success(request, f"L'actualité « {news.title} » est maintenant {status}.")
    return redirect('manage_publications')


@user_passes_test(lambda u: u.is_staff)
def toggle_news_pin(request, news_id):
    news = get_object_or_404(News, id=news_id)
    news.is_pinned = not news.is_pinned
    news.save()
    status = "épinglée en haut" if news.is_pinned else "désépinglée"
    messages.success(request, f"L'actualité « {news.title} » est maintenant {status}.")
    return redirect('manage_publications')


@user_passes_test(lambda u: u.is_staff)
def preview_news(request, news_id):
    news = get_object_or_404(News, id=news_id)
    return render(request, 'analytics/prof/publication_preview.html', {'news': news})


@user_passes_test(lambda u: u.is_staff)
def create_publication(request):
    if request.method == "POST":
        form = PublicationForm(request.POST, request.FILES)
        if form.is_valid():
            pub = form.save()
            messages.success(request, f"Publication « {pub.title} » créée avec succès.")
            return redirect('/dashboard/publications/?tab=research')
    else:
        form = PublicationForm()
    return render(request, 'analytics/prof/publication_form.html', {'form': form, 'title': 'Créer une publication de recherche', 'type': 'research'})


@user_passes_test(lambda u: u.is_staff)
def edit_publication(request, pub_id):
    pub = get_object_or_404(Publication, id=pub_id)
    if request.method == "POST":
        form = PublicationForm(request.POST, request.FILES, instance=pub)
        if form.is_valid():
            pub = form.save()
            messages.success(request, f"Publication « {pub.title} » modifiée avec succès.")
            return redirect('/dashboard/publications/?tab=research')
    else:
        form = PublicationForm(instance=pub)
    return render(request, 'analytics/prof/publication_form.html', {'form': form, 'pub': pub, 'title': 'Modifier la publication', 'type': 'research'})


@user_passes_test(lambda u: u.is_staff)
def delete_publication(request, pub_id):
    pub = get_object_or_404(Publication, id=pub_id)
    title = pub.title
    pub.delete()
    messages.success(request, f"Publication « {title} » supprimée.")
    return redirect('/dashboard/publications/?tab=research')


# ==========================================
# 2. COURSES MANAGEMENT
# ==========================================

@user_passes_test(lambda u: u.is_staff)
def manage_courses(request):
    search_query = request.GET.get('search', '').strip()
    level_filter = request.GET.get('level', '').strip()
    status_filter = request.GET.get('status', '').strip()

    queryset = Subject.objects.all()

    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query)
        )
    if level_filter:
        queryset = queryset.filter(level=level_filter)
    if status_filter == 'published':
        queryset = queryset.filter(is_published=True, is_archived=False)
    elif status_filter == 'archived':
        queryset = queryset.filter(is_archived=True)
    elif status_filter == 'unpublished':
        queryset = queryset.filter(is_published=False, is_archived=False)

    queryset = queryset.order_by('level', 'code')
    paginator = Paginator(queryset, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    levels = Subject.LEVEL_CHOICES

    context = {
        'page_obj': page_obj,
        'search': search_query,
        'level_filter': level_filter,
        'status_filter': status_filter,
        'levels': levels
    }
    return render(request, 'analytics/prof/courses.html', context)


@user_passes_test(lambda u: u.is_staff)
def create_course(request):
    if request.method == "POST":
        form = SubjectForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save()
            messages.success(request, f"Matière « {course.name} » créée avec succès.")
            return redirect('manage_courses')
    else:
        form = SubjectForm()
    return render(request, 'analytics/prof/course_form.html', {'form': form, 'title': 'Créer un cours'})


@user_passes_test(lambda u: u.is_staff)
def edit_course(request, course_id):
    course = get_object_or_404(Subject, id=course_id)
    if request.method == "POST":
        form = SubjectForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            course = form.save()
            messages.success(request, f"Matière « {course.name} » modifiée avec succès.")
            return redirect('manage_courses')
    else:
        form = SubjectForm(instance=course)
    return render(request, 'analytics/prof/course_form.html', {'form': form, 'course': course, 'title': 'Modifier le cours'})


@user_passes_test(lambda u: u.is_staff)
def delete_course(request, course_id):
    course = get_object_or_404(Subject, id=course_id)
    name = course.name
    course.delete()
    messages.success(request, f"Cours « {name} » supprimé avec succès.")
    return redirect('manage_courses')


@user_passes_test(lambda u: u.is_staff)
def duplicate_course(request, course_id):
    original_subject = get_object_or_404(Subject, id=course_id)
    new_code = f"{original_subject.code}_copy"
    suffix = 1
    while Subject.objects.filter(code=new_code).exists():
        new_code = f"{original_subject.code}_copy{suffix}"
        suffix += 1

    duplicated_subject = Subject.objects.create(
        name=f"{original_subject.name} (Copie)",
        code=new_code,
        level=original_subject.level,
        description=original_subject.description,
        thumbnail=original_subject.thumbnail,
        is_published=False
    )
    for res in original_subject.resources.all():
        CourseResource.objects.create(
            subject=duplicated_subject,
            title=res.title,
            description=res.description,
            file=res.file,
            video_url=res.video_url,
            resource_type=res.resource_type,
            folder_name=res.folder_name
        )
    messages.success(request, f"Cours [{original_subject.code}] dupliqué en [{duplicated_subject.code}].")
    return redirect('manage_courses')


@user_passes_test(lambda u: u.is_staff)
def archive_course(request, course_id):
    course = get_object_or_404(Subject, id=course_id)
    course.is_archived = not course.is_archived
    course.save()
    status = "archivé" if course.is_archived else "restauré"
    messages.success(request, f"Le cours « {course.name} » a été {status}.")
    return redirect('manage_courses')


# ==========================================
# 3. RESOURCES MANAGEMENT
# ==========================================

@user_passes_test(lambda u: u.is_staff)
def manage_resources(request):
    subject_id = request.GET.get('subject', '')
    search_query = request.GET.get('search', '').strip()

    subjects = Subject.objects.all()
    queryset = CourseResource.objects.all()

    if subject_id:
        queryset = queryset.filter(subject_id=subject_id)
    if search_query:
        queryset = queryset.filter(title__icontains=search_query)

    # Group by folders/categories
    resources_by_folder = {}
    for res in queryset.order_by('folder_name', 'resource_type', 'title'):
        folder = res.folder_name or "Sans dossier"
        if folder not in resources_by_folder:
            resources_by_folder[folder] = []
        resources_by_folder[folder].append(res)

    context = {
        'resources_by_folder': resources_by_folder,
        'subjects': subjects,
        'selected_subject': subject_id,
        'search': search_query
    }
    return render(request, 'analytics/prof/resources.html', context)


@user_passes_test(lambda u: u.is_staff)
def create_resource(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    if request.method == "POST":
        form = CourseResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.subject = subject
            resource.save()

            # Create notification
            Notification.objects.create(
                type='COMMENT', # default log alert
                title="Nouveau support téléversé",
                message=f"Le support « {resource.title} » a été ajouté à la matière {subject.code}."
            )

            # Handle JSON response for drag and drop
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Fichier téléversé.'})

            messages.success(request, f"Ressource « {resource.title} » ajoutée.")
            return redirect(f'/dashboard/resources/?subject={subject.id}')
    else:
        form = CourseResourceForm()
    return render(request, 'analytics/prof/resource_form.html', {'form': form, 'subject': subject, 'title': 'Ajouter un support'})


@user_passes_test(lambda u: u.is_staff)
def edit_resource(request, resource_id):
    resource = get_object_or_404(CourseResource, id=resource_id)
    if request.method == "POST":
        form = CourseResourceForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            resource = form.save()
            messages.success(request, f"Ressource « {resource.title} » modifiée.")
            return redirect(f'/dashboard/resources/?subject={resource.subject.id}')
    else:
        form = CourseResourceForm(instance=resource)
    return render(request, 'analytics/prof/resource_form.html', {'form': form, 'resource': resource, 'title': 'Modifier le support'})


@user_passes_test(lambda u: u.is_staff)
def delete_resource(request, resource_id):
    resource = get_object_or_404(CourseResource, id=resource_id)
    subj_id = resource.subject.id
    title = resource.title
    resource.delete()
    messages.success(request, f"Ressource « {title} » supprimée.")
    return redirect(f'/dashboard/resources/?subject={subj_id}')


# ==========================================
# 4. E-LEARNING MANAGEMENT (Trainings & Modules)
# ==========================================

@user_passes_test(lambda u: u.is_staff)
def manage_elearning(request):
    trainings = Training.objects.all().order_by('-created_at')
    certificates = Certificate.objects.all().order_by('-issued_at')[:15]

    # Sort modules inside training list
    trainings_data = []
    for t in trainings:
        trainings_data.append({
            'obj': t,
            'modules': t.modules.all().order_by('order'),
            'certificates_count': t.certificates.count()
        })

    context = {
        'trainings': trainings_data,
        'recent_certificates': certificates
    }
    return render(request, 'analytics/prof/elearning.html', context)


@user_passes_test(lambda u: u.is_staff)
def create_training(request):
    if request.method == "POST":
        form = TrainingForm(request.POST, request.FILES)
        if form.is_valid():
            t = form.save()
            messages.success(request, f"Formation « {t.title} » créée.")
            return redirect('manage_elearning')
    else:
        form = TrainingForm()
    return render(request, 'analytics/prof/training_form.html', {'form': form, 'title': 'Créer une formation'})


@user_passes_test(lambda u: u.is_staff)
def edit_training(request, training_id):
    training = get_object_or_404(Training, id=training_id)
    if request.method == "POST":
        form = TrainingForm(request.POST, request.FILES, instance=training)
        if form.is_valid():
            training = form.save()
            messages.success(request, f"Formation « {training.title} » modifiée.")
            return redirect('manage_elearning')
    else:
        form = TrainingForm(instance=training)
    return render(request, 'analytics/prof/training_form.html', {'form': form, 'training': training, 'title': 'Modifier la formation'})


@user_passes_test(lambda u: u.is_staff)
def delete_training(request, training_id):
    training = get_object_or_404(Training, id=training_id)
    title = training.title
    training.delete()
    messages.success(request, f"Formation « {title} » supprimée.")
    return redirect('manage_elearning')


@user_passes_test(lambda u: u.is_staff)
def create_module(request, training_id):
    training = get_object_or_404(Training, id=training_id)
    if request.method == "POST":
        form = ModuleForm(request.POST, request.FILES)
        if form.is_valid():
            m = form.save(commit=False)
            m.training = training
            m.save()
            messages.success(request, f"Module « {m.title} » créé.")
            return redirect('manage_elearning')
    else:
        # Auto-compute next order value
        next_order = training.modules.count() + 1
        form = ModuleForm(initial={'order': next_order})
    return render(request, 'analytics/prof/module_form.html', {'form': form, 'training': training, 'title': 'Ajouter un module'})


@user_passes_test(lambda u: u.is_staff)
def edit_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if request.method == "POST":
        form = ModuleForm(request.POST, request.FILES, instance=module)
        if form.is_valid():
            module = form.save()
            messages.success(request, f"Module « {module.title} » modifié.")
            return redirect('manage_elearning')
    else:
        form = ModuleForm(instance=module)
    return render(request, 'analytics/prof/module_form.html', {'form': form, 'module': module, 'title': 'Modifier le module'})


@user_passes_test(lambda u: u.is_staff)
def delete_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    title = module.title
    module.delete()
    messages.success(request, f"Module « {title} » supprimé.")
    return redirect('manage_elearning')


@user_passes_test(lambda u: u.is_staff)
def reorder_modules(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            orders = data.get("orders", [])
            for item in orders:
                Module.objects.filter(id=item['id']).update(order=item['order'])
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    return JsonResponse({"success": False, "error": "Requête invalide."}, status=400)


# ==========================================
# 5. QUIZ MANAGEMENT
# ==========================================

@user_passes_test(lambda u: u.is_staff)
def create_quiz(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if request.method == "POST":
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.module = module
            quiz.save()
            messages.success(request, f"Quiz créé pour le module « {module.title} ».")
            return redirect('manage_elearning')
    else:
        form = QuizForm()
    return render(request, 'analytics/prof/quiz_form.html', {'form': form, 'module': module, 'title': 'Créer le Quiz'})


@user_passes_test(lambda u: u.is_staff)
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == "POST":
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            quiz = form.save()
            messages.success(request, f"Quiz « {quiz.title} » modifié.")
            return redirect('manage_elearning')
    else:
        form = QuizForm(instance=quiz)
    return render(request, 'analytics/prof/quiz_form.html', {'form': form, 'quiz': quiz, 'title': 'Modifier le Quiz'})


@user_passes_test(lambda u: u.is_staff)
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    title = quiz.title
    quiz.delete()
    messages.success(request, f"Quiz « {title} » supprimé.")
    return redirect('manage_elearning')


@user_passes_test(lambda u: u.is_staff)
def manage_quiz_questions(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.prefetch_related('choices').all()
    context = {
        'quiz': quiz,
        'questions': questions
    }
    return render(request, 'analytics/prof/quiz_questions.html', context)


@user_passes_test(lambda u: u.is_staff)
def create_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == "POST":
        q_form = QuestionForm(request.POST)
        if q_form.is_valid():
            question = q_form.save(commit=False)
            question.quiz = quiz
            question.save()

            # Save options/choices
            choices_text = request.POST.getlist('choice_text')
            correct_index = request.POST.get('correct_choice')

            for i, text in enumerate(choices_text):
                if text.strip():
                    is_correct = (str(i) == correct_index)
                    Choice.objects.create(question=question, text=text.strip(), is_correct=is_correct)

            messages.success(request, "Question ajoutée avec succès.")
            return redirect('manage_quiz_questions', quiz_id=quiz.id)
    else:
        q_form = QuestionForm()
    return render(request, 'analytics/prof/question_form.html', {'q_form': q_form, 'quiz': quiz, 'title': 'Créer une question'})


@user_passes_test(lambda u: u.is_staff)
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    quiz = question.quiz
    choices = question.choices.all()

    if request.method == "POST":
        q_form = QuestionForm(request.POST, instance=question)
        if q_form.is_valid():
            question = q_form.save()

            # Refresh choices
            question.choices.all().delete()
            choices_text = request.POST.getlist('choice_text')
            correct_index = request.POST.get('correct_choice')

            for i, text in enumerate(choices_text):
                if text.strip():
                    is_correct = (str(i) == correct_index)
                    Choice.objects.create(question=question, text=text.strip(), is_correct=is_correct)

            messages.success(request, "Question modifiée.")
            return redirect('manage_quiz_questions', quiz_id=quiz.id)
    else:
        q_form = QuestionForm(instance=question)

    return render(request, 'analytics/prof/question_form.html', {
        'q_form': q_form,
        'quiz': quiz,
        'question': question,
        'choices': choices,
        'title': 'Modifier la question'
    })


@user_passes_test(lambda u: u.is_staff)
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    quiz_id = question.quiz.id
    question.delete()
    messages.success(request, "Question supprimée.")
    return redirect('manage_quiz_questions', quiz_id=quiz_id)


# ==========================================
# 6. STUDENTS TRACKING
# ==========================================

@user_passes_test(lambda u: u.is_staff)
def manage_students(request):
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()

    queryset = User.objects.filter(is_staff=False)

    if search_query:
        queryset = queryset.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    if status_filter == 'active':
        queryset = queryset.filter(is_active=True)
    elif status_filter == 'suspended':
        queryset = queryset.filter(is_active=False)

    queryset = queryset.order_by('-date_joined')
    paginator = Paginator(queryset, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'search': search_query,
        'status_filter': status_filter
    }
    return render(request, 'analytics/prof/students.html', context)


@user_passes_test(lambda u: u.is_staff)
def student_detail(request, student_id):
    student = get_object_or_404(User, id=student_id, is_staff=False)

    # E-learning progress
    progress_data = []
    for t in Training.objects.all():
        progress = t.get_progress_for_user(student)
        progress_data.append({
            'training': t,
            'progress': progress
        })

    # Quiz submissions
    submissions = QuizSubmission.objects.filter(student=student).order_by('-submitted_at')

    # Download logs
    downloads = DownloadTracker.objects.filter(user=student).order_by('-timestamp')

    context = {
        'student': student,
        'progress_data': progress_data,
        'submissions': submissions,
        'downloads': downloads
    }
    return render(request, 'analytics/prof/student_detail.html', context)


# ==========================================
# 7. APPOINTMENTS SCHEDULER
# ==========================================

@user_passes_test(lambda u: u.is_staff)
def manage_appointments(request):
    if request.method == "POST":
        # Create a new slot
        start_str = request.POST.get('start_time')
        end_str = request.POST.get('end_time')

        if start_str and end_str:
            start_time = timezone.datetime.fromisoformat(start_str)
            end_time = timezone.datetime.fromisoformat(end_str)

            AppointmentSlot.objects.create(
                start_time=start_time,
                end_time=end_time,
                is_booked=False
            )
            messages.success(request, "Créneau créé avec succès sur le calendrier.")
        return redirect('manage_appointments')

    slots = AppointmentSlot.objects.all().order_by('start_time')
    context = {
        'slots': slots
    }
    return render(request, 'analytics/prof/appointments.html', context)


@user_passes_test(lambda u: u.is_staff)
def accept_appointment(request, slot_id):
    slot = get_object_or_404(AppointmentSlot, id=slot_id)
    slot.status = 'ACCEPTED'
    slot.save()

    # Notify by email
    try:
        send_mail(
            "Rendez-vous confirmé",
            f"Bonjour {slot.student_name},\n\nVotre demande de rendez-vous pour le {slot.start_time.strftime('%d/%m/%Y à %H:%M')} a été acceptée par le professeur.",
            settings.DEFAULT_FROM_EMAIL,
            [slot.student_email],
            fail_silently=True
        )
    except Exception:
        pass

    messages.success(request, f"Le rendez-vous avec {slot.student_name} a été accepté.")
    return redirect('manage_appointments')


@user_passes_test(lambda u: u.is_staff)
def reject_appointment(request, slot_id):
    slot = get_object_or_404(AppointmentSlot, id=slot_id)
    slot.status = 'REJECTED'
    slot.save()

    # Notify by email
    try:
        send_mail(
            "Rendez-vous refusé",
            f"Bonjour {slot.student_name},\n\nVotre demande de rendez-vous pour le {slot.start_time.strftime('%d/%m/%Y à %H:%M')} a été refusée par le professeur.",
            settings.DEFAULT_FROM_EMAIL,
            [slot.student_email],
            fail_silently=True
        )
    except Exception:
        pass

    messages.success(request, f"Le rendez-vous avec {slot.student_name} a été rejeté.")
    return redirect('manage_appointments')


@user_passes_test(lambda u: u.is_staff)
def reschedule_appointment(request, slot_id):
    slot = get_object_or_404(AppointmentSlot, id=slot_id)
    if request.method == "POST":
        new_start_str = request.POST.get('start_time')
        new_end_str = request.POST.get('end_time')

        if new_start_str and new_end_str:
            slot.start_time = timezone.datetime.fromisoformat(new_start_str)
            slot.end_time = timezone.datetime.fromisoformat(new_end_str)
            slot.status = 'PENDING'
            slot.save()

            # Notify by email
            try:
                send_mail(
                    "Rendez-vous déplacé",
                    f"Bonjour {slot.student_name},\n\nVotre rendez-vous a été déplacé par le professeur. La nouvelle date est le {slot.start_time.strftime('%d/%m/%Y à %H:%M')}.\nMerci de confirmer votre présence.",
                    settings.DEFAULT_FROM_EMAIL,
                    [slot.student_email],
                    fail_silently=True
                )
            except Exception:
                pass

            messages.success(request, f"Le rendez-vous avec {slot.student_name} a été déplacé.")
    return redirect('manage_appointments')


# ==========================================
# 8. NOTIFICATIONS CENTER
# ==========================================

@user_passes_test(lambda u: u.is_staff)
def manage_notifications(request):
    notifications = Notification.objects.all()
    paginator = Paginator(notifications, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'analytics/prof/notifications.html', {'page_obj': page_obj})


@user_passes_test(lambda u: u.is_staff)
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})


@user_passes_test(lambda u: u.is_staff)
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    notification.delete()
    messages.success(request, "Notification supprimée.")
    return redirect('manage_notifications')


# ==========================================
# 9. PROFESSOR PROFILE
# ==========================================

@user_passes_test(lambda u: u.is_staff)
def manage_profile(request):
    profile = ProfessorProfile.objects.first()
    if not profile:
        profile = ProfessorProfile.objects.create(name="Professeur", title="Enseignant-Chercheur", biography="Biographie...")

    if request.method == "POST":
        action = request.POST.get('action')

        if action == 'credentials':
            user_form = UserProfileForm(request.POST, instance=request.user)
            profile_form = ProfessorProfileForm(request.POST, request.FILES, instance=profile)
            password_form = PasswordChangeForm(request.user)

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, "Informations de profil mises à jour.")
                return redirect('manage_profile')

        elif action == 'password':
            user_form = UserProfileForm(instance=request.user)
            profile_form = ProfessorProfileForm(instance=profile)
            password_form = PasswordChangeForm(request.user, request.POST)

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Keep the user logged in
                messages.success(request, "Mot de passe modifié avec succès.")
                return redirect('manage_profile')
            else:
                messages.error(request, "Veuillez corriger les erreurs de mot de passe.")
    else:
        user_form = UserProfileForm(instance=request.user)
        profile_form = ProfessorProfileForm(instance=profile)
        password_form = PasswordChangeForm(request.user)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form
    }
    return render(request, 'analytics/prof/profile.html', context)


@user_passes_test(lambda u: u.is_staff)
def manage_contact_messages(request):
    search_query = request.GET.get('search', '').strip()
    messages_list = ContactMessage.objects.all().order_by('-created_at')

    if search_query:
        messages_list = messages_list.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(subject__icontains=search_query) |
            Q(message__icontains=search_query)
        )

    paginator = Paginator(messages_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search': search_query,
    }
    return render(request, 'analytics/prof/contact_messages.html', context)


@user_passes_test(lambda u: u.is_staff)
def delete_contact_message(request, msg_id):
    if request.method == "POST":
        msg = get_object_or_404(ContactMessage, id=msg_id)
        subject = msg.subject
        msg.delete()
        messages.success(request, f"Message « {subject} » supprimé avec succès.")
    return redirect('manage_contact_messages')
