from pygate.base.doc import Document
import pickle
import sys
import traceback
from abc import abstractmethod, abstractproperty, ABCMeta
import logging
log=logging.getLogger(__name__)



# def corpusFileSentsToDoc(c):
#     fids=c.fileids()
#     corpus=c
#     for fid in fids:
#         doc =Document(corpus.sents(fid))
#         doc.addDocFeature('file_id', fid)
#         yield doc

        
class Pipeline:
    '''Pipeline consists of 
        1: Data Source << use setCorpus() to set a corpus datasource
        2: set of Processing Resources (PRs)
        3: data sinks wich are added to the chain of PRs
    '''
    def __init__(self, corpus=None):
        self.__PRs=[]
        if corpus:
            self.setCorpus(corpus)
    
    def setCorpus(self, corpus):
        self.corpus=corpus        
        self.docI=corpus.iter_docs()
        return self
        
    def addPR(self, a):
        self.__PRs.add(a)
        return self
    
    def setPRs(self, PRs):
        self.__PRs=PRs
        return self

    def process(self, maxDocs=float('inf')):
        '''apply all the annotators in the pipeline to each doc until maxDocs
            since the process function uses a Generator (yield) of docs from the corpus, it will continue from the last processed
            document when process() is called again.
        '''
        i=0
        j=0
        docs=[]
        exceptions=[]
        for doc in self.docI:
            try:
                if i>=maxDocs:
                    break
                else:
                    for a in self.__PRs:
                        a.process(doc)
                docs.append(doc)
                i+=1
            except Exception as e:
                root_cause = sys.exc_info()
                exceptions.append(PipelineException(root_cause,doc))
                log.exception(e.message)
                j+=1

        log.info( 'pipeline processed:'+ str(i) + 'documents, skipped:'+ str(j))
        return PipeLineResults(docs, exceptions)
    
    def processDoc(self, doc):
        for pr in self.__PRs:
            pr.process(doc)            
        return doc       


class PR(object):
    '''All PRs should define  how to process a doc'''
    __metaclass__ = ABCMeta

    @abstractmethod
    def process(self,doc):
        '''
        define how to process the document.
        :type doc Document
        :param doc: document to process.
        :return:
        '''
        pass

    def save(self, prFile):
        '''
        Save the processing resource with its state
        :param prFile: file to save
        :return: None.
        '''
        f = open(prFile, 'wb')
        pickle.dump(self, f)
        f.close()

    @classmethod
    def load(self, prFile):
        '''
        Load a PR from a file with all it's saved state. Ex, ML PR getting loaded with a saved model.
        :param prFile:
        :return:
        '''
        f = open(prFile , 'rb')
        pr = pickle.load(f)
        f.close()
        return pr




class DataSink(PR):
    '''setting a data sink will store data form docs into it'''
    def __init__(self):
        self.data=[]

    def process(self,doc):
        '''by default store all annotated docs coming from the pipe.'''
        self.data.append(doc)

    def getData(self):
        return self.data

class DataSource(PR):

    def iter_docs(self):
        pass

class PipeLineResults(DataSource, DataSink):

    def __init__(self, docs, exceptions):
        self.docs = docs
        self.exceptions = exceptions

    def __iter__(self):
        for doc in self.docs:
            yield doc

    def iter_docs(self):
        for doc in self.docs:
            yield doc


class PipelineException(Exception):
    def __init__(self, root_cause, doc ):
        # root_cause = root_type, root_value, root_traceback=sys.exc_info()
        self.root_cause=root_cause
        self.doc=doc

    def printStackTrace(self):
        traceback.print_exception(*self.root_cause)

    def message(self):
        self.root_cause[1].args

