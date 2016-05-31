
# coding: utf-8

# In[27]:

from __future__ import division  # Python 2 users only
import nltk, re, pprint
from nltk import word_tokenize
from nltk.corpus import *
import pandas as pd
# import sys
# reload(sys)
import nltk.tag.stanford
from nltk.tree import *
from pygate import *

tree=ParentedTree.fromstring("""(ROOT\n  (S\n    (NP (EX There))\n    (VP (VBZ is)\n      (NP\n        (NP (DT a) (NN study))\n        (VP (VBG being)\n          (VP (VBN conducted)\n            (PP (IN by)\n              (NP\n                (NP (NNP Dr.) (NNP Cheryl) (NNP Olson))\n                (CC and)\n                (NP (PRP$ her) (NN team))))\n            (PP (IN at)\n              (NP\n                (NP (NNP Massachusetts) (NNP General) (NNP Hospital) (POS 's))\n                (NP\n                  (NP (-LRB- -LRB-) (NN MGH) (-RRB- -RRB-))\n                  (NP (NN Center)))))\n            (PP (IN for)\n              (NP\n                (NP (NNP Mental) (NNP Health))\n                (CC and)\n                (NP (NNP Media)\n                  (CC and)\n                  (NNP Harvard))))\n            (S\n              (VP (TO to)\n                (VP (VB prove)\n                  (SBAR (IN that)\n                    (S\n                      (NP (JJ violent) (NNS games))\n                      (VP (VBP help)\n                        (S\n                          (NP (NNS students))\n                          (VP (VB deal)\n                            (PP (IN with)\n                              (NP (NN stress)\n                                (CC and)\n                                (NN aggression)))))))))))))))\n    (. .)))""")



tree.leaf_treeposition(0)
tree.treepositions((0, 1, 1, 1, 1,0, 0, 0))

def getTokensWithinSubtree(sent, tree, subtree ):
    spos=subtree.treeposition()
    lpos=subtree.leaf_treeposition(0)
    subStart=tree.treepositions("leaves").index(spos+lpos)
    subEnd=subStart+len(subtree.leaves())
    doc=sent.getDoc()
    return doc.getTokens()[sent.tStart+subStart : sent.tStart+subEnd ]

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

        doc.addAnnotationSet('SubClause', self.clauses)

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
                tEnd=tokens[-1].tEnd
                cStart=tokens[0].cStart
                cEnd=tokens[-1].cEnd
                text=doc.getText()[cStart:cEnd]
                ann=Annotation(text,tStart,tEnd,cStart,cEnd,'SubClause')
                annots.append(ann)
        else:
            ann=Annotation(sent.text, sent.tStart, sent.tEnd, sent.cStart, sent.cEnd, 'SubClause')
            annots.append(ann)