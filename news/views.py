from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from .models import News, Tag
from .forms import NewsForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class NewsListView(ListView):
    """ 
    Назначение: Этот класс-представление используется для отображения списка опубликованных новостей.
    Атрибуты:
    - model: Модель, которая используется для списка (News).
    - template_name: Шаблон, который будет отображаться (news/news_list_active.html).
    - context_object_name: Имя переменной контекста, которое будет использоваться в шаблоне (news_list).
    - queryset: Запрос, который будет использоваться, фильтрующий новости по статусу 'published' и сортирующий по дате публикации в порядке убывания.
    """
    model = News
    template_name = 'news/news_list_active.html'
    context_object_name = 'news_list'
    paginate_by = 10
    queryset = News.objects.filter(status='published').order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['published_count'] = News.objects.filter(status='published').count()
        return context

class NewsDetailView(DetailView):
    """
    Назначение: Этот класс-представление используется для отображения детальной информации о новости.
    Атрибуты:
    - model: Модель, которая используется для детального представления (News).
    - template_name: Шаблон, который будет отображаться (news/news_detail.html).
    - context_object_name: Имя переменной контекста, которая будет использоваться в шаблоне (news).
    - get_object: Переопределяет метод для увеличения счетчика просмотров новости перед отображением.
    """
    model = News
    template_name = 'news/news_detail.html'
    context_object_name = 'news'

    def get_object(self, queryset=None):
        """
        Метод для получения объекта новости и увеличения счетчика просмотров.
        """
        news = super().get_object(queryset)
        news.increase_views()
        return news

class NewsByTagView(ListView):
    """
    Назначение: Этот класс-представление используется для отображения новостей, связанных с определенным тегом.
    Атрибуты:
    - model: Модель, которая используется для списка (News).
    - context_object_name: Имя переменной контекста, которая будет использоваться в шаблоне (news_list).
    """
    model = News
    context_object_name = 'news_list'
    paginate_by = 10

    def get_queryset(self):
        """
        Метод для получения списка новостей, связанных с определенным тегом и со статусом 'published'.
        """
        self.tag = get_object_or_404(Tag, name=self.kwargs['tag_name'])
        status = self.kwargs.get('status', 'published')
        return News.objects.filter(tags=self.tag, status=status).order_by('-pub_date')

    def get_template_names(self):
        """
        Метод для определения шаблона, который будет использоваться в зависимости от статуса новостей.
        """
        status = self.kwargs.get('status', 'published')
        if status == 'archived':
            return ['news/news_list_archived.html']
        else:
            return ['news/news_list_active.html']

    def get_context_data(self, **kwargs):
        """
        Метод для добавления тега и статуса в контекст.
        """
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        context['status'] = self.kwargs.get('status', 'published')
        context['news_count'] = self.get_queryset().count()
        return context

class ArchivedNewsView(ListView):
    """
    Назначение: Этот класс-представление используется для отображения архивных новостей.
    Атрибуты:
    - model: Модель, которая используется для списка (News).
    - template_name: Шаблон, который будет отображаться (news/news_list_archived.html).
    - context_object_name: Имя переменной контекста, которая будет использоваться в шаблоне (news_list).
    - queryset: Запрос для получения списка архивных новостей, отсортированных по дате публикации в порядке убывания.
    """
    model = News
    template_name = 'news/news_list_archived.html'
    context_object_name = 'news_list'
    paginate_by = 10
    queryset = News.objects.filter(status='archived').order_by('-pub_date')

    def get_context_data(self, **kwargs):
        """
        Метод для добавления количества архивных новостей в контекст.
        """
        context = super().get_context_data(**kwargs)
        context['archived_count'] = News.objects.filter(status='archived').count()
        context['archived'] = True
        return context

class ActiveNewsSearchView(ListView):
    """
    Метод для получения списка активных новостей, связанных с определенным запросом.
    Атрибуты:
    - model: Модель, которая используется для списка (News).
    - template_name: Шаблон, который будет отображаться (news/news_list_active.html).
    - context_object_name: Имя переменной контекста, которая будет использоваться в шаблоне (news_list).
    - paginate_by: Количество новостей на странице (10).
    - get_queryset: Метод для фильтрации списка новостей в зависимости от запроса.
    - get_context_data: Метод для добавления параметров запроса в контекст.
    """
    model = News
    template_name = 'news/news_list_active.html'
    context_object_name = 'news_list'
    paginate_by = 10

    def get_queryset(self):
        """
        Метод для фильтрации списка активных новостей в зависимости от запроса.
        """
        query = self.request.GET.get('q')
        sort_by = self.request.GET.get('sort_by', 'pub_date')
        order = self.request.GET.get('order', 'desc')
        status = 'published'  # Статус активных новостей

        news_list = News.objects.filter(status=status)

        if query:
            """
            Фильтруем новости по заголовку или содержанию.
            """
            news_list = news_list.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )

        if sort_by:
            """
            Сортируем новости по указанному полю.
            """
            if order == 'desc':
                sort_by = f'-{sort_by}'
            news_list = news_list.order_by(sort_by)

        return news_list

    def get_context_data(self, **kwargs):
        """
        Метод для добавления параметров запроса в контекст.
        """
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        context['sort_by'] = self.request.GET.get('sort_by', 'pub_date')
        context['order'] = self.request.GET.get('order', 'desc')
        context['search_count'] = self.get_queryset().count()
        context['status'] = 'published'
        context['published_count'] = self.get_queryset().count()  # Добавляем published_count в контекст
        return context

class ArchivedNewsSearchView(ListView):
    """
    Метод для получения списка архивных новостей, связанных с определенным запросом.
    Атрибуты:
    - model: Модель, которая используется для списка (News).
    - template_name: Шаблон, который будет отображаться (news/news_list_archived.html).
    - context_object_name: Имя переменной контекста, которая будет использоваться в шаблоне (news_list).
    - paginate_by: Количество новостей на странице (10).
    - get_queryset: Метод для фильтрации списка архивных новостей в зависимости от запроса.
    - get_context_data: Метод для добавления параметров запроса в контекст.
    """
    model = News
    template_name = 'news/news_list_archived.html'
    context_object_name = 'news_list'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        sort_by = self.request.GET.get('sort_by', 'pub_date')
        order = self.request.GET.get('order', 'desc')
        status = 'archived'  # Статус архивных новостей

        news_list = News.objects.filter(status=status)

        if query:
            news_list = news_list.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )

        if sort_by:
            if order == 'desc':
                sort_by = f'-{sort_by}'
            news_list = news_list.order_by(sort_by)

        return news_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        context['sort_by'] = self.request.GET.get('sort_by', 'pub_date')
        context['order'] = self.request.GET.get('order', 'desc')
        context['search_count'] = self.get_queryset().count()
        context['status'] = 'archived'
        context['archived_count'] = self.get_queryset().count()  # Добавляем published_count в контекст
        return context

class ProposeNewsView(CreateView):
    """ 
    Назначение: Этот класс-представление используется для создания новой новости от лица пользователя.
    Атрибуты:
    - model: Модель, которая используется для создания (News).
    - form_class: Форма, которая будет использоваться для создания (NewsForm).
    - template_name: Шаблон, который будет отображаться (news/propose_news.html).
    - success_url: URL, на который будет перенаправлен пользователь после успешного создания новости (news_list).
    """
    model = News
    form_class = NewsForm
    template_name = 'news/propose_news.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        news = form.save(commit=False)
        news.status = 'draft'  # Устанавливаем статус "Не проверено"
        news.save()
        form.save_m2m()  # Сохраняем связанные теги
        return super().form_valid(form)
    
class SiteInformationView(TemplateView):
    template_name = 'news/site_information.html'