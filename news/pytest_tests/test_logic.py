from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_user_can_create_comment(author_client, author, news, news_for_args,
                                 form_data):
    """Проверяю, что пользователь может отправить комментарий."""
    url = reverse('news:detail', args=news_for_args)
    assertRedirects(author_client.post(url, data=form_data), f'{url}#comments')
    assert Comment.objects.count() == 1
    new_news = Comment.objects.get()
    assert new_news.text == form_data['text']
    assert new_news.author == author
    assert new_news.news == news


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news_for_args, form_data):
    """Проверяю, что анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=news_for_args)
    login_url = reverse('users:login')
    assertRedirects(
        client.post(url, data=form_data), f'{login_url}?next={url}'
    )
    assert Comment.objects.count() == 0


def test_user_cant_use_bad_words(author_client, news_for_args):
    """
    Проверяю, что если комментарий содержит запрещённые слова, он не будет
    опубликован, а форма вернёт ошибку.
    """
    response = author_client.post(
        reverse('news:detail', args=news_for_args),
        data={'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    )
    assert WARNING in response.context['form'].errors['text']
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, comment_for_args,
                                   news_for_args):
    """
    Проверяю, что авторизованный пользователь может удалить свой комментарий.
    """
    response = author_client.delete(
        reverse('news:delete', args=comment_for_args)
    )
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(
        response, reverse('news:detail', args=news_for_args) + '#comments'
    )
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_comment_of_another_user(not_author_client,
                                                        comment_for_args,):
    """
    Проверяю, что авторизованный пользователь не может удалить чужой
    комментарий.
    """
    response = not_author_client.delete(
        reverse('news:delete', args=comment_for_args)
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(author_client, comment_for_args, form_data,
                                 comment, news_for_args, news, author):
    """
    Проверяю, что авторизованный пользователь может редактировать свой 
    комментарий.
    """
    form_data = {'text': 'Обновлённый комментарий'}
    response = author_client.post(
        reverse('news:edit', args=comment_for_args), data=form_data
    )
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(
        response, reverse('news:detail', args=news_for_args) + '#comments'
    )
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


def test_user_cant_edit_comment_of_author_user(not_author_client,
                                               comment_for_args,
                                               form_data, comment):
    """
    Проверяю, что авторизованный пользователь не может редактировать чужой
    комментарий.
    """
    response = not_author_client.post(
        reverse('news:edit', args=comment_for_args), data=form_data
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
