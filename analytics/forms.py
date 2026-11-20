from django import forms
from django.contrib.auth.models import User
from core.models import News, NewsAttachment, ProfessorProfile
from courses.models import Subject, CourseResource
from elearning.models import Training, Module, Quiz, Question, Choice
from research.models import Publication
from scheduler.models import AppointmentSlot

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'slug', 'content', 'image', 'is_published', 'is_pinned', 'published_at']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Titre de l\'actualité'}),
            'slug': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'slug-de-l-actualite'}),
            'content': forms.Textarea(attrs={'class': 'form-control form-control-custom', 'rows': 6, 'placeholder': 'Contenu...'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control form-control-custom'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'published_at': forms.DateTimeInput(attrs={'class': 'form-control form-control-custom', 'type': 'datetime-local'}),
        }


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['title', 'authors', 'pub_type', 'journal_or_book', 'year', 'pages', 'abstract', 'pdf_file', 'code_link', 'data_link', 'doi']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-custom'}),
            'authors': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Ex: A. Dupont, B. Martin'}),
            'pub_type': forms.Select(attrs={'class': 'form-select form-control-custom'}),
            'journal_or_book': forms.TextInput(attrs={'class': 'form-control form-control-custom'}),
            'year': forms.NumberInput(attrs={'class': 'form-control form-control-custom'}),
            'pages': forms.TextInput(attrs={'class': 'form-control form-control-custom'}),
            'abstract': forms.Textarea(attrs={'class': 'form-control form-control-custom', 'rows': 4}),
            'pdf_file': forms.ClearableFileInput(attrs={'class': 'form-control form-control-custom'}),
            'code_link': forms.URLInput(attrs={'class': 'form-control form-control-custom'}),
            'data_link': forms.URLInput(attrs={'class': 'form-control form-control-custom'}),
            'doi': forms.TextInput(attrs={'class': 'form-control form-control-custom'}),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'level', 'description', 'thumbnail', 'is_published', 'is_archived']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-custom'}),
            'code': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Ex: INF401'}),
            'level': forms.Select(attrs={'class': 'form-select form-control-custom'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-custom', 'rows': 4}),
            'thumbnail': forms.ClearableFileInput(attrs={'class': 'form-control form-control-custom'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_archived': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CourseResourceForm(forms.ModelForm):
    class Meta:
        model = CourseResource
        fields = ['title', 'description', 'file', 'video_url', 'resource_type', 'folder_name']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-custom'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-custom', 'rows': 3}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control form-control-custom'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'https://...'}),
            'resource_type': forms.Select(attrs={'class': 'form-select form-control-custom'}),
            'folder_name': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Ex: Chapitre 1 (optionnel)'}),
        }


class TrainingForm(forms.ModelForm):
    class Meta:
        model = Training
        fields = ['title', 'description', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-custom'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-custom', 'rows': 4}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control form-control-custom'}),
        }


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'video_url', 'downloadable_file', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-custom'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-custom', 'rows': 4}),
            'video_url': forms.URLInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'https://...'}),
            'downloadable_file': forms.ClearableFileInput(attrs={'class': 'form-control form-control-custom'}),
            'order': forms.NumberInput(attrs={'class': 'form-control form-control-custom'}),
        }


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'passing_score']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-custom'}),
            'passing_score': forms.NumberInput(attrs={'class': 'form-control form-control-custom', 'min': 0, 'max': 100}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'points']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control form-control-custom', 'rows': 3}),
            'points': forms.NumberInput(attrs={'class': 'form-control form-control-custom'}),
        }


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control form-control-custom'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProfessorProfileForm(forms.ModelForm):
    class Meta:
        model = ProfessorProfile
        fields = ['name', 'title', 'biography', 'expertise', 'distinctions', 'avatar', 'linkedin', 'github', 'twitter', 'google_scholar']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-custom'}),
            'title': forms.TextInput(attrs={'class': 'form-control form-control-custom'}),
            'biography': forms.Textarea(attrs={'class': 'form-control form-control-custom', 'rows': 5}),
            'expertise': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Matières séparées par des virgules'}),
            'distinctions': forms.Textarea(attrs={'class': 'form-control form-control-custom', 'rows': 3, 'placeholder': 'Une par ligne'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control form-control-custom'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control form-control-custom'}),
            'github': forms.URLInput(attrs={'class': 'form-control form-control-custom'}),
            'twitter': forms.URLInput(attrs={'class': 'form-control form-control-custom'}),
            'google_scholar': forms.URLInput(attrs={'class': 'form-control form-control-custom'}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control form-control-custom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-control-custom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-custom'}),
        }
