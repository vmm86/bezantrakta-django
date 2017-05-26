from django.http import Http404
from django.shortcuts import render

from .models import Article


def show_index(request):
    data = {
        'article_title': 'Hello, world!',
        'article_text': '<p>You`re at the pages index!</p>',
    }
    return render(request, 'article.html', data)


def show_article(request, slug):
    article = Article.objects.filter(slug=slug, is_published=True,)
    # Сначала ищем страницу, привязанную к текущему домену
    try:
        article = article.get(domain__slug=request.domain,)
    except Article.DoesNotExist:
        # Затем ищем "общую" страницу, не привязанную ни к одному из доменов
        try:
            article = article.get(domain__slug=None,)
        except Article.DoesNotExist:
            # Если не находим ничего - ошибка 404
            raise Http404(
                'К сожалению, запрошенная Вами страница не существует'
            )

    data = {
        'article_title': article.title,
        'article_description': article.description,
        'article_keywords': article.keywords,
        'article_text': article.text,
    }
    return render(request, 'article.html', data)
