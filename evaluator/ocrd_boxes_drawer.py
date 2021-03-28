import os
import codecs
import cv2
from bs4 import BeautifulSoup
# from xml.dom import minidom
import numpy as np


#%%
image_filename = "/Users/sven/oclr/evaluator/data/images/sophoclesplaysa05campgoog_0146.tif"
image = cv2.imread(image_filename)
copy = image.copy()


#%% FOR OCRD
ocrd_filename = "/Users/sven/oclr/evaluator/data/ocr/ocrd_ocr/OCR-D-OCR_word/OCR-D-OCR_sophoclesplaysa05campgoog_0012.xml"
ocrd = minidom.parse(ocrd_filename)

#%%
words = ocrd.getElementsByTagName("pc:Word")

words[0].


#%%
words[0].getAttribute("id")
test =words[0].getElementsByTagName("pc:TextEquiv")[0].getElementsByTagName("pc:Unicode")[0].firstChild.nodeValue


def get_ocrd_coords(word):
    coords = word.getElementsByTagName("pc:Coords")[0].getAttribute("points").split()
    coords = [point.split(",") for point in coords]
    coords = [[int(coord) for coord in point] for point in coords]
    return coords




word_rectangles = []
for word in words :
    word_rectangles.append(get_ocrd_coords(word))


for rectangle in word_rectangles:
    word_rectangles_draw = cv2.rectangle(copy, (rectangle[0][0],rectangle[0][1]), (rectangle[2][0], rectangle[2][1]), (0, 0, 255), 2)


# cv2.imwrite("ocrd_boxes.tif", copy)


#%% For lace
file = codecs.open("/Users/sven/oclr/evaluator/data/groundtruth/sophoclesplaysa05campgoog_0146.html", 'r')
soup = BeautifulSoup(file.read(), "html.parser")
lines = soup.find_all("html:span", attrs={"class":"ocr_line"})
words = soup.find_all("html:span", attrs={"class":"ocr_word"})

# line_rectangles = []
# for line in lines:
#     temp = line["title"].split()
#     line_rectangles.append([int(temp[1]), int(temp[2]), int(temp[3]), int(temp[4][:-1])])

word_rectangles = []
for word in words:
    temp = word["title"].split()
    word_rectangles.append([int(temp[1]), int(temp[2]), int(temp[3]), int(temp[4])])

# for rectangle in line_rectangles:
#     line_rectangles_draw = cv2.rectangle(copy, (rectangle[0], rectangle[1]), (rectangle[2], rectangle[3]), (0, 0, 255), 10)

for rectangle in word_rectangles:
    word_rectangles_draw = cv2.rectangle(copy, (rectangle[0], rectangle[1]), (rectangle[2], rectangle[3]), (0, 255, 0), 2)

#%%


cv2.imwrite("all_boxes.tif", copy)




# %% for ocrd lines
ocrd_lines = ocrd.getElementsByTagName("pc:TextLine")
ocrd_line_polygons = []
for line in ocrd_lines:
# line = ocrd_lines[0]
    coords = line.getElementsByTagName("pc:Coords")[0].getAttribute("points").split()
    coords = [coord.split(",") for coord in coords]
    coords = [[int(coord[0]), int(coord[1])] for coord in coords]
    coords = np.array(coords)
    coords = coords.reshape((-1,1,2))
    ocrd_line_polygons.append(coords)


