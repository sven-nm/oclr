import codecs
import utils
from bs4 import BeautifulSoup
from xml.dom import minidom
import os
import cv2


class Registrable:
    """In case of later integration with dhSegment"""
    pass

class File(Registrable):
    def __init__(self, filename):
        self.filename = filename


class Image(File):
    
    def __init__(self, args, filename):
        self.image_matrix = cv2.imread(os.path.join(args.IMG_DIR, self.filename))
        self.height = self.image_matrix.shape[0]
        self.width = self.image_matrix.shape[1]
        self.copy = self.image_matrix.copy()


class ZonesMasks(File):

    #TODO upgrade this to read VIA annotation. Build alternative constructors from_svg & from_VIA

    def __init__(self, args, filename):
        self.svg = minidom.parse(os.path.join(args.SVG_DIR, filename))

        # Retrieve image and file-name
        self.linked_image = self.svg.getElementsByTagName("image")[0]
        self.linked_image_name = os.path.basename(self.linked_image.getAttribute("xlink:href"))
        self.linked_image_height = cv2.imread(os.path.join(args.IMG_DIR, self.linked_image_name)).shape[0]
        self.linked_image_width = cv2.imread(os.path.join(args.IMG_DIR, self.linked_image_name)).shape[1]

        # Retrieve svg viewports dimensions
        self.svg_height = float(self.svg.getElementsByTagName("svg")[0].getAttribute("height"))
        self.svg_width = float(self.svg.getElementsByTagName("svg")[0].getAttribute("width"))

        # Retrieve SVG zones
        self.zones = [r for r in self.svg.getElementsByTagName('rect') if r.getAttribute("data-rectangle-type") in
                 ["commentary", "page_number", "primary_text", "title", "app_crit", "translation"]]


class LaceOcr(File):

    def __init__(self, args, filename, data_type="groundtruth"): #TODO : maybe find a better way

        if data_type == "groundtruth":
            self.file = codecs.open(os.path.join(args.GROUNDTRUTH_DIR, filename), 'r')
        elif data_type == "ocr":
            self.file = codecs.open(os.path.join(args.OCR_DIR, filename), 'r')

        self.source = BeautifulSoup(self.file.read(), "html.parser")
        self.lines = self.source.find_all("html:span", attrs={"class": "ocr_line"}) # TODO here make it from class segment
        self.words = self.source.find_all("html:span", attrs={"class": "ocr_word"})


class Segment(Registrable):
    """This is the main class for segment-like elements"""

    def __init__(self, id=None, coords=None, type_=None, contents=None, source=None):
        """This is the basic constructor which will always be called by called by format-specific alternative
        constructors (class-methods below)."""

        self.id = id
        self.coords = coords
        self.type = type_
        self.contents = contents
        self.source = source


    @classmethod
    def from_lace_svg(cls, zone, image, svg):
        """Creates a segment from a lace_svg file"""

        x1 = int(round(float(zone.getAttribute("x")) * image.width / svg.width)), # svg coordinates must be converted from viewport dimensions
        x2 = x1 + int(round(float(zone.getAttribute("width")) * image.width / svg.width)),
        y1 = int(round(float(zone.getAttribute("y")) * image.height / svg.height))
        y2 = y1 + int(round(float(zone.getAttribute("height")) * image.height / svg.height))

        # Coords are list of (x,y)-point-tuples, going clockwise around the figure, consistent with PAGE-XML notation
        coords = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

        id = zone.getAttribute('id')
        type_ = zone.getAttribute("data-rectangle-type")


        return cls(id, coords, type_, None, zone)


    @classmethod
    def from_ocr(cls, segment):
        """This constructor uses the functions from utils which accept both Lace and OCR-D."""
        id = utils.get_id(segment)
        coords = utils.get_coords(segment)
        type_ = utils.get_type(segment)
        contents = segment.contents

        return cls(id, coords, type_, contents, segment)



