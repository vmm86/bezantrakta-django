from django.shortcuts import get_object_or_404, render

from .models import Article


def show_index(request):
    data = {
        'title': 'Hello, world!',
        'text': '<p>You`re at the pages index!</p>'
    }
    return render(request, 'article/article.html', data)


def show_article(request, slug):
    article_values = Article.objects.values('title', 'description', 'keywords', 'text')
    # Выдаём страницу, привязанную к текущему домену или ошибку 404
    article = get_object_or_404(article_values, slug=slug, is_published=True, domain_id=request.domain_id)

    data = {
        'title': article['title'],
        'description': article['description'],
        'keywords': article['keywords'],
        'text': article['text'],
    }
    return render(request, 'article/article.html', data)
