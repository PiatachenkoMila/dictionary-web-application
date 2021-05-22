from django.shortcuts import render
from ..python_prog.freq_dict_prog import FreqDict


class FreqDictWebPage:
    def __init__(self, request, ner_mode=False):
        self.request = request
        self.ner_mode = ner_mode

    def display_form(self, term="", content="", selected_f="", selected_a="",
                     selected_inv="", checked="checked", fstart="", fend=""):
        # коли передаємо параметр прапорця "за зростанням", якщо він ввімкнений,
        # передається на сервер у вигляді checked=on; але на веб-сторінці для
        # ввімкнення прапорця прапорець повинен мати атрибут checked, отже,
        # робимо відповідну заміну
        if checked == "on":
            checked = "checked"
        if self.ner_mode:
            html_page = "dict/freq_dict_ner.html"
        else:
            html_page = "dict/freq_dict.html"
        return render(self.request, html_page,
                      {"termin": term, "content": content,
                       "selected_f": selected_f, "selected_a": selected_a,
                       "selected_inv": selected_inv, "checked": checked,
                       "fstart": fstart, "fend": fend})

    def process_form(self, form):
        # Коли користувач натискає на кнопку "ПОШУК",
        # форма надсилається на сервер.
        # отримуємо з форми слово для пошуку
        term = form.data.get("term", "")
        # отримуємо значення спадного списку сортування
        # (за частотою, за алфавітом, за інвертованим алфавітом)
        # На html-сторінці маємо
        """
        <select id = "search_by_combo" name = "search_by_combo"
                style="width: 100%;">
            <option {{selected_f}} value="f">Частотою</option>
            <option {{selected_a}} value ="a">Алфавітом</option>
                <option {{selected_inv}} value ="inv">Інверт. алфавітом</option>
        </select>
        """
        # замість {{selected_f}} {{selected_a}} {{selected_inv}} може бути
        # - порожній рядок, якщо даний елемент спадного списку не вибрано
        # - "selected", якщо даний елемент спадного списку зараз вибрано
        combo = form.data.get("search_by_combo", "")
        # з форми отримали, який же параметр сортування вибрано
        if combo == "a":  # вибрано за алфавітом
            selected_a = "selected"
            selected_inv = ""
            selected_f = ""
        elif combo == "inv":  # вибрано за інвертованим алфавітом
            selected_inv = "selected"
            selected_a = ""
            selected_f = ""
        else:  # вибрано за частотою
            selected_f = "selected"
            selected_a = ""
            selected_inv = ""
        # отримуємо значення прапорця "за зростанням"
        checked = form.data.get("check", "")
        # отримуємо значення обмеження за частотою
        fstart = form.data.get("fstart", "")
        fend = form.data.get("fend", "")
        # передаємо отримані з форми параметри пайтон-програмі
        # для побудови частотного словника
        freq_dict_class = FreqDict(term=term, selected_a=selected_a,
                                   selected_f=selected_f,
                                   selected_inv=selected_inv,
                                   checked=checked, fstart=fstart, fend=fend,
                                   ner_mode=self.ner_mode)
        # побудова частотної таблиці
        freq_dict_class.perform_search()
        # побудовану таблицю отримуємо як html-таблицю
        content = freq_dict_class.get_freq_table()
        # відображення сторінки частотного словника разом з
        # побудованою частотною таблицею
        return self.display_form(term=term, content=content,
                                 selected_a=selected_a, selected_f=selected_f,
                                 selected_inv=selected_inv, checked=checked,
                                 fstart=fstart, fend=fend)

    def proceed(self, form):
        # коли користувач переходить на сторінку частотного словника
        # мета функції: видобути параметри з html-форми
        # (слово для пошуку, параметри сортування: за частотою,
        # за алфавітом, за інвертованим алфавітом, сортування за зростанням,
        # за спаданням, обмеження за частотою)
        # обробити дані й показати сторінку вже
        # з обробленими даними (отримати таблицю частот)
        if self.request.method == "POST" or self.request.GET:
            return self.process_form(form)
        else:
            return self.display_form()
