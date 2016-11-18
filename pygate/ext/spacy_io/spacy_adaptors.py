from pygate.base.doc import Document
from pygate.base.annotation import Annotation
import spacy

class SpacySpan(Annotation):
    def __init__(self, span, annoType, doc=None):
        super(SpacySpan, self).__init__(span.text, span.start, span.end, span.start_char, span.end_char, annoType, doc)
        self.spacy = span

    def __getitem__(self, key):
        # TODO: use the one in doc. self.doc[key] to get the original token annotation
        if isinstance(key, slice):
            return self.span[key]
        elif isinstance(key, int):
            return self.span[key]
        else:
            return self.items[key]


class SpacyToken(Annotation):
    def __init__(self, tkn, doc=None):
        super(SpacyToken, self).__init__(tkn.text, tkn.i, tkn.i, tkn.idx, tkn.idx + len(tkn), 'Token', doc)
        self.spacy = tkn

    def __getitem__(self, key):
        # TODO: use the one in doc. self.doc[key] to get the original token annotation
        if isinstance(key, slice):
            return self.span[key]
        elif isinstance(key, int):
            return self.span[key]
        else:
            return self.items[key]


class SpacyDoc(Document):
    """
    A wrapper and adaptor for spacy.tokens.doc.Doc class
        https://spacy.io/docs#doc
    """
    en_nlp = spacy.load('en')

    def __init__(self, src_text):
        """
            A wrapper for spacy.tokens.doc.Doc class
            https://spacy.io/docs#doc
            :param src_text:
            :param kwargs: kwargs to be parsed to spacy pipeline for this doc. doc = nlp(u'Some text.', parse=False)
            """
        super(SpacyDoc, self).__init__(src_text)
        self.spacy = SpacyDoc.en_nlp(self.text)

    def unwrap(self):
        return self.spacy_doc

    @Document.sents.getter
    def sents(self):
        if (len(self._sents) == 0):
            self._Document__set_sents([SpacySpan(s, "Sentence", self) for s in self.spacy.sents])
        return self._sents

    @Document.tokens.getter
    def tokens(self):
        if (len(self._tokens) == 0):
            self._Document__set_tokens([SpacyToken(t, self) for t in self.spacy])
        return self._tokens


    def find_in_lemma(self, sub, cStart=0, cEnd=None):
        '''
        Ex: lemmatized text of the document. This will give the corresponding original tokens to best of its extent.
        :param text:
        :param sub:
        :param cStart:
        :param cEnd:
        :return:
        '''
        if not cEnd:
            cEnd = self.tokens[-1].cEnd

        if self.cindex['Token'] == None:
            self._make_cindex('Token')
        tkn_index = self.cindex['Token']

        tokens = None
        if cStart < cEnd:
            cidx = self.spacy[0:-1].lemma_.find(sub, cStart)
            if cidx >= 0:
                s_start = max(0, cidx - int(cidx * 0.1))
                s_end = min(cidx + len(sub) + int(cidx * 0.1), len(self.text))
                intervals = tkn_index[s_start:s_end]

                tokens=[]
                subs=sub.split(' ')
                m=0
                intervals=sorted(intervals,key=lambda tup: tup[0])
                for inl in intervals:
                    if m >=len(subs):
                        break
                    match = subs[m]
                    if inl[2].spacy.lemma_ == match:
                        tokens.append(inl[2])
                        m+=1
                    elif m>0:
                        m=0
                        tokens=[]
        return tokens

