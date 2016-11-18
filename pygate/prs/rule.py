from pygate import PR, DocumentStore, Annotation
import re

class SPMRulePR(PR):
    """Python Sequention Pattern Matching and rules PR."""

    # (@Token.features.ner=='I'):span --> @Entity:e -> {e.subType=span.features.ner }
    # (@Token.features.ner!='O'):span --> @Entity:e ->  e.subType=span.features['ner']; e.subType='yay'
    # @SubClause.labels.pred==1  -->  @Claim

    pat_span=re.compile('\(.*\):')
    pat_span_name=re.compile('[A-Za-z0-9_]+')
    pat_annotType=re.compile('@[A-Za-z0-9_]+')

    def __init__(self, rules):
        self.rules=rules

    def process(self,doc):
        ## supports only one rule at this time.
        rules=self.rules
        split=rules.split('-->')
        LHS= split[0]
        RHS= split[1]

        #supports only one span for now
        span_match=self.pat_span.match(LHS)
        if span_match:
            span=LHS[span_match.start()+1: span_match.end()-2]
            span_name_match=self.pat_span_name.match(LHS, span_match.end())
            span_name=LHS[span_name_match.start():span_name_match.end()]
        else:
            span=LHS
            span_name='span'

        if self.__check_regex(span):
            raise NotImplemented('annot seq regex not implemented')

        span1_seq1_filter=span.split('@')[1]
        span1_seq1_anns=doc.filter_items(span1_seq1_filter)

        #for each span execute RHS
        for span1_seq1_ann in span1_seq1_anns:
            self.execRHS(doc, RHS, **{span_name:span1_seq1_ann})



    def execRHS(self,doc, RHS, **kwargs):
        # default lhs annotation is span. It'll get set by the kwargs.
        span=Annotation("",0,0,0,0,'')
        for key,value in kwargs.items(): # initialize variables for spans defined on lhs.
            exec(key+"=kwargs[key]")

        #find annot to make
        split=RHS.split('->')
        annot_declaration=split[0]
        annoType=self.pat_annotType.findall(annot_declaration)[0][1:]
        annot=Annotation(span.text, span.tStart, span.tEnd, span.cStart, span.cEnd, annoType, doc)
        doc.add_annotation(annot)
        if len(split)>1:
            var_name=annot_declaration.split(":")[1]
            exec(var_name+"=annot")
            code=split[1].strip()
            exec(code)

    def __check_regex(self, span):
        if span.endswith(')+'):
            group=span[1:-3]
            op='+'
            return group, op

    def __regex_plus(self):
        pass

from pygate.export.brat import BratServer
##test method
if __name__ == "__main__":
    docStore=DocumentStore('./')
    docStore.load_docs(fileids='Former.*')
    doc=docStore.get_docs()[0]
    doc.set_annotation_set('Entity', [])
    spm=SPMRulePR("(@Token.features.ner!='O'):span --> @Entity:e ->  e.subType=span.features['ner']")

    spm.process(doc)
    print doc['Entity'][0].subType
    # print doc['Claim'][0].subType
    docStore.save_docs()

    bs=BratServer(dataDir='~/CMProject/viz/brat-v1.3_Crunchy_Frog/data/povmap')
    bs.saveDoc(doc, ['Entity', 'Claim'])