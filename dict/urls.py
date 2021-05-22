from django.conf import settings  # імпорт модуля з налаштуваннями сайту
# імпорт для підтримки оформлення покликань на сторінки
from django.conf.urls import url
# імпорт для підтримки покликання на теку зі статичними файлами
from django.conf.urls.static import static
from . import views  # імпорт модуля з відображеннями

urlpatterns = [
    # на головній сторінці - відображення сторінки термінів
    url(r'^$', views.dictionary, name='dictionary'),
    # відображення сторінки з термінами
    url(r'^dictionary/$', views.dictionary, name='dictionary'),
    # відображення сторінки частотного словника
    url(r'^freq_dict/$', views.freq_dict, name='freq_dict'),
    # відображення сторінки частотних характеристик словоформ термінів
    url(r'^freq_wordform/$', views.freq_wordform, name='freq_wordform'),
    # відображення на сторінку перегляду джерела контексту
    url(r'^show_text/$', views.show_text, name='show_text'),
    # відображення сторінки конкорданса
    url(r'^concordance/$', views.concordance, name='concordance'),
    # відображення для сторінки введення тексту реферування
    url(r'^record/new/$', views.record_new, name='record_new'),
    # відображення сторінки перегляду результатів реферування
    url(r'^record/(?P<pk>[0-9]+)/$', views.record_detail, name='record_detail'),

    # відображення для термінів іменованих сутностей
    url(r'^dictionary_ner/$', views.dictionary_ner, name='dictionary_ner'),
    # сторінка з частотним словником ім. сутн.
    url(r'^freq_dict_ner/$', views.freq_dict_ner, name='freq_dict_ner'),
    # частотні характеристики словоформ (терміни іменованих сутн.)
    url(r'^freq_wordform_ner/$', views.freq_wordform_ner,
        name='freq_wordform_ner'),
    # перегляд джерела контексту з промаркованими іменованими сутностями
    url(r'^show_text_ner/$', views.show_text_ner, name='show_text_ner'),
    # сторінка конкордансу іменованих сутностей
    url(r'^concordance_ner/$', views.concordance_ner, name='concordance_ner'),
    # потрібно дадати покликання на теку статичних файлів
  ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
