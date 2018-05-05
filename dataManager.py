from __future__ import division
import os 
import PyQt5

import csv
from openImagesReader import openImagesDataParser
from objDetectVariables import bbox, boundingRect, category, image
#import objDetectVariables as oDV
import qtWrapperClasses 


#This programs directory
currDir = os.path.dirname(os.path.realpath(__file__))
metaDataPath = currDir + "/data/data.metadata"


#This module is responsible for holding static info, and storing info non-volatile Info.


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
    pathToTFLabels=None
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
        self.pathToTFLabels = self.currDir + "/data/labels.pbtxt"
        self.getCategoriesFromCVS(self.pathToLabel)
        self.createTfLabelsFile()
        self.verifyImageAnnots()

    def getCategoriesFromCVS(self, cvsPath=None):
        del self._categories[:]
        
        if cvsPath is None:
            cvsPath = self.pathToLabel

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

    #Goes through each ctg and ensures that the image id matches there name, after an image id has changed.
    def verifyImageAnnots(self):
        for row in self.getCSVReader(metaDataPath):
            self.verifyImgAnnot(row[2])
                

    def verifyImgAnnot(self, csvURL):
        
        for row in self.getCSVReader(csvURL):
            index = self.getctgIndex(str(row[0]))
            if index != int(row[1]):
                print(csvURL + " Failed verification.")
                row[1] = index
                print(row)
                self.fixAnnot(csvURL)
            
        return

    def fixAnnot(self, csvURL):
        rows = []
        for row in self.getCSVReader(csvURL):
            row[1] = self.getctgIndex(str(row[0]))
            rows.append(row)
        
        with open(csvURL, 'w+') as f:
            writer = csv.writer(f, dialect='excel', delimiter=',')
            for row in rows:
                writer.writerow(row)
        
        return


    def updateImageAnnot(self, img, annots, width, height):
        assert isinstance(img, image)
        #Opening file as w+ removes earlier data.
        with open(img.getImageAnnotURL(), 'w+') as f:
            
            csvreader = csv.writer(f,delimiter=',', dialect='excel')
            for annot in annots:
                assert isinstance(annot, qtWrapperClasses.Annotation)
                
                index = annot.currentIndex() 
                fileName=img.getImageName()
                ctg = str(annot.itemText(index))
                print("Height %f width: %f" %(height, width))
                ##Normalize the rect data.
                x1= annot.getRect().x1() /width
                y1=annot.getRect().y1() / height
                x2 = annot.getRect().x2() / width
                y2=annot.getRect().y2() / height
                #Initial index starts at 0, we start at 1
                row = [ctg, index + 1, fileName, x1, y1, x2, y2 ]
                print(row)
                csvreader.writerow(row)
        f.close()
        return

    def createTfLabelsFile(self):
        self.clearTFLabels()
        #Open the csv file at second line the first line is reserved by tf as space not occupied by object.
        with open(self.pathToLabel, 'r') as f:
            #next(f)
            csvreader = csv.reader(f, dialect='excel', delimiter=',')

            ID = 1
            for row in csvreader:
                self.addTfLbls(ID, str(row[0]))
                ID = ID + 1
        return

    def clearTFLabels(self):
        f = open(self.pathToTFLabels, mode='w+')
        f.close()
        return
    def addTfLbls(self, ID, name):
        with open(self.pathToTFLabels, 'a') as f:
            csvWriter = csv.writer(f, dialect='excel', delimiter=',')
            idRow = "  id: " + str(ID)
            nameRow = "  name: " + "'" + name + "'"
            csvWriter.writerow(["item {"])
            csvWriter.writerow([idRow])
            csvWriter.writerow([nameRow])
            csvWriter.writerow("}")
            f.close()
        return

    def openCSVLabels(self):
        #Open the csv file at second line the first line is reserved by tf as space not occupied by object.
        with open(self.pathToLabel, 'r') as f:
            #next(f)
            return csv.reader(f, dialect='excel', delimiter=',')

    #Adds category 
    def addCtg(self, ctgText):
        if self.getctgIndex(ctgText) is not 0:
            print("Category "+ str(ctgText) + " already exists.")
            return
        #Update the drop down list.
        #Add directory if it doesn't exist, also validate dirs
        with open(self.pathToLabel, "a") as f:
            writer = csv.writer(f, dialect='excel', delimiter=',')
            writer.writerow([ctgText])
        f.close()
        #Update the labels file.
        self.onLabelsModified()
        return

    #Removes a ctg from the file.
    def removeCtg(self, ctg):
        index = self.getctgIndex(ctg)
        rows = []
        if index is 0:
            print(ctg + " does not exist.")
            return
        reader = self.getCSVReader(self.pathToLabel)
        i = 0
        for row in reader:
            if i == index:
                #Dont add the ctg we want to delete.
                continue
            rows.append(row)
            i = i + 1
    
        if len(row) > 0:
            with open(self.pathToLabel, 'w+') as f:
                writer = csv.writer(f, dialect='excel', delimiter=',')
                for row in rows:
                    writer.writerow(row)
            
        f.close()
        self.onLabelsModified()
        
        return            

    def getctgIndex(self, ctg):
        index = 1
        for row in self.getCSVReader(self.pathToLabel):
            if str(row[0]) == ctg:
                return index 
            index = index + 1
        return 0        

    def clearAllCtgs(self):    
        f = open(self.pathToLabel, 'w+')
        writer = csv.writer(f, dialect='excel', delimiter=',')
        #writer.writerow(["???"])
        f.close()
        self.onLabelsModified()

    def getCSVReader(self, csvURL):
        f = open(csvURL, 'r') 
        csvreader = csv.reader(f, dialect='excel', delimiter=',')
        return csvreader
    
    #This functions ensures updates when the labels have been modified.
    def onLabelsModified(self):
        #Create new tfLabels file.
        self.createTfLabelsFile()
        #Update local categories.
        self.getCategoriesFromCVS()
        #Update the image annotations to reflect
        self.verifyImageAnnots()
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


#if __name__=="__main__":
    #dmanager = dataManager()
    # dmanager.createTfLabelsFile()
    # dmanager.clearAllCtgs()
    # dmanager.addCtg("Lion")
    # dmanager.addCtg("Zebra")
    # dmanager.removeCtg("Zebra")
    