import tensorflow as tf
import sys
from io import BytesIO
from enum import Enum
from PIL import Image, ImageDraw
import os, csv, base64
from object_detection.utils import dataset_util
import argparse
import json
from random import shuffle
from resizeimage import resizeimage

flags = tf.app.flags
flags.DEFINE_string('output_path', '', '/home/ahmad/sda4/python/tensorFlow/objectDetection/data.record')
FLAGS = flags.FLAGS 

#This programs directory
currDir = os.path.dirname(os.path.realpath(__file__))
class tfRecordsCreator:
    delim = ','
    destDir = None
    #Image size as required ssd_coco
    imageSize  = [300,300]
    
    def __init__(self, Dir=None):
        self.destDir = Dir
        return


    def openCSV(self, csvURL):
        csvFile =  open(csvURL, 'r')
        reader = csv.reader(csvFile, delimiter=self.delim)
        return reader    

    #Resize Image is a boolean (0,1), whether to resize the image to 300x300 usually used by ssd's.
    def storeTFRecords(self, resizeImage, tfRecordFilePath):
        
        metaData = currDir + "/data/data.metadata"
        #Create file if it doesn't exist.
        if not os.path.exists(tfRecordFilePath):
            f = open(tfRecordFilePath, 'w+')
            f.close()
        writer = tf.python_io.TFRecordWriter(tfRecordFilePath)
        with open(metaData, mode='r') as f:
            _csv = csv.reader(f, dialect='excel', delimiter=',')
            for row in _csv:
                data = self.getTFRecord(resizeImage, str(row[1]), str(row[2]))
                writer.write(data.SerializeToString())

        writer.close()
    
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


def main():
    parser = argparse.ArgumentParser(description="Testing arg")
    parser.add_argument('Type', type=str, help='The type of data, validate(v) or train(t)')
    parser.add_argument('DestDir', type=str, help='The destination directory for the tfrecord')
    parser.add_argument('Classes', type=str, nargs='+', help='The classes we are searching for.')
    args = parser.parse_args()

    mode = args.Type
    destDir = args.DestDir
    classes = args.Classes
    writer = tf.python_io.TFRecordWriter(destDir + "data300x300.record")
    objDetectTF = oDTF(destDir)

    dirs = []
    tfRecords = []
    for c in classes:
        if mode == 'v':
            #objDetectTF.storeDirTFRecord(c , BaseDirVal + c , writer)
            tfData = objDetectTF.getDirTFRecordsFromDir(c, BaseDirVal + c)
            #Shuffle the data every time we go to a different directory.
            shuffle(tfData)
            #Add the tfRecords from this directoy.
            tfRecords.extend(tfData)

            #dirs.append(BaseDirVal + c)
        elif mode == 't':
            #objDetectTF.storeDirTFRecord(c, BaseDir + c , writer)
            tfData = objDetectTF.getDirTFRecordsFromDir(c, BaseDir + c)
            shuffle(tfRecords)
            tfRecords.extend(tfData)
        else:
            print("Invalid type.")
    #Shuffle once more for good measure
    shuffle(tfRecords)
    shuffle(tfRecords)
    dataCount = 0
    for data in tfRecords:
        writer.write(data.SerializeToString())
        dataCount = dataCount + 1
    print( "Wrote %s number of tfRecords." %(str(dataCount)))
    writer.close()
    
if __name__ == '__main__':
    #tf.app.run()
    #main()
    tfRC = tfRecordsCreator()
    tfdir = currDir + "/tfRecords/tf.record"
    print(tfdir)
    tfRC.storeTFRecords(1, tfdir)