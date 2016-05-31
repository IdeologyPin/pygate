__author__ = 'sasinda'
from nltk.corpus import *
from pygate import *
from pycorenlp import StanfordCoreNLP


class StanfordAnnotator(PR):
    def __init__(self, annotators='tokenize,ssplit,pos,parse,lemma,ner', cacheDir='./corenlp'):#depparse
        self.annotators=annotators
        self.nlp = StanfordCoreNLP('http://localhost:9000')
        if not os.path.exists(cacheDir):
            os.makedirs(cacheDir)
        self.cache= os.listdir(cacheDir)
        self.cacheDir=cacheDir

    def getOutput(self, doc):
        jsonFile=doc.getId()+'.json'
        output=None
        outfile=None
        if jsonFile in self.cache:
            outfile=open(self.cacheDir+"/"+jsonFile, 'r')
            output=json.load(outfile, encoding='UTF-8')
        else:
            outfile=open(self.cacheDir+"/"+jsonFile, 'w')
            output=self.nlp.annotate(doc.getString(), properties={
                  'annotators': self.annotators,
                  'outputFormat': 'json',
                  'timeout': '600000'

            }, encoding='UTF-8')
            json.dump(output, outfile)
        outfile.close()
        return output

    def process(self, doc):
        output=self.getOutput(doc)

        sents=[]
        tokens=[]
#         print "output", json.dumps(output)
        tStart=0
        tEnd=0
        cStart=0
        cEnd=0
        text=doc.getText()
        for s in output['sentences']:
            sentText=[]
            sentTokens=[]
            for t in s['tokens']:
#               print t
                txt_bfr=t['before']
                txt_tkn=t['originalText']
                sentText.append(txt_bfr)
                sentText.append(txt_tkn)

                cStart=text.find(txt_tkn, cStart)
                cEnd=cStart+len(txt_tkn)

                token=Annotation(t['originalText'],tEnd,tEnd,cStart, cEnd, 'Token', doc)
                token.setFeature('pos', t['pos'])
                token.setFeature('lemma', t['lemma'])
                token.setFeature('ner', t['ner'])
                token.setFeature('index', t['index'])
                tokens.append(token)
                sentTokens.append(token)
                tEnd+=1

            sentCStart=sentTokens[0].cStart
            sentCEnd=sentTokens[-1].cEnd
            sentText=u''.join(sentText)
            # print sentText
            sent=Annotation(sentText, tStart, tEnd, sentCStart, sentCEnd, 'Sentence', doc)
            tStart=tEnd

            sent.setFeature('constituency-parse', s['parse'])
            sent.setFeature('dep-parse', 'not implemented!')
            sent.setFeature('index', s['index'])
            sent.setRelation('tokens',sentTokens)
            sents.append(sent)
#         pr-
        doc.setSents(sents)
        doc.setTokens(tokens)


argCorpus = PlaintextCorpusReader('../data/CE-ACL-14/articles', '.*')

argCorpus =NltkCorpus(argCorpus)


pipeline=Pipeline(argCorpus)
docStore=DocumentStore('./docs')
pipeline.setPRs([StanfordAnnotator(),  docStore])
pipeline.process()


len(doc.getSents())
print doc.getSents()
