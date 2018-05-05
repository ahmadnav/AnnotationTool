#This module is responsible for choosing which image is shown, and the UI for image preview and managing.
import os
from objDetectVariables import image, bbox, boundingRect
import csv

imageFolder = os.path.dirname(os.path.realpath(__file__)) + "/data/picsAndAnnots/"
metaDataFile = os.path.dirname(os.path.realpath(__file__)) + "/data/data.metadata"

class imageManager:
    extentions = ['.jpg']
    #Array of images
    images = []

    def __init__(self):
        #print(imageFolder)
        return

    #Retrieves Images from folders.
    def getImages(self):

        with open(metaDataFile, mode='r'):
            _csv = csv.reader(f, dialect='excel', delimeter=',')                    
            for row is _csv:
                #self.storeImage(fileName, realFilePath, realAnnotPath)
                self.storeImage(row[0], row[1], row[2])
        return

    def storeImage(self, imageName, imagePath, annotPath):
        _bboxs = self.getImageAnnots(annotPath)
        img = image(imagePath,annotPath, imageName, _bboxs)
        self.images.append(img)
        for _img in self.images:
            for bbox in _img.getbboxAnnots():
                print(bbox.getRect().x1())
        return

    def getImageAnnots(self, annotFilePath):
        i = 3
        _bboxs = []
        with open(annotFilePath) as f :
            for row in csv.reader(f, delimiter=',', dialect='excel'):
                _rect = boundingRect(  float(row[i+0]),float(row[i+1]), float(row[i+2]), float(row[i+3]))
                _bbox = bbox(row[0], _rect)
                
                _bboxs.append(_bbox)
        return _bboxs

    #Sets the current Image.
    def setCurrentImage(self):
        return

if __name__== "__main__":
    imgclass = imageManager()
    imgclass.getImages()