from __future__ import division  # Python 2 users only

# coding: utf-8

# In[1]:


import nltk, re, pprint
from nltk import word_tokenize
from nltk.corpus import *
import pandas as pd
from pycorenlp import StanfordCoreNLP
# import sys
# reload(sys)
from pygate import *
import pygate as pg
reload(pg)
import json
import nltk.tag.stanford
from nltk.tree import *
import os


# pg.DataSink()


# In[2]:

#server for pycorenlp
#run this in terminal
# java -Xmx6g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer 9000


# ### read in dataframe to test

# In[3]:

claim_df = pd.read_excel('./data/CE-ACL-14/2014_7_18_ibm_CDCdata.xls')
# evid_df=pd.read_excel('data/CE-ACL-14/2014_7_18_ibm_CDEdata.xls')
claim_df['Claim'] = claim_df['Claim'].apply(lambda x: x.encode("ascii", "ignore"))


# In[4]:

# argCorpus=PlaintextCorpusReader('data/CE-ACL-14/articles', '.*')
argCorpus = PlaintextCorpusReader('./data/CE-ACL-14/articles', '.*')


# ### classes defined

# In[5]:

class LabelAnnotator(PR):
    def __init__(self, labelDataFrame):
        self.df=labelDataFrame

    def process(self, doc):
        df=self.df
        article_id =doc.getDocFeature('file_id');
        article_id=article_id.replace('_', ' ')
        df= df[df['Article'] == article_id]
        print "processing" , df.shape[0]
        for sent in doc.getSents():
            sent.addLabel(0)
            for claim in df['Claim']:
                if claim in sent.text:
                    sent.setLabel(0,1)


# In[6]:

class StanfordAnnotator(PR):
    def __init__(self, annotators='tokenize,ssplit,pos,parse'):#depparse
        self.annotators=annotators
        self.nlp = StanfordCoreNLP('http://localhost:9000')

    def process(self, doc):
        output=self.nlp.annotate(doc.getText(), properties={
              'annotators': self.annotators,
              'outputFormat': 'json',
              'timeout': '600000'

        })
        sents=[]
        tokens=[]
#         print "output", json.dumps(output)
        tStart=0
        tEnd=0
        for s in output['sentences']:
            sentText=[]
            sentTokens=[]
            for t in s['tokens']:
#                 print t
                sentText.append(t['before'])
                sentText.append(t['originalText'])

                token=Annotation(t['originalText'],tEnd,tEnd,t['characterOffsetBegin'], t['characterOffsetEnd'], 'Token', doc)
                token.setFeature('pos', t['pos'])
                token.setFeature('index', t['index'])
                tokens.append(token)
                sentTokens.append(token)
                tEnd+=1

            cStart=s['tokens'][0]['characterOffsetBegin']
            cEnd=s['tokens'][-1]['characterOffsetEnd']
            sentText="".join(sentText)
            print sentText
            sent=Annotation(sentText, tStart, tEnd, cStart, cEnd, 'Sentence', doc)
            tStart=tEnd

            sent.setFeature('constituency-parse', s['parse'])
            sent.setFeature('dep-parse', 'not implemented!')
            sent.setFeature('index', s['index'])
#           sent.setRelation('tokens',sentTokens)
            sents.append(sent)
#         pr-
        doc.setSents(sents)
        doc.setTokens(tokens)


# In[7]:

def getTokensWithinSubtree(sent, tree, subtree ):
    spos=subtree.treeposition()
    lpos=subtree.leaf_treeposition(0)
    subStart=tree.treepositions("leaves").index(spos+lpos)
    subEnd=subStart+len(subtree.leaves())
    doc=sent.getDoc()
    return doc.getTokens()[sent.tStart+subStart : sent.tStart+subEnd ]


# In[8]:

class SubClauseAnnotator(PR):
    def __init__(self):
        pass

    def process(self,doc):
        self.sBar=False
        self.clauses=[]
        sents=doc.getSents()

        for s in sents:
            parse=s.getFeature('constituency-parse')
            tree=ParentedTree.fromstring(parse)
            subclauses=[]
            self.traverseTree(tree, subclauses )
            annots=self.makeAnnotations(s, tree, subclauses)
            self.clauses.extend(annots)

        doc.setAnnotationSet('SubClause', self.clauses)

    def traverseTree(self, tree, clauses, sBar=False):
        label=tree.label()
#         print("node:", label )
        if(label=='SBAR'):
            sBar=True
        if(sBar and label=='S'):
            clauses.append(tree)
            sBar=False
        for subtree in tree:
            if type(subtree) == nltk.tree.ParentedTree:
                self.traverseTree(subtree,clauses,sBar)

    def makeAnnotations(self, sent, tree, subclauses):
        annots=[]
        doc=sent.getDoc()
        if len(subclauses)>0:
#             tree.draw()
            for clause in subclauses:
                tokens=getTokensWithinSubtree(sent, tree, clause )
                tStart=tokens[0].tStart
                tEnd=tokens[-1].tEnd+1
                cStart=tokens[0].cStart
                cEnd=tokens[-1].cEnd
                text=doc.getText()[cStart:cEnd]
                ann=Annotation(text,tStart,tEnd,cStart,cEnd,'SubClause')
                ann.setRelation('tokens', tokens)
                annots.append(ann)
        else:
            ann=Annotation(sent.text, sent.tStart, sent.tEnd, sent.cStart, sent.cEnd, 'SubClause')
            annots.append(ann)
        return annots


# ### test example

# In[9]:

# print argCorpus.fileids()
pipeline=Pipeline(argCorpus)
docStore=pg.DocumentStore('./docs')
pipeline.setPRs([StanfordAnnotator(), LabelAnnotator(claim_df), SubClauseAnnotator(),  docStore])


# In[10]:

sampleDoc = Document("A 2001 study found that exposure to violent video games causes at least a temporary increase in aggression and that this exposure correlates with aggression in the real world.")
sampleDoc.setId("hello")
pipeline.processDoc(sampleDoc)
# SubClauseAnnotator().process(sampleDoc)
print 'sc---' , sampleDoc['SubClause'][1]
print 'full-' ,sampleDoc.getSents()[0]
print docStore.docs


# In[11]:

pipeline.process(maxDocs=2)


# In[12]:

s="ss"
s.decode(encoding='UTF-8')





