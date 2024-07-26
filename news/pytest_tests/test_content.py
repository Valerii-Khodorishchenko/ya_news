import pytest
from django.urls import reverse
from django.conf import settings


from news.forms import CommentForm

@pytest.mark.django_db
def test_news_count(client, list_news):
    """
    Проверяю, что количество новостей на главной странице — не более
    settings.NEWS_COUNT_ON_HOME_PAGE.
    """
    response = client.get(reverse('news:home'))
    news_count = (response.context['object_list']).count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, list_news):
    """
    Проверяю, что новости отсортированы от самой свежей к самой старой. Свежие
    новости в начале списка.
    """
    response = client.get(reverse('news:home'))
    all_dates = [news.date for news in response.context['news_list']]
    assert all_dates == sorted(all_dates, reverse=True)


@pytest.mark.django_db
def test_comment_order(client, news_for_args, list_comments):
    """
    Проверяю, что комментарии на странице отдельной новости отсортированы от
    старых к новым: старые в начале списка, новые — в конце.
    """
    response = client.get(reverse('news:detail', args=news_for_args))
    assert 'news' in response.context
    news = response.context['news']
    all_timestamps = [comment.created for comment in news.comment_set.all()]
    assert all_timestamps == sorted(all_timestamps)


# @pytest.mark.django_db
# def test_anonymous_client_has_no_form(client, news_for_args):
#     response = client.get(reverse('news:detail', args=news_for_args))
#     assert 'form' not in response.context


# @pytest.mark.django_db
# def test_authorized_client_has_form(not_author_client, news_for_args):
#     response = not_author_client.get(reverse('news:detail',
#                                              args=news_for_args))
#     assert 'form' in response.context
#     assert isinstance(response.context['form'], CommentForm)

@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, form_in_context',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('not_author_client'), True),
    )
)
def test_client_has_form(parametrized_client, form_in_context, news_for_args):
    """
    Проверяю, что анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости, а авторизованному доступна.
    """
    response = parametrized_client.get(reverse('news:detail',
                                               args=news_for_args))
    assert ('form' in response.context) == form_in_context
    if form_in_context:
        assert isinstance(response.context['form'], CommentForm)
