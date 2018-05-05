from PyQt5 import QtGui, QtWidgets, QtCore, uic,Qt
import os, io, sys, copy, numpy
import math
from PIL import Image, ImageQt
from resizeimage import resizeimage
from objDetectVariables import boundingRect 
from qtWrapperClasses import imgPreviewLbl, imgListWidget
from dataManager import metaData, csvReader
#from Classes import *

qtUIMainWindow = "/home/ahmad/sda4/Software/programs/objDetect/objDetectProgram.ui"
UI_MainWindow, QtBaseClass = uic.loadUiType(qtUIMainWindow)

#Classes in bracket are inherited, i.e. imageSearchGUI is derived from them.
class objDetectMainWindow(QtWidgets.QMainWindow, UI_MainWindow):
    prvPicLbl = None
    #Wrapper for QtLabel for previewing Pics; Stores information pretaining to the image preview label(qtdesigner UI Label for PixMaps).
    imgprvlblClass = None
    imgListWidgetClass = None
    metaDataClass = metaData()
    #Progress bar to indicate how many of the images have been tfRecorded.
    tfRecordsprogressBar = None

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        UI_MainWindow.__init__(self)
        
        
        #print(_bboxs[0].getCategory().getnumericId() + " Name " + _bboxs[0].getCategory().getName())
        
        #Function of inherited class, has to be called first.
        self.setupUi(self)
        
        self.setupVars()
        self.setupUI()
        
        
    
    #Sets up the required Variables.
    def setupVars(self):
        #The latter is the name in qtCreator
        self.prvPicLbl = self.imgprvlabel
        #Instantiations
        self.imgprvlblClass  = imgPreviewLbl(self.imgprvlabel)
        self.tfRecordsprogressBar = self.tfRecordProgress
        

    #Sets up the ui buttons etc...
    def setupUI(self):
        #self.actionGetImages.triggered.connect( self.getAndStoreImages)
        print("Setting up UI")
        k = self.label
        # Image preview is a lable which signals a mousepressevent whenever a mouse is pressed within it.
        self.prvPicLbl.mousePressEvent = self.slotImgPrvMousePressed
        self.prvPicLbl.mouseMoveEvent = self.slotImgPrbMouseMove
        self.prvPicLbl.mouseReleaseEvent = self.slotImgPrvMouseRelease
        self.keyPressEvent = self.slotImgPrvKeyPressed
        #self.previewPic("/home/ahmad/sda4/Software/data/objectDetection/Crocodile/0026bb1742e969b7.jpg")
        self.imgListWidgetClass = imgListWidget( self.imgListWidget, self.imgprvlblClass)
        self.imgListWidgetClass.displayImages()

        assert isinstance(self.tfRecordsprogressBar, Qt.QProgressBar)
        
        self.tfRecordsprogressBar.reset()

        self.saveAnnotsBtn.clicked.connect(self.slotStoreAnnotPressed)
        self.rmvctgButton.clicked.connect(self.slotRmvCtgPressed)
        self.addctgButton.clicked.connect(self.slotAddCtgPressed)
        self.createTfRecords.clicked.connect(self.slotStoreTFRecordsPressed)
        return


    

    def getPixMap(self, imgPath):
        label = self.imgprvlabel
        #Scale the image so it fits in the preview
        size = label.size()
        print(size)

        img = Image.open(imgPath)
        #Resizes the image to these dims, while keeping the aspect ratio.
        resizedImg = resizeimage.resize('thumbnail',img,[size.width(),size.height()])
        width, height = resizedImg.size
        print("Image Size (w,h): %i, %i " %(width, height))
        #img.thumbnail([300,300])

        imgqt = ImageQt.ImageQt(resizedImg)
        

        pixMap = QtGui.QPixmap.fromImage(imgqt)




        return pixMap        

    ##Call backs for when the label (preview image is pressed)
    def slotImgPrvMousePressed(self, event):
        self.imgprvlblClass.onMouseClick(event)
        return
    def slotImgPrbMouseMove(self, event):
        self.imgprvlblClass.onMouseMove(event)
        return
    def slotImgPrvMouseRelease(self, event):
        print("Image Label Released at x: %i, y: %i" %(event.pos().x(), event.pos().y()))
        self.imgprvlblClass.onMouseRelease(event.pos())
        return
    def slotImgPrvKeyPressed(self, event):
        #print("Key Pressed " + str(event.key()))
        self.imgprvlblClass.OnKeyPressed(event)
        return

    def slotStoreAnnotPressed(self, event):
        self.imgprvlblClass.updateCurrentPicAnnot()
        return            

    def slotRmvCtgPressed(self, event):
        self.imgprvlblClass.removeCtg(str(self.ctgListComboBox.currentText()))
    
    def slotAddCtgPressed(self, event):
        self.imgprvlblClass.addCtg(self.addCtglineEdit.text())
        return

    def slotStoreTFRecordsPressed(self, event):
        i = int(self.imgResize.isChecked())
        print("Resizing Images " + str(i))
        self.imgprvlblClass.storeTFRecords(i ,self.tfRecordsprogressBar)

def main():
    
    #Starts the over arching app under which the window loads.
    app = QtWidgets.QApplication(sys.argv)
    window = objDetectMainWindow()
    window.show()  
    sys.exit(app.exec_())

if __name__=="__main__":
    main()