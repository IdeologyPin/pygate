from pygate import PR, Annotation, Document

from relegence import Relegence

class RelEntityTagger(PR):

    def __init__(self, entity_tag_name='Entity'):

        self.rs=Relegence()
        self.tagger=self.rs.tagger
        self.entity_tag_name = entity_tag_name


    def process(self,doc):
        '''
        :type doc Document
        :param doc:
        :return:
        '''

        res=self.tagger.get_tags(doc['url'])
        entities=res["result"]["tags"]["entities"]
        annots=[]
        for e in entities:
            for instance in e['instances']:
                if instance['field']=='Body':
                    cStart=instance['offset']
                    cEnd=cStart+instance['length']

                    Annotation(doc.text, 0,0, cStart,cEnd, self.entity_tag_name, doc )
