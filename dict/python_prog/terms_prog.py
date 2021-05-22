from ..python_prog.database_functions import DatabaseFunctions
from ..python_prog.spell_checker import SpellChecker
from ..python_prog.concordance_prog import Concordance
import locale
import string


class Terms:
    def __init__(self, term="", term_id="", by_id=False, ner_mode=False):
        self.term = string.capwords(term.strip())
        self.term_id = term_id
        self.tran_term_id = int()
        self.term_exist = False
        self.search_by_id = by_id
        self.ner_mode = ner_mode
        self.display_registry = False

    def get_translation_term_id(self):
        # визначити translation_id
        dbf = DatabaseFunctions()
        term_to_search = self.term.lower()
        if self.ner_mode:
            terms_table = "terms_ner"
        else:
            terms_table = "terms"
        if not self.term_id:
            # якщо id ще не визначено, тобто здійснюється пошук за власне
            # терміном, визначаємо id за цим терміном
            term_id = dbf.get_term_id_by_given_term(term_to_search, terms_table)
        else:
            term_id = self.term_id
        # з бази даних дізнаємось translation_id
        self.tran_term_id = dbf.get_translation_term_id(term_id, terms_table)
        return self.tran_term_id, term_id

    def get_term_by_its_id(self):
        # визначити власне термін за його id
        dbf = DatabaseFunctions()
        if self.ner_mode:
            terms_table = "terms_ner"
        else:
            terms_table = "terms"
        self.term = string.capwords(dbf.get_term_by_its_id(self.term_id,
                                                           terms_table))

    def get_context(self):
        # дістаємо рандомний контекст цього терміна
        concordance_class = Concordance(word=self.term.lower(), page="",
                                        ner_mode=self.ner_mode)
        # здійснили пошук в конкордансі
        concordance_class.concordance_search()
        # result_str - код html-сторінки для відображення контексту
        # (сам абзац контексту, покликання "показати джерело",
        # картинка з мікрофоном для відтворення аудіо,
        # покликання "Show more context")
        # random_context - власне рандомний контекст
        # context_id - id цього рандомного контексту в базі даних
        result_str, random_context, context_id = \
            concordance_class.get_random_context()
        return result_str, random_context, context_id

    def is_term_exist_in_base(self):
        # перевіряємо, що термін існує в базі
        dbf = DatabaseFunctions()
        term_to_search = self.term.lower()
        if self.ner_mode:
            terms_table = "terms_ner"
        else:
            terms_table = "terms"
        all_terms_and_ids = dbf.get_all_terms_and_their_ids(terms_table)
        all_terms = [x[1] for x in all_terms_and_ids]
        if term_to_search in all_terms:
            self.term_exist = True

    def dictionary_search(self):
        dbf = DatabaseFunctions()
        term_to_search = self.term.lower()
        if self.ner_mode:
            terms_table = "terms_ner"
        else:
            terms_table = "terms"
        # дістаємо тлумачення терміна (можна через власне термін, або за id)
        if self.search_by_id:
            return dbf.get_term_definition_by_term_id(self.term_id, terms_table)
        else:
            return dbf.get_term_definition(term_to_search, terms_table)

    def if_no_term_in_base(self):
        # якщо терміна немає в базі, маємо вивести на екран покликання
        # з пропозиціями термінів
        dbf = DatabaseFunctions()
        sc = SpellChecker()
        term_to_search = self.term.lower()
        if self.ner_mode:
            terms_table = "terms_ner"
            last_ukr_term_num = 50
        else:
            terms_table = "terms"
            last_ukr_term_num = 100
        all_terms_and_ids = dbf.get_all_terms_and_their_ids(terms_table)
        if not self.term_exist:
            # якщо поле пошуку порожнє, буде виведено список усіх термінів
            if term_to_search == "":
                candidates = all_terms_and_ids
                all_terms_and_ids.sort(key=lambda x: locale.strxfrm(x[1]))
                self.display_registry = True
                return self.show_all_suggestions(candidates, last_ukr_term_num)
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
            dictionary_html_page = "dictionary_ner"
        else:
            dictionary_html_page = "dictionary"
        # формування пропозицій термінів, виводимо покликання на терміни
        # кожен кандидат із candidates має формат [id терміна, власне термін]
        s = "<p>Did you mean: / Можливо, Ви мали на увазі:<br>"
        for c in candidates:
            s += """<a 
            href="/{2}?tr_id={0}">{1}</a><br>""".format(c[0],
                                                        string.capwords(c[1]),
                                                        dictionary_html_page)
        s += "</p>"
        return s

    def show_all_suggestions(self, candidates, last_ukr_term_num):
        eng, ukr = self.split_terms(candidates, last_ukr_term_num)
        if self.ner_mode:
            dictionary_html_page = "dictionary_ner"
        else:
            dictionary_html_page = "dictionary"
        s = """<table><tr>
        <th align="left">Українські кінотерміни</th>
        <th align="left">Англійські кінотерміни</th></tr>"""
        for i in range(len(eng)):
            link_eng = """<a 
            href="/{2}?tr_id={0}">{1}</a><br>""".format(eng[i][0],
                                                        string.capwords(eng[i][1]),
                                                        dictionary_html_page)
            link_ukr = """<a 
            href="/{2}?tr_id={0}">{1}</a><br>""".format(ukr[i][0],
                                                        string.capwords(ukr[i][1]),
                                                        dictionary_html_page)
            s += "<tr>"
            s += "<td>{0}</td><td>{1}</td>".format(link_ukr, link_eng)
            s += "</tr>"
        s += "</table>"
        return s

    @staticmethod
    def split_terms(candidates, last_ukr_term_num):
        # кожен елемент списку candidates - це
        # список [термін, частота id терміна]
        # розподіл термінів за мовами: якщо id терміна <= 100 => укр. термін
        # інакше англ. термін
        eng = []
        ukr = []
        for c in candidates:
            if c[0] <= last_ukr_term_num:
                ukr.append(c)
            else:
                eng.append(c)
        return eng, ukr
