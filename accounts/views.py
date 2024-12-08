from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignupForm

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to a home page or dashboard
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})