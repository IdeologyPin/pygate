from pygate import Document, Annotation
import pygate as pg


brat = pg.export.BratFormat()

def test_saveAsBrat():

    doc=Document(u"Sample Text\nHello World!")
    doc.addAnnotation(Annotation('Text', 1,1,7,11,'Sample'))
    brat.saveAsBrat(doc, ['Sample'],'~/tmp/')

