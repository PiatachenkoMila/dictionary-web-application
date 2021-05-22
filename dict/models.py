from django.db import models  # імпорт для підтримки django-моделей
# імпорт функції, що виконує автоматичне реферування
from dict.python_prog.text_summarization import run_summarization
# Create your models here.


class Record(models.Model):
    # модель (таблиця в базі даних Django) для авт. реферування
    text = models.TextField()  # властивість оригінальний текст
    summary_text = models.TextField(null=True)  # властивість текст-резюме

    def save_record(self):
        # функція для запуску процесу реферування
        self.summary_text = run_summarization(self.text)
        # збереження отриманого тексту до бази у вигляді текстового рядка
        # списку речень
        self.save()

    def record_to_html(self):
        # функція для відображення тексту реферату у вигляді html-таблиці
        # конвертація змінної із текстового рядка до python-списку
        sentences_list = eval(self.summary_text)
        len_sentences = len(sentences_list)  # кількість речень
        if len_sentences > 0:  # якщо кількість речень > 0
            html_code = """<tr><td rowspan="{0}">{1}</td><td>{2}</td></tr>""".format(len_sentences, self.text, sentences_list[0])
        else:
            # якщо не вдалося побудувати резюме, вивести лише оригінальний текст
            html_code = """<tr><td rowspan="{0}">{1}</td><td>{2}</td></tr>""".format(len_sentences, self.text, "")
        for i in range(1, len(sentences_list)):
            html_code += "<tr><td>{0}</td></tr>".format(sentences_list[i])
        self.summary_text = html_code
