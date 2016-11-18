from pygate import PR
from collections import defaultdict

import httplib2

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials


def get_google_service():
    """
        to initialize googlecredentials
    """
    credentials = GoogleCredentials.get_application_default()
    scoped_credentials = credentials.create_scoped(
        ['https://www.googleapis.com/auth/cloud-platform'])
    http = httplib2.Http()
    scoped_credentials.authorize(http)
    return discovery.build('language', 'v1beta1', http=http)


class SentimentAnalyserPR(PR):

    def __init__(self, level):
        self.level = level
        self.service = get_google_service()

    def process(self, doc):
        '''
        :param doc:
        :return:
        '''
        annots=doc[self.level]
        print len(annots)
        for ann in annots:
            gs = self.get_sentiment(ann)
            ann.features['gs_magnitude'] = gs[0]
            ann.features['gs_score'] = gs[1]


    def get_sentiment(self, span):
        """
            use google cloud nlp to get sentiment
        """

        body = {'document': {
            'type': 'PLAIN_TEXT',
            'content': span.text
        }
        }
        request = self.service.documents().analyzeSentiment(body=body)
        response = request.execute()
        return [response["documentSentiment"]["magnitude"], response["documentSentiment"]["polarity"]]
