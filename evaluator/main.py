import codecs
import pandas as pd
import utils
import cv2
import numpy as np
from bs4 import BeautifulSoup
from xml.dom import minidom
from or_utils import file_management
from or_utils.cli import args


# TODO : make for loop over files
# TODO : make for loop over regions
# TODO : retrieve all the results.
# TODO : retrieve types of errors
# TODO : Create dinglehopper like comparison files

for filename in os.listdir(args.IMG_DATA_DIR):
    if filename[-3:] in ["png", "jpg", "tif", "jp2"]:



# Image and overlap matrix
image_filename = "sophoclesplaysa05campgoog_0146.tif"
image = file_management.Image(args, image_filename)
image_matrix = np.ndarray((3, image.height, image.width),
                          dtype=object)  # Creates a blank image matrix that we will use later
image_matrix[:, :, :] = ''

# SVG
svg_filename = "sophoclesplaysa05campgoog_0146.svg"
svg = file_management.ZonesMasks(args, image_filename)

for zone in svg.zones:
    zone = file_management.Segment.from_lace_svg()
    image_matrix[0, zone.coords[0][1]:zone.coords[2][1],
    zone.coords[0][0]:zone.coords[2][0]] = zone.type  # adds zone name to matrix, eg. "primary" text

# For lace gt
gt_filename = "sophoclesplaysa05campgoog_0146.html"
groundtruth = file_management.LaceOcr(args, gt_filename)

# For lace ocr
ocr_filename = "sophoclesplaysa05campgoog_0146.html"
ocr = file_management.LaceOcr(args, gt_filename)

# FOR OCRD  #TODO CONTINUE HERE
# ocrd_filename = "ocrd177.xml"
# ocrd = minidom.parse(ocrd_filename)
# # ocrd words
# ocrd_words = ocrd.getElementsByTagName("pc:Word")

# ocrd lines
# ocrd_lines = ocrd.getElementsByTagName("pc:TextLine")
# ocrd_line_polygons = []
# for line in ocrd_lines:
# # line = ocrd_lines[0]
#     coords = line.getElementsByTagName("pc:Coords")[0].getAttribute("points").split()
#     coords = [coord.split(",") for coord in coords]
#     coords = [[int(coord[0]), int(coord[1])] for coord in coords]
#     coords = np.array(coords)
#     coords = coords.reshape((-1,1,2))
#     ocrd_line_polygons.append(coords)


# SEGMENTS TO MATRIX

# Warning : This is assiming no words are over lapping in a single ocr !
for word in ocr.words:
    word = file_management.Segment.from_ocr(word)
    image_matrix[2, zone.coords[0][1]:zone.coords[2][1], zone.coords[0][0]:zone.coords[2][0]] = word.id

# for word in ocrd_words:
#     coords = utils.get_coords(word)
#     image_matrix.iloc[coords["x1"]:coords["x3"],coords["y1"]:coords["y3"]] += ","+utils.get_id(word)


# %% Calculate IOU in matrix

error_counts = {"total_chars": 0,
                "total_distance": 0,
                "total_words": 0,
                "false_words": 0,
                }

for word in groundtruth.words:
    word = file_management.Segment.from_ocr(word)
    image_matrix[1, zone.coords[0][1]:zone.coords[2][1], zone.coords[0][0]:zone.coords[2][0]] = word.id

    # easy solution : get the major element in ocr matrix for gt coordinates
    scores = {}
    array = image_matrix[2, zone.coords[0][1]:zone.coords[2][1], zone.coords[0][0]:zone.coords[2][0]]

    for id in set(array.flatten()):
        scores[id] = len(array[array == id])

    # LIPSTICK ON A MUDDY PIG TO GET THE VALUE THAT HAS THE MAX SCORE # TODO change this horror
    good_id = list(scores.keys())[list(scores.values()).index(max(scores.values()))]

    # Extract content from cell # TODO Write function in utils for that (OCR-D not compatible at the moment)
    try:
        gt_text = word.contents[0]
    except IndexError:
        gt_text = ''

    try:
        ocr_text = ocr.source.find_all("html:span", {"id": good_id})[0].contents[0]
    except IndexError:
        ocr_text = ''

    distance = utils.compute_levenshtein(gt_text, ocr_text)
    error_counts["total_chars"] += len(gt_text)
    error_counts["total_distance"] += distance
    error_counts["total_words"] += 1

    if distance > 0:
        error_counts["false_words"] += 1

    print("{}  {}  {}".format(gt_text, ocr_text, distance))
    print("   ")

cer = error_counts["total_distance"] / error_counts["total_chars"]
wer = error_counts["false_words"] / error_counts["total_words"]



