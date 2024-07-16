from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from news.models import News


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(title='Заголовок', text='Текст')

    # def test_home_page(self):
    #     url = reverse('news:home')
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, HTTPStatus.OK)

    # def test_detail_page(self):
    #     url = reverse('news:detail', args=(self.news.pk,))
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, HTTPStatus.OK)

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
