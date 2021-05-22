from django import forms  # імпорт Django-форм

from .models import Record  # імпорт необхідного класу моделі


# Create your forms here.


class FormDictionary(forms.Form):
    pass


class FormFreqDict(forms.Form):
    pass


class FormFreqWordform(forms.Form):
    pass


class FormShowText(forms.Form):
    pass


class FormConcordance(forms.Form):
    pass


class RecordForm(forms.ModelForm):
    # клас форми, що прив'язана до моделі, необхідної для реферування
    class Meta:
        model = Record  # вказується, який саме клас моделі використати
        # вказується перелік полів моделі, доступних користувачу для введення
        # у веб-формі
        fields = ('text',)
