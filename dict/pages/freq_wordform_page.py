from django.shortcuts import render
from ..python_prog.freq_wordform_prog import FreqWordform
import string


class FreqWordformWebPage:
    def __init__(self, request, ner_mode=False):
        self.request = request
        self.ner_mode = ner_mode

    def display_form(self, term="", content=""):
        if self.ner_mode:
            html_page = "dict/freq_wordform_ner.html"
        else:
            html_page = "dict/freq_wordform.html"
        return render(self.request, html_page,
                      {"termin": term, "content": content})

    def process_form(self, form):
        term = form.data.get("term", "")
        freq_wordform_class = FreqWordform(term=term, ner_mode=self.ner_mode)
        content = freq_wordform_class.get_freq_table()
        return self.display_form(term=string.capwords(term), content=content)

    def proceed(self, form):
        # Коли відкривається сторінка з частотами вживань словоформ, маємо
        # видобути з форми параметр-термін, обробити дані (побудувати таблицю
        # частот вживань словоформ), і завантажити сторінку вже з
        # побудованою таблицею
        if self.request.method == "POST" or self.request.GET:
            return self.process_form(form)
        else:
            return self.display_form()
