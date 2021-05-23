import sys
import os
sys.path.append(os.getcwd())
from annotation_helper.zone_detector import detect_zones, merge_lace_and_detected_zones
from annotation_helper.utils import write_csv_manually
from oclr_utils import file_management
from oclr_utils.cli import args
import logging


csv_dict = {"filename": [],
            "file_size": [],
            "file_attributes": [],
            "region_count": [],
            "region_id": [],
            "region_shape_attributes": [],
            "region_attributes": []}

for filename in os.listdir(args.IMG_DIR):
    if filename[-3:] in ["png", "jpg", "tif", "jp2"]:
        logging.info("Processing image " + filename)

        detect_zones(args, filename, csv_dict)
        # svg = file_management.ZonesMasks.from_lace_svg(args, filename[:-4], filename[-4:])
        svg.convert_lace_svg_to_via_csv_dict(args)

# if args.merge_zones:
#     merged_zones = merge_lace_and_detected_zones(detected_zones, file_management.ZonesMasks.csv_dict, args)

write_csv_manually("detected_annotations.csv", csv_dict, args)
logging.info("{} zones were automatically detected".format(len(csv_dict["filename"])))


