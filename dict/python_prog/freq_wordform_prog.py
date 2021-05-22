from ..python_prog.database_functions import DatabaseFunctions
import string


class FreqWordform:
    def __init__(self, term="", ner_mode=False):
        self.term = term
        self.ner_mode = ner_mode
        self.dbf = DatabaseFunctions()

    def get_freq_table(self):
        # побудова таблиці частот вживання словоформ вказаного терміну та
        # представлення її у вигляді html-таблиці
        if self.ner_mode:
            terms_table = "terms_ner"
            wordforms_table = "wordforms_ner"
        else:
            terms_table = "terms"
            wordforms_table = "wordforms"
        frequencies = self.dbf.get_wordform_frequencies(self.term, terms_table,
                                                        wordforms_table)
        r = """<table id="freq_table">
        <tbody>
        <tr>
        <th>Word<br>Слово</th>
        <th>Frequency<br>Частота</th>
        </tr>
        """
        for record in frequencies:
            r += """
            <tr>
            <td>{0}</td>
            <td>{1}</td>
            </tr>
            """.format(string.capwords(record[0]), record[1])
        r += "</tbody></table>"
        if self.ner_mode:
            concordance_html_page = "concordance_ner"
            dictionary_html_page = "dictionary_ner"
            term_id = self.dbf.get_term_id_by_given_term(self.term, terms_table)
            r += """<br><br><table id="freq_table"><tbody>
            <tr>
            <td><a href="/{2}?tr_id={3}">Dictionary</a></td>
            <td><a href="/{1}?word={0}">Concordance</a></td>
            </tr>
            </tbody></table>
            """.format(self.term.lower(), concordance_html_page,
                       dictionary_html_page, term_id)
        return r
