"""
`extracters.py` stores all the function used to extract data from images, hocr, html or PAGE-xml formats.
"""

import os
import numpy as np
import cv2
from oclr_utils import file_management
from typing import List


def get_image_format(args: type) -> str :
    """Retrieve the image format of the first image in IMG_DIR. Returns a `.xxx`-like string"""
    for filename in os.listdir(args.IMG_DIR):
        if filename[-4:] in [".png", ".tif",".jpg", ".jp2"]:
            image_format = filename[-4:]
            break
    return image_format


def get_id(args: "ArgumentParser", segment: "Segment", data_type: str) -> str:
    """ Retrieves id from a lace or an ocrd segment.
    :param args: an argument parser
    :param segment: a segment
    :param data_type: the type of data (groundtruth or ocr)
    :return: ID of the segment
    """
    if args.ocr_engine == "ocrd" and data_type == "ocr":
        id = segment.getAttribute("id")
    else:
        id = segment["id"]
    return id


def get_coords(args, segment, data_type):
    """ Retrieves coords from a lace or an ocrd segment.
        Input :  a segment.
        Returns : coords as a list of (x,y)-coords-tuples,
        with the following order for rectangles : upper left, upper right, down right, down left """

    if args.ocr_engine == "ocrd" and data_type == "ocr":
        coords = segment.getElementsByTagName("pc:Coords")[0].getAttribute("points").split()
        coords = [(int(coord.split(",")[0]), int(coord.split(",")[1])) for coord in coords]

    else :  # exception raised if lace segment
        coords = segment["title"].split()
        coords = [(int(coords[1]), int(coords[2])), (int(coords[3]), int(coords[2])),
                  (int(coords[3]), int(coords[4])), (int(coords[1]), int(coords[4]))]

        # Make sure the segment is at least one-pixel wide
        if coords[0][0] == coords[2][0]:
            coords[2] = (coords[2][0]+1, coords[2][1])
            coords[1] = (coords[1][0] + 1, coords[1][1])

        if coords[0][1] == coords[2][1]:
            coords[2] = (coords[2][0], coords[2][1]+1)
            coords[3] = (coords[3][0], coords[3][1]+1)

    return coords


def get_content(args, segment, data_type):
    """Retrieves the content of a segment"""
    if args.ocr_engine == "ocrd" and data_type == "ocr":
        content = segment.getElementsByTagName("pc:TextEquiv")[0].getElementsByTagName("pc:Unicode")[
            0].firstChild.nodeValue
    else:
        try:
            content = segment.contents[0]
        except IndexError:
            content = ""

    return content



def get_segment_zonetype(segment: "Segment", overlap_matrix: "ndarray") -> str:
    """Get the zonetype of a segment ("commentary", "app_crit"...) by selecting the maximally overlap value.

    :return: The zone type ; "no_zone" if the segment does not belong to any zone.
    """

    array = overlap_matrix[0, segment.coords[0][1]:segment.coords[2][1], segment.coords[0][0]:segment.coords[2][0]]
    uniques, counts = np.unique(array, return_counts=True)
    zone_type = uniques[counts.argmax()]
    zone_type = "no_zone" if zone_type == '' else zone_type

    return zone_type


def get_corresponding_ocr_word(args: "ArgumentParser", gt_word: "Segment",
                               ocr: "OcrObject", overlap_matrix: "ndarray") -> "Segment":
    """Get the ocr-segment maximally overlapping a given groundtruth segment.

    :param ocr: The OcrObject containg all ocr-segments
    :return: The corresponding ocr-segment.
    """

    array = overlap_matrix[2, gt_word.coords[0][1]:gt_word.coords[2][1],
            gt_word.coords[0][0]:gt_word.coords[2][0]]
    uniques, counts = np.unique(array, return_counts=True)
    ocr_id = uniques[counts.argmax()]

    if ocr_id == "":
        ocr_word = gt_word
        ocr_word.content = ""

    else:
        for word in ocr.words:
            if word.id == ocr_id:
                ocr_word = word

    return ocr_word


def find_included_contours(coords: List[tuple], image: "Image") -> str:
    """Finds the contours included in a segments surrounding box.

    :return: The zone type ; "no_zone" if the segment does not belong to any zone.
    """

    array = image.overlap_matrix[3, coords[0][1]:coords[2][1], coords[0][0]:coords[2][0]]
    contours = [image.contours[unique] for unique in np.unique(array) if unique != -1]

    # Exludes contours that would increase the height of the surrounding box
    contours_new = []
    for contour in contours:
        if (np.max(contour[:, :, 1:2]) <= coords[2][1]) and (
                np.min(contour[:, :, 1:2]) >= coords[0][1]):
            contours_new.append(contour)

    return contours_new


def get_contours(image_matrix: "ndarray") -> List["ndarray"]:
    """Retrieves the contours of shapes and glyphs on an image-array using cv2.

    :param image_matrix: matrix returned by `cv2.imread()`
    :return: the list contours, a list of ndarray of shape (number of points, 1, 2)
    """
    gray = cv2.cvtColor(image_matrix, cv2.COLOR_BGR2GRAY)
    _, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    return contours


# TODO : Merge with annotation helper
def get_bounding_rectangles(contours: List["ndarray"], coords: List[tuple]) -> List[tuple]:
    """Concatenate provided contours-arrays and finds the smallest bounding rectangle."""

    try:
        all_contours = contours.pop(0)
        for contour in contours:
            all_contours = np.concatenate((all_contours,contour), axis=0)
        x, y, w, h = cv2.boundingRect(all_contours)
        rect_coords = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]

        return rect_coords

    except IndexError:  # If the segment is empty

        return coords

