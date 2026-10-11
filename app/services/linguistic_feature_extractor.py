import re
import unicodedata

class LinguisticFeatureExtractor:
    """Detect explicit Arabic/English linguistic markers.

    This is a conservative marker extractor, not a semantic
    entailment validator.
    """

    @staticmethod
    def _normalize(text):
        text = unicodedata.normalize('NFKC', text)
        text = re.sub('[\\u064b-\\u065f\\u0670]', '', text)
        text = re.sub('\\s+', ' ', text)
        return text.strip().casefold()

    def extract(self, statement):
        if not isinstance(statement, str):
            raise TypeError('statement must be a string')
        if not statement.strip():
            raise ValueError('statement cannot be empty')
        text = self._normalize(statement)
        must = bool(re.search('\\b(?:must|required|mandatory)\\b', text) or re.search('(?<!\\\\w)(?:\\ي\\ج\\ب|\\ي\\ل\\ز\\م|\\ي\\ت\\ع\\ي\\ن)(?!\\\\w)', text))
        should = bool(re.search('\\b(?:should|recommended|advised)\\b', text) or re.search('(?<!\\\\w)(?:\\ي\\ن\\ص\\ح|\\ي\\ن\\ب\\غ\\ي|\\ي\\ف\\ض\\ل)(?!\\\\w)', text))
        may = bool(re.search('\\b(?:may|permitted|allowed)\\b', text) or re.search('(?<!\\\\w)(?:\\ي\\م\\ك\\ن|\\ي\\ج\\و\\ز|\\ي\\س\\م\\ح)(?!\\\\w)', text))
        if must:
            modality = 'MUST'
        elif should:
            modality = 'SHOULD'
        elif may:
            modality = 'MAY'
        else:
            modality = 'NONE'
        negated = bool(re.search('\\b(?:must|should|may)\\s+not\\b', text) or re.search('(?<!\\w)يجب\\s+(?:ألا|الا|أن\\s+لا)(?!\\w)', text))
        conditional = bool(re.search('\\bif\\b', text) or re.search('(?<!\\w)(?:إذا|اذا|إن)(?!\\w)', text))
        exception = bool(re.search('\\b(?:unless|except)\\b', text) or re.search('(?<!\\w)(?:ما\\s+لم|إلا|الا)(?!\\w)', text))
        return {'modality': modality, 'negated': negated, 'conditional': conditional, 'exception': exception}
