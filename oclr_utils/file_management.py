import codecs
from oclr_utils import extracters
from bs4 import BeautifulSoup
from xml.dom import minidom
import os
import cv2
from oclr_utils import extracters
import numpy as np
from typing import List, Tuple


class Registrable:
    """In case of later integration with dhSegment"""
    pass


class File(Registrable):
    """The default class for file objects.

    :param filename: a filename without extension
    """

    def __init__(self, filename: str):
        self.filename = filename


class Image(File):
    """The default class for images.

    :param filename: a filename without extension
    """

    def __init__(self, args: "argparse.ArgumentParser", filename: str):
        super(Image, self).__init__(filename)
        self.image_format = extracters.get_image_format(args)  #: type: str, pattern: ".xxx"
        self.image_matrix = cv2.imread(os.path.join(args.IMG_DIR, self.filename + self.image_format))  #: type: ndarray
        self.height = self.image_matrix.shape[0]
        self.width = self.image_matrix.shape[1]
        self.copy = self.image_matrix.copy()
        self.contours = extracters.get_contours(self.image_matrix)

        # Initialise overlap_matrix
        self.overlap_matrix = np.ndarray((4, self.height, self.width), dtype=object)
        self.overlap_matrix[:, :, :] = ''
        self.overlap_matrix[3, :, :] = -1

        # Add contours points to overlap_matrix
        for i, contour in enumerate(self.contours):
            for point in contour:
                self.overlap_matrix[3, point[0][1], point[0][0]] = i


class ZonesMasks(File):
    """The default class for lace .svg zones"""

    # TODO upgrade this to read VIA annotation. Build alternative constructors from_svg & from_VIA

    def __init__(self, args: "argparse.ArgumentParser", filename: str, image_format: str):
        """Constructor.

        :param filename: a filename without extension
        :param image_format: image extension format with a pattern ".xxx"
        """
        super(ZonesMasks, self).__init__(filename)
        self.svg = minidom.parse(os.path.join(args.SVG_DIR, self.filename + ".svg"))

        # Retrieve image and file-name
        self.linked_image = self.svg.getElementsByTagName("image")[0]
        self.linked_image_name = os.path.basename(self.linked_image.getAttribute("xlink:href"))[0:-4] + image_format

        # Retrieve svg viewports dimensions
        self.height = float(self.svg.getElementsByTagName("svg")[0].getAttribute("height"))
        self.width = float(self.svg.getElementsByTagName("svg")[0].getAttribute("width"))

        # Retrieve SVG zones
        self.zones = [r for r in self.svg.getElementsByTagName('rect') if r.getAttribute("data-rectangle-type") in
                      ["commentary", "page_number", "primary_text", "title", "app_crit", "translation"]]


class Segment(Registrable):
    """The default class for segment-like elements ; The default constructor should always be called by format-specific alternative
    constructors (class-methods below).

    :param id: The ID of the segment
    :param coords: The coords of the segment
    :param zone_type: The type of region the segment is delimitating \
    (for zones) or included in (for words) (e.g. "commentary").
    :param data_type: The data type of the object ("groundtruth" or "ocr")
    :param content: The text of the segment, None for zone-like segments
    :param source: The original xml-like object (bs4 or dom object)
    """

    def __init__(self, content: str = None,
                 contours: List[tuple] = None,
                 coords: List[Tuple] = None,
                 data_type: str = None,
                 id: str = None,
                 print_coords : List[tuple] = None,
                 source: object = None,
                 zone_type: str = None):

        self.content = content
        self.contours = contours
        self.coords = coords  #: coords reduced to the contours they included ; used for analysis
        self.data_type = data_type  #: the type of data, "ocr" or "groundtruth"
        self.id = id
        self.print_coords = print_coords  #: Coords used only for final html rendering.
        self.source = source
        self.zone_type = zone_type

        self.print_width = self.print_coords[1][0] - self.print_coords[0][0]
        self.print_height = self.print_coords[2][1] - self.print_coords[0][1]

    @classmethod
    def from_lace_svg(cls, zone: "Segment", image: "Image", svg: "ZonesMasks"):
        """This constructor creates a segment from a lace_svg file"""

        x1 = int(round(float(zone.getAttribute(
            "x")) * image.width / svg.width))  # svg coordinates must be converted from viewport dimensions
        x2 = x1 + int(round(float(zone.getAttribute("width")) * image.width / svg.width))
        y1 = int(round(float(zone.getAttribute("y")) * image.height / svg.height))
        y2 = y1 + int(round(float(zone.getAttribute("height")) * image.height / svg.height))

        # Coords are list of (x,y)-point-tuples, going clockwise around the figure, consistent with PAGE-XML notation
        coords = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

        id = zone.getAttribute('id')
        zone_type = zone.getAttribute("data-rectangle-type")

        return cls(id=id, print_coords=coords, coords=coords, zone_type=zone_type, source=zone)

    @classmethod
    def from_ocr(cls, args: "argparse.ArgumentParser", image: "Image", segment: "Segment", data_type: str,
                 empty_word: bool = False):
        """This constructor uses the functions from utils which accept both Lace and OCR-D."""

        content = extracters.get_content(args, segment, data_type)
        print_coords = extracters.get_coords(args, segment, data_type)
        contours = extracters.find_included_contours(print_coords, image)
        coords = extracters.get_bounding_rectangles(contours, print_coords)
        id = extracters.get_id(args, segment, data_type)

        if empty_word:
            id = ""

        return cls(content=content, contours=contours, coords=coords, data_type=data_type, id=id, 
                   print_coords=print_coords, source=segment)


class OcrObject(File):
    """The default class for groundtruth and ocr-object ; Constructor builds instances depending on the engine and the
    data-type.

    :param args: an argparse parser
    :param filename: a filename without extension
    :param data_type: the data type of the object ("groundtruth" or "ocr")
    """

    def __init__(self, args: "argparse.ArgumentParser", image: "Image", filename: str, data_type: str):

        if data_type == "groundtruth":
            self.filename = filename
            self.file = codecs.open(os.path.join(args.GROUNDTRUTH_DIR, self.filename + ".html"), 'r')
            self.source = BeautifulSoup(self.file.read(), "html.parser")
            self.words = self.source.find_all("html:span", attrs={"class": "ocr_word"})
            self.words = [Segment.from_ocr(args, image, gt_word, "groundtruth") for gt_word in self.words]



        else:
            if args.ocr_engine == "lace":
                self.filename = filename
                self.file = codecs.open(os.path.join(args.OCR_DIR, self.filename + ".html"), 'r')
                self.source = BeautifulSoup(self.file.read(), "html.parser")
                self.lines = self.source.find_all("html:span", attrs={"class": "ocr_line"})
                self.words = self.source.find_all("html:span", attrs={"class": "ocr_word"})
                self.words = [Segment.from_ocr(args, image, ocr_word, "ocr") for ocr_word in self.words]

            else:  # for ocrd
                # Find the corresponding file :
                for filename_ in os.listdir(args.OCR_DIR):
                    if filename_.endswith(filename + ".xml"):
                        self.filename = filename_[:-4]

                self.source = minidom.parse(os.path.join(args.OCR_DIR, self.filename + ".xml"))
                self.lines = self.source.getElementsByTagName("pc:TextLine")
                self.words = self.source.getElementsByTagName("pc:Word")
                self.words = [Segment.from_ocr(args, image, ocr_word, "ocr") for ocr_word in self.words]
