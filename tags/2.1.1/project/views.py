from django.contrib.messages import get_messages
from django.shortcuts import redirect, render


def error(request):
    """Вывод сообщений для пользователя, как правило, в случае ошибок на сайте.

    Сообщения об ошибках выводятся, если они актуальны, иначе - редирект на главную страницу.
    """
    context = {}
    return (
        render(request, 'error.html', context, status=400) if
        get_messages(request) else
        redirect('/')
    )


def error_400(request):
    context = {}
    return (
        render(request, 'error.html', context, status=400) if
        get_messages(request) else
        redirect('/')
    )


def error_403(request):
    context = {}
    return (
        render(request, 'error.html', context, status=403) if
        get_messages(request) else
        redirect('/')
    )


def error_404(request):
    context = {}
    return (
        render(request, 'error.html', context, status=404) if
        get_messages(request) else
        redirect('/')
    )


def error_410(request):
    context = {}
    return (
        render(request, 'error.html', context, status=410) if
        get_messages(request) else
        redirect('/')
    )


def error_500(request):
    context = {}
    return (
        render(request, 'error.html', context, status=500) if
        get_messages(request) else
        redirect('/')
    )


def error_503(request):
    context = {}
    return (
        render(request, 'error.html', context, status=503) if
        get_messages(request) else
        redirect('/')
    )
