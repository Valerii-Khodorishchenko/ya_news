from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from news.models import Comment, News


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(title='Заголовок', text='Текст')
        # Создаём двух пользователей с разными иминами:
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель Простой')
        # От имени первого пользователя создаём комментарий к новости:
        cls.comment = Comment.objects.create(
            news=cls.news,
            author=cls.author,
            text='Текст комментария'
        )

    def test_pages_availability(self):
        # Создаём набор тестовых данных - кортеж кортежей.
        # Каждый вложений кортеж содержит два элемента:
        # имя пути и позиционные аргументы для функции revverse().
        urls = (
            # Путь для главной страницы не принимает
            # никаких позиционных аргументов,
            # поэтому вторым параметром ставим None.
            ('news:home', None),
            # Путь для страницы новости
            # принимает в качестве позиционного аргумента
            # id(в данном случае pk) записи; передаём его в кортеже.
            ('news:detail', (self.news.pk,)),
            # Так же из пункта 6 плана тестирования проверим страници логина,
            # логаута, регистрации пользователя.
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None)
        )
        # Итерируемся по внешнему кортежу
        # и распаковываем содержимое вложенных кортежей:
        for name, args in urls:
            with self.subTest(name=name):
                # Передаём имя и позиционный аргумент в reverse()
                # и получаем адрес страницы для GET-запроса:
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_comment_edit_nd_delete(self):
        user_statuses = (
            (TestRoutes.author, HTTPStatus.OK),
            (TestRoutes.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in user_statuses:
            # Логиним пользователя в клиенте:
            self.client.force_login(user)
            # Для кождой пары "пользователь - ожидаемый ответ"
            # перебераем имена тестируемых страниц:
            for name in ('news:edit', 'news:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.comment.pk,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        # Сохраняем адрес страницы логина:
        login_url = reverse('users:login')
        # В цикле перебераем имена страниц, с которых ожидаем редирект:
        for name in ('news:edit', 'news:delete'):
            with self.subTest(name=name):
                # Получаем адрес страницы редактирования или удаления
                # комментария:
                url = reverse(name, args=(self.comment.pk,))
                # Получаем ожидаемый адрес страницы логина,
                # на который будет перенаправлен пользователь.
                # Учитываем, что в адресе будет параметр next, в котором
                # передаётся адрес страницы, с которой пользователь был
                # переадресован.
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                # Проверяем, что редирект приведёт именно на указанную ссылку.
                self.assertRedirects(response, redirect_url)
