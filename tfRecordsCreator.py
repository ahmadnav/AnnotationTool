from __future__ import division
import tensorflow as tf
import sys
from io import BytesIO
from enum import Enum
from PIL import Image, ImageDraw
import os, csv, base64
from object_detection.utils import dataset_util
import argparse
from random import shuffle
from resizeimage import resizeimage
import PyQt5

flags = tf.app.flags
flags.DEFINE_string('output_path', '', '/home/ahmad/sda4/python/tensorFlow/objectDetection/data.record')
FLAGS = flags.FLAGS 
#This programs directory
currDir = os.path.dirname(os.path.realpath(__file__))
metaDataPath = currDir + "/data/data.metadata"

class tfRecordsCreator:
    delim = ','
    destDir = None
    #Image size as required ssd_coco
    imageSize  = [300,300]
    
    def __init__(self, Dir=None):
        self.destDir = Dir
        return


    def openCSV(self, csvURL):
        csvFile =  open(csvURL, mode='r')
        reader = csv.reader(csvFile, delimiter=self.delim)
        return reader    

    def numImages(self):
        i = 0
        for row in self.openCSV(metaDataPath):
            i = i + 1
        return i

    #Resize Image is a boolean (0,1), whether to resize the image to 300x300 usually used by ssd's.
    def storeTFRecords(self, resizeImage, tfRecordFilePath, progressBar):
        assert isinstance(progressBar, PyQt5.Qt.QProgressBar)
        totalPics = self.numImages()

        metaData = currDir + "/data/data.metadata"
        #Create file if it doesn't exist.
        if not os.path.exists(tfRecordFilePath):
            f = open(tfRecordFilePath, 'w+')
            f.close()
        writer = tf.python_io.TFRecordWriter(tfRecordFilePath)
        with open(metaData, mode='r') as f:
            _csv = csv.reader(f, dialect='excel', delimiter=self.delim)
            i = 0
            for row in _csv:
                imageAnnotPath = str(row[2])
                imagePath = str(row[1])
                if not os.path.exists(imageAnnotPath):
                    print("No annotation file found for " + imagePath)
                    i = i + 1
                    self.updateProgressBar(i,totalPics,progressBar)
                    continue
                data = self.getTFRecord(resizeImage, imagePath, imageAnnotPath)
                if data is not None:
                    writer.write(data.SerializeToString())
                i = i + 1
                self.updateProgressBar(i,totalPics,progressBar)

                
        progressBar.reset()

        writer.close()
    
    def updateProgressBar(self, i, total, progressBar):
        assert isinstance(progressBar, PyQt5.Qt.QProgressBar)
        progress = float (i/total * 100)
        print(progress)
        progressBar.setValue(progress)
        return

    #Gets tfRecord from a directory which contains images of a certian category.
    #Resize Image is a boolean (0,1), whether to resize the image to 300x300 usually used by ssd's.
    def getTFRecord(self, resizeImage,imagePath, imageInfoPath):
        csv = self.openCSV(imageInfoPath)
        xmins = []
        xmaxs = []
        ymins = []
        ymaxs = []
        #Category Names
        classes_text = []
        #Category index as in labels.txt
        classes = []
        #closeToOne=0.99
        i = 3
        for row in csv:
            xmin =float(row[i+0])
            ymin =float(row[i+1])
            xmax = float(row[i+2])
            ymax = float(row[i+3])
            xmins.append(xmin)
            xmaxs.append(xmax)
            ymins.append(ymin)
            ymaxs.append(ymax)

            category = str(row[0])
            index = row[1]
            classes_text.append(category.encode())
            classes.append(int(index))
        
        if len(xmins) is 0:
            print("No Image Annotations found for " + imagePath)
            return None
        
        tfRecord  = self.createTFAnnot(resizeImage, category, imagePath,classes_text, classes, xmins, xmaxs, ymins, ymaxs)
        return tfRecord

    def createTFAnnot(self, resizeImage,imageName,imagePath, classes_text, classes,xmins, xmaxs, ymins, ymaxs):
     
        img = Image.open(imagePath)
        encoded_image_data = None 
        

        if resizeImage:
            with BytesIO() as output:
                
                img = resizeimage.resize('thumbnail',img,self.imageSize)
                img.save(output,'JPEG')
                encoded_image_data = bytes(output.getvalue())        
        else:
            encoded_image_data =  bytes(tf.gfile.GFile(imagePath,'rb').read())        
        
        width,height = img.size
        #The tfRecord constructor expects bytes instead of string.
        filename = imagePath.encode()
        image_format = b'jpeg'


        tfRecord = tf.train.Example(features=tf.train.Features(feature={
            'image/height': dataset_util.int64_feature(height),
            'image/width': dataset_util.int64_feature(width),
            'image/filename': dataset_util.bytes_feature(filename),
            'image/source_id': dataset_util.bytes_feature(filename),
            'image/encoded': dataset_util.bytes_feature(encoded_image_data),
            'image/format': dataset_util.bytes_feature(image_format),
            'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
            'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
            'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
            'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
            'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
            'image/object/class/label': dataset_util.int64_list_feature(classes),
        })) 

        return tfRecord


    def getImageListInDirs(self,dirs):
        imagePaths = []
        for directory in dirs:
            for subdir,dirs, files in os.walk(directory):
                for file in files:
                    ext = os.path.splitext(file)[-1].lower()
                    #Get all the extention jpg
                    if ext in extentions:
                        #Base file name
                        fileName = os.path.splitext(file)[0]
                        
                        fileDir = directory + fileName
                        
                        imagePath = fileDir + ".jpg"
                        imagePaths.append(imagePath)
        
        return imagePaths

# if __name__ == '__main__':
#     #tf.app.run()
#     #main()
#     tfRC = tfRecordsCreator()
#     tfdir = currDir + "/tfRecords/tf.record"
#     print(tfdir)
#     tfRC.storeTFRecords(1, tfdir)