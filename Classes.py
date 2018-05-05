#This module contains self-made variables used by this program.
import numpy
import copy
#This module contains qt wrapper classes as used by this program.
from PyQt5 import QtGui, QtWidgets, QtCore, uic,Qt
import os, io, sys, copy, numpy
import math, csv
from PIL import Image, ImageQt
from resizeimage import resizeimage
import copy
import os 
import PyQt5
import csv


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
            assert isinstance(annot, qtWrapperClasses.Annotation)
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
        self.category = _bbox.getCategory()
        self.rect = _bbox.getRect()
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
        
        ctg = category(0, self.itemText(index), index)
        print(ctg.getName())
        self.setCategory(ctg)
        return

    def setInitCtg(self,index):
        self.setCurrentIndex(index)
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
            
            annot = Annotation(self.label, _bbox)
            #print(annot.getRect().x2())
            self.annotationManager.addAnnotation(annot)
            ctg = annot.category
            assert isinstance(ctg, category)
            annot.setInitCtg(ctg.getnumericId())
            
            # pos = QtCore.QSize(_bbox.getRect().x1(), _bbox.getRect().y1())
            pos = QtCore.QPoint(_bbox.getRect().x1(), _bbox.getRect().y1())
            annot.move(pos)
            annot.show()

        return
            
    def updateCurrentPicAnnot(self):
        dmanager.updateImageAnnot(self.currimage, self.annotationManager.getNormalizedAnnots())
        return        
            
        
        
openImagesClassDescription = "/home/ahmad/sda4/Software/data/openImages/2017_11/class-descriptions.csv"

#This class converts openimages data to ours.

class openImagesDataParser:

    def __init__(self):
        return
    
    def openCSV(self, csvURL):
        csvFile =  open(csvURL, 'r')
        reader = csv.reader(csvFile, delimiter=',')
        return reader
    
    def getNameFromClassID(self, classID):
        className = None
        #Row [2] is the label name.
        _csv = self.openCSV(openImagesClassDescription)
        print("LOOking for class ID " + classID)
        for row in _csv:
            #print(row[0])
            if classID == row[0]:
                className = row[1]
                print("classid " + row[0] + "Class name "+ className)
            
            
        
        return className


class csvReader:
    
    def __init__(self):
        return 

    #Returns bboxs from csvURL
    @staticmethod
    def bboxFromCSV(csvURL, imageHeight, imageWidth):

        i = 3
        _bboxs = []
        with open(csvURL) as f :
            for row in csv.reader(f, delimiter=',', dialect='excel'):
                #print("Numeric ID " + row[1])
                ctg = category(0,row[0], int(row[1]))

                _rect = boundingRect( float(row[i+0]) * imageWidth,float(row[i+1]) * imageHeight, 
                float(row[i+2]) * imageWidth, float(row[i+3]) * imageHeight)
                #print("From bboxfromCSV BBox x1: %i, y1: %i, x2: %i, y2: %i" %(_rect.x1(), _rect.y1(), _rect.x2(), _rect.y2() ))
                
                _bbox = bbox(ctg, _rect)
                #print("BBOX numeric id" + ctg.getnumericId())
                _bboxs.append(_bbox)
                rect = _bbox.getRect()
                
    
        return _bboxs




#This class will be responsible for storing, and updating the meta data of the program. Which primarily stores the 
#paths to images and there annotations.
class metaData:
    metaDataPath = currDir + "/data/data.metadata"
    metaDataCSVReader = None
    metaDataCSVWriter = None
    extentions = ['.jpg']
    openImagesDataParser = openImagesDataParser()
    labelPath = currDir + "/data/labels.txt"

    def __init__(self):
        assert isinstance(self.openImagesDataParser, openImagesDataParser)
        self.setup()
        return

    def setup(self):
        #self.setcsvwriter()
        self.createMetaData()
        self.convertCSVFiles()
        return
        
    #Retrieves Images from folders, and stores them as meta data.
    def createMetaData(self):
        
        f = open(self.metaDataPath,'w+')
        _csv = csv.writer(f, dialect='excel', delimiter=',')
        

        imageFolder = os.path.dirname(os.path.realpath(__file__)) + "/data/picsAndAnnots/"
        for subdir,dirs, files in os.walk(imageFolder):
            for file in files:
                ext = os.path.splitext(file)[-1].lower()
                fileName = os.path.splitext(file)[0]
                realImagePath = imageFolder + file
                realAnnotPath = imageFolder + fileName + ".txt"
                #Get all the extention jpg, and store there imageURL and bbox annotations, as images.
                if ext in self.extentions:
                    #print(realImagePath)
                    #self.addRow(fileName, realImagePath, realAnnotPath)
                    _csv.writerow([fileName,realImagePath,realAnnotPath])         
        return

    #Helper function to convert csv files imported from elsewhere.
    def convertCSVFiles(self):
        csvurls = self.getCSVURLs()
        
        mod = False
        for url in csvurls:
            self.rewriteCSV(url)

    def rewriteCSV(self, url):
        oldrows = []
        with open(url) as f:
            _csv = csv.reader(f, delimiter=',', dialect='excel')

            for row in _csv:
                if len(row) > 7:
                    
                    oldrows.append(row)
            
            f.close()

        if len(oldrows) > 0:
            
            with open(url,'w+') as f:
                _csv = csv.writer(f, delimiter=',', dialect='excel')
                print("Modifying data")  + url
                for row in oldrows:
                    ctg = self.openImagesDataParser.getNameFromClassID(row[2])
                    fileName = row[0]
                    # x1 = row[4]
                    # y1 = row[5]
                    # x2 = row[6]
                    # y2 = row[7]
                    x1 = row[4]
                    x2 = row[5]
                    y1 = row[6]
                    y2 = row[7]                    
                    _csv.writerow([ctg, self.getImageID(ctg),fileName,x1,y1,x2,y2])                    
            
            f.close()

    def openCSV(self, csvURL):
        csvFile =  open(csvURL, 'r')
        reader = csv.reader(csvFile, delimiter=',')
        return reader

    def getImageID(self, ctg):
        _csv = self.openCSV(self.labelPath)
        i = 0
        for row in _csv:
            if row[0] == ctg:
                print("Found " + ctg + " with ID " + str(i)) 
                return i
            i = i + 1

        return -1

    #Returns a list of image Urls.
    def getImageURLs(self):
        imgurls = []

        with open(self.metaDataPath) as f:
            _csv = csv.reader(f, dialect='excel', delimiter=',')
            for row in _csv:
                imgurls.append(row[1])
        
        return imgurls

    def getCSVURLs(self):
        imgurls = []

        with open(self.metaDataPath) as f:
            _csv = csv.reader(f, dialect='excel', delimiter=',')
            for row in _csv:
                imgurls.append(row[2])
        
        return imgurls

    #Adds image info to meta data.
    def addRow(self, imageName, imagePath, annotPath):
        with open(self.metaDataPath,'w+') as f:
            _csv = csv.writer(f, dialect='excel', delimiter=',')
            _csv.writerow([imageName,imagePath,annotPath]) 
            
        return

    def setcsvwriter(self):
        if not os.path.exists(self.metaDataPath):
            f= open(self.metaDataPath, 'w+')
            f.close()        
        with open(self.metaDataPath,'w+') as f:
            
            self.metaDataCSVWriter = csv.writer(f, dialect='excel', delimiter=',')

        return


#This class contains functions responsible for managing user data, pictures, annotations etc..
class dataManager:
    currDir = None
    pathToLabel = None
    #List of categories(category)
    _categories = []

    def __init__(self):
        #Gets info from non-volatile media.
        self.setup()
        return

    #Sets up variables
    def setup(self):
        self.currDir = dir_path = os.path.dirname(os.path.realpath(__file__))
        self.pathToLabel = self.currDir + "/data/labels.txt"
        self.getCategoriesFromCVS(self.pathToLabel)

    def getCategoriesFromCVS(self, cvsPath):
        
        if not os.path.exists(cvsPath):
            print("Labels file doesnt exist")
            return
        
        with open(cvsPath,'rb') as csvFile:
            reader = csv.reader(csvFile,delimiter=',')
            #Start category id's at 1
            ctgid = 1
            for row in reader:
                self._categories.append(category(ctgid,row[0],ctgid))
                ctgid = ctgid + 1
            csvFile.close()
            
            
    def updateImageAnnot(self, img, annots):
        assert isinstance(img, image)
        #Opening file as w+ removes earlier data.
        with open(img.getImageAnnotURL(), 'w+') as f:
            
            csvreader = csv.writer(f,delimiter=',', dialect='excel')
            for annot in annots:
                assert isinstance(annot, qtWrapperClasses.Annotation)
                index = annot.currentIndex()
                fileName=img.getImageName()
                ctg = annot.itemText(index)
                x1= annot.getRect().x1()
                y1=annot.getRect().y1()
                x2 = annot.getRect().x2()
                y2=annot.getRect().y2()
                csvreader.writerow([ctg, index, fileName, x1, y1, x2, y2 ])

        return

    #Adds category 
    def addCtg(self):
        #Update the drop down list.
        #Add directory if it doesn't exist, also validate dirs
        return

    def storeCategories(self, ctgs):
        return

    def updateMetaData(self):
        #Update the csv(txt) file which holds, image name(uID), and its annotations.
        
        return

    def getCategories(self):
        return self._categories

    def getCategoriesString(self):
        ctgs = []
        for category in self.getCategories():
            ctgs.append(category.getName())
        
        return ctgs

class manager:
    data = None

    def __init__(self):
        self.data = dataManager()

    def getData(self):
        return self.data

    def getCategoriesString(self):
        ctgs = []
        for category in self.data.getCategories():
            ctgs.append(category.getName())
        
        return ctgs