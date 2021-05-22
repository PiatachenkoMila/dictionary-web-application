from ..python_prog.database_functions import DatabaseFunctions
import string


class FreqDict:
    def __init__(self, term="", selected_a="", selected_f="", selected_inv="",
                 checked="", fstart="", fend="", ner_mode=False):
        self.dbf = DatabaseFunctions()
        self.term = term.strip().lower()
        self.checked = checked
        self.ner_mode = ner_mode
        self.frequencies = ""
        if selected_f != "":
            self.order_by = "частотою"
        elif selected_a != "":
            self.order_by = "алфавітом"
        elif selected_inv != "":
            self.order_by = "інверт. алфавітом"
        else:
            self.order_by = "частотою"
        if fstart != "":
            try:
                self.fstart = int(fstart)
            except ValueError:
                self.fstart = ""
        else:
            self.fstart = ""
        if fend != "":
            try:
                self.fend = int(fend)
            except ValueError:
                self.fend = ""
        else:
            self.fend = ""

    def get_frequencies(self, select_statement, criteria):
        try:
            r = self.dbf.get_frequency_dict(select_statement, criteria)
        except self.dbf.conn.OperationalError:
            r = []
        return r

    def perform_search(self):
        # функція для фільтрації таблиці частотного словника
        # відбувається генерація sql-запиту, що відбирає лексеми та їх частоти
        # відповідно до введених критеріїв
        criteria = ""
        word_to_search = self.term
        # отримання з форми параметрів "обмежити за частотою"
        frequency_from = self.fstart
        frequency_to = self.fend
        # параметр "сортувати за"
        order_by_ = self.order_by
        # якщо прапорець "за зростанням" не встановлено
        if self.checked == "":
            asc_desc = "DESC"
        else:
            asc_desc = "ASC"
        # відбір даних здійснюватиметься за полем term таблиці термінів
        # Якщо ner_mode=True, за таблицею terms_ner
        # Інакше, якщо ner_mode=False, за таблицею terms
        if self.ner_mode:
            table_name = "terms_ner"
        else:
            table_name = "terms"
        word_field = "term"
        # відповідно до параметра сортування, вказується поле, за яким
        # здійснити сортування в частині запиту ORDER BY
        if order_by_ == "частотою":
            order_by = "freq"
        else:
            order_by = word_field
        # вираз відбору полів із таблиці. Підставили у вираз значення
        # word_field та table_name
        select_statement = "SELECT DISTINCT {0}, freq, id FROM {1} ". \
            format(word_field, table_name)
        # комбінування WHERE-виразу відповідно до введених параметрів
        # фільтрації за словом та частотою
        if word_to_search != "":
            criteria += """{0} LIKE "%{1}%" """.format(word_field,
                                                       word_to_search)
        if word_to_search != "" and (frequency_from != "" or
                                     frequency_to != ""):
            criteria += " AND "
        try:
            if frequency_from != "" and frequency_to != "":
                criteria += "freq BETWEEN {0} AND {1}". \
                    format(int(frequency_from), int(frequency_to))
            elif frequency_from != "" and frequency_to == "":
                criteria += "freq >= {0}".format(int(frequency_from))
            elif frequency_from == "" and frequency_to != "":
                f_to = int(frequency_to)
                if f_to > 0:
                    criteria += "freq BETWEEN 1 AND {0}".format(f_to)
                else:
                    criteria += "freq <= {0}".format(f_to)
        # якщо до полів "частота з" та "частота по" введено нечислові дані,
        except ValueError:
            pass
        # якщо поля фільтрації за словом та поля обмеження за частотою
        # є порожніми, виводимо лексеми в частотному
        # словнику з ненульовою частотою: WHERE 1
        if word_to_search == "" and frequency_from == "" and frequency_to == "":
            criteria += " freq > 0 "
        if word_to_search != "" and frequency_from == "" and frequency_to == "":
            criteria += " AND freq > 0 "
        # дописуємо до sql-виразу поле для сортування та
        # порядок, у якому сортувати
        criteria += " ORDER BY {0} {1}".format(order_by, asc_desc)
        # дістаємо з бази таблицю частот відповідно до складеного sql-виразу
        frequencies = self.get_frequencies(select_statement, criteria)
        is_reverse = asc_desc == "DESC"
        is_invert = order_by_ == "інверт. алфавітом"
        if order_by == word_field:
            frequencies = self.correct_alphabet_sorting(frequencies,
                                                        reverse=is_reverse,
                                                        invert=is_invert)
        self.frequencies = frequencies

    @staticmethod
    def correct_alphabet_sorting(dictionary, reverse, invert):
        # використовується локаль (locale), бо ASCII-символи
        # українського алфавіту розташовані в ASCII-таблиці не разом
        # (літери ЄІЇ)
        import locale
        locale.setlocale(locale.LC_ALL, "")
        dictionary = [list(x) for x in dictionary]
        # Якщо вказано метод сортування "за інвертованим алфавітом"
        if invert:
            for i in range(len(dictionary)):
                # Інвертуємо кожну словосполуку
                dictionary[i][0] = dictionary[i][0][::-1]
        sorted_dict = sorted(dictionary, key=lambda x: locale.strxfrm(x[0]),
                             reverse=reverse)
        if invert:
            for i in range(len(sorted_dict)):
                # Інвертуємо кожну словосполуку назад,
                # вже в відсортованому за інвертованим алфавітом словнику
                sorted_dict[i][0] = sorted_dict[i][0][::-1]
        return sorted_dict

    def get_freq_table(self):
        # побудовану таблицю частот представляємо у вигляді html-таблиці
        if self.term == "":
            # Якщо поле пошуку порожнє, виводиться реєстр термінів,
            # поділ термінів на два списки: англ. та укр.
            if self.ner_mode:
                last_ukr_term_num = 50
            else:
                last_ukr_term_num = 100
            eng, ukr = self.split_terms(self.frequencies, last_ukr_term_num)
            max_eng = len(eng)
            max_ukr = len(ukr)
            # Побудова таблиці частот для реєстру термінів (чотири колонки:
            # 1) англ. термін 2) частота 3) укр. термін 4) частота)
            r = """<table id="freq_table">
            <tbody>
            <tr>
            <th>Word<br>Слово</th>
            <th>Frequency<br>Частота</th>
            <th>Word<br>Слово</th>
            <th>Frequency<br>Частота</th>
            </tr>
            """
            for i in range(max(max_ukr, max_eng)):
                if i < max_eng:
                    eng_link = self.generate_link(eng[i][0])
                    eng_freq = eng[i][1]
                else:
                    eng_link = ""
                    eng_freq = ""
                if i < max_ukr:
                    ukr_link = self.generate_link(ukr[i][0])
                    ukr_freq = ukr[i][1]
                else:
                    ukr_link = ""
                    ukr_freq = ""
                r += """
                    <tr>
                    <td>{0}</td>
                    <td>{1}</td>
                    <td>{2}</td>
                    <td>{3}</td>
                    </tr>
                    """.format(eng_link, eng_freq, ukr_link, ukr_freq)
            r += "</tbody></table>"
        else:
            # Інакше побудова таблиці частот (дві колонки: термін і частота)
            r = """<table id="freq_table">
            <tbody>
            <tr>
            <th>Word<br>Слово</th>
            <th>Frequency<br>Частота</th>
            </tr>
            """
            for record in self.frequencies:
                r += """
                <tr>
                <td>{0}</td>
                <td>{1}</td>
                </tr>
                """.format(self.generate_link(record[0]), record[1])
            r += "</tbody></table>"
        return r

    # генерація покликання для лексеми в частотній таблиці для
    # переходу на сторінку частот вживання словоформ
    def generate_link(self, term):
        if self.ner_mode:
            name_of_html_page = "freq_wordform_ner"
        else:
            name_of_html_page = "freq_wordform"
        return """<a href="/{0}?term={1}">{2}</a><br>""". \
            format(name_of_html_page, term, string.capwords(term))

    @staticmethod
    def split_terms(candidates, last_ukr_term_num):
        # кожен елемент списку candidates - це
        # список [термін, частота id терміна]
        # розподіл термінів за мовами: якщо id терміна <= 100 => укр. термін
        # інакше англ. термін
        eng = []
        ukr = []
        for c in candidates:
            if c[2] <= last_ukr_term_num:
                ukr.append(c)
            else:
                eng.append(c)
        return eng, ukr
