from django.shortcuts import get_object_or_404, render

from ..models import Article


def article(request, slug):
    """Вывод HTML-страницы, привязанной к текущему сайту.

    Если запрошенная страница не существует - выдаётся ошибка 404.

    Args:
        slug (str): Псевдоним HTML-страницы.
    """
    article_values = Article.objects.values(
        'title',
        'description',
        'keywords',
        'text'
    )

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
