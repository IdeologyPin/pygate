from pygate import PR, Document, Annotation
from pygate.ext.spacy_io import SpacyDoc
import textacy_keyterms as keyterms


class KeyTermAnnotatorPR(PR):
    def process(self, doc):
        '''
        :type doc SpacyDoc
        :param doc:
        :return:
        '''
        ranked_results = keyterms.sgrank(doc.spacy)
        # ranked_results= [(u'damage', 0.10639087570986679), (u'tremor', 0.08286867428357408)...
        for result in ranked_results:
            tkns = doc.find_in_lemma(result[0])
            a=doc.make_annotation(tkns, 'KeyTerm')
            # :type a Annotation
            a['score']=result[1]
            a['key_term']=result[0]
