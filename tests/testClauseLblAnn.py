from pygate import *
import  numpy as np
import pandas as pd

# import codecs
# import sys
# #
# # UTF8Writer = codecs.getwriter('utf8')
# # sys.stdout = UTF8Writer(sys.stdout)

#
# claim_df = pd.read_excel('./data/CE-ACL-14/2014_7_18_ibm_CDCdata.xls')
# # evid_df=pd.read_excel('data/CE-ACL-14/2014_7_18_ibm_CDEdata.xls')
# claim_df['Claim'] = claim_df['Claim'].apply(lambda x: x.encode("ascii", "ignore"))
#
# docStore=DocumentStore('./docs')
# docStore.loadDocs(fileids='Criticism_of_atheism.*')
# doc= docStore.getDocs()[0]
# print docStore.getDocs()[0].getSents()

# class ClauseLabelAnnotator(PR):
#     def __init__(self, labelDataFrame):
#         self.df=labelDataFrame
#
#     def process(self, doc):
#         df=self.df
#         article_id =doc.getId();
#         article_id=article_id.replace('_', ' ')
#         df= df[df['Article'] == article_id]
# #         print "processing" , df.shape[0]
#         for clause in doc['SubClause']:
#             clause.addLabel(0)
#             print clause
#             for claim in df['Claim']:
#                 if claim in clause.text:
#                     clause.setLabel(0,1)
#                     print 'matched:------', claim
#
#
# ca=ClauseLabelAnnotator(claim_df)
# ca.process(doc)
#
# labels=[]
# for c in doc['SubClause']:
#     labels.append(c.getLabels()[0])
#
# print np.sum(labels)
print os.path.abspath('')

