from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from news.models import News


class TestHomePage(TestCase):
    # Вынесем ссылку на домащнюю страницу в арибуты класса.
    HOME_URL = reverse('news:home')

    @classmethod
    def setUpTestData(cls):
        # # Если объектов порядка десяти
        # for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        #     News.objects.create(title=f'Новость {index}', text='Просто текст.')
        #     # Или тоже самое
        #     news = News(title=f'Новость {index}', text='Просто текст.')
        #     news.save()

        # # Если объектов порядка сотен и больше. А ЛУЧШЕ ВСЕГДА!!!
        # all_news = []
        # for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        #     news = News(title=f'Новость {index}', text ='Просто текст.')
        #     all_news.append(news)
        # News.objects.bulk_create(all_news)

        #   ЕЩЕ КРУЧЕ ЮЗАТЬ ЛИСТКОМПРИХЕНШЕН:
        News.objects.bulk_create(
            News(title=f'Новость{index}', text='Просто текст.')
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
