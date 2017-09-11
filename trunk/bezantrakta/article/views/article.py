from django.shortcuts import get_object_or_404, render

from ..models import Article


def article(request, slug):
    article_values = Article.objects.values('title', 'description', 'keywords', 'text')
    # Вывод страницы, привязанной к текущему домену или ошибки 404
    article = get_object_or_404(
        article_values,
        slug=slug,
        is_published=True,
        domain_id=request.domain_id
    )

    data = {
        'title': article['title'],
        'description': article['description'],
        'keywords': article['keywords'],
        'text': article['text'],
    }
    return render(request, 'article/article.html', data)
