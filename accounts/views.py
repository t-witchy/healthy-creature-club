from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .forms import LoginForm
from .forms import SignupForm


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Signup successful! Welcome to Healthy Creature Club.")
            return redirect('/')  # Redirect to your homepage or dashboard
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST, request=request)
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                login(request, user)
                remember_me = request.POST.get('remember-me', None)
                if not remember_me:
                    # If remember me is not checked, set session to expire when browser closes
                    request.session.set_expiry(0)
                else:
                    # If remember me is checked, set a longer session expiry
                    # For example, 2 weeks:
                    request.session.set_expiry(1209600)

                messages.success(request, "You are now logged in!")
                return redirect('index')  # Redirect to a homepage or dashboard
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})