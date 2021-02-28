import cv2
import numpy as np


def count_overlaps(word):
    """Argument : a text unit of a certain type (Region, line, word).
    Returns the number other texts unit of the same type overlapping with it"""
    pass



#%% CREATE OVERLAP MATRIX.

import time
start_time = time.time()

image_filename = "img177.tif"
image = cv2.imread(image_filename)
image_matrix = np.zeros((image.shape[0], image.shape[1]), dtype="int64")

ocrd_words = ocrd.getElementsByTagName("pc:Word")
ocrd_word_rectangles = []

for word in ocrd_words[:100]:
# word = ocrd_words[0]
    coords = word.getElementsByTagName("pc:Coords")[0].getAttribute("points").split()
    coords = [coord.split(",") for coord in coords]
    coords = [[int(coord[0]), int(coord[1])] for coord in coords]
    coords = np.array(coords)
    ocrd_word_rectangles.append(coords)

for rectangle in ocrd_word_rectangles:
    image_matrix[rectangle[0,1]:rectangle[2,1], rectangle[0,0]:rectangle[1,0]] +=1

print("--- %s seconds ---" % (time.time() - start_time))



#%%

image_matrix[rectangle[0,1]:rectangle[2,1], rectangle[0,0]:rectangle[1,0]]