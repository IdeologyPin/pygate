import requests
import json

_API_KEY = 'V7lmZgPn7NGdEYSp9DGA8l1AsK5zRy8I'
_HOST = 'http://api.relegence.com/'
_HOST_STAGING = 'http://stage.api.relegence.com/'
_CACHE = {}


class Relegence:
    '''
    Religence API client
    documentation for endpoints are at http://www.aolpublishers.com/support/documentation/relegence/services/
    '''

    def __init__(self, API_KEY=_API_KEY):
        self.API_KEY = API_KEY
        self.stories = self.Stories(self)
        self.trending = self.Trending(self)
        self.taxenomy = self.Taxenomy(self)
        self.tagger=self.Tagger(self)
        self._def_params = {'apikey': self.API_KEY}

    '''
    '''

    class Trending:
        __req_base = _HOST + 'trending/'
        def __init__(self, outer):
            self.outer=outer
            self.topics = []

        # @cached
        def by_subject(self, subject_id, params={}):
            '''
                params={'withDocs': True}
            '''
            params['lastActivityDaysBack']= 120
            params['creationDaysBack'] = 30
            params['minScore'] = 0.7
            params['count'] = 20
            params['docsPerTopic'] = 5
            params['orberBy'] = 'magScore'
            p = merge_dicts(self.outer._def_params, params);
            resp=requests.get(self.__req_base+subject_id, params=p)
            return to_json(resp)

    '''
    '''

    class Stories:
        _req_base = _HOST + 'stories/'

        def __init__(self, outer):
            self.outer = outer

        # @cached
        def by_subject(self, subject_id, params={}):
            '''
                params={'withDocs': True}
            '''
            p = merge_dicts(self.outer._def_params, params);
            return to_json(requests.get(self._req_base + subject_id, params=p))

        def by_story_id(self, story_id, params={}):
            '''
                params={'numDocs': 100}
            '''
            params = {'numDocs': 50}
            p = merge_dicts(self.outer._def_params, params);
            return to_json(requests.get(self._req_base + story_id, params=p))

    class Taxenomy:
        __req_base = _HOST + '/taxobrowser/'

        def __init__(self, parent):
            self.req_subjects = '/hierarchy/subjects'
            self.req_nodetypes = '/hierarchy/nodetypes'
            self.parent=parent

        # @cached
        def get_subjects_hierarchy(self, params={}):
            p = merge_dicts(params, self.parent._def_params)
            return to_json(requests.get(self.__req_base + self.req_subjects, params=p))

        # @cached
        def get_nodetypes_hierarchy(self, params={}):
            p = merge_dicts(params, self.parent._def_params)
            return to_json(requests.get(self.__req_base + self.req_nodetypes, params=p))

    class Tagger:
        __req_base=_HOST + "/tagger/2.0"

        def __init__(self):
            pass

        def get_tags(self,art_url, params={}):
            p = merge_dicts(params, self.parent._def_params)
            p['url'] = art_url
            return to_json(requests.get(self.__req_base , params=p))




def merge_dicts(x, y):
    # return x.update(y);
    return dict(x.items() + y.items())


def to_json(resp):
    if (resp.status_code == 200):
        return resp.json()
    else:
        resp.raise_for_status()
