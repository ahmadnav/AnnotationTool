#This module contains self-made variables used by this program.
import numpy
#import qtWrapperClasses
import copy


class annotationManager:
    annotations = []    
    currentAnnot = None

    def __init__(self):
        return
    
    def addAnnotation(self, annot):
        self.annotations.append(annot)
        return

    def getAnnotations(self):
        return self.annotations

    def getRects(self):
        rects = []
        for annot in self.annotations:
            #assert isinstance(annot, Annotation)
            rects.append(annot.getRect())
        
        return rects

    def setCurrAnnot(self, annot):
        self.currentAnnot = annot

    def getcurrentAnnot(self):
        return self.currentAnnot

    def clearAll(self):
        
        for annot in self.annotations:
            annot.delete()
        #Make sure all references to the annotations are cleared.
        del self.annotations[:]

    def getNormalizedAnnots(self, width, height):
        annots = []
        for annot in self.annotations:
            #assert isinstance(annot, qtWrapperClasses.Annotation)
            rect = annot.getRect()
            normRect = boundingRect(rect.x1()/width, rect.y1()/ height, rect.x2()/width, rect.y2()/height)
            
            _annot = copy.deepcopy(annot)
            _annot.setRect(normRect)
            annots.append(_annot)
        return annots

#Represents a category
class category:
    #Unique ID
    _id = None
    #Human Readable Name
    _name = None
    #Numeric ID
    _nid = None

    def __init__(self, id=None, name=None,nid=None):
        self._nid = nid
        self._id = id
        self._name = name
        return

    def getName(self):
        return self._name

    def getId(self):
        return self._id

    def getnumericId(self):
        return self._nid
    
class bbox:
    rect = None
    category = None

    def __init__(self, categ=None ,rect=None):
        self.category = categ
        self.rect = rect
        #assert isinstance( self.category ,category)
        return

    def fromBBox(self,_bbox):
        assert isinstance(_bbox, bbox)
        print("Setting from bbox %s and id %i" %(_bbox.getCategory().getName(), _bbox.getCategory().getnumericId()) )
        self.category = _bbox.getCategory()
        self.rect = _bbox.getRect()
        print("@Setting from bbox %s and id %i" %(self.category.getName(), self.category.getnumericId()) )
        return

    def setRect(self, rect):
        self.rect = rect

    def setCategory(self, category):
        self.category = category

    def getRect(self):
        return self.rect

    def getCategory(self):
        return self.category
    
    

class boundingRect:
    rect = []
    def __init__(self, x1, y1, x2, y2):
        #print("From bounding rect init BBox x1: %f, y1: %f, x2: %f, y2: %f" %(x1, y1, x2, y2 ))
        self.rect = [x1, y1, x2, y2]

    def setMax(self, width, height):
        self.boundMax(width, height)
        
    
    #Ensures that the rect does not exceed this dimenstions.
    def boundMax(self, width, height):
        print("Bound max called")
        xs = [self.rect[0], self.rect[2]]
        ys = [self.rect[1], self.rect[3]]

        xs = numpy.clip(xs, 0,width)
        ys = numpy.clip(ys, 0, height)

        self.rect = [xs[0],ys[0], xs[1],ys[1]]

    def x1(self):
        return self.rect[0]
    def y1(self):
        return self.rect[1]
    def x2(self):
        return self.rect[2]
    def y2(self):
        return self.rect[3]

class image:
    
    imageURL = None
    imageAnotURL = None
    imageName = None
    def __init__(self, imageName, imageUrl, imageAnnotURL):
        
        self.imageURL = imageUrl
        self.imageAnotURL = imageAnnotURL
        self.imageName = imageName
        return

    def getImageAnnotURL(self):
        return self.imageAnotURL

    def getImageURL(self):
        return self.imageURL

    def setImageURL(self, url):
        self.imageURL = url
        return

    def getImageName(self):
        return self.imageName

    