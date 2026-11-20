import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import ProfessorProfile, News, ContactMessage
from courses.models import Subject, CourseResource
from elearning.models import Training, Module, Quiz, Question, Choice, StudentProgress, QuizSubmission
from scheduler.models import AppointmentSlot
from analytics.models import PageView, DownloadTracker

import os
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_dummy_pdf(title, filename, subdir='courses/docs'):
    media_dir = os.path.join(settings.MEDIA_ROOT, *subdir.split('/'))
    os.makedirs(media_dir, exist_ok=True)
    filepath = os.path.join(media_dir, filename)

    if not os.path.exists(filepath):
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'TitleStyle',
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=20
        )
        body_style = ParagraphStyle(
            'BodyStyle',
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#334155'),
            spaceAfter=12
        )

        story = [
            Paragraph(f"SUPPORT DE COURS : {title}", title_style),
            Spacer(1, 10),
            Paragraph("Ceci est un document de démonstration académique.", body_style),
            Paragraph("Ce document simule le contenu officiel du cours, incluant les concepts théoriques, les formules et les exercices pratiques associés à cette matière.", body_style),
            Paragraph("Dans une utilisation réelle, le professeur peut remplacer ce fichier par ses propres slides de cours, fiches de TD ou sujets d'examens directement depuis le panneau d'administration de Django.", body_style),
            Spacer(1, 15),
            Paragraph("<b>Contenu clé abordé :</b>", body_style),
            Paragraph("- Introduction aux concepts fondamentaux et modélisation théorique.", body_style),
            Paragraph("- Exemples d'applications pratiques et études de cas.", body_style),
            Paragraph("- Exercices types corrigés et questions d'auto-évaluation.", body_style),
        ]
        doc.build(story)

    return os.path.join(subdir, filename)

class Command(BaseCommand):
    help = "Popule la base de données avec des données de démonstration complètes et réalistes."

    def handle(self, *args, **options):
        self.stdout.write("Début du peuplement de la base de données...")

        # 1. Création des Utilisateurs
        prof_user, created = User.objects.get_or_create(
            username="prof",
            email="professeur.academix@univ.fr",
            is_staff=True,
            is_superuser=True
        )
        if created:
            prof_user.set_password("password123")
            prof_user.save()
            self.stdout.write("Utilisateur Professeur créé: 'prof' / 'password123'")

        student_user, created = User.objects.get_or_create(
            username="student",
            email="jean.dupont@etu.univ.fr",
            first_name="Jean",
            last_name="Dupont"
        )
        if created:
            student_user.set_password("password123")
            student_user.save()
            self.stdout.write("Utilisateur Étudiant créé: 'student' / 'password123'")

        # 2. Profil du Professeur
        profile, created = ProfessorProfile.objects.get_or_create(
            name="Dr. Alex Academix",
            defaults={
                "title": "Professeur des Universités en Intelligence Artificielle & Sciences des Données",
                "biography": (
                    "Alex Academix est enseignant-chercheur en informatique depuis plus de 15 ans. "
                    "Titulaire d'un doctorat en Machine Learning de l'Université Pierre et Marie Curie, "
                    "ses recherches portent sur l'apprentissage profond et l'éthique de l'IA.\n\n"
                    "Il enseigne les algorithmes d'optimisation, la science des données et la programmation Python. "
                    "Il coordonne plusieurs projets de recherche nationaux et collabore activement avec l'INRIA."
                ),
                "expertise": "Intelligence Artificielle, Machine Learning, Deep Learning, Programmation Python, Éthique des algorithmes",
                "distinctions": (
                    "Prix National de l'Innovation Pédagogique (2024)\n"
                    "Membre de l'Association Française d'Intelligence Artificielle (AFIA)\n"
                    "Meilleur Article Scientifique - Conférence Nationale d'Informatique (2022)"
                ),
                "linkedin": "https://linkedin.com",
                "github": "https://github.com",
                "twitter": "https://twitter.com",
                "google_scholar": "https://scholar.google.com"
            }
        )
        if created:
            self.stdout.write("Profil du Professeur créé.")

        # 3. Actualités / Blog
        News.objects.get_or_create(
            title="Ouverture des inscriptions aux formations E-learning",
            slug="ouverture-inscriptions-e-learning",
            defaults={
                "content": (
                    "Nous avons le plaisir de vous annoncer l'ouverture officielle de l'espace E-learning. "
                    "Vous pouvez dès aujourd'hui vous inscrire au module 'Introduction au Machine Learning' "
                    "et tester vos connaissances grâce aux quiz interactifs pour obtenir votre certificat."
                ),
                "is_published": True
            }
        )
        News.objects.get_or_create(
            title="Conférence invitée sur l'éthique de l'IA",
            slug="conference-invitee-ethique-ia",
            defaults={
                "content": (
                    "Le Dr. Academix animera une conférence publique intitulée 'Les biais algorithmiques dans l'apprentissage automatique'. "
                    "Rendez-vous le jeudi 18 juin à 14h dans l'amphithéâtre C ou en direct sur Teams."
                ),
                "is_published": True
            }
        )

        # 4. Matières & Supports
        subj_ia, created = Subject.objects.get_or_create(
            code="INF501",
            defaults={
                "name": "Introduction à l'Intelligence Artificielle",
                "level": "L3",
                "description": "Ce cours présente les bases historiques et fondamentales de l'intelligence artificielle symbolique et connexionniste."
            }
        )
        subj_python, created = Subject.objects.get_or_create(
            code="INF402",
            defaults={
                "name": "Programmation Avancée et Algorithmique Python",
                "level": "L2",
                "description": "Maîtrise des structures de données avancées, de la programmation orientée objet et de la complexité en Python."
            }
        )
        subj_dl, created = Subject.objects.get_or_create(
            code="INF603",
            defaults={
                "name": "Deep Learning et Réseaux de Neurones",
                "level": "M1",
                "description": "Conception, entraînement et optimisation d'architectures de réseaux profonds pour la vision et les séries temporelles."
            }
        )
        subj_nlp, created = Subject.objects.get_or_create(
            code="INF604",
            defaults={
                "name": "Traitement du Langage Naturel (NLP)",
                "level": "M2",
                "description": "Modèles de langue, représentation de mots vectorielle, architectures Transformers et grands modèles de langage (LLMs)."
            }
        )

        # INF501 Resources
        CourseResource.objects.get_or_create(
            subject=subj_ia,
            title="CM1 - Introduction et Historique de l'IA",
            defaults={
                "description": "Définition de l'IA, test de Turing, systèmes experts et historique depuis le Dartmouth Summer Research Project.",
                "resource_type": "COURS"
            }
        )
        CourseResource.objects.get_or_create(
            subject=subj_ia,
            title="CM2 - Algorithmes de Recherche Informée (A*)",
            defaults={
                "description": "Recherche heuristique dans les arbres et graphes de décision. Optimisation spatiale et temporelle de A*.",
                "resource_type": "COURS"
            }
        )
        CourseResource.objects.get_or_create(
            subject=subj_ia,
            title="TD1 - Recherche Guidée et Exploration d'États",
            defaults={
                "description": "Exercices d'application sur les algorithmes de recherche en largeur (BFS), profondeur (DFS) et A*.",
                "resource_type": "TD"
            }
        )
        CourseResource.objects.get_or_create(
            subject=subj_ia,
            title="TP1 - Recherche heuristique et jeu du Taquin",
            defaults={
                "description": "Implémentation d'un solveur de Taquin (8-puzzle) en Python en testant différentes heuristiques de distance (Manhattan vs. mal placées).",
                "resource_type": "TP"
            }
        )
        CourseResource.objects.get_or_create(
            subject=subj_ia,
            title="Examen Final 2024 - Intelligence Artificielle et Logique",
            defaults={
                "description": "Sujet officiel de l'examen de session 1 portant sur les systèmes de recherche, minimax et la logique des prédicats.",
                "resource_type": "EXAM"
            }
        )

        # INF402 Resources
        CourseResource.objects.get_or_create(
            subject=subj_python,
            title="CM1 - Programmation Orientée Objet avancée en Python",
            defaults={
                "description": "Héritage multiple, encapsulation, décorateurs (@property, @classmethod), méthodes spéciales (__init__, __str__, __call__).",
                "resource_type": "COURS"
            }
        )
        CourseResource.objects.get_or_create(
            subject=subj_python,
            title="TD1 - Complexité Algorithmique et Récursivité",
            defaults={
                "description": "Calcul de la complexité temporelle et spatiale avec la notation Big-O. Exercices sur les fonctions récursives.",
                "resource_type": "TD"
            }
        )
        res_tp, created = CourseResource.objects.get_or_create(
            subject=subj_python,
            title="TP1 - Analyse de données scientifiques avec Pandas et Numpy",
            defaults={
                "description": "Sujet guidé et dataset de ventes pour apprendre la manipulation de DataFrames, filtrage, agrégation et calculs vectoriels.",
                "resource_type": "TP"
            }
        )
        CourseResource.objects.get_or_create(
            subject=subj_python,
            title="Rattrapage 2024 - Programmation Python",
            defaults={
                "description": "Sujet de rattrapage orienté pratique (conception d'un outil d'analyse de fichiers de logs universitaires).",
                "resource_type": "EXAM"
            }
        )
        CourseResource.objects.get_or_create(
            subject=subj_python,
            title="Livre recommandé - Fluent Python",
            defaults={
                "description": "Ouvrage de référence de Luciano Ramalho pour maîtriser les fonctionnalités natives et avancées de Python.",
                "resource_type": "SUPP"
            }
        )

        # INF603 (Deep Learning) Resources
        CourseResource.objects.get_or_create(
            subject=subj_dl,
            title="CM1 - Du Perceptron au Réseau de Neurones Multicouche (MLP)",
            defaults={
                "description": "Modélisation biologique et mathématique du neurone, fonctions d'activation (Sigmoid, ReLu), calcul matriciel et rétropropagation du gradient.",
                "resource_type": "COURS"
            }
        )
        CourseResource.objects.get_or_create(
            subject=subj_dl,
            title="CM2 - Réseaux Convolutifs (CNN) pour la Classification d'Images",
            defaults={
                "description": "Opérations de convolution, pooling, couches denses. Analyse d'architectures historiques (LeNet, AlexNet, VGG).",
                "resource_type": "COURS"
            }
        )
        CourseResource.objects.get_or_create(
            subject=subj_dl,
            title="TD1 - Rétropropagation du Gradient Pas à Pas",
            defaults={
                "description": "Exercices théoriques de dérivation de la perte par rapport aux poids d'un réseau simple à une couche cachée.",
                "resource_type": "TD"
            }
        )
        CourseResource.objects.get_or_create(
            subject=subj_dl,
            title="TP1 - Entraînement de votre premier MLP sur MNIST avec PyTorch",
            defaults={
                "description": "Chargement des données MNIST, création du modèle MLP, boucle d'entraînement, calcul de l'Accuracy et visualisation des prédictions.",
                "resource_type": "TP"
            }
        )
        CourseResource.objects.get_or_create(
            subject=subj_dl,
            title="TP2 - Classification fine CIFAR-10 et Data Augmentation",
            defaults={
                "description": "Mise en place d'un réseau convolutif custom pour classer 10 catégories d'images. Expérimentation avec dropout et surapprentissage.",
                "resource_type": "TP"
            }
        )
        CourseResource.objects.get_or_create(
            subject=subj_dl,
            title="Examen Final 2024 - Deep Learning et Architectures Modernes",
            defaults={
                "description": "Sujet théorique et pratique portant sur le tuning d'hyperparamètres et la résolution de problèmes par vision artificielle.",
                "resource_type": "EXAM"
            }
        )
        CourseResource.objects.get_or_create(
            subject=subj_dl,
            title="Reference Book - Deep Learning (Goodfellow et al.)",
            defaults={
                "description": "Lien vers la version en ligne gratuite du livre de référence officiel du Deep Learning édité par MIT Press.",
                "resource_type": "SUPP"
            }
        )

        # INF604 (NLP) Resources
        CourseResource.objects.get_or_create(
            subject=subj_nlp,
            title="CM1 - Représentation de Mots et Embeddings (Word2Vec)",
            defaults={
                "description": "Concepts de sémantique distributionnelle, modèle Skip-Gram et Continuous Bag-of-Words (CBOW), évaluation d'embeddings.",
                "resource_type": "COURS"
            }
        )
        CourseResource.objects.get_or_create(
            subject=subj_nlp,
            title="CM2 - Architecture Transformer et Mécanisme d'Attention",
            defaults={
                "description": "Limites des RNNs, Self-Attention, Multi-Head Attention, encodeur-décodeur et architecture de base de Vaswani et al. (Attention Is All You Need).",
                "resource_type": "COURS"
            }
        )
        CourseResource.objects.get_or_create(
            subject=subj_nlp,
            title="TD1 - Mécanisme de Self-Attention à la Main",
            defaults={
                "description": "Calcul matriciel des Query, Key, Value et des scores d'attention normalisés pour une phrase simple.",
                "resource_type": "TD"
            }
        )
        CourseResource.objects.get_or_create(
            subject=subj_nlp,
            title="TP1 - Classification de Sentiments avec BERT",
            defaults={
                "description": "Utilisation de PyTorch et HuggingFace Transformers pour fine-tuner un modèle BERT pré-entraîné sur des critiques de films IMDB.",
                "resource_type": "TP"
            }
        )
        CourseResource.objects.get_or_create(
            subject=subj_nlp,
            title="TP2 - Fine-tuning LoRA de Llama-3 sur Dataset d'Instructions",
            defaults={
                "description": "Implémentation pratique du fine-tuning efficace avec PEFT / QLoRA sur GPU pour adapter Llama-3 à une tâche académique spécifique.",
                "resource_type": "TP"
            }
        )
        CourseResource.objects.get_or_create(
            subject=subj_nlp,
            title="Examen Final 2024 - Modèles de Langage et Transformers",
            defaults={
                "description": "Sujet théorique sur les architectures autoregressives, l'alignement et les métriques d'évaluation du NLP (BLEU, ROUGE).",
                "resource_type": "EXAM"
            }
        )

        # 5. E-learning : Formations, Modules et Quiz
        # Formation 1: Machine Learning
        t1, created = Training.objects.get_or_create(
            title="Introduction pratique au Machine Learning",
            defaults={
                "description": "Apprenez les bases théoriques et pratiques du Machine Learning supervisé et non supervisé avec Scikit-Learn."
            }
        )

        t1_m1, created = Module.objects.get_or_create(
            training=t1, order=1,
            defaults={
                "title": "Concepts clés et cycle de vie des données",
                "description": "Dans ce premier module, nous allons explorer les types d'apprentissage (supervisé, non supervisé) et voir comment préparer et diviser un jeu de données.",
                "video_url": "https://www.youtube.com/watch?v=aircAruvnKk"
            }
        )
        t1_m2, created = Module.objects.get_or_create(
            training=t1, order=2,
            defaults={
                "title": "Régression Linéaire et Logistique",
                "description": "Explication théorique et implémentation pratique de la régression linéaire simple/multiple et de la classification binaire avec la régression logistique.",
                "video_url": "https://www.youtube.com/watch?v=aircAruvnKk"
            }
        )
        t1_m3, created = Module.objects.get_or_create(
            training=t1, order=3,
            defaults={
                "title": "Arbres de Décision et Modèles d'Ensemble",
                "description": "Introduction aux arbres de décision (critère de Gini, entropie) et extension vers les forêts aléatoires (Random Forests) et l'algorithme XGBoost.",
                "video_url": "https://www.youtube.com/watch?v=aircAruvnKk"
            }
        )

        # Quiz pour T1 Module 1
        t1_m1_quiz, created = Quiz.objects.get_or_create(
            module=t1_m1,
            defaults={"title": "Quiz - Fondements du ML", "passing_score": 70}
        )
        q = Question.objects.get_or_create(quiz=t1_m1_quiz, text="Quel type d'apprentissage nécessite des données étiquetées ?", defaults={"points": 1})[0]
        Choice.objects.get_or_create(question=q, text="Apprentissage supervisé", defaults={"is_correct": True})
        Choice.objects.get_or_create(question=q, text="Apprentissage non supervisé", defaults={"is_correct": False})
        Choice.objects.get_or_create(question=q, text="Apprentissage par renforcement", defaults={"is_correct": False})

        q = Question.objects.get_or_create(quiz=t1_m1_quiz, text="Quelle bibliothèque Python est la référence standard pour le ML classique ?", defaults={"points": 1})[0]
        Choice.objects.get_or_create(question=q, text="Scikit-Learn", defaults={"is_correct": True})
        Choice.objects.get_or_create(question=q, text="TensorFlow", defaults={"is_correct": False})
        Choice.objects.get_or_create(question=q, text="Django", defaults={"is_correct": False})

        q = Question.objects.get_or_create(quiz=t1_m1_quiz, text="Que signifie le surapprentissage (overfitting) ?", defaults={"points": 1})[0]
        Choice.objects.get_or_create(question=q, text="Le modèle mémorise le bruit des données d'entraînement et se généralise mal", defaults={"is_correct": True})
        Choice.objects.get_or_create(question=q, text="Le modèle est trop simple pour capturer les tendances des données", defaults={"is_correct": False})
        Choice.objects.get_or_create(question=q, text="Le modèle prend trop de temps à s'entraîner", defaults={"is_correct": False})

        # Quiz pour T1 Module 2
        t1_m2_quiz, created = Quiz.objects.get_or_create(
            module=t1_m2,
            defaults={"title": "Quiz - Régression & Classification", "passing_score": 70}
        )
        q = Question.objects.get_or_create(quiz=t1_m2_quiz, text="Quelle fonction de coût est couramment minimisée pour la régression linéaire ?", defaults={"points": 1})[0]
        Choice.objects.get_or_create(question=q, text="Erreur Quadratique Moyenne (MSE)", defaults={"is_correct": True})
        Choice.objects.get_or_create(question=q, text="Entropie Croisée (Cross-Entropy)", defaults={"is_correct": False})
        Choice.objects.get_or_create(question=q, text="Erreur Absolue Moyenne (MAE)", defaults={"is_correct": False})

        q = Question.objects.get_or_create(quiz=t1_m2_quiz, text="La régression logistique sert à résoudre des problèmes de :", defaults={"points": 1})[0]
        Choice.objects.get_or_create(question=q, text="Classification", defaults={"is_correct": True})
        Choice.objects.get_or_create(question=q, text="Régression continue", defaults={"is_correct": False})
        Choice.objects.get_or_create(question=q, text="Réduction de dimension", defaults={"is_correct": False})

        # Formation 2: Deep Learning & Vision par Ordinateur
        t2, created = Training.objects.get_or_create(
            title="Deep Learning & Vision par Ordinateur",
            defaults={
                "description": "Découvrez le fonctionnement des architectures profondes et appliquez-les sur des tâches de traitement d'images complexes."
            }
        )
        t2_m1, created = Module.objects.get_or_create(
            training=t2, order=1,
            defaults={
                "title": "Introduction aux Réseaux de Neurones",
                "description": "Ce module présente le neurone formel, le calcul matriciel sous-jacent à la propagation avant (Forward Pass) et la correction des poids par descente de gradient.",
                "video_url": "https://www.youtube.com/watch?v=aircAruvnKk"
            }
        )
        t2_m2, created = Module.objects.get_or_create(
            training=t2, order=2,
            defaults={
                "title": "Vision Artificielle avec les CNNs",
                "description": "Comprenez comment les couches convolutives extraisent des features géométriques d'une image, et comment les couches de pooling réduisent la dimensionnalité.",
                "video_url": "https://www.youtube.com/watch?v=aircAruvnKk"
            }
        )
        t2_m3, created = Module.objects.get_or_create(
            training=t2, order=3,
            defaults={
                "title": "Détection d'objets en temps réel avec YOLO",
                "description": "Étudiez le fonctionnement de l'algorithme You Only Look Once (YOLO) pour la détection et la localisation simultanée de classes multiples dans une vidéo.",
                "video_url": "https://www.youtube.com/watch?v=aircAruvnKk"
            }
        )

        # Quiz pour T2 Module 2
        t2_m2_quiz, created = Quiz.objects.get_or_create(
            module=t2_m2,
            defaults={"title": "Quiz - Convolution & Pooling", "passing_score": 70}
        )
        q = Question.objects.get_or_create(quiz=t2_m2_quiz, text="Quel est le rôle principal d'une couche de Pooling dans un CNN ?", defaults={"points": 1})[0]
        Choice.objects.get_or_create(question=q, text="Réduire les dimensions spatiales des cartes de caractéristiques pour diminuer les calculs", defaults={"is_correct": True})
        Choice.objects.get_or_create(question=q, text="Ajouter de la non-linéarité au modèle", defaults={"is_correct": False})
        Choice.objects.get_or_create(question=q, text="Classifier l'image en catégories finales", defaults={"is_correct": False})

        q = Question.objects.get_or_create(quiz=t2_m2_quiz, text="Quelle fonction d'activation est la plus utilisée au sein des couches cachées d'un CNN ?", defaults={"points": 1})[0]
        Choice.objects.get_or_create(question=q, text="ReLU (Rectified Linear Unit)", defaults={"is_correct": True})
        Choice.objects.get_or_create(question=q, text="Sigmoïde", defaults={"is_correct": False})
        Choice.objects.get_or_create(question=q, text="Tangente Hyperbolique (Tanh)", defaults={"is_correct": False})

        # Formation 3: Data Science avec Python
        t3, created = Training.objects.get_or_create(
            title="Traitement de Données & Visualisation avec Python",
            defaults={
                "description": "Maîtrisez les outils incontournables de la science des données pour importer, nettoyer, explorer et visualiser tout type d'information."
            }
        )
        t3_m1, created = Module.objects.get_or_create(
            training=t3, order=1,
            defaults={
                "title": "Analyse et Manipulation de Données avec Pandas",
                "description": "Apprenez à utiliser les Series et les DataFrames de Pandas. Importation de fichiers CSV, nettoyage des valeurs manquantes et requêtes SQL-like.",
                "video_url": "https://www.youtube.com/watch?v=aircAruvnKk"
            }
        )
        t3_m2, created = Module.objects.get_or_create(
            training=t3, order=2,
            defaults={
                "title": "Visualisation Scientifique Interactive",
                "description": "Découvrez comment raconter une histoire avec les données (data storytelling) en créant des graphiques percutants avec Matplotlib et Seaborn.",
                "video_url": "https://www.youtube.com/watch?v=aircAruvnKk"
            }
        )

        # Quiz pour T3 Module 1
        t3_m1_quiz, created = Quiz.objects.get_or_create(
            module=t3_m1,
            defaults={"title": "Quiz - Pandas & DataFrames", "passing_score": 70}
        )
        q = Question.objects.get_or_create(quiz=t3_m1_quiz, text="Quelle méthode Pandas permet de grouper des données en fonction d'une colonne ?", defaults={"points": 1})[0]
        Choice.objects.get_or_create(question=q, text="groupby()", defaults={"is_correct": True})
        Choice.objects.get_or_create(question=q, text="pivot()", defaults={"is_correct": False})
        Choice.objects.get_or_create(question=q, text="merge()", defaults={"is_correct": False})

        q = Question.objects.get_or_create(quiz=t3_m1_quiz, text="Quelle fonction permet d'obtenir un résumé statistique rapide (moyenne, écart-type, quartiles) d'un DataFrame ?", defaults={"points": 1})[0]
        Choice.objects.get_or_create(question=q, text="describe()", defaults={"is_correct": True})
        Choice.objects.get_or_create(question=q, text="info()", defaults={"is_correct": False})
        Choice.objects.get_or_create(question=q, text="head()", defaults={"is_correct": False})

        # 6. Projets de Recherche et Publications
        from research.models import Publication, ResearchProject

        Publication.objects.get_or_create(
            title="Explainable Artificial Intelligence for Clinical Decision Support",
            defaults={
                "authors": "A. Academix, L. Bernard, C. Dupont",
                "pub_type": "JOURNAL",
                "journal_or_book": "IEEE Transactions on Neural Networks and Learning Systems",
                "year": 2024,
                "pages": "Vol. 35, No. 4, pp. 1120-1135",
                "abstract": "This paper presents a novel framework for interpreting complex deep learning models in healthcare datasets."
            }
        )
        Publication.objects.get_or_create(
            title="Ethical Concerns in Generative Language Models",
            defaults={
                "authors": "A. Academix, S. Martin",
                "pub_type": "CONF",
                "journal_or_book": "International Conference on Machine Learning (ICML)",
                "year": 2023,
                "pages": "pp. 450-458",
                "abstract": "We analyze semantic drift and factual errors in generative AI models across translation benchmarks."
            }
        )

        ResearchProject.objects.get_or_create(
            title="Projet ANR-IA_ETHICS : Éthique et Transparence des Algorithmes d'Apprentissage",
            defaults={
                "description": "Projet collaboratif financé par l'ANR visant à concevoir des méthodes d'explication de boîte noire pour les réseaux profonds.",
                "status": "CURRENT",
                "start_date": datetime.date(2023, 10, 1),
                "partners": "CNRS, Université de Sorbonne, INRIA Paris",
                "funding": "Agence Nationale de la Recherche (ANR)"
            }
        )

        ResearchProject.objects.get_or_create(
            title="Projet de Thèse : Apprentissage Auto-supervisé pour l'Imagerie Médicale 3D",
            defaults={
                "description": "Opportunité de thèse de doctorat de 3 ans financée par l'Université. Objectif : Réduire le besoin de données annotées en imagerie médicale par des approches contrastives auto-supervisées.",
                "status": "FUTURE",
                "start_date": datetime.date(2026, 10, 1),
                "partners": "CHU de Sorbonne, INRIA Paris",
                "funding": "Bourse ministérielle (Ministère de la Recherche)"
            }
        )

        ResearchProject.objects.get_or_create(
            title="Projet ANR-NLP_MULTILINGUAL : Modèles de Langage Souverains Multilingues",
            defaults={
                "description": "Collaboration européenne visant à développer de grands modèles de langue optimisés pour les dialectes régionaux et langues minoritaires européennes.",
                "status": "FUTURE",
                "start_date": datetime.date(2027, 1, 1),
                "partners": "LIUM, Université d'Edimbourg, BSC Barcelone",
                "funding": "Horizon Europe (En attente de validation)"
            }
        )

        ResearchProject.objects.get_or_create(
            title="Projet H2020-AI_HEALTH : Diagnostic Assisté par Intelligence Artificielle en Cardiologie",
            defaults={
                "description": "Projet européen de 4 ans ayant abouti à la création d'un système de classification automatique des ECGs par réseaux de neurones récurrents, avec un taux de précision de 98%.",
                "status": "PAST",
                "start_date": datetime.date(2020, 1, 1),
                "end_date": datetime.date(2023, 12, 31),
                "partners": "Inserm, AP-HP, Siemens Healthineers",
                "funding": "Union Européenne (Horizon 2020)"
            }
        )

        ResearchProject.objects.get_or_create(
            title="Projet CNRS-ROBUST : Robustesse des Modèles face aux Attaques Adversariales",
            defaults={
                "description": "Étude théorique et applicative sur la sécurité des réseaux profonds. Développement de techniques d'entraînement adversarial robuste face aux perturbations d'images.",
                "status": "PAST",
                "start_date": datetime.date(2018, 9, 1),
                "end_date": datetime.date(2021, 8, 31),
                "partners": "CNRS, Université Paris-Saclay",
                "funding": "CNRS Défi INPhyNi"
            }
        )


        # 7. Créneaux de Rendez-vous (Scheduler)
        now = timezone.now()

        # 1 slot in the past (booked)
        t_past_start = now - datetime.timedelta(days=1)
        t_past_end = t_past_start + datetime.timedelta(minutes=30)
        AppointmentSlot.objects.get_or_create(
            start_time=t_past_start,
            end_time=t_past_end,
            defaults={
                "is_booked": True,
                "student": student_user,
                "student_name": "Jean Dupont",
                "student_email": "jean.dupont@etu.univ.fr",
                "student_notes": "Sujet de mémoire de recherche L3"
            }
        )

        # 2 slots in the future (1 free, 1 booked)
        t_fut1_start = now + datetime.timedelta(days=2, hours=10) # 10:00 AM
        t_fut1_end = t_fut1_start + datetime.timedelta(minutes=30)
        AppointmentSlot.objects.get_or_create(
            start_time=t_fut1_start,
            end_time=t_fut1_end,
            defaults={"is_booked": False}
        )

        t_fut2_start = now + datetime.timedelta(days=3, hours=14, minutes=30) # 2:30 PM
        t_fut2_end = t_fut2_start + datetime.timedelta(minutes=30)
        AppointmentSlot.objects.get_or_create(
            start_time=t_fut2_start,
            end_time=t_fut2_end,
            defaults={
                "is_booked": True,
                "student": student_user,
                "student_name": "Jean Dupont",
                "student_email": "jean.dupont@etu.univ.fr",
                "student_notes": "Aide sur les exercices du TD 1"
            }
        )

        # 8. Logs et Statistiques fictifs (pour peupler les graphiques de démo)
        # Visits Log
        PageView.objects.create(page_name="Accueil", user=None)
        PageView.objects.create(page_name="Accueil", user=student_user)
        PageView.objects.create(page_name="Supports de cours", user=student_user)
        PageView.objects.create(page_name="E-learning", user=student_user)
        PageView.objects.create(page_name="Recherche et Publications", user=None)
        PageView.objects.create(page_name="Contact et RDV", user=None)

        # Downloads Log
        DownloadTracker.objects.create(resource=res_tp, user=student_user)
        DownloadTracker.objects.create(resource=res_tp, user=None)

        # Student E-learning progress
        StudentProgress.objects.get_or_create(
            student=student_user,
            module=t1_m1,
            defaults={"completed": True}
        )

        # Ensure all CourseResources have a dummy PDF file associated
        for resource in CourseResource.objects.all():
            if not resource.file:
                # generate filename safe from special characters
                safe_title = "".join([c if c.isalnum() else "_" for c in resource.title])
                filename = f"resource_{resource.id}_{safe_title}.pdf"
                relative_path = create_dummy_pdf(resource.title, filename, subdir='courses/docs')
                resource.file = relative_path
                resource.save()

        # Ensure all Modules have a dummy PDF file associated
        for module in Module.objects.all():
            if not module.downloadable_file:
                safe_title = "".join([c if c.isalnum() else "_" for c in module.title])
                filename = f"module_{module.id}_{safe_title}.pdf"
                relative_path = create_dummy_pdf(module.title, filename, subdir='elearning/modules')
                module.downloadable_file = relative_path
                module.save()

        self.stdout.write(self.style.SUCCESS("Base de données peuplée avec succès !"))
