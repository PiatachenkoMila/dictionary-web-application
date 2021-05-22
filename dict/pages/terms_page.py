from django.shortcuts import render

from ..python_prog.terms_prog import Terms
from django.conf import settings
if settings.ENABLE_TTS_AUDIO:
    from ..python_prog.google_cloud_voice import convert_text_to_speech


# Клас оброблення сторінки термінів
class TermsWebPage:
    def __init__(self, request, ner_mode=False):
        self.request = request
        self.ner_mode = ner_mode

    def display_form(self, term="", definition="", term_and_sound="",
                     def_source="", tran_term_id="", context="", term_reg="",
                     current_term_id="", context_id=""):
        # Функція для завантаження сторінки з обробленими даними
        # Передаємо наступну інформацію:
        # term: термін, definition: тлумачення
        # Є ситуація, коли на сторінці термінів мікрофон для відтворення аудіо
        # не є потрібним: коли сторінка завантажується перший раз і користувач
        # ще не ввів термін; коли такого терміна не знайдено в базі - виводиться
        # список пропозицій термінів
        # Аналогічно def_source - мікрофон для тлумачення
        # tran_term_id: id терміна іншою мовою для двомовного словника.
        # Цей id зберігається у прихованому полі, потрібний для переходу до
        # цього ж терміна, але іншою мовою.
        # context: відображати контекст терміна на сторінці

        # Наприклад, на веб-сторінці dictionary.html маємо:
        # <p>{{termin_def}}<img id="def_icon" onclick="audio_def.play ( )"
        #                      src="{{definition_src}}"></p>
        # {{termin_def}} - шаблонний тег Django: за допомогою  функції render
        # вказуємо, які дані підставити на веб-сторінку
        # у цьому місці: тобто definition - тлумачення;
        # Аналогічно, замість {{definition_src}} на веб-сторінці буде розміщено
        # вміст змінної def_source
        if self.ner_mode:
            html_form_action = "dictionary_ner"
        else:
            html_form_action = "dictionary"
        return render(self.request, "dict/dictionary.html",
                      {"termin": term, "termin_def": definition,
                       "termin_and_sound": term_and_sound, "context_": context,
                       "definition_src": def_source, "tran_id": tran_term_id,
                       "termin_reg": term_reg,
                       "current_term_id": current_term_id,
                       "context_id": context_id,
                       "html_form_action": html_form_action})

    def process_form(self, form, call_by_id):
        # Користувач ввів термін, натиснув кнопку "ПОШУК".
        # Форму, що розміщена на сторінці було надіслано на сервер.
        # Функція призначена для оброблення введених користувачем даних.
        # Визначаємо введений термін
        term = form.data.get("term", "")
        # Визначаємо translation_id (зберігається на формі у прихованому полі)
        term_id = form.data.get("tr_id", "")
        # Є два "режими" визначення потрібного терміна:
        # 1) Той термін, який ввів користувач
        # 2) Для двомовного словника потрібний термін задається за допомогою
        # id (відобразити термін з таким id)
        if call_by_id:
            # Коли визначаємо за id
            # Клас Terms - клас з пайтон-кодом для роботи з базою
            # даних (дістаємо з бази, напр. тлумачення)
            terms_class = Terms(term_id=term_id, by_id=call_by_id,
                                ner_mode=self.ner_mode)
            # Визначаємо власне термін за вказаним id цього терміна
            terms_class.get_term_by_its_id()
            # Перевірка, чи існує введений термін в базі даних
            terms_class.is_term_exist_in_base()
        else:
            # Якщо ж користувач вказав термін, ініціалізуємо клас терміном
            terms_class = Terms(term=term, by_id=call_by_id,
                                ner_mode=self.ner_mode)
            # Перевірка, чи існує введений термін в базі даних
            terms_class.is_term_exist_in_base()
        # Визначивши власне термін, зберігаємо його до змінної, щоб
        # потім відобразити його на веб-сторінці
        term_to_display_on_page = terms_class.term
        # Якщо термін існує в базі:
        if terms_class.term_exist:
            # Не відображати на екрані напис "Реєстр термінів"
            term_reg = ""
            # визначаємо translation_id для двомовного словника
            tran_term_id, current_term_id = \
                terms_class.get_translation_term_id()
            # тлумачення
            definition = terms_class.dictionary_search()
            # definition_or_suggestions: на веб-сторінці маємо відобразити
            # або термін (і його тлумачення),
            # або пропозиції вибору терміна (якщо термін не знайдено в базі)
            # У даному випадку термін знайдено і зберігаємо тлумачення
            definition_or_suggestions = definition
            # context_div - це контент html-сторінки для відображення контексту
            # random_context - власне контекст (потрібний для озвучки)
            # context_id - id цього контексту в базі даних
            context_div, random_context, context_id = terms_class.get_context()
        else:
            # Якщо термін не знайдено, знайти пропозиції для вибору термінів,
            # усе інше - як порожні рядки
            tran_term_id = ""
            definition = ""
            suggestions = terms_class.if_no_term_in_base()
            if terms_class.display_registry:
                term_reg = """Terms Registry / Реєстр термінів"""
            else:
                term_reg = ""
            definition_or_suggestions = suggestions
            context_div = ""
            random_context = ""
            current_term_id = ""
            context_id = ""
        # Якщо тлумачення терміна існує, вказати шлях до файлу з
        # картинкою мікрофону для терміна
        if definition != "":
            term_and_sound = """
                <h2><strong>""" + term_to_display_on_page + """</strong>
                <img src="/static/img/1.png" id="term_icon"
                onclick="audio_term.play ( )">
                <a href="javascript:{}" 
                onclick="document.getElementById('my_form').submit(); 
                return false;">Translation/Переклад</a>
                </h2>
            """
        else:
            # Немає тлумачення:
            term_and_sound = """
            <h2><strong>""" + term_to_display_on_page + """</strong></h2>"""
        if definition != "":
            # вказати шлях до файлу з картинкою мікрофону (для тлумачення)
            def_src = "/static/img/1.png"
        else:
            def_src = ""  # не відображати мікрофон для тлумачення
        # озвучення терміна
        if settings.ENABLE_TTS_AUDIO:
            if term_to_display_on_page != "":
                convert_text_to_speech(term_to_display_on_page,
                                       "dict/static/mp3/term_{0}.mp3".
                                       format(current_term_id))
            # озвучення тлумачення
            if definition != "":
                convert_text_to_speech(definition,
                                       "dict/static/mp3/definition_{0}.mp3".
                                       format(current_term_id))
            # озвучення контексту
            if context_div != "":
                convert_text_to_speech(random_context,
                                       "dict/static/mp3/context_{0}.mp3".
                                       format(context_id))
        # Після оброблення маємо відобразити сторінку з усіма зібраними даними
        return self.display_form(term=term_to_display_on_page,
                                 definition=definition_or_suggestions,
                                 context=context_div,
                                 term_and_sound=term_and_sound,
                                 def_source=def_src, tran_term_id=tran_term_id,
                                 term_reg=term_reg,
                                 current_term_id=current_term_id,
                                 context_id=context_id)

    def proceed(self, form):
        # Коли користувач переходить на сторінку термінів
        # виконується код, коли користувач виконав певні дії на сторінці:
        # наприклад, ввів термін до текстового поля
        # та натиснув кнопку "ПОШУК"
        # Є два способи надіслати форму веб-сторінки на сервер для оброблення
        # 1) method="post"
        # 2) method="get" (через query_string): в рядку адрес будуть відображені
        # параметри та їх значення
        # наприклад:dictionary?term=термін&tr_id=1
        # method="post" буде використовуватись, коли користувач
        # вводить термін
        # Query string - коли термін визначається за id
        # Мета цієї функції - видобути введений користувачем термін
        # і translation_id, обробити сторінку і показати
        # її вже з обробленими даними
        if self.request.method == "POST":
            return self.process_form(form, call_by_id=False)
        else:
            if not self.request.GET:
                return self.display_form()
            else:
                return self.process_form(form, call_by_id=True)
