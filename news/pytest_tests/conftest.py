from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(django_user_model):
    client = Client()
    client.force_login(django_user_model.objects.create(username='Не автор'))
    return client


@pytest.fixture
@pytest.mark.django_db
def news():
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def news_for_args(news):
    return (news.pk,)


@pytest.fixture
@pytest.mark.django_db
def list_news():
    return News.objects.bulk_create(
        News(
            title=f'Новость{index}',
            text='Просто текст.',
            date=datetime.today() - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
@pytest.mark.django_db
def comment(news, author):
    return Comment.objects.create(news=news, author=author, text='Текст')


@pytest.fixture
@pytest.mark.django_db
def comment_for_args(comment):
    return (comment.pk,)


@pytest.fixture
@pytest.mark.django_db
def list_comments(news, author):
    comments =[]
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text='text'
        )
        comment.created = timezone.now() + timedelta(days=index)
        comment.save()
        comments.append(comment)
    return comments


@pytest.fixture
def form_data():
    return {
        'text': 'Новый комментарий'
    }
