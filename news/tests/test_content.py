from datetime import datetime, timedelta

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from news.models import News


class TestHomePage(TestCase):
    # Вынесем ссылку на домащнюю страницу в арибуты класса.
    HOME_URL = reverse('news:home')

    @classmethod
    def setUpTestData(cls):
        # Вычисляем текущую дату.
        today = datetime.today()
        News.objects.bulk_create(
            News(
                title=f'Новость{index}',
                text='Просто текст.',
                # Для каждой новости уменьшаем дату на index дней от tody,
                # где index - счётчик цикла.
                date=today - timedelta(days=index)
            )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        )

    def test_news_count(self):
        # Загружаем главную страницу.
        response = self.client.get(self.HOME_URL)
        # Код ответа не проверяем, его уже провенили в тестах маршрутов.
        # Получаем список объектов из словаря контекста.
        object_list = response.context['object_list']
        # news/views.py
        # class NewsList(generic.ListView):
        #     """Список новостей."""
        #     model = News
        #     template_name = 'news/home.html'
        #     # заменяет object_list и new_list на news_feed
        #     context_object_name = 'news_feed'

        # Определяем количество записей в списке.
        news_count = object_list.count()
        # Проверяем что на странице именно 10 новостей.
        self.assertEqual(news_count, settings.NEWS_COUNT_ON_HOME_PAGE)

    def test_news_order(self):
        response = self.client.get(self.HOME_URL)
        object_list = response.context['news_list']
        # Получаем даты новостей в том порядке, как они выведены на странице.
        all_danes = [news.date for news in object_list]
        sorted_dates = sorted(all_danes, reverse=True)
        # Проверяем, что исходный список был отсортирован правильно.
        self.assertEqual(all_danes, sorted_dates)
