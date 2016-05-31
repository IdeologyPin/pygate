__author__ = 'sasinda'
import  numpy as np
from pygate.annotation import Annotation

class Document(Annotation):
    '''Documents can handle token level, sentence level and span level annotations.'''

    def __init__(self, srcText):
#       srcType can be Raw, Sent, Word/Token
        self.src=srcText
        self.id = srcText[0:10].encode('ascii', 'ignore').replace(' ',"_")

        if type(srcText)==str:
            self.string=srcText
            self.text=unicode(srcText)
            #Keep everythin in unicode. Just encode to byte string when transfering to server etc.
        elif type(srcText)==unicode:
            self.text=srcText
            self.string=srcText.encode('utf-8', 'ignore')
        else:
            raise ValueError('srcText should be either string or unicode')


        super(self.__class__ , self).__init__(self.text, 0, -1, 0, len(self.text), 'Document')

        self.tokens = []
        self.sents = []
        self.tknFeatures = []
        self.sentFeatures = []

        self.setAnnotationSet('Document', [self])
        self.docFeatures={}
        self.items['raw']=srcText
        self.items['doc-features']=self.docFeatures
        self.items['Token']=self.tokens
        self.items['Sentence']=self.sents

    def setAnnotationSet(self, annType, annots):
        '''@annType is the annotation type. ex: Entity.
           @annots are a list of annotations'''
        for i,a in enumerate(annots):
            a.setIdx(i)
        self.items[annType]= annots

    def addAnnotation(self, annot):
        if self.items.has_key(annot.annoType):
            lst=self.items[annot.annoType]
        else:
            lst=[]
            self.items[annot.annoType]=lst
        annot.setIdx(len(lst))
        lst.append(annot)

    def getRaw(self):
        return self.src

    def getText(self):
        '''returns the unicode text, encode to utf-8 when transferring to servers or getting a string to print'''
        return self.text

    def getString(self):
        '''returns the utf-8 encoded text'''
        return self.string

    def getSents(self):
        return self.sents

    def getTokens(self):
        return self.tokens;

    def setTokens(self, tokens):
        self.tokens=tokens
        self.setAnnotationSet('Token',tokens)

    def setSents(self, sents):
        self.sents=sents
        self.setAnnotationSet('Sentence',sents)

    def getAnnotation(start, end):
        '''return the annotation spanning the tokens indexed by start and end token
            @param start= start token id
            @param end  = end token id
        '''
        pass

    def getAllTokenLabels(self, name):
        return [t.getLabel(name) for t in self.tokens]

    def getAllSentLabels(self,name):
        return [s.getLabel(name) for s in self.sents]

    def getAllLabels(self, annType, lblName):
        return [a.getLabel(lblName) for a in self.items[annType]]

    def getSentLabels(self, idx):
        return [s.labels[idx] for s in self.sents]

    def setTokenFeature(self, i,fname, fval):
        self.tokens[i].features[fname]=fval

    def getTokenFeatures(self, i):
        '''get feature set for token i'''
        return self.tokens[i].features

    def getTokenFeatureSets(self):
        return [t.features for t in self.tokens]


    def getSentFeatures(self, i):
        '''get feature set for token i'''
        return self.sents[i].features

    def getSentFeatureSets(self):
        return [s.features for s in self.sents]

    def setSentFeature(self, i, fname, fval ):
        self.sents[i].features[fname]=fval

    def setDocFeature(self, fname, fval ):
        self.docFeatures[fname]=fval

    def getDocFeature(self, fname ):
        return self.docFeatures[fname]

    def getId(self):
        return self.id

    def setId(self,id):
        self.id=id
        self.setDocFeature('file_id',id)

    def filterItems(self, filter_expression):
        """
           supported ops are: == strict equal , =~ regex equal, != not equal, <, > <=, >=
        :param filter_expression:
        :return:
        """
        #TODO: add full filter support. http: // stackoverflow.com / questions / 2371436 / evaluating - a - mathematical - expression - in -a - string
        args=[filter_expression]
        binaryOp=None
        for op in self.ops:
            if filter_expression.find(op)>-1:
                args = filter_expression.split(op)
                binaryOp=op
                break

        keys=args[0].split('.')

        filtered=[]
        items=self[keys[0]]
        if binaryOp:
            for item in items:
                a=item[keys[1]][keys[2]]
                b=eval(args[1])
                if self.ops[binaryOp](a,b):
                    filtered.append(item)
        else:
            filtered=items
        return filtered


    ops={
        '==':lambda a,b: a==b,
        '!=':lambda a,b: a!=b
    }
    # def __missing__(self,key):
    #     return [None]

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "doc("+str(self.sents[:1])+ '//sentf'+str(self.getSentFeatureSets()[:1])[0:100]+"//tknf"+str(self.getTokenFeatureSets()[:1])[0:100]+")"






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
        self.docs[doc.getId()]=doc

    def saveDocs(self, dir=None , type='pickle', duplicates='overwrite'):
        if not dir:
            dir=self.dir
        #TODO move to fileutils
        if not os.path.exists(dir):
            os.makedirs(dir)

        for doc in self.docs.values():
            file = doc.getId()
            file = dir + "/" + file + ".pkl"
            pickle.dump(doc, open(file, "wb"))

    def loadDocs(self, fileids='.*', dir=None, type='pickle'):
        if not dir:
            dir=self.dir
        pattern = re.compile(fileids)
        files=[]
        for file in os.listdir(dir):
            if pattern.match(file) and not re.search('.DS_Store', file):
                doc=pickle.load( open( dir+"/"+ file, "rb" ) )
                self.docs[doc.getId()]=doc

    def getDocs(self):
        return self.docs.values()

    def docMap(self):
        return self.docs

    def fileids(self):
        return self.docs.keys()

    def getDocumentIterator(self):
        return self.docs.itervalues()


class NltkCorpus(DataSource):
    def __init__(self, nltkCorpus, parasToDocs=False):
        self.nltkCorpus=nltkCorpus

    def getDocumentIterator(self):
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