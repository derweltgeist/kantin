from django import forms
from django.core.mail import EmailMessage
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()

def verify_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    verify_path = reverse("activate", kwargs={"uidb64": uid, "token": token})
    verify_url = request.build_absolute_uri(verify_path)

    msg = EmailMessage(
        subject="Kantin ITB: Verify your email address",
        body=f"Click the link to activate your account:\n\n{verify_url}\n",
        from_email=None,  # Uses DEFAULT_FROM_EMAIL from settings.py
        to=[user.email],
    )
    msg.encoding = "utf-8"
    msg.send()
    
class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email", "username", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_active = False
        user.username = self.cleaned_data["username"]
        if commit:
            user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password:
            user = User(email=email) if email else None
            try:
                validate_password(password, user=user)
            except ValidationError as e:
                self.add_error("password", e)

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "Passwords do not match.")

        return cleaned_data


class LoginForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_active = False
        user.username = self.cleaned_data["username"]
        if commit:
            user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            self.user = authenticate(
                self.request,
                username=email,  # or email=email depending on your custom User USERNAME_FIELD
                password=password,
            )
            if self.user is None:
                raise forms.ValidationError("Invalid email or password.")
            if not self.user.is_active:
                raise forms.ValidationError("This account is not activated.")

        return cleaned_data