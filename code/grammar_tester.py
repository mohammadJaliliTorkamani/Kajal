from lark import Lark, exceptions


class GrammarHandler:
    def __init__(self, parser: str):
        self.parser = parser

    def extract_parsing_error(self, inferred_grammar, record_source) -> str | None:
        try:
            parser = Lark(inferred_grammar, parser=self.parser)
            parser.parse(record_source)
            return None
        except exceptions.LarkError as e:
            return str(e)

    def get_parse_tree(self, inferred_grammar, record_source):
        if not self.is_valid_grammar(inferred_grammar):
            return None
        parser = Lark(inferred_grammar, parser=self.parser)

        try:
            return parser.parse(record_source).pretty()
        except Exception:
            return None

    def is_parsable(self, inferred_grammar, record_source) -> bool:
        if self.is_valid_grammar(inferred_grammar) and self.get_parse_tree(inferred_grammar, record_source):
            return True
        return False

    def is_valid_grammar(self, inferred_grammar):
        try:
            Lark(inferred_grammar, parser=self.parser)
            return True
        except Exception as e:
            return False
