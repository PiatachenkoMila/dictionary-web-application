import Levenshtein


class SpellChecker:
    @staticmethod
    def score(original, tested):
        d = Levenshtein.distance(original, tested)
        return max(0.0, 1.0 - 1.0 * d / len(original))
