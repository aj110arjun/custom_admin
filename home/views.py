from .models import UserAuths
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control


@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    show_user = UserAuths.objects.all()
    return render(request, 'index.html', {'users': show_user})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login_user(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            request.session['user_email'] = user.email

            response = redirect('index')

            response.set_cookie('last_login_email', user.email, max_age=30*24*60*60)

            return response
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
    
    return render(request, 'login.html')





@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def signup_user(request):
    
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        fullname = request.POST['fullname']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return redirect('signup')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=fullname
        )
        messages.success(request, "Account created successfully. Please log in.")
        return redirect('login')

    return render(request, 'signup.html')


def logout_view(request):
    request.session.flush()
    logout(request)
    response = redirect('login')
    response.delete_cookie('last_login_email')
    messages.success(request, "Logged out successfully.")
    return response


