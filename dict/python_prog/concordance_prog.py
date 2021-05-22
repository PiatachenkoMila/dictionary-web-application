from ..python_prog.database_functions import DatabaseFunctions
from ..python_prog.spell_checker import SpellChecker
import re
import random
import string


class Concordance:
    def __init__(self, word="", page="", ner_mode=False):
        # Число контекстів на одній сторінці конкордансу
        self.context_num_on_page = 10
        # Виділення словоформ в контекстах конкордансу
        # відбувається так: <mark>Словоформа</mark>
        # А при перезавантаженні сторінки для озвучення контекстів на мікрофони
        # встановлюється покликання, що містить покликання на цю ж саму сторінку
        # з введенною словоформою. А при маркуванні словоформ всі фрагменти,
        # що містять словоформу, маркуються таким чином. Тому при надходженні
        # словоформи на сервер, маємо прибрати <mark>, </mark>
        word = word.replace("<mark>", "")
        word = word.replace("</mark>", "")
        self.word = string.capwords(word.strip())
        self.term_exist = False
        self.ner_mode = ner_mode
        if page == "":
            self.page = 1
        else:
            self.page = int(page)
        # Індекс контексту в конкордансі, з якого починається
        # певна сторінка конкордансу
        self.c_start = 10 * (self.page - 1)
        # Індекс останнього контексту на цій сторінці
        # Наприклад, на першій сторінці індекси з 0 до 9,
        # на другій сторінці з 10 до 19, на третій - з 20 до 29.
        self.c_end = self.c_start + 9
        self.dbf = DatabaseFunctions()

    def is_term_exist_in_base(self):
        # Перевірка на те, що словоформа є терміном з бази
        dbf = DatabaseFunctions()
        term_to_search = self.word.lower()
        if self.ner_mode:
            terms_table = "terms_ner"
        else:
            terms_table = "terms"
        all_terms_and_ids = dbf.get_all_terms_and_their_ids(terms_table)
        all_terms = [x[1] for x in all_terms_and_ids]
        if term_to_search in all_terms:
            self.term_exist = True

    def if_no_term_in_base(self):
        dbf = DatabaseFunctions()
        sc = SpellChecker()  # клас, що відповідає за підбір найбільш
        # схожих термінів, якщо термін введено з помилкою
        term_to_search = self.word.lower()
        if self.ner_mode:
            terms_table = "terms_ner"
        else:
            terms_table = "terms"
        all_terms_and_ids = dbf.get_all_terms_and_their_ids(terms_table)
        if not self.term_exist:
            # якщо поле пошуку порожнє, буде виведено список усіх термінів
            if term_to_search == "":
                candidates = all_terms_and_ids
            else:
                # відсортуємо всі терміни бази за коефіцієнтом відстані
                # Левенштейна для введеного користувачем терміна
                all_terms_and_ids.sort(key=lambda x: sc.score(x[1],
                                                              term_to_search),
                                       reverse=True)
                # обмеження п'ятьма найбільш схожими термінами
                candidates = all_terms_and_ids[:5]
            return self.show_suggestions(candidates)
        return ""

    def show_suggestions(self, candidates):
        if self.ner_mode:
            concordance_html_page = "concordance_ner"
        else:
            concordance_html_page = "concordance"
        # кожен кандидат із candidates має формат [id терміна, власне термін]
        s = "<p>Можливо, Ви мали на увазі:<br>"
        for c in candidates:
            s += """<a href="/{1}?word={0}">
            {0}</a><br>""".format(string.capwords(c[1]), concordance_html_page)
        s += "</p>"
        return s

    def concordance_search(self):
        # Пошук в конкордансі
        result_str = ""
        word_to_search = self.word.lower()
        if self.ner_mode:
            terms_table = "terms_ner"
            wordforms_table = "wordforms_ner"
            wordform_context_relation_table = "wordform_context_relation_ner"
            last_ukr_term_num = 50
            concordance_html_page = "concordance_ner"
            show_text_html_page = "show_text_ner"
        else:
            terms_table = "terms"
            wordforms_table = "wordforms"
            wordform_context_relation_table = "wordform_context_relation"
            last_ukr_term_num = 100
            concordance_html_page = "concordance"
            show_text_html_page = "show_text"
        try:
            if word_to_search != "":
                wordforms = self.dbf.get_wordforms_by_term(word_to_search,
                                                           terms_table,
                                                           wordforms_table)
            else:
                return ""
        except self.dbf.conn.OperationalError:
            return self.if_no_term_in_base()
        if len(wordforms) == 0:
            return self.if_no_term_in_base()
        # Усі контексти цього терміна
        self.concordance = \
            self.dbf.get_contexts_of_given_term(word_to_search, terms_table,
                                                wordforms_table,
                                                wordform_context_relation_table,
                                                last_ukr_term_num)
        last_index_in_concordance = len(self.concordance) - 1
        # визначаємо останній елемент на сторінці (це або останній контекст
        # конкордансу, або останній контекст на цій сторінці)
        last_item_to_display = min(last_index_in_concordance, self.c_end)
        # визначаємо номер останньої сторінку конкордансу
        last_page = last_index_in_concordance // 10
        # виведення контекстів на веб-сторінку
        for j in range(self.c_start, last_item_to_display + 1):
            result_str += "{0}. ".format(j + 1)
            result_str += self.concordance[j][1]
            id_ = self.concordance[j][0]
            context_id = self.concordance[j][2]
            result_str += """<a href=
            "/{5}?word={2}&page={3}&play={4}"><img src="/static/img/1.png">
            </a>    <a 
            href="/{6}?id={0}&cid={1}"> Show source / 
            Показати джерело</a>
            <br><br>""".format(id_, context_id, self.word, self.page, j,
                               concordance_html_page, show_text_html_page)
        # сортування словоформ цього терміна за кількістю літер в
        # словоформі, від найдовшого слова до найкоротшого
        wordforms.sort(key=len, reverse=True)
        # маркування словоформ
        for wordform in wordforms:
            result_str = self.mark_wordform(result_str, wordform)
        # далі навігаційні покликання на інші сторінки конкордансу
        if last_page > 1:
            if self.page > 1:
                result_str += """<a 
                href="/{2}?word={0}&page={1}"> Previous 
                / Попередня <br></a>   """.format(self.word, str(self.page - 1),
                                                  concordance_html_page)
            if last_item_to_display < last_index_in_concordance:
                result_str += """<a 
                href="/{2}?word={0}&page={1}"> Next 
                / Наступна</a><br>""".format(self.word, str(self.page + 1),
                                             concordance_html_page)
            if last_page < 10:
                for i in range(last_page + 1):
                    result_str += """<a 
                    href="/{2}?word={0}&page={1}"> {1}</a>""". \
                        format(self.word, i + 1, concordance_html_page)
            else:
                if self.page < 4:
                    for i in range(5):
                        result_str += """<a
                        href="/{2}?word={0}&page={1}"> 
                        {1}</a>""".format(self.word, i + 1,
                                          concordance_html_page)
                    result_str += "....."
                    for i in range(last_page - 2, last_page + 1):
                        result_str += """<a 
                        href="/{2}?word={0}&page={1}"> 
                        {1}</a>""".format(self.word, i + 1,
                                          concordance_html_page)
                else:
                    result_str += """<a 
                    href="/{2}?word={0}&page={1}"> {1}</a>""". \
                        format(self.word, 1, concordance_html_page)
                    result_str += "....."
                    if self.page < last_page - 3:
                        for i in range(self.page - 2, self.page + 3):
                            result_str += """<a 
                            href="/{2}?word={0}&page={1}"> {1}
                            </a>""".format(self.word, i + 1,
                                           concordance_html_page)
                    else:
                        for i in range(self.page - 2, last_page):
                            result_str += """<a 
                            href="/{2}?word={0}&page={1}"> {1}
                            </a>""".format(self.word, i + 1,
                                           concordance_html_page)
                    if last_page - self.page > 3:
                        result_str += "....."
                    result_str += """<a 
                    href="/{2}?word={0}&page={1}"> {1}</a>""". \
                        format(self.word, last_page + 1, concordance_html_page)
        return result_str

    @staticmethod
    def mark_wordform(text, wordform):
        def span_matches(match):
            html = '<mark>{0}</mark>'
            return html.format(match.group(0))

        return re.sub(wordform, span_matches, text, flags=re.I)

    def get_random_context(self):
        if self.ner_mode:
            terms_table = "terms_ner"
            wordforms_table = "wordforms_ner"
            concordance_html_page = "concordance_ner"
            show_text_html_page = "show_text_ner"
        else:
            terms_table = "terms"
            wordforms_table = "wordforms"
            concordance_html_page = "concordance"
            show_text_html_page = "show_text"
        # рандомний контекст для сторінки термінів
        # словоформи цього терміна
        wordforms = self.dbf.get_wordforms_by_term(self.word.lower(),
                                                   terms_table,
                                                   wordforms_table)
        result_str = "<h3>Context / Контекст</h3>"
        # генерація рандомного числа в межах від нуля до
        # останнього індексу в конкордансі
        if len(self.concordance) == 0:
            return "", ""
        end_num = len(self.concordance) - 1
        random_num = random.randint(0, end_num)
        random_context = self.concordance[random_num][1]  # рандомний контекст
        result_str += random_context
        id_ = self.concordance[random_num][0]
        context_id = self.concordance[random_num][2]
        result_str += """<img src="/static/img/1.png" id="cont_icon" 
        onclick="audio_cont.play ( )">   <a 
        href="/{4}?id={0}&cid={1}"> Show source / Показати джерело
        </a><br><br>""".format(id_, context_id, self.word, random_num,
                               show_text_html_page)
        result_str += """<a 
        href="/{1}?word={0}"> Show more context / Показати 
        більше контекстів</a><br><br>""".format(self.word,
                                                concordance_html_page)
        # сортуємо словоформи
        wordforms.sort(key=len, reverse=True)
        # маркуємо їх
        for wordform in wordforms:
            result_str = self.mark_wordform(result_str, wordform)
        return result_str, random_context, context_id
