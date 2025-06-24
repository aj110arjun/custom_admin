from .models import UserAuths
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re


# Welcome Page View
@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    show_user = UserAuths.objects.all()
    return render(request, 'index.html', {'users': show_user})

# Login View
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login_user(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        errors = {}

        if not username:
            errors['username'] = "Username is required."
        if not password:
            errors['password'] = "Password is required."

        if errors:
            return render(request, 'login.html', {
                'errors': errors,
                'form_data': {
                    'username': username,
                }
            })

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_staff:
                errors['staff_user'] = "Admin Users can't log in here."
                return render(request, 'login.html', {
                    'errors': errors,
                    'form_data': {'username': username}
                })

            login(request, user)

            request.session['user_email'] = user.email

            response = redirect('index')
            response.set_cookie('last_login_email', user.email, max_age=30*24*60*60)

            return response
        else:
            errors['username'] = "Invalid username"
            return render(request, 'login.html', {
                'errors': errors,
                'form_data': {'username': username}
            })

    return render(request, 'login.html')





# Signup View
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def signup_user(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name','').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()

        errors = {}

        if not first_name:
            errors['first_name'] = "First name is required."
        if not username:
            errors['username'] = "Username is required."
        if not email:
            errors['email'] = "Email is required."
        if not password1 or not password2:
            errors['password'] = "Password fields cannot be empty."

        if password1 != password2:
            errors['password_match'] = "Passwords do not match."
        elif len(password1) < 6:
            errors['password'] = "Password must be at least 6 characters long."

        if first_name and not re.match(r'^[A-Za-z\s]+$', first_name):
            errors['first_name'] = "First Name must contain only letters and spaces."
        if last_name and not re.match(r'^[A-Za-z\s]+$', last_name):
            errors['last_name'] = "Last Name must contain only letters and spaces."

        try:
            validate_email(email)
        except ValidationError:
            errors['email'] = "Enter a valid email address."

        if User.objects.filter(username=username).exists():
            errors['username'] = "Username already taken."
        if User.objects.filter(email=email).exists():
            errors['email'] = "Email already in use."

        if errors:
            for error in errors.values():
                messages.error(request, error)

            return render(request, 'signup.html', {
                'form_data': {
                    'first_name': first_name,
                    'last_name': last_name,
                    'username': username,
                    'email': email,
                },
                'errors': errors,  
            })


        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )
        messages.success(request, "Account created successfully. Please log in.")
        return redirect('login')

    return render(request, 'signup.html')
# Logout View
def logout_view(request):
    request.session.flush()
    logout(request)
    response = redirect('login')
    response.delete_cookie('last_login_email')
    messages.success(request, "Logged out successfully.")
    return response


