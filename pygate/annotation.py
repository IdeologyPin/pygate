__author__ = 'sasinda'
from utils.collection import DotDict
class Annotation(object):
    def __init__(self, text, tStart, tEnd, cStart, cEnd, annoType, doc=None):
        self.features = DotDict()
        self.labels = DotDict()
        self.attributes=DotDict()
        self.items={'features':self.features, 'labels':self.labels, 'attributes':self.attributes}
        self.tStart = tStart
        self.tEnd = tEnd
        self.cStart = cStart
        self.cEnd = cEnd
        self.annoType = annoType
        self.subType=annoType
        self.doc = doc
        self.relations = {}
        self.idx = -1
        if type(text) == unicode:
            self.text = text
        else:
            self.text = unicode(text, 'UTF-8')

    def setIdx(self, idx):
        self.idx = idx

    def getText(self):
        '''Return the original text in unicode format. Use getString to get as unicode encoded byte string'''
        return self.text

    def getString(self):
        return self.text.encode('UTF-8', 'ignore')

    def setFeature(self, fname, fval):
        self.features[fname] = fval

    def getFeature(self, fname):
        return self.features[fname]

    def setFeatures(self, featureDic):
        if type(featureDic) is not DotDict:
            self.features=DotDict()
            self.features.update(featureDic)

    def updateFeatures(self, featureDic):
        self.features.update(featureDic)

    def getFeatures(self):
        return self.features

    def setLabel(self, name, value):
        self.labels[name] = value

    def getLabel(self, name):
        return self.labels[name]

    def getLabels(self):
        return self.labels

    def setAttribute(self, name, value):
        self.attributes[name]=value

    def getAttribute(self, name):
        return self.attributes[name]

    def setRelation(self, relName, annots):
        """
            Use the Relation wrapper class to add additional details to the annotation.
        """
        self.relations[relName] = annots

    def getRelation(self, relName):
        return self.relations[relName]

    def getContainingAnnots(self, annotType):
        pass

    def getDoc(self):
        return self.doc

    def __getitem__(self, key):
        return self.items[key]

    def __setitem__(self, key, value):
        if key in ('features', 'labels', 'attributes'):
            raise KeyError("Cannot replace the inbuilt items 'features', 'labels', 'attributes'")
        self.items[key] = value


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



