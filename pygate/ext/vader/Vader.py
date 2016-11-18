from pygate import PR, Document, Annotation
from vaderSentiment.vaderSentiment import sentiment as vaderSentiment


class VaderSentimentPR(PR):
    '''
    https://medium.com/@aneesha/quick-social-media-sentiment-analysis-with-vader-da44951e4116#.a0cpnukda
    '''

    def __init__(self, level):
        self.level = level

    def process(self, doc):
        for ann in doc[self.level]:
            vs = vaderSentiment(ann.text)
            ann.features['vs_pos'] = vs.pos
            ann.features['vs_neg'] = vs.neg
            ann.features['vs_neu'] = vs.neu
            ann.features['vs_compound'] = vs.compound
