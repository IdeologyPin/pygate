from nltk.tree import *
class TreeUtils:
    @classmethod
    def tree(self, clause_ann):
        return ParentedTree.fromstring(clause_ann.getFeature('constituency-parse'))

    @classmethod
    def getTokensWithinSubtree(self, sent, tree, subtree):
        spos = subtree.treeposition()
        lpos = subtree.leaf_treeposition(0)
        subStart = tree.treepositions("leaves").index(spos + lpos)
        subEnd = subStart + len(subtree.leaves())
        doc = sent.getDoc()
        return doc.getTokens()[sent.tStart + subStart: sent.tStart + subEnd]

    @classmethod
    def traverseTree(self, tree):
        label = tree.label()
        print("node:", label)
        for subtree in tree:
            if type(subtree) == nltk.tree.ParentedTree:
                self.traverseTree(subtree)