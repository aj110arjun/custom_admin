from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control, never_cache
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import Q
import re


# Login View
@never_cache
def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('custom_admin_home')

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        errors={}

        if not username:
            errors['username'] = "Username is required"
        if not password:
            errors['password'] = "Password is required"

        if user is not None: 
            if user.is_staff:

                login(request, user)

                request.session['admin_username'] = user.username
                request.session.set_expiry(3600)  

                response = redirect('custom_admin_home')
                response.set_cookie('admin_email', user.email, max_age=7*24*60*60)  
                return response
            else:
                errors['username'] = 'Access denied. Not an admin user.'
                return render(request, 'custom_admin/login.html', {'errors': errors, 'form_data': {'username':username}})
        else:
            errors['common'] = 'Invalid username or password'
            return render(request, 'custom_admin/login.html', {'errors': errors, 'form_data': {'username':username}})

    return render(request, 'custom_admin/login.html')


# Dashboard View
@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def custom_admin_home(request):
    admin_name = request.session.get('admin_username', 'Unknown Admin')
    total_users = User.objects.count()
    active_users = User.objects.filter(is_staff=False).count()
    staff_users = User.objects.filter(is_staff=True).count()

    query = request.GET.get('q')
    if query:
        search = User.objects.filter(name__icontains=query)
    else:
        search = User.objects.all()

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'staff_users': staff_users,
        'admin_name': admin_name,
        'query': query,
        'search': search,
    }
    return render(request, 'custom_admin/main.html', context)


# Staff View
@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def users(request):
    query = request.GET.get('q')

    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )
    else:
        users = User.objects.all()

    context = {
        'users': users,
        'query': query,
    }
    return render(request, 'custom_admin/users.html', context)


# Logout View
@never_cache
def logout_then_redirect(request):
    request.session.flush()
    logout(request)

    response = redirect('admin_login')
    response.delete_cookie('admin_email')

    return response


# Edit User View
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='admin_login')
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    errors = {}

    if request.method == 'POST':
        user.username = request.POST['username']
        user.email = request.POST['email']
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.is_staff = True if request.POST.get('is_staff') == 'on' else False

        if not user.first_name:
            errors['first_name'] = "First name is required."
        elif not re.match(r'^[A-Za-z]+$', user.first_name):
            errors['first_name'] = "First name must contain only letters."

        if user.last_name and not re.match(r'^[A-Za-z\s]+$', user.last_name):
            errors['last_name'] = "Last name must contain only letters and spaces."

        if not user.username:
            errors['username'] = "Username is required."

        if not user.email:
            errors['email'] = "Email is required."

        new_password = request.POST.get("new_password", "").strip()
        confirm_password = request.POST.get("confirm_password", "").strip()

        if new_password or confirm_password:
            if new_password != confirm_password:
                errors['password'] = "Passwords do not match."
            elif len(new_password) < 6:
                errors['password'] = "Password must be at least 6 characters long."
            else:
                user.set_password(new_password)

        if not errors:
            user.save()
            messages.success(request, "User updated successfully.")
            if not user.is_staff:
                return redirect('nonstaffs')
            

    return render(request, 'custom_admin/edit_user.html', {'user': user, 'errors': errors})


# Delete User View
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect('nonstaffs')


# Nonstaff View
@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def nonstaffs(request):
    query = request.GET.get('q')

    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )
    else:
        users = User.objects.all()

    context = {
        'users': users,
        'query': query,
    }

    return render(request, 'custom_admin/nonstaff.html', context)


# Create User View
@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def create_user(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        is_staff = request.POST.get('is_staff') == 'on'

        errors = {}

        if not first_name:
            errors['first_name'] = "First name is required."
        elif not re.match(r'^[A-Za-z]+$', first_name):
            errors['first_name'] = "First name must contain only letters."

        if last_name and not re.match(r'^[A-Za-z\s]+$', last_name):
            errors['last_name'] = "Last name must contain only letters and spaces."

        if not username:
            errors['username'] = "Username is required."
        elif User.objects.filter(username=username).exists():
            errors['username'] = "Username already exists."

        if not email:
            errors['email'] = "Email is required."
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors['email'] = "Enter a valid email address."
            else:
                if User.objects.filter(email=email).exists():
                    errors['email'] = "Email is already in use."
        if not password:
            errors['password'] = "Password is required."
        elif len(password) < 6:
            errors['password'] = "Password must be at least 6 characters long."

        if errors:
            return render(request, 'custom_admin/create_user.html', {
                'errors': errors,
                'form_data': {
                    'first_name': first_name,
                    'last_name': last_name,
                    'username': username,
                    'email': email,
                    'is_staff': is_staff
                }
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=is_staff
        )
        messages.success(request, "User created successfully.")
        return redirect('nonstaffs')

    return render(request, 'custom_admin/create_user.html')





