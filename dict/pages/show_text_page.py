from django.shortcuts import render
from ..python_prog.show_text_prog import ShowText


class ShowTextWebPage:
    def __init__(self, request, ner_mode=False):
        self.request = request
        self.ner_mode = ner_mode

    def display_form(self, text_header="", content=""):
        return render(self.request, "dict/show_text.html",
                      {"text_header": text_header, "text_from_corpus": content})

    def process_form(self, form):
        id_ = form.data.get("id", "")
        context_id = form.data.get("cid", "")
        show_text_class = ShowText(id_, context_id, self.ner_mode)
        header, text = show_text_class.get_header_and_text()
        return self.display_form(text_header=header, content=text)

    def proceed(self, form):
        if self.request.method == "POST" or self.request.GET:
            return self.process_form(form)
        else:
            return self.display_form()
