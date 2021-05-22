# Create your views here.
# імпорт спеціальних функцій для відображень
from django.shortcuts import render, get_object_or_404, redirect

from .forms import FormDictionary, FormFreqDict, FormFreqWordform, \
    FormShowText, FormConcordance, RecordForm  # імпорт необхідної форми
from .models import Record  # імпорт необхідної моделі
from .pages.concordance_page import ConcordanceWebPage
from .pages.freq_dict_page import FreqDictWebPage
from .pages.freq_wordform_page import FreqWordformWebPage
from .pages.show_text_page import ShowTextWebPage
from .pages.terms_page import TermsWebPage


def helper_method(request, class_object, form_class):
    if request.method == "POST":
        form = form_class(request.POST)
    else:
        form = form_class(request.GET)
    return class_object.proceed(form)


def dictionary(request):
    terms_web_page = TermsWebPage(request=request, ner_mode=False)
    return helper_method(request, terms_web_page, FormDictionary)


def dictionary_ner(request):
    terms_web_page = TermsWebPage(request=request, ner_mode=True)
    return helper_method(request, terms_web_page, FormDictionary)


def freq_dict(request):
    freq_dict_web_page = FreqDictWebPage(request=request, ner_mode=False)
    return helper_method(request, freq_dict_web_page, FormFreqDict)


def freq_dict_ner(request):
    freq_dict_web_page = FreqDictWebPage(request=request, ner_mode=True)
    return helper_method(request, freq_dict_web_page, FormFreqDict)


def freq_wordform(request):
    freq_wordform_web_page = FreqWordformWebPage(request=request,
                                                 ner_mode=False)
    return helper_method(request, freq_wordform_web_page, FormFreqWordform)


def freq_wordform_ner(request):
    freq_wordform_web_page = FreqWordformWebPage(request=request, ner_mode=True)
    return helper_method(request, freq_wordform_web_page, FormFreqWordform)


def show_text(request):
    show_text_web_page = ShowTextWebPage(request=request, ner_mode=False)
    return helper_method(request, show_text_web_page, FormShowText)


def show_text_ner(request):
    show_text_web_page = ShowTextWebPage(request=request, ner_mode=True)
    return helper_method(request, show_text_web_page, FormShowText)


def concordance(request):
    concordance_web_page = ConcordanceWebPage(request=request, ner_mode=False)
    return helper_method(request, concordance_web_page, FormConcordance)


def concordance_ner(request):
    concordance_web_page = ConcordanceWebPage(request=request, ner_mode=True)
    return helper_method(request, concordance_web_page, FormConcordance)


def record_detail(request, pk):
    # метод-відображення сторінки перегляду результатів реферування
    # record - екземпляр класу моделі, дані отримані з рядка таблиці
    # в базі даних відповідно до вказаного параметра pk - id необхідного рядка
    record = get_object_or_404(Record, pk=pk)
    # перетворення збереженого у базі даних списку речень тексту реферату
    # до вигляду html_таблиці
    record.record_to_html()
    # перенаправлення на веб-сторінку перегляду результату
    return render(request, 'dict/record_detail.html', {'record': record})


def record_new(request):
    # метод-відображення сторінки для введення тексту для реферування
    if request.method == "POST":
        # користувач надіслав введений текст через форм - сторінку отримано
        # методом POST
        # екземпляр класу форми, що містить введений користувачем текст
        form = RecordForm(request.POST)
        if form.is_valid():  # якщо форма є валідною
            # екземпляр класу моделі - введений текст передано до класу моделі
            model_object = form.save(commit=False)
            # виклик методу моделі для запуску функції реферування
            # та збереження в базі
            model_object.save_record()
            # перенаправлення до сторінки перегляду результату реферування
            return redirect('record_detail', pk=model_object.pk)
    else:
        # завантажується веб-сторінка з формою для введення тексту - метод GET
        form = RecordForm()
    return render(request, 'dict/record_edit.html', {'form': form})
