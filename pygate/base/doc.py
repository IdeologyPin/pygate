__author__ = 'sasinda'
from annotation import Annotation
from collections import defaultdict
from intervaltree import Interval, IntervalTree


class Document(Annotation):
    '''Documents can handle token level, sentence level and span level annotations.'''

    def __init__(self, src_text):
        #       srcType can be Raw, Sent, Word/Token
        self._src = src_text
        self._id = src_text[0:10].encode('ascii', 'ignore').replace(' ', "_")

        if type(src_text) == str:
            self._string = src_text
            self._text = unicode(src_text)
            # Keep everythin in unicode. Just encode to byte string when transfering to server etc.
        elif type(src_text) == unicode:
            self._text = src_text
            self._string = src_text.encode('utf-8', 'ignore')
        else:
            raise ValueError('srcText should be either string or unicode')

        super(Document, self).__init__(self.text, 0, -1, 0, len(self.text), 'Document')

        self._tokens = []
        self._sents = []
        self.tknFeatures = []
        self.sentFeatures = []

        self.set_annotation_set('Document', [self])
        self.docFeatures = {}
        self.items['raw'] = src_text
        self.items['doc-features'] = self.docFeatures
        self.items['Token'] = self._tokens
        self.items['Sentence'] = self._sents

        self.index = defaultdict(lambda: None)
        self.cindex = defaultdict(lambda: None)

    def set_annotation_set(self, annType, annots):
        '''@annType is the annotation type. ex: Entity.
           @annots are a list of annotations'''
        for i, a in enumerate(annots):
            a.idx = i
        self.items[annType] = annots

    def clear_annotation_set(self, annType):
        # TODO code to remove from anno index.
        del self.items[annType]

    def add_annotation(self, annot):
        if self.items.has_key(annot.annoType):
            lst = self.items[annot.annoType]
        else:
            lst = []
            self.items[annot.annoType] = lst
        annot.idx = len(lst)
        lst.append(annot)

    def make_annotation(self, tokens, ann_type):
        '''

        :param tokens:
        :param ann_type:
        :return:
        '''
        stkn=tokens[0]
        etkn=tokens[-1]
        a=Annotation(self.text[stkn.cStart:etkn.cEnd],stkn.tStart,etkn.tEnd, stkn.cStart, etkn.cEnd, ann_type, self)
        self.add_annotation(a)
        return a

    def get_raw(self):
        return self.src

    @property
    def text(self):
        '''returns text in the original encoding of the doc'''
        return self._text

    @property
    def string(self):
        '''returns the utf-8 encoded text'''
        return self._string


    def annots(self, ann_type):
        return  self.items[ann_type]

    @property
    def sents(self):
        return self._sents

    def __set_sents(self, sents):
        self._sents = sents
        self.set_annotation_set('Sentence', sents)

    @property
    def tokens(self):
        return self._tokens

    def get_tokens(self, cStart=0, cEnd=-1):
        if cStart == 0 and cEnd == -1:
            return self._tokens

        if self.cindex['Token'] == None:
            self._make_cindex('Token')
        tkn_index = self.cindex['Token']
        intervals = tkn_index[cStart:cEnd]
        tokens = []
        for i in intervals:
            tokens.append(i[2])
        return tokens

    def __set_tokens(self, tokens):
        self._tokens = tokens
        self.set_annotation_set('Token', tokens)

    def _make_cindex(self, ann_type):
        tree = IntervalTree()
        self.cindex[ann_type] = tree
        spans = None
        # special cases may be implemented by subclasses
        # for sents and tokens to be lazy loaded. So use the self.tokens, self.sents properties rather than the items.
        if ann_type == 'Token':
            spans = self.tokens
        elif ann_type == 'Sentence':
            spans = self.sents
        else:
            spans = self.items[ann_type]
        for span in spans:
            tree[span.cStart: span.cEnd] = span

    def find(self, sub, cStart=0, cEnd=None):
        """same as string.find(s, sub[, start[, end]])
            @param cStart= start character to begin find from
            @param cEnd= end character to stop search on
            @return tokens of the 1st occurence.
        """
        if not cEnd:
            cEnd = self.tokens[-1].cEnd

        if self.cindex['Token'] == None:
            self._make_cindex('Token')
        tkn_index = self.cindex['Token']

        tokens = None
        if cStart < cEnd:
            cidx = self.text.find(sub, cStart)
            if cidx >= 0:
                intervals = tkn_index[cidx:cidx + len(sub)]
                tokens = []
                for i in intervals:
                    tokens.append(i[2])
        return tokens



    def cfind(self, sub, start=None, end=None):
        raise "not implemented"

    def query_overlapping_x(self, x_type, y):
        pass

    def query_overlappedby_y(self, x, y_type):
        cindex = self.__query_ready(y_type)
        return cindex[x.cStart: x.cEnd]

    def __query_ready(self, ann_type):
        if self.cindex[ann_type] == None:
            self._make_cindex(ann_type)
        return self.cindex[ann_type]

    def query(self, query, **kwargs):

        '''
            support for Allen's operations.
            b= before, m= meets, o= overalps, s=starts, d=during, ds=strictly during f=finshes, e=equal
            https://en.wikipedia.org/wiki/Allen%27s_interval_algebra
            return the annotation spanning the tokens indexed by start and end token
            @param start= start token id
            @param end  = end token id
            Select s FROM PATTERN Token t during Sentence s WHERE t=$t
        '''
        # TODO: Supports X_type token and ops 'd', 'o' only for the moment. Externalize logic to a Allen's Engine.
        raise NotImplemented

    def query_atomic(self, x_type, op,y):
        if x_type == 'Token':
            if op == 'd' or op == 'o':
                start = y.start
                end = y.en
                return [self.tokens[i] for i in range(start, end)]
            else:
                raise "operation not supported."
        else:
            raise "Only Token as x_type is supported at the moment!"

    def to_array(self, annType, features='*'):
        """

        :param annType: convert the given annotation type into a feature array.
        :param features:
        :return:
        """
        return [t.features for t in self.items[annType]]

    def to_label_array(self, annType, labels='*'):
        """
        gives the labels of each annotation element of annType as an array.
        :param annType:
        :param labels:
        :return:
        """
        return [t.labels for t in self.items[annType]]

    # def get_all_token_labels(self, name):
    #     return [t.getLabel(name) for t in self.tokens]
    #
    # def get_all_sent_labels(self, name):
    #     return [s.getLabel(name) for s in self.sents]
    #
    # def get_all_labels(self, annType, lblName):
    #     return [a.getLabel(lblName) for a in self.items[annType]]
    #
    # def get_sent_labels(self, idx):
    #     return [s.labels[idx] for s in self.sents]
    #
    # def set_token_feature(self, i, fname, fval):
    #     self.tokens[i].features[fname]=fval
    #
    # def get_token_features(self, i):
    #     '''get feature set for token i'''
    #     return self.tokens[i].features
    #
    def get_token_feature_sets(self):
        return [t.features for t in self.tokens]

    #
    #
    # def getSentFeatures(self, i):
    #     '''get feature set for token i'''
    #     return self.sents[i].features
    #
    def get_sent_feature_sets(self):
        return [s.features for s in self.sents]

    #
    # def setSentFeature(self, i, fname, fval ):
    #     self.sents[i].features[fname]=fval

    def set_doc_feature(self, fname, fval):
        self.docFeatures[fname] = fval

    def get_doc_feature(self, fname):
        return self.docFeatures[fname]

    @property
    def id(self):
        return self._id

    @id.setter
    def setId(self, id):
        self._id = id
        self.set_doc_feature('file_id', id)

    def filter_items(self, filter_expression):
        """
           supported ops are: == strict equal , =~ regex equal, != not equal, <, > <=, >=
        :param filter_expression:
        :return:
        """
        # TODO: add full filter support. http: // stackoverflow.com / questions / 2371436 / evaluating - a - mathematical - expression - in -a - string
        args = [filter_expression]
        binaryOp = None
        for op in self.ops:
            if filter_expression.find(op) > -1:
                args = filter_expression.split(op)
                binaryOp = op
                break

        keys = args[0].split('.')

        filtered = []
        items = self[keys[0]]
        if binaryOp:
            for item in items:
                a = item[keys[1]][keys[2]]
                b = eval(args[1])
                if self.ops[binaryOp](a, b):
                    filtered.append(item)
        else:
            filtered = items
        return filtered

    ops = {
        '==': lambda a, b: a == b,
        '!=': lambda a, b: a != b
    }

    # def __missing__(self,key):
    #     return [None]

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "doc(" + str(self.sents[:1]) + '//sentf' + str(self.get_sent_feature_sets()[:1])[0:100] + "//tknf" + str(
            self.get_token_feature_sets()[:1])[0:100] + ")"


__author__ = 'sasinda'
from pipe import *
import pickle
import os
import re

class DocumentStore(DataSink, DataSource):
    def __init__(self, dir):
        self.docs = {}
        self.dir=dir
        self.data = self.docs

    def process(self, doc):
        self.docs[doc.id]=doc

    def save_docs(self, dir=None, type='pickle', duplicates='overwrite'):
        if not dir:
            dir=self.dir
        #TODO move to fileutils
        if not os.path.exists(dir):
            os.makedirs(dir)

        for doc in self.docs.values():
            file = doc.id
            file = dir + "/" + file + ".pkl"
            pickle.dump(doc, open(file, "wb"))

    def load_docs(self, fileids='.*', dir=None, type='pickle'):
        if not dir:
            dir=self.dir
        pattern = re.compile(fileids)
        files=[]
        for file in os.listdir(dir):
            if pattern.match(file) and not re.search('.DS_Store', file):
                doc=pickle.load( open( dir+"/"+ file, "rb" ) )
                self.docs[doc.id]=doc

    def get_docs(self):
        return self.docs.values()

    def doc_map(self):
        return self.docs

    def fileids(self):
        return self.docs.keys()

    def itervalues(self):
        return self.docs.itervalues()

    def __iter__(self):
        yield self.itervalues()

class AnnotationStore(DataSink, DataSource):

    def __init__(self, ann_type):
        self.annots = []
        self.ann_type = ann_type
        self.data = self.annots

    def process(self, doc):
        for ann in doc[self.ann_type]:
            self.annots.append(ann)


class NltkCorpus(DataSource):
    def __init__(self, nltkCorpus, parasToDocs=False):
        self.nltkCorpus=nltkCorpus

    def iter_docs(self):
        return self.corpusFilesToDoc(self.nltkCorpus)

    def corpusFilesToDoc(self,c):
        for fid in c.fileids():
            if fid!='.DS_Store':
                doc =Document(c.raw(fid))
                doc.setId(fid)
                yield doc

    def corpusParasToDoc(self,c):
        for p in c.paras():
            yield Document(p)

    def fileids(self):
        return self.nltkCorpus.fileids()

