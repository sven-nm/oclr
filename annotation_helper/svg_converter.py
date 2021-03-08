import cv2
from xml.dom import minidom
import os
from annotation_helper import utils
import logging


# TODO : Actualize this with oclr_utils classes
def convert_svg(args):
    """Convert svg-files from lace into VIA2 readable csv-files.
    Returns a `'key':[values]`-like dictionnary containing all the imported rectangles for all the images"""

    csv_dict = {"filename": [],
                "file_size": [],
                "file_attributes": [],
                "region_count": [],
                "region_id": [],
                "region_shape_attributes": [],
                "region_attributes": []}

    for svg_file in os.listdir(args.SVG_DIR):

        if svg_file[-3:] == "svg":

            logging.info("Processing image " + svg_file)

            svg = minidom.parse(os.path.join(args.SVG_DIR, svg_file))

            # Retrieve relevant rectangles
            rectangles = [r for r in svg.getElementsByTagName('rect') if r.getAttribute("data-rectangle-type") in
                          ["commentary", "page_number", "primary_text", "title", "app_crit", "translation"]]

            # Retrieve image and file-name
            linked_image = svg.getElementsByTagName("image")[0]
            linked_image_name = os.path.basename(linked_image.getAttribute("xlink:href"))
            linked_image_height = cv2.imread(os.path.join(args.IMG_DIR, linked_image_name)).shape[0]
            linked_image_width = cv2.imread(os.path.join(args.IMG_DIR, linked_image_name)).shape[1]

            # Retrieve svg viewports dimensions
            svg_height = float(svg.getElementsByTagName("svg")[0].getAttribute("height"))
            svg_width = float(svg.getElementsByTagName("svg")[0].getAttribute("width"))

            # Creates first level dictionaries, with each zone as key.
            for rectangle in rectangles:
                csv_dict["filename"].append(os.path.basename(linked_image_name))
                csv_dict["file_size"].append(os.stat(
                    os.path.join(args.IMG_DIR,
                                 linked_image_name)).st_size)
                csv_dict["file_attributes"].append({})
                csv_dict["region_count"].append(len(rectangles))
                csv_dict["region_id"].append(rectangle.getAttribute("data-rectangle-ordinal"))
                csv_dict["region_shape_attributes"].append({"name": "rect",
                                                            "x": int(round(float(
                                                                rectangle.getAttribute(
                                                                    "x")) * linked_image_width / svg_width)),
                                                            "y": int(round(float(
                                                                rectangle.getAttribute(
                                                                    "y")) * linked_image_height / svg_height)),
                                                            "width": int(round(float(
                                                                rectangle.getAttribute(
                                                                    "width")) * linked_image_width / svg_width)),
                                                            "height": int(round(float(rectangle.getAttribute(
                                                                "height")) * linked_image_height / svg_height)),
                                                            })
                csv_dict["region_attributes"].append({"text": rectangle.getAttribute("data-rectangle-type")})

    utils.write_csv_manually("lace_annotations.csv", csv_dict, args)

    print("{} zones were extraxcted from svg data".format(len(csv_dict["filename"])))

    return csv_dict
