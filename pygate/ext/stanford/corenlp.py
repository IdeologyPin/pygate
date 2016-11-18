from pygate import PR, Document, Annotation
from pycorenlp import StanfordCoreNLP
import os
import json
# java -Xmx6g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer 9000 -encoding utf-8
class StanfordAnnotator(PR):
    def __init__(self, annotators='tokenize,ssplit,pos,parse,lemma,ner', cacheDir='./corenlp'):  # depparse
        self.annotators = annotators
        self.nlp = StanfordCoreNLP('http://localhost:9000')
        if not os.path.exists(cacheDir):
            os.makedirs(cacheDir)
        self.cache = os.listdir(cacheDir)
        self.cacheDir = cacheDir

    def getOutput(self, doc):
        jsonFile = doc.getId() + '.json'
        output = None
        outfile = None
        if jsonFile in self.cache:
            outfile = open(self.cacheDir + "/" + jsonFile, 'r')
            output = json.load(outfile, encoding='UTF-8')
        else:
            outfile = open(self.cacheDir + "/" + jsonFile, 'w')
            output = self.nlp.annotate(doc.getString(), properties={
                'annotators': self.annotators,
                'outputFormat': 'json',
                'timeout': '600000'

            }, encoding='UTF-8')
            json.dump(output, outfile)
        outfile.close()
        return output

    def process(self, doc):
        output = self.getOutput(doc)

        sents = []
        tokens = []
        #         print "output", json.dumps(output)
        tStart = 0
        tEnd = 0
        cStart = 0
        cEnd = 0
        text = doc.text()
        for s in output['sentences']:
            sentText = []
            sentTokens = []
            for t in s['tokens']:
                #               print t
                txt_bfr = t['before']
                txt_tkn = t['originalText']
                sentText.append(txt_bfr)
                sentText.append(txt_tkn)

                cStart = text.find(txt_tkn, cStart)
                cEnd = cStart + len(txt_tkn)

                token = Annotation(t['originalText'], tEnd, tEnd, cStart, cEnd, 'Token', doc)
                token.set_feature('pos', t['pos'])
                token.set_feature('lemma', t['lemma'])
                token.set_feature('ner', t['ner'])
                token.set_feature('index', t['index'])
                tokens.append(token)
                sentTokens.append(token)
                tEnd += 1

            sentCStart = sentTokens[0].cStart
            sentCEnd = sentTokens[-1].cEnd
            sentText = u''.join(sentText)
            # print sentText
            sent = Annotation(sentText, tStart, tEnd, sentCStart, sentCEnd, 'Sentence', doc)
            tStart = tEnd

            sent.set_feature('constituency-parse', s['parse'])
            sent.set_feature('dep-parse', 'not implemented!')
            sent.set_feature('index', s['index'])
            sent.set_relation('tokens', sentTokens)
            sents.append(sent)
        # pr-
        doc.setSents(sents)
        doc.set_tokens(tokens)