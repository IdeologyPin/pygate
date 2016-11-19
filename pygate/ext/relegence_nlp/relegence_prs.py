from pygate import PR, Annotation, Document

from relegence import Relegence


class RelEntityTagger(PR):
    def __init__(self, entity_tag_name='Entity'):

        self.rs = Relegence()
        self.tagger = self.rs.tagger
        self.entity_tag_name = entity_tag_name

    def process(self, doc):
        '''
        :type doc Document
        :param doc:
        :return:
        '''
        res = self.tagger.get_tags(doc['url'])
        entities = res["result"]["tags"]["entities"]
        annots = []
        for e in entities:
            wikidata_id = None

            ref = e['references']
            for r in ref:
                if r['type'] == 'Wikidata':
                    wikidata_id = r["id"]

            name_s=e['name'].split(' ')

            for instance in e['instances']:
                if instance['field'] == 'Body':
                    cStart = max(0, instance['offset'] -15)
                    cEnd = min( cStart + instance['length'] +15 , len(doc.text))

                    tokens=[]
                    for ns in name_s:
                        tkns = doc.find(ns, cStart, cEnd)
                        if tkns!=None:
                            tokens.extend(tkns)
                    tokens=sorted(tokens, key=lambda t:t.cStart)

                    if len(tokens)>0:
                        ann = doc.make_annotation(tokens, self.entity_tag_name)
                        ann['wikidata'] = wikidata_id
                            # Annotation(doc.text, 0,0, cStart,cEnd, self.entity_tag_name, doc )
