from django import forms
from .models import News, Tag

class NewsForm(forms.ModelForm):
    """ 
    Определяет поле формы tags, которое позволяет пользователю выбирать несколько значений из модели Tag.
    """
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(), # возвращает все объекты модели Tag
        widget=forms.CheckboxSelectMultiple, #  представляет поле в виде списка чекбоксов, что позволяет пользователю выбирать несколько значений.
        required=False # указывает, что это поле не является обязательным для заполнения.
    )

    class Meta:
        """
        Определяет модель и поля формы.
        """
        model = News
        fields = ['title', 'brief', 'content', 'tags', 'image']