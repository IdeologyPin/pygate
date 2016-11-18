__author__ = 'sasinda'
from collections import defaultdict
from pygate.utils.collection import DotDict

class Annotation(object):
    def __init__(self, text, tStart, tEnd, cStart, cEnd, annoType, doc=None):
        self.features = DotDict()
        self.labels = DotDict()
        self.attributes = DotDict()
        self.items = {'features': self.features, 'labels': self.labels, 'attributes': self.attributes}
        self.tStart = tStart
        self.tEnd = tEnd
        self.cStart = cStart
        self.cEnd = cEnd
        self.annoType = annoType
        self.subType = annoType
        self.doc = doc
        self.relations = defaultdict(lambda : [])
        self.idx = -1
        if type(text) == unicode:
            self._text = text
        else:
            self._text = unicode(text, 'UTF-8')

    @property
    def text(self):
        '''Return the original text in unicode format. Use getString to get as unicode encoded byte string'''
        return self._text

    @property
    def string(self):
        return self._text.encode('UTF-8', 'ignore')

    def set_feature(self, fname, fval):
        self.features[fname] = fval

    def get_feature(self, fname):
        return self.features[fname]

    def set_features(self, featureDic):
        if type(featureDic) is not DotDict:
            self.features = DotDict()
            self.features.update(featureDic)

    def update_features(self, featureDic):
        self.features.update(featureDic)

    def get_features(self):
        return self.features

    def set_label(self, name, value):
        self.labels[name] = value

    def get_label(self, name):
        return self.labels[name]

    def get_labels(self):
        return self.labels

    def set_attribute(self, name, value):
        self.attributes[name] = value

    def get_attribute(self, name):
        return self.attributes[name]

    def set_relation(self, relName, annots):
        """
            Use the Relation wrapper class to add additional details to the annotation.
        """
        self.relations[relName] = annots

    def add_relation(self, relName, annot):
        self.relations[relName].append(annot)

    def get_relation(self, relName):
        return self.relations[relName]

    def get_containing_annots(self, annotType):
        pass

    def get_doc(self):
        return self.doc

    def __getitem__(self, key):
        if isinstance(key, slice):
            raise NotImplemented()
        elif isinstance(key, int):
            if key > 0:
                return self.doc[self.tStart + key]
            else:
                return self.doc[self.tEnd + 1 + key]
        else:
            return self.items[key]

    def __setitem__(self, key, value):
        if key in ('features', 'labels', 'attributes'):
            raise KeyError("Cannot replace the inbuilt items 'features', 'labels', 'attributes'")
        self.items[key] = value

    def __contains__(self, key):
        return self.items.__contains__(key)

    def __delitem__(self, key):
        return self.items.__delitem__(key)

    def __str__(self):
        # if type(self.__repr__()==unicode):
        #     return 'unicode'
        # else:
        #     return 'string'
        # return self.__repr__().encode('ascii', errors='ignore')
        return self.__repr__()

    def __repr__(self):
        return u''.join([self.text, u''.join(
            ['//', self.annoType, ':', str(self.idx), '//tidx', str(self.tStart), ":", str(self.tEnd)])]).encode(
            'UTF-8', 'ignore')

