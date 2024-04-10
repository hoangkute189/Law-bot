from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .forms import CustomUserCreationForm


def login_user(request):
    page = 'login'
    user = "None"

    if request.user.is_authenticated:
        return redirect('font-end-template')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request,'Tài khoản không tồn tại!')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Đăng nhập thành công!')
            return redirect('font-end-template')
        else:
            messages.error(request, 'Username or password không chính xác!')

    return render(request, 'users/login_register.html', {'page': page, 'user': user})


def register_user(request):
    page = 'register'
    form = CustomUserCreationForm()
    context = {'page': page, 'form':form}

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request, 'Tạo tài khoản thành công!')

            login(request, user)
            return redirect('font-end-template')


    return render(request, 'users/login_register.html', context=context)


def logout_user(request):
    logout(request)
    messages.success(request, 'Đăng xuất thành công!')
    return redirect('user-login')