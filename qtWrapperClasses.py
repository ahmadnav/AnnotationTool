#This module contains qt wrapper classes as used by this program.
from PyQt5 import QtGui, QtWidgets, QtCore, uic,Qt
import os, io, sys, copy, numpy
import math, csv
from PIL import Image, ImageQt
from resizeimage import resizeimage
import dataManager
from dataManager import manager, csvReader, dataManager
from objDetectVariables import boundingRect, bbox, annotationManager, category, image
#import objDetectVariables as oDV
import copy

dmanager = dataManager()
#Stores image file paths, and csv annot paths/names.
metaDataFile = os.path.dirname(os.path.realpath(__file__)) + "/data/data.metadata"

#This class is wrapper for Qcombobox and its corresponding bounding box + its own chosen category. 
class Annotation(Qt.QComboBox, bbox):
    annot = None
    #Parent widget of this class in the imgpreviewlabel.
    def __init__(self, Parent, bboxParent=None):
        #Initialize the inherited classes
        
        Qt.QComboBox.__init__(self, Parent)
        bbox.__init__(self)
        if bboxParent is not None:
            self.fromBBox(bboxParent)

        ctg = self.category
        #assert isinstance(ctg, category)
        #print(ctg)
        self.setUp()
        return

    def setUp(self):
        
        self.currentIndexChanged.connect(self.textChanged)
        self.addItems(dmanager.getCategoriesString())

    def textChanged(self, index):
        #Index is related to row which is related to labels.txt file.
        ctg = category(0, self.itemText(index), index)
        print(ctg.getName())
        self.setCategory(ctg)
        return

    #This is called from outside where init index starts at 1
    def setInitCtg(self,index):
        self.setCurrentIndex(index - 1)
        self.textChanged(index - 1)
        return

    def delete(self):
        print("Deleting")
        self.deleteLater()
        self.clear()


# This class the ImageListWidget which is responsible for displaying thumbnail images of images.
class imgListWidget(QtWidgets.QListWidget):
    imgpreviewClass = None
    #Parent wi
    def __init__(self, QListWidgetParent, imgPreviewClass):
        QtWidgets.QListWidget.__init__(self,QListWidgetParent)
        self.imgpreviewClass = imgPreviewClass
        self.setup()
        return
    
    def setup(self):
        self.itemClicked.connect(self.slotItemPressed)
        assert isinstance(self.imgpreviewClass, imgPreviewLbl)
        
        #self.imgpreviewClass.
        
        return

    #Displays images , updates
    def displayImages(self):
        with open(metaDataFile ,mode='r') as f:
            _csv = csv.reader(f, dialect='excel', delimiter=',')
            for row in _csv:
                self.addImage(row[1], row[0], row[2])

        print("Total Image count: "  + str( self.count()))
        return

    #Gets the clicked Image.
    def chooseImage(self):
        return

    def addImage(self, imgURL, imageName, imgCSVUrl):
        self.setViewMode(QtWidgets.QListView.IconMode)
        img = image(imageName, imgURL, imgCSVUrl)
        item = imageQListWidgetItem(img)
        item.setText(imageName)
        icon = QtGui.QIcon()        
        item.setSizeHint(QtCore.QSize(100,100))
        self.setIconSize(QtCore.QSize(100,100))
        self.setFixedSize( QtCore.QSize( 341,431))
        #self.setFixedSize( self.size())
        self.setWindowTitle("Pictures")
        icon.availableSizes
        icon.addPixmap(QtGui.QPixmap( imgURL), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        #icon.addPixmap(pixMap, QtGui.QIcon.Normal, QtGui.QIcon.Off)
        
        item.setIcon(icon)        
        self.addItem(item)        
        return

    def slotItemPressed(self,event):
        #print(event.text())
        #print(event.getimgURL())
        self.imgpreviewClass.setCurrentPreviewPic(event.getImage())
        return

#Wrapper form qlistwidget item which stores an individual image shown in a list.
class imageQListWidgetItem(QtWidgets.QListWidgetItem):
    _image = image(None,None,None)

    def __init__(self, img):
        QtWidgets.QListWidgetItem.__init__(self)
        self._image = img
        return
    
    def getimgURL(self):
        return self._image.getImageURL()
        
    def getImage(self):
        return self._image
    def getCSVURL(self):
        return self._image.getImageAnnotURL()
    
#This class handles variables, temporary storage  specifically for the image preview label
class imgPreviewLbl:
    label = None
    #Stores the position of the latest click (mouse Down).
    lastClickPos = None
    currPreviewPic = None
    imageURL = "/home/ahmad/sda4/Software/data/objectDetection/Crocodile/0026bb1742e969b7.jpg"
    #Python Image Object
    currImage = None
    #Specific image object contains annot and image url.
    currimage = image(None,None,None)
    imageqt = None
    prvimgPixMap = None

    annotationManager = annotationManager()

    def __init__(self, _label):
        self.label = _label
        #self.previewPic(self.imageURL)
        
        assert isinstance(self.annotationManager, annotationManager)

        return

    def onMouseClick(self, event):
        if self.currImage is None:
            print("No Image Selected.")
            return
        #print("Image Label Pressed at x: %i, y: %i" %(event.pos().x(), event.pos().y()))
        self.setLastClickPos(event.pos())        
        #Parent widget it the label.
        qbox = Annotation(self.label)
        items = dmanager.getCategoriesString()
        
        
        qbox.move(event.pos())
        qbox.setCategory(qbox.currentText())
        qbox.show()

        self.annotationManager.addAnnotation(qbox)
        self.annotationManager.setCurrAnnot(qbox)
        
    def onMouseMove(self, event):    
        if self.currImage is None:
            print("No Image Selected.")
            return        
        print("Mouse at x: %i, y: %i" %(event.pos().x(), event.pos().y()))        
        #_rect = boundingRect(self.lastClickPos.x(), self.lastClickPos.y(), event.pos().x(), event.pos().y())
        _rect = self.getBBox(event.pos().x(), event.pos().y())
        self.drawPreviewRect(_rect)

    def OnKeyPressed(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.clearAnnot()
        

    def clearAnnot(self):
        self.annotationManager.clearAll()
        #print("Escape Deleting all annot")
        self.drawAllAnnots()


    def setLastClickPos(self, lastClickPos):
        self.lastClickPos = lastClickPos

    def setCurrPreviewPic(self, prvPic):
        self.currImage = prvPic
    
    #Handles the events when mouse button is released. Primarily stores the bounding box location.
    def onMouseRelease(self, mouseReleasePos):
        if self.currImage is None:
            print("No Image Selected.")
            return        
        #Set up the current bbox.
        rect = self.getBBox(mouseReleasePos.x(), mouseReleasePos.y())
        currentAnnot = self.annotationManager.getcurrentAnnot()
        assert isinstance(currentAnnot, Annotation)
        currentAnnot.setRect(rect)
        currentAnnot.setCategory(currentAnnot.currentText())

        self.drawRects(self.annotationManager.getRects())
        #self.printAllAnnots()

    def printAllAnnots(self):
        for annot in self.annotationManager.getAnnotations():
            assert isinstance(annot, Annotation)
            rect = annot.getRect()
            print("Category: " + annot.getCategory().getName())
            print("BBox x1: %f, y1: %f, x2: %f, y2: %f" %(annot.getRect().x1(), rect.y1(), rect.x2(), rect.y2() ))        

    #Returns a bounding box rectangle based on 2 points.
    def getBBox(self, p1, p2):
        
        width, height = self.currImage.size
        #This is the point within the label where the user first clicked.
        x1 = self.lastClickPos.x() 
        y1 = self.lastClickPos.y() 
        x2 = p1
        y2 = p2

        rectangle = boundingRect(x1, y1,x2,y2)
        #Sets the maxes.
        rectangle.setMax(width, height)
        return rectangle

    def drawAllAnnots(self):
        self.drawRects(self.annotationManager.getRects())

    def drawPreviewRect(self, rect):
        #Draw all the previous rects
        # for _rect in self.bbox:
        #     self.drawRect(_rect)
        #Draw Current Rect
        #self.bbox.append(rect) 
        _rect=[]
        if len(self.annotationManager.getRects()) > 0:
            _rect = copy.deepcopy(self.annotationManager.getRects())
        _rect.append(rect)
        self.drawRects(_rect)
        #self.bbox = self.bbox[:-1]

    #Draws multiple rectangle on the image.
    def drawRects(self, rects):
        #image = Image.Image()

        imgqt = ImageQt.ImageQt(self.currImage)
        pixMap = QtGui.QPixmap.fromImage(imgqt)
        painter = QtGui.QPainter(pixMap)
        painter.setPen(QtGui.QColor(255,0,0,255))
        
        width, height = self.currImage.size
        
        for rect in rects:
            if rect is None:
                continue
            print("Drawing Rects BBox x1: %f, y1: %f, x2: %f, y2: %f" %(rect.x1(), rect.y1(), rect.x2(), rect.y2() ))     
            print("Width %f, Height %f." %(width,height))
            x1 = rect.x2()
            x2 = rect.x1()
            y1 = rect.y1()
            y2 = rect.y2()

            _width  = x2 - x1
            _height = y2 - y1
            painter.drawRect(x1 , y1 , _width , _height )
        painter.end()
        
        self.label.setPixmap(pixMap)
        return

    def drawRect(self, rect):
        imgqt = ImageQt.ImageQt(self.currImage)
        pixMap = QtGui.QPixmap.fromImage(imgqt)

        painter = QtGui.QPainter(pixMap)
        
        
        painter.setPen(QtGui.QColor(255,0,0,255))
        _width  = rect.x2() - rect.x1()
        _height = rect.y2() - rect.y1()
        painter.drawRect(rect.x1(), rect.y1(), _width, _height)
        painter.end()
        
        self.label.setPixmap(pixMap)

    def setCurrentPreviewPic(self, _image):
        assert isinstance(_image,image)
        self.currimage = _image
        
        self.previewPic()
        return

    #Shows the image are path in the preview label.
    def previewPic(self):
        imgPath = self.currimage.getImageURL()
        imgCSVUrl = self.currimage.getImageAnnotURL()

        label = self.label

        #Scale the image so it fits in the preview
        size = label.size()
        #print(size)

        img = Image.open(imgPath)
        #Resizes the image to these dims, while keeping the aspect ratio.
        resizedImg = resizeimage.resize('thumbnail',img,[size.width(),size.height()])
        width, height = resizedImg.size
        #print("Image Size (w,h): %i, %i " %(width, height))
        #img.thumbnail([300,300])

        imgqt = ImageQt.ImageQt(resizedImg)
        
        #pixMap = self.getPixMap("/home/ahmad/sda4/Software/data/objectDetection/Crocodile/0026bb1742e969b7.jpg")
        pixMap = QtGui.QPixmap.fromImage(imgqt)
        #Set this pix map as the current one displayed on the label.
        #self.setCurrPreviewPic(resizedImg)
        self.currImage = resizedImg

        self.imageqt = imgqt
        self.prvimgPixMap = pixMap
        label.setPixmap(pixMap)     

        #Clear past annotations.
        self.annotationManager.clearAll()
        self.fillAnnotManager(imgCSVUrl)
        self.drawAllAnnots()
        self.printAllAnnots()
        return

    # Populates the current annot with the annotations.
    def fillAnnotManager(self, csvURL):
        width, height = self.currImage.size
        #Returns bboxs from csvURL's
        bboxs = csvReader.bboxFromCSV(csvURL, height, width)
        #print("Filling annot Manager")
        for _bbox in bboxs:
            assert isinstance(_bbox, bbox)
            print(csvURL)
            print("1Setting ID to " + str( _bbox.getCategory().getnumericId() ) + " " + _bbox.getCategory().getName())
            annot = Annotation(self.label, _bbox)
            #print(annot.getRect().x2())
            self.annotationManager.addAnnotation(annot)
            ctg = annot.getCategory()
            assert isinstance(ctg, category)
            print("Setting ID to " + str( ctg.getnumericId() ) + " " + annot.getCategory().getName())
            annot.setInitCtg(_bbox.category.getnumericId())
            
            # pos = QtCore.QSize(_bbox.getRect().x1(), _bbox.getRect().y1())
            pos = QtCore.QPoint(_bbox.getRect().x1(), _bbox.getRect().y1())
            annot.move(pos)
            annot.show()

        return
            
    def updateCurrentPicAnnot(self):
        width, height = self.currImage.size

        dmanager.updateImageAnnot(self.currimage, self.annotationManager.getAnnotations(), width, height)
        return        
            
        
    def removeCtg(self, ctg):
        dmanager.removeCtg(ctg)

    def addCtg(self, ctg):
        dmanager.addCtg(ctg)