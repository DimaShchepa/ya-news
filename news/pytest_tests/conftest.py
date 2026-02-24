import pytest

from django.test.client import Client
from datetime import datetime, timedelta

from yanews import settings
from news.models import News, Comment


@pytest.fixture
def author(django_user_model):  
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):  
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст ',
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        text='Текст комментария',
        author=author,
        news=news,
    )
    return comment


@pytest.fixture
def comments(author, news):
    comment_list = []
    for i in range(5):
        comment = Comment.objects.create(
            text='Текст комментария',
            author=author,
            news=news,
            created=datetime.now() - timedelta(days=4 - i)
        )
        comment_list.append(comment)
    return comment_list


@pytest.fixture
def slug_for_args(news):
    return (news.pk,)


@pytest.fixture(autouse=True)
def list_news():
    today = datetime.now().date()
    news_list = []
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE):
        news = News(
            title=f'Новость #{i}',
            text=f'Текст новости {i}',
            date=today - timedelta(days=i)
        )
        news_list.append(news)
    News.objects.bulk_create(news_list)


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }
