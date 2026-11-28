from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from .forms import SignupForm, LoginForm, verify_email

User = get_user_model()

# Create your views here.
def signup(request):
    status = "hidden"
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            verify_email(request, user)
            status = ""
    else:
        form = SignupForm()
    return render(request, "account/signup.html", {"form": form, "display" : status})

def login(request):
    if request.user.is_authenticated:
        return redirect("/home")  # replace with your target url name

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            return redirect("home")
    else:
        form = LoginForm()

    return render(request, "account/login.html", {"form": form})

def activate(request, uidb64, token):
    message = ""

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=["is_active"])
            user.backend = "django.contrib.auth.backends.ModelBackend"
            login(request)
            return redirect("home")

    return render(request, "account/invalid.html", {"message" : message}, status=400)
