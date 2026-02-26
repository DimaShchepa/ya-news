from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf


@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client):
    """
    Главная страница доступна анонимному пользователю.
    """
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
        'name,news_obj',
        (('news:home', None),
         ('news:detail', pytest.lazy_fixture('news')),
         ('users:login', None),
         ('users:signup', None))
)
@pytest.mark.django_db
def test_detail_news_availability_for_anonymous_user(client, name, news_obj):
    """
    Происходит проверка:
    1. Анонимный пользователь может открывать отдельные новости.
    2. Запрос анонимного пользователя на выход из системы перенаправляет
    на домашнюю страницу
    """
    kwargs = {}

    if name == 'news:detail' and news_obj is not None:
        kwargs['pk'] = news_obj.pk

    url = reverse(name, kwargs=kwargs)
    if name == 'users:logout':
        response = client.post(url)
        assert response.status_code == HTTPStatus.FOUND
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, name, expected_status',
    [
        (lf('not_author_client'), 'news:detail', HTTPStatus.OK),

        (lf('not_author_client'), 'news:edit', HTTPStatus.NOT_FOUND),
        (lf('not_author_client'), 'news:delete', HTTPStatus.NOT_FOUND),

        (lf('author_client'), 'news:detail', HTTPStatus.OK),
        (lf('author_client'), 'news:edit', HTTPStatus.OK),
        (lf('author_client'), 'news:delete', HTTPStatus.OK),
    ],
)
@pytest.mark.django_db
def test_comment_deletion_and_editing_pages_are_available_to_author(
        parametrized_client, name, comment, expected_status
        ):
    """
    Проверяет доступность страниц редактирования и удаления комментариев
    для разных типов пользователей.
    """
    url = reverse(name, kwargs={'pk': comment.pk})
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('slug_for_args')),
        ('news:delete', pytest.lazy_fixture('slug_for_args')),
    ),
)
@pytest.mark.django_db
def test_redirects(client, name, args):
    """
    Неавторизованный пользователь, перенаправляется на страницу входа,
    при попытке редактирования или удаления комментария.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
