__author__ = 'sasinda'
from pygate import PR
from nltk import classify
import sklearn.metrics
import collections as coll
import numpy as np
from copy import copy
import pickle


class ClassifierPR(PR):
    '''
    @param model= needs to be a NLTK ML model. Wrap scikit models as NLTK's SklearnClassifier.
    @param outputKey = the label name that the precicted annotation will have.
    @param mode = inference: for running model against test samples
                  train: for collecting the training dataset.
                  Need to explicitly run train() after the pipeline is complete to start training the model.
    '''

    def __init__(self, modelClass, level, featureFilter=None, inputLabel='class', outputLabel='pred', mode='train'):
        self.modelClass = modelClass
        self.model = None
        self.mode = mode
        self.level = level
        self.outputLabel = outputLabel
        self.inputLabel = inputLabel
        self.filtr = featureFilter
        self.data_set = {'all': []}

    def process(self, doc):
        level = self.level
        outputKey = self.outputLabel
        if self.mode == 'train':
            self.collectTrainSet(doc)
        elif self.mode == 'inference':
            self.predict(doc)

    def collectTrainSet(self, doc):
        if self.filtr:
            feats = self.__filterFeatures(self.filtr)
        else:
            feats = [(t.get_features(), t.get_label(self.inputLabel)) for t in doc[self.level]]
        self.data_set['all'].extend(feats)

    def __filterFeatures(self):
        raise NotImplemented

    def getDataSet(self, name):
        ''' trainSet is [(features:{}, label:str)] list of tuples'''
        return self.data_set[name]

    def split(self, splits={'validation': 0.2, 'train': 0.8}):
        '''splits the dataset into train and validation'''
        all_data = self.data_set['all']
        start = 0
        for key, value in splits.iteritems():
            split = int(len(all_data) * value)
            self.data_set[key] = all_data[start:start + split]
            start += split

    def train(self, modelParams={}, dataset_name='train', validate=True):
        '''
#         @param classRatios: list of tuples, class label and ratio.
          @param positive to negative ratio as a tuple.
        '''

        if not self.data_set.has_key(dataset_name): self.split()
        if not self.data_set.has_key(dataset_name): raise ValueError(
            "Please split the dataset before training. Call to this method ran split with default parameters, so you may use dataset_name as train, or explicitly split")

        train_set = self.data_set['train']
        self.model = self.modelClass.train(train_set, **modelParams)
        if validate: self.validate()

    def validate(self, dataset_name='validation'):

        if not self.data_set.has_key(dataset_name):  raise ValueError("Please split the dataset before validation")

        val_set = self.data_set[dataset_name]
        predlist = self.model.classify_many([feat for feat, label in val_set])
        truelist = []
        for i in range(len(predlist)):
            actual_label = val_set[i][1]
            truelist.append(actual_label)

        print 'pos precision:', sklearn.metrics.precision_score(truelist, predlist, pos_label=1)
        print 'pos recall:', sklearn.metrics.recall_score(truelist, predlist, pos_label=1)
        print 'pos F-measure:', sklearn.metrics.f1_score(truelist, predlist, pos_label=1)
        print 'neg precision:', sklearn.metrics.precision_score(truelist, predlist, pos_label=0)
        print 'neg recall:', sklearn.metrics.recall_score(truelist, predlist, pos_label=0)
        print 'neg F-measure:', sklearn.metrics.f1_score(truelist, predlist, pos_label=0)

    def trainCrossValidate(self):
        raise NotImplemented

    def balanceDataset(self, classRatios, data_set_from='train', data_set_to='train', randomShuffle=True):
        balancer = coll.defaultdict(list)
        for datum in self.data_set[data_set_from]:
            cls = datum[1]
            balancer[cls].append(datum)

        common_denom = len(self.data_set[data_set_from])
        for cls, ratio_term in classRatios:
            common_denom = min(common_denom, len(balancer[cls]) / ratio_term)

        balancedSet = []
        for cls, ratio_term in classRatios:
            balancedSet.extend(balancer[cls][:int(common_denom * ratio_term)])

        if randomShuffle:
            np.random.shuffle(balancedSet)
        self.data_set[data_set_to] = balancedSet

    def predict(self, doc):
        feats = [t.get_features() for t in doc[self.level]]
        preds = self.model.classify_many(feats)
        for i, ann in enumerate(doc[self.level]):
            ann.set_label(self.outputLabel, preds[i])

    def save(self, prFile, setMode='inference'):
        me = self
        me.mode = setMode
        if setMode == 'inference':
            me = copy(self)
            me.data_set = None
            me.balanced_data_set = None

        super(self.__class__, me).save(prFile)