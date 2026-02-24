import pytest
from http import HTTPStatus

from django.urls import reverse

from news.forms import WARNING, BAD_WORDS
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_cant_create_comment(client, news, form_data):
    """
    Проверяется, что анонимному пользователю нельзя создавать комментарии.
    """
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_redirect = f'{login_url}?next={url}'
    assert response.url == expected_redirect
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_user_can_cteate_comment(news, author_client,
                                        author, form_data):
    """
    Происходит проверка, что авторизованный пользователь
    имеет право создавать комментарии.
    """
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = author_client.post(url, data=form_data)
    redirected_url = response.url.split('#')[0]
    assert redirected_url == url

    assert Comment.objects.count() == 1

    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


@pytest.mark.django_db
def test_censorship_of_comments(author_client, news, form_data):
    """
    Проверяет, что комментарий с запрещёнными словами не публикуется.
    """
    url = reverse('news:detail', kwargs={'pk': news.pk})
    form_data['text'] = f'{WARNING}, {BAD_WORDS}'
    response = author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_not_author_cant_edit_comments(not_author_client, author, comment):
    """
    Не автор не может редактировать чужие комментарии.
    """
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    form_data = {'text': 'Отредактированный текст'}
    response = not_author_client.post(url, data=form_data)

    assert response.status_code in [HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND]

    comment.refresh_from_db()
    assert comment.text != form_data['text']
    assert comment.author == author


@pytest.mark.django_db
def test_not_author_cant_delete_comments(not_author_client, comment):
    """
    Не автор не имеет право удалять чужие комментарии.
    """
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = not_author_client.post(url)

    assert response.status_code in [HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND]

    assert Comment.objects.filter(pk=comment.pk).exists()


@pytest.mark.django_db
def test_author_can_edit_comments(author_client, news, author, comment):
    """
    Автор может редактировать свои комментарии.
    """
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    form_data = {'text': 'Отредактированный текст'}
    response = author_client.post(url, data=form_data)

    assert response.status_code == HTTPStatus.FOUND

    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == author

    expected_redirect = f'{reverse('news:detail',
                                   kwargs={'pk': news.pk})}#comments'
    assert response.url == expected_redirect


@pytest.mark.django_db
def test_author_can_delete_comments(author_client, news, comment):
    """
    Автор может удалять свои комментарии.
    """
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = author_client.post(url)

    assert response.status_code == HTTPStatus.FOUND

    assert not Comment.objects.filter(pk=comment.pk).exists()

    expected_redirect = f'{reverse('news:detail',
                                   kwargs={'pk': news.pk})}#comments'
    assert response.url == expected_redirect
