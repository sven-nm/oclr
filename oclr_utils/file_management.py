import codecs
from oclr_utils import extracters
from bs4 import BeautifulSoup
from xml.dom import minidom
import os
import cv2
import numpy as np


class Registrable:
    """In case of later integration with dhSegment"""
    pass


class File(Registrable):
    def __init__(self, filename):
        self.filename = filename


class Image(File):
    
    def __init__(self, args, filename):
        super(Image, self).__init__(filename)
        self.image_matrix = cv2.imread(os.path.join(args.IMG_DIR, filename))
        self.height = self.image_matrix.shape[0]
        self.width = self.image_matrix.shape[1]
        # self.copy = self.image_matrix.copy()


class ZonesMasks(File):

    #TODO upgrade this to read VIA annotation. Build alternative constructors from_svg & from_VIA

    def __init__(self, args, filename):
        super(ZonesMasks, self).__init__(filename)
        self.svg = minidom.parse(os.path.join(args.SVG_DIR, filename))

        # Retrieve image and file-name
        self.linked_image = self.svg.getElementsByTagName("image")[0]
        self.linked_image_name = os.path.basename(self.linked_image.getAttribute("xlink:href"))[0:-3]+"tif" #TODO change this for multiple format

        # Retrieve svg viewports dimensions
        self.height = float(self.svg.getElementsByTagName("svg")[0].getAttribute("height"))
        self.width = float(self.svg.getElementsByTagName("svg")[0].getAttribute("width"))

        # Retrieve SVG zones
        self.zones = [r for r in self.svg.getElementsByTagName('rect') if r.getAttribute("data-rectangle-type") in
                 ["commentary", "page_number", "primary_text", "title", "app_crit", "translation"]]


class OcrObject(File):

    def __init__(self, args, image_filename, data_type):

        # TODO this should be an extracter
        if data_type == "groundtruth":
            self.filename = image_filename[0:-3] + "html"
            self.file = codecs.open(os.path.join(args.GROUNDTRUTH_DIR, self.filename), 'r')
            self.source = BeautifulSoup(self.file.read(), "html.parser")
            self.lines = self.source.find_all("html:span", attrs={"class": "ocr_line"})
            self.words = self.source.find_all("html:span", attrs={"class": "ocr_word"})

        else:
            if args.ocr_engine == "lace":
                self.filename = image_filename[0:-3]+"html"
                self.file = codecs.open(os.path.join(args.OCR_DIR, self.filename), 'r')
                self.source = BeautifulSoup(self.file.read(), "html.parser")
                self.lines = self.source.find_all("html:span", attrs={"class": "ocr_line"})
                self.words = self.source.find_all("html:span", attrs={"class": "ocr_word"})

            else:
                # Find the corresponding file :
                for filename_ in os.listdir(args.OCR_DIR):
                    if filename_.endswith(image_filename[0:-3]+"xml"):
                        self.filename = filename_

                self.source = minidom.parse(os.path.join(args.OCR_DIR, self.filename))
                self.lines = self.source.getElementsByTagName("pc:TextLine")
                self.words = self.source.getElementsByTagName("pc:Word")




class Segment(Registrable):
    """This is the main class for segment-like elements"""

    def __init__(self, id=None, coords=None, type_=None, content=None, source=None):
        """This is the basic constructor which will always be called by called by format-specific alternative
        constructors (class-methods below)."""

        self.id = id
        self.coords = coords
        self.type = type_
        self.content = content
        self.source = source
        self.width = self.coords[1][0]-self.coords[0][0]
        self.height = self.coords[2][1] - self.coords[0][1]


    @classmethod
    def from_lace_svg(cls, zone, image, svg):
        """Creates a segment from a lace_svg file"""

        x1 = int(round(float(zone.getAttribute("x")) * image.width / svg.width))  # svg coordinates must be converted from viewport dimensions
        x2 = x1 + int(round(float(zone.getAttribute("width")) * image.width / svg.width))
        y1 = int(round(float(zone.getAttribute("y")) * image.height / svg.height))
        y2 = y1 + int(round(float(zone.getAttribute("height")) * image.height / svg.height))

        # Coords are list of (x,y)-point-tuples, going clockwise around the figure, consistent with PAGE-XML notation
        coords = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

        id = zone.getAttribute('id')
        type_ = zone.getAttribute("data-rectangle-type")


        return cls(id, coords, type_, None, zone)


    @classmethod
    def from_ocr(cls, args, segment, data_type):
        """This constructor uses the functions from utils which accept both Lace and OCR-D."""
        id = extracters.get_id(args, segment, data_type)
        coords = extracters.get_coords(args, segment, data_type)
        type_ = extracters.get_type(args, segment, data_type)
        content = extracters.get_content(args, segment, data_type)

        return cls(id, coords, type_, content, segment)



