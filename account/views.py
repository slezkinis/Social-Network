from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, RegisterForm, VerificateForm
from django.core.mail import send_mail
import random
import datetime


def user_login(request):
    errors = []
    if request.method == 'GET' and request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if user.profile.is_verificated:
                        return redirect('/')
                    else:
                        return redirect('/auth/verificate')
                else:
                    errors.append('Аккаунт отключён! Напишите разрабам)!')
            else:
                errors.append('Неправильный логин или пароль')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form, "errors": errors})


def register(request):
    errors = []
    if request.method == 'GET' and request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')
            if password != password2:
                errors.append('Пароли не совпадают!')
                pass
            else:
                users = User.objects.filter(email=email)
                if users:
                    errors.append('Аккаунт с таким имейлом уже существует!')
                    pass
                else:
                    if User.objects.filter(username=username):
                        errors.append('Аккаунт с таким именем пользователя уже существует!')
                        pass
                    else:
                        user = User.objects.create_user(username=username, email=email, password=password)
                        user.profile.code = random.randint(1000, 9999)
                        user.profile.save()
                        send_mail('Подтверждение аккаунта', f'Недавно вы зарегистрировались на нашей платформе. Ниже проверочный код: \n{user.profile.code}', 'register@slezkinis.ru', [user.email])
                        login(request, user)
                        return redirect('/auth/verificate')
    else:
        form = RegisterForm()
    return render(request, 'account/signup.html', {'form': form, "errors": errors})


def verificate(request):
    errors = []
    if not request.user.is_authenticated or (request.method == 'GET' and request.user.profile.is_verificated):
        return redirect('/')
    if request.method == 'POST':
        form = VerificateForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            user = request.user
            if not code.isdigit():
                errors.append('Неверный код подтверждения')
                pass
            else:
                if user.profile.code == int(code):
                    user.profile.is_verificated = True
                    user.profile.save()
                    return redirect('/')
                else:
                    errors.append('Неверный код подтверждения')
                    pass
    else:
        form = VerificateForm()
    return render(request, 'account/verificate.html', {'form': form, "errors": errors})


def update_code(request):
    if request.user.is_authenticated and 'auth/verificate/' in request.META.get("HTTP_REFERER"):
        if request.user.profile.last_generated_code is None or datetime.datetime.now().minute - request.user.profile.last_generated_code.minute >= 1:
            user = request.user
            user.profile.code = random.randint(1000, 9999)
            user.profile.last_generated_code = datetime.datetime.now()
            user.profile.save()
            send_mail('Подтверждение аккаунта', f'Сейчас был сгенерирован новый проверочный код. \n{user.profile.code}', 'register@slezkinis.ru', [user.email])
            print(request.META.get("HTTP_REFERER"))
        else:
            pass
        return redirect(request.META.get("HTTP_REFERER", "/"))
    return redirect('/')


def logout_view(request):
    if request.method == 'GET' and request.user.is_authenticated:
        user = request.user
        context = {
            'avatar': request.build_absolute_uri(f'/media/{user.profile.avatar}'),
            'name': user.username
        }
        return render(request, 'account/logout.html', context=context)
    elif request.method == 'POST':
        logout(request)
        return redirect('/')
    else:
        return redirect('/')
    