import os
import codecs
import cv2
from bs4 import BeautifulSoup
from xml.dom import minidom

#%%
image_filename = "img146.tif"
image = cv2.imread(image_filename)
copy = image.copy()


#%% FOR OCRD
ocrd_filename = "ocrd146.xml"
ocrd = minidom.parse(ocrd_filename)

#%%
words = ocrd.getElementsByTagName("pc:Word")
coords = words[0].getElementsByTagName("pc:Coords")[0].getAttribute("points").split()
coords = coords[0].split(",")+coords[2].split(",")
coords = [int(coord) for coord in coords]




#%% For lace
lines = soup.find_all("html:span", attrs={"class":"ocr_line"})
words = soup.find_all("html:span", attrs={"class":"ocr_word"})

line_rectangles = []
for line in lines: 
    temp = line["title"].split()
    line_rectangles.append([int(temp[1]), int(temp[2]), int(temp[3]), int(temp[4][:-1])])

word_rectangles = []
for word in words:
    temp = word["title"].split()
    word_rectangles.append([int(temp[1]), int(temp[2]), int(temp[3]), int(temp[4])])

#%%
for rectangle in line_rectangles:
    line_rectangles_draw = cv2.rectangle(copy, (rectangle[0], rectangle[1]), (rectangle[2], rectangle[3]), (0, 0, 255), 10)

for rectangle in word_rectangles:
    word_rectangles_draw = cv2.rectangle(copy, (rectangle[0], rectangle[1]), (rectangle[2], rectangle[3]), (0, 255, 0), 2)




cv2.imwrite("lace_boxes.tif", copy)

