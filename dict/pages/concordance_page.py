from django.shortcuts import render
from ..python_prog.concordance_prog import Concordance
from django.conf import settings
if settings.ENABLE_TTS_AUDIO:
    from ..python_prog.google_cloud_voice import convert_text_to_speech


class ConcordanceWebPage:
    def __init__(self, request, ner_mode=False):
        self.request = request
        self.ner_mode = ner_mode

    def display_form(self, word="", content="", page="", play_now="",
                     context_to_play=""):
        # завантаження сторінки з обробленими даними.
        # Підставляємо на веб-сторінку словосполуку, яку шукає користувач,
        # content - самі контексти,
        # page - номер сторінки, на якій зараз знаходимось
        # Контекстів може бути якзавгодно багато, не можна вивести їх на одну
        # сторінку, бо це призведе до перенавантаження браузера та всього
        # девайсу (комп'ютера, телефона, планшета, ін.)
        # Тому контексти розподіляються на сторінки - максимум
        # по 10 контекстів на сторінку
        # context_to_play - id контексту в базі даних, який необхідно озвучити
        # play_now - для озвучення контекстів:
        # ОЗВУЧЕННЯ КОНТЕКСТІВ:
        # Кожен мікрофон напроти контексту зберігає в собі покликання на цю ж
        # сторінку конкордансу, але з параметром play
        # що позначає номер контексту, який потрібно відтворити. Коли
        # користувач натискає на мікрофон, сторінка перезавантажується,
        # отримує параметр з id контексту, відбувається озвучення контексту,
        # відразу після завантаження сторінки на ній виконується
        # javascript-функція, яка відтворює озвучений контекст.
        # Після того, як відтворення контексту добігає кінця, сторінка знову
        # перезавантажується, але вже не отримує параметр з id контексту.
        # play_now - це ім'я javascript-функції, яку потрібно виконати для
        # відтворення контексту на сторінці. Якщо не потрібно відтворювати
        # аудіо, тоді play_now - порожній рядок,
        # інакше play_now = "play_audio()"
        if self.ner_mode:
            html_form_action = "concordance_ner"
        else:
            html_form_action = "concordance"
        return render(self.request, "dict/concordance.html",
                      {"word": word, "content": content, "page": page,
                       "play_now": play_now,
                       "context_to_play": context_to_play,
                       "html_form_action": html_form_action})

    def process_form(self, form, is_post):
        # Коли користувач натискає на кнопку "ПОШУК",
        # форма надсилається на сервер
        # Відбувається оброблення введених даних
        # Видобуваємо словосполуку
        word_to_search = form.data.get("word", "")
        # видобуваємо номер сторінки
        # коли користувач шукає термін, параметр з номером сторінки не
        # має передаватися на сервер
        if not is_post:
            page = form.data.get("page", "")
        else:
            page = ""
        # Видобуваємо параметр play, відповідає за номер контексту,
        # який потрібно озвучити і відтворити
        play = form.data.get("play", "")
        concordance_class = Concordance(word=word_to_search, page=page,
                                        ner_mode=self.ner_mode)
        # здійснюємо пошук контекстів в конкордансі
        content = concordance_class.concordance_search()
        # Якщо отримано id контексту для озвучення
        if play != "":
            # дістаємо цей контекст з конкордансу
            text_to_play = concordance_class.concordance[int(play)][1]
            # озвучення контексту
            if settings.ENABLE_TTS_AUDIO:
                convert_text_to_speech(text_to_play,
                                       "dict/static/mp3/context_{0}.mp3".
                                       format(play))
            # назва javascript-функції на сторінці для відтворення аудіо при
            # завантаженні сторінки
            play_now = "play_audio()"
        else:
            play_now = ""
        # відображення сторінки з обробленими даними
        return self.display_form(word=concordance_class.word, page=page,
                                 content=content, play_now=play_now,
                                 context_to_play=play)

    def proceed(self, form):
        # коли користувач переходить на сторінку конкордансу
        # мета функції: видобути параметри з html-форми (словосполуку,
        # номер сторінки та параметр play з id контексту для озвучення),
        # обробити дані й показати сторінку вже з обробленими даними
        if self.request.method == "POST":
            return self.process_form(form, is_post=True)
        else:
            if not self.request.GET:
                return self.display_form()
            else:
                return self.process_form(form, is_post=False)
