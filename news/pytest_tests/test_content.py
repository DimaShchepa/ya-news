import pytest
from django.urls import reverse

from yanews import settings


@pytest.mark.django_db
def test_count_news_limit_on_home_page(client):
    """
    Проверяется лимит новостей на главной странице.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_sorted_by_date_desc(client):
    """
    Проверяет, что новости на главной странице отсортированы по дате:
    от новых к старым.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    dates = [news.date for news in object_list]

    expected_dates = sorted(dates, reverse=True)

    assert dates == expected_dates


@pytest.mark.django_db
def test_comments_chronological_order(client, news):
    """
    Проверяется хронологический порядок новостей.
    """
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    news_object = response.context.get('news')

    comment_list = list(news_object.comment_set.all())
    displayed_dates = [comment.created for comment in comment_list]
    expected_dates = sorted(displayed_dates)
    assert displayed_dates == expected_dates


@pytest.mark.django_db
def test_comment_form_visibility(client, news, not_author_client):
    """
    Проверяет видимость формы комментария для анонимных и
    авторизованных пользователей.
    """
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response_anonimous = client.get(url)
    assert 'form' not in response_anonimous.context

    response_authorized = not_author_client.get(url)
    assert 'form' in response_authorized.context
