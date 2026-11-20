from django import forms
from django.contrib.auth.models import User
from .models import ContactMessage

class StudentRegistrationForm(forms.ModelForm):
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={"class": "form-control form-control-custom"}))
    password_confirm = forms.CharField(label="Confirmer le mot de passe", widget=forms.PasswordInput(attrs={"class": "form-control form-control-custom"}))

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control form-control-custom"}),
            "first_name": forms.TextInput(attrs={"class": "form-control form-control-custom"}),
            "last_name": forms.TextInput(attrs={"class": "form-control form-control-custom"}),
            "email": forms.EmailInput(attrs={"class": "form-control form-control-custom"}),
        }
        labels = {
            "username": "Nom d'utilisateur",
            "first_name": "Prénom",
            "last_name": "Nom de famille",
            "email": "Adresse e-mail",
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "Les mots de passe ne correspondent pas.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control form-control-custom", "placeholder": "Votre nom"}),
            "email": forms.EmailInput(attrs={"class": "form-control form-control-custom", "placeholder": "votre.email@exemple.com"}),
            "subject": forms.TextInput(attrs={"class": "form-control form-control-custom", "placeholder": "Sujet de votre message"}),
            "message": forms.Textarea(attrs={"class": "form-control form-control-custom", "rows": 5, "placeholder": "Écrivez votre message ici..."}),
        }
