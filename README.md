# AnnotationTool
Annotation tool for creating bounding boxes, creates  text files with annotation information which can easily be used to train visual machine learning algorithms. Also create tfRecords files for tensorflow training.


###REQUIREMENTS###
pip install \
pyqt5 \
imageresize \
csv \
math \
copy \
tensorflow 

This program was created with qt 5.5.1 source installation.



###USAGE####
Place images in ./data/picsAndAnnots/
Run start.sh
Create tfRecord stored in tfRecords folder, click the check box to scale images down to 300x300 for storage in tfRecords file, useful for Single Shot Detectors.
