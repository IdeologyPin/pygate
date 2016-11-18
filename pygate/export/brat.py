import re

from IPython.display import IFrame

from pygate.base.doc import *
from pygate.utils.fileUtils import *


# import codecs

class BratFormat(object):

    def saveAsBrat(self, doc, annotypes, dir):

        annFile=os.path.expanduser(os.path.join(dir, ".".join([doc.getId(),'ann'])))
        txtFile=os.path.expanduser(os.path.join(dir, ".".join([doc.getId(),'txt'])))

        if not os.path.exists(dir):
            os.makedirs(dir)

        with open(txtFile, 'w') as txtFile:
            txtFile.write(doc.getString())
            txtFile.close()

        with open(annFile, 'w') as annFile:
            id_prefix=0
            for type in annotypes:
                self.__saveAnnotsOfType(doc, type, annFile, id_prefix)
                id_prefix+=1
            annFile.close()

    def __saveAnnotsOfType(self, doc, type, annFile, id_prefix):
        annots=doc[type]
        for ann in annots:
            line="".join(['T', str(ann.idx) , '-', type , '\t' , ann.subType , ' ', str(ann.cStart),' ', str(ann.cEnd), '\t', ann.text(), '\n'])
            annFile.write(line.encode('utf-8'))

    def __saveRelationship(self):
        pass


class BratServer(DataSink):

    def __init__(self, dataDir, host='localhost', port='8001', username=None, keyfile=None, ssh_port='20'):
        """
        :param dataDir:
        :param host:
        :param port: the port brat server is running on.
        :param username: host machines username. if an aws ubuntu server it may be 'ubuntu'
        :param keyfile: private key file to scp to remote server
        """
        self.serverDir = dataDir
        self.host = host
        self.username = username
        self.keyfile = keyfile
        self.port=port
        self.ssh_port=ssh_port

        self.formatter=BratFormat()
        #TODO if subdirs under brat/data dir.
        self.dataDir=re.compile("[/\\\]").split(self.serverDir)[-1]

    def saveDocs(self, annotypes):
        for doc in self.data:
            self.saveDoc(doc, annotypes)

    def saveDoc(self,doc, annotypes):
        if self.host=='localhost':
            self.__savelocal(doc, annotypes)

    def __savelocal(self,doc, annotypes):
        self.formatter.saveAsBrat(doc,annotypes, self.serverDir)

    def draw(self, doc, annotypes):
        self.saveDoc(doc, annotypes)
        return IFrame("".join(['http://', self.host, ':', self.port, '/index.xhtml#/', self.dataDir, doc.getId()]), width='100%', height=700)
