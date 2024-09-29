from django.urls import path
from .views import NewsListView, NewsDetailView, NewsByTagView, ArchivedNewsView, ActiveNewsSearchView, ArchivedNewsSearchView, ProposeNewsView, SiteInformationView
from . import views
from django.conf import settings
from django.conf.urls.static import static

# Урлы для новостей + статические файлы

urlpatterns = [
    path('', NewsListView.as_view(), name='news_list'),
    path('archived/', ArchivedNewsView.as_view(), name='archived_news'),
    path('<int:pk>/', NewsDetailView.as_view(), name='news_detail'),
    path('tag/<str:tag_name>/', NewsByTagView.as_view(), name='news_by_tag'),
    path('tag/<str:tag_name>/<str:status>/', NewsByTagView.as_view(), name='news_by_tag_status'),
    path('search/', ActiveNewsSearchView.as_view(), name='search'),
    path('search/archived/', ArchivedNewsSearchView.as_view(), name='search_archived'),
    path('propose/', ProposeNewsView.as_view(), name='propose_news'),
    path('site-information/', SiteInformationView.as_view(), name='site_information'),
] 

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)