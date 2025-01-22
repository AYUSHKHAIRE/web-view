from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout

# Create your views here.


def index(request):
    return render(request, 'core/index.html')


def Register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if confirm_password == password:
            if User.objects.filter(username=username).exists():
                messages.info(request, "This user already exists ")
                return redirect("register")
            else:
                if User.objects.filter(email=email).exists():
                    messages.info(request, "This email address already exists")
                    return redirect('register')
                else:
                    user = User.objects.create_user(
                        username=username, email=email, password=password)
                    user.save()
                    our_user = authenticate(
                        username=username, password=password)
                    if our_user is not None:
                        login(request, our_user)
                        messages.success(
                            request, f'welcome to ecom !! dear {username} ')
                        return redirect('/', username=username)

        else:
            messages.info(request, "Please enter same password in both fields")
            return redirect('register')
    return render(request, 'accounts/register.html')


def Login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            messages.info(request, 'Please enter both username and password.')
            return render(request, 'accounts/login.html')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome to datan, dear {username}!')
            return redirect('/', username=username)
        else:
            messages.info(
                request, 'Login failed. Please check your username/password.')
    return render(request, 'accounts/login.html')


def Logout(request):
    logout(request)
    messages.success(
        request, f'logged out successfully !!')
    return redirect('/')