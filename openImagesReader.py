import csv


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