from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize('name, subpath', (
    ('news:home', None),
    ('news:detail', pytest.lazy_fixture('news_for_args')),
    ('users:login', None),
    ('users:logout', None),
    ('users:signup', None)
))
def test_pages_availability_for_anonymous_user(name, subpath, client):
    """
    Проверяю, что:
        -Главная страница доступна анонимному пользователю.
        -Страница отдельной новости доступна анонимному пользователю.
        -Страницы регистрации пользователей, входа в учётную запись и выхода из
    неё доступны анонимным пользователям.
    """
    response = client.get(reverse(name, args=subpath))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_availability_for_comment_edit_and_delete(
    parametrized_client, expected_status, name, comment_for_args):
    """
    Проверяю что:
        - Cтраницы удаления и редактирования комментария доступны автору
        комментария.
        - Авторизованный пользователь не может зайти на страницы редактирования
        или удаления чужих комментариев (возвращается ошибка 404).
    """
    response = parametrized_client.get(reverse(name, args=comment_for_args))
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_redirect_for_anonymous_client(client, name, comment_for_args):
    """
    Проверяю что при попытке перейти на страницу редактирования или удаления
    комментария анонимный пользователь перенаправляется на страницу авторизации
    .
    """
    login_url = reverse('users:login')
    url = reverse(name, args=comment_for_args)
    assertRedirects(client.get(url), f'{login_url}?next={url}')
