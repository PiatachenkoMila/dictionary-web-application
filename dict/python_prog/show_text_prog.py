from ..python_prog.database_functions import DatabaseFunctions
from collections import defaultdict
import re


class ShowText:
    def __init__(self, text_id, context_id, ner_mode=False):
        # id тексту в корпусі
        self.text_id = text_id
        # id контексту в конкордансі
        self.context_id = context_id
        self.ner_mode = ner_mode

    def get_header_and_text(self):
        # отримуємо текст із корпусу та його заголовок
        dbf = DatabaseFunctions()
        context_from_base = dbf.get_context_by_its_id(self.context_id)
        header, content, ner_positions = dbf.get_text_by_id(self.text_id)
        # маркуємо необхідний контекст
        if self.ner_mode:
            content = self.mark_context_ner_mode(content, ner_positions)
        else:
            content = self.mark_context(content, context_from_base)
        return header, content

    @staticmethod
    def mark_context(text, context):
        def span_matches(match):
            html = '<mark>{0}</mark>'
            return html.format(match.group(0))

        return re.sub(re.escape(context), span_matches, text, flags=re.I)

    @staticmethod
    def mark_context_ner(text, context, entity_type):
        def span_matches(match):
            pattern = re.compile(r"{0}{1}{0}".format(r"\b", context))
            html = '<mark_{1}>{0} [{1}]</mark_{1}>'
            if re.search(pattern, match.group(0)):
                return html.format(match.group(0), entity_type)
            return match.group(0)
        return re.sub(re.compile(r"\b{0}\b".format(re.escape(context))),
                      span_matches, text)

    def mark_context_ner_mode(self, content, ner_positions):
        content_copy = content
        parsed_ner_positions = self.parse_ner_positions(ner_positions)
        dbf = DatabaseFunctions()
        list_of_ids = ",".join(list(parsed_ner_positions.keys()))
        entity_types = dbf.select_named_entities_types(list_of_ids)
        entity_types_dict = {}
        for item in entity_types:
            entity_types_dict[item[0]] = item[1]
        already_processed = ""
        for k, v in parsed_ner_positions.items():
            entity_type = entity_types_dict[int(k)]
            start = int(parsed_ner_positions[k][0][0])
            end = int(parsed_ner_positions[k][0][1])
            part = content_copy[start:end]
            if part not in already_processed:
                already_processed += part
                content = self.mark_context_ner(content, part, entity_type)
        return content

    @staticmethod
    def parse_ner_positions(ner):
        pos = defaultdict(list)
        ner = ner[1:-1]
        by_entities = ner.split(";")
        by_entities = [x for x in by_entities if x]
        for ent in by_entities:
            entity, positions = ent.split(":")
            positions = positions.split("|")
            for p in positions:
                p_ = p[1:-1]
                v1, v2 = p_.split(",")
                pos[entity].append([v1, v2])
        return pos
