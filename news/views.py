from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, TemplateView, DeleteView
from django.views import View
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from .models import News, Tag, Comment
from .forms import NewsForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse


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
    
    def get_context_data(self, **kwargs):
        """ Метод для добавления комментариев и формы добавления комментариев в контекст. """
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all().order_by('-created_at') # Сортируем комментарии по дате создания в порядке убывания
        comment_form = CommentForm() # Cоздаем форму для добавления комментариев
        comment_form.fields['content'].widget.attrs.update({'class': 'form-control'}) # Добавляем класс для стилизации поля формы
        context['comment_form'] = comment_form # Добавляем форму в контекст
        return context

    def post(self, request, *args, **kwargs):
        """ Метод для обработки POST-запросов. """
        self.object = self.get_object()
        if 'content' in request.POST: # Проверяем, что в POST-запросе есть поле 'content', это означает, что пользователь пытается добавить комментарий
            # Обработка добавления комментария
            form = CommentForm(request.POST) # Создаем форму для добавления комментариев с данными из POST-запроса
            if form.is_valid(): # Проверяем, что данные формы валидны
                comment = form.save(commit=False) # Создаем объект комментария без сохранения в базу данных
                comment.news = self.object # Привязывает комментарий к текущей новости
                comment.author = request.user # Привязывает комментарий к текущему пользователю
                comment.save() # Сохраняем комментарий в базу данных
                return redirect('news_detail', pk=self.object.pk) # Перенаправляет пользователя на страницу деталей новости
        elif 'like_comment' in request.POST: # Проверяем, что в POST-запросе есть поле 'like_comment', это означает, что пользователь пытается лайкнуть комментарий
            # Обработка лайка комментария
            comment_id = request.POST.get('like_comment') # Получаем идентификатор комментария из POST-запроса
            comment = get_object_or_404(Comment, id=comment_id) # Получаем объект комментария из базы данных по его идентификатору или генерируем ошибку 404, если комментарий не найден
            if request.user in comment.likes.all(): # Проверяем, лайкнул ли текущий пользователь этот комментарий
                comment.likes.remove(request.user) # Если да, то удаляем лайк
            else:
                comment.likes.add(request.user) # Если нет, то добавляем лайк
            return redirect('news_detail', pk=self.object.pk) # Перенаправляет пользователя на страницу-details новости

        context = self.get_context_data(object=self.object)
        context['comment_form'] = form
        return render(request, self.template_name, context)
    
class DeleteCommentView(DeleteView):
    """Удаление комментария"""
    model = Comment
    success_url = reverse_lazy('news_list')

    def get_success_url(self):
        """ Метод для перенаправления пользователя на страницу новости, к которой принадлежал удаленный комментарий. """
        return reverse_lazy('news_detail', kwargs={'pk': self.object.news.id})

    def get_object(self, queryset=None):
        """ Метод для получения объекта комментария. И если текущий пользователь не является автором комментария или администратором, то генерирует ошибку """
        obj = super().get_object(queryset)
        if not (self.request.user == obj.author or self.request.user.is_staff):
            raise PermissionDenied("You do not have permission to delete this comment.")
        return obj

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
        self.tag = get_object_or_404(Tag, slug=self.kwargs['tag_slug'])
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
        news.author = self.request.user if self.request.user.is_authenticated else User.objects.get(id=1)  # Устанавливаем автора, если пользователь аутентифицирован, иначе администратора
        news.save()
        form.save_m2m()  # Сохраняем связанные теги
        return super().form_valid(form)


class SiteInformationView(TemplateView):
    """
    Класс для получения информации о сайте. 
    Атрибуты:
    - template_name: Шаблон, который будет отображаться (news/site_information.html).
    """
    template_name = 'news/site_information.html'