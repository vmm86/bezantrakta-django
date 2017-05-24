from django.http import Http404
from django.shortcuts import render

from .models import Article


def show_index(request):
    data = {
        'article_title': 'Hello, world!',
        'article_text': '<p>You`re at the pages index!</p>',
    }
    return render(request, 'article.html', data)


def show_article(request, article_slug):
    # Сначала ищем страницу, привязанную к текущему домену
    try:
        article = Article.objects.get(
            slug=article_slug,
            domain__slug=request.domain_slug,
        )
    except Article.DoesNotExist:
        # Затем ищем "общую" страницу, не привязанную ни к одному из доменов
        try:
            article = Article.objects.get(
                slug=article_slug,
                domain__slug=None,
            )
        except Article.DoesNotExist:
            # Если не находим ничего - ошибка 404
            raise Http404(
                'К сожалению, запрошенная Вами страница не существует'
            )

    data = {
        'article_title': article.title,
        'article_text': article.text,
    }
    return render(request, 'article.html', data)
