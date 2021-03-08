import sys
import os
sys.path.append(os.getcwd())
from annotation_helper.zone_detector import detect_zones, merge_lace_and_detected_zones
from annotation_helper.svg_converter import convert_svg
from oclr_utils.cli import args

# merging Lace and detected zones
detected_zones = detect_zones(args)
lace_zones = convert_svg(args)
if args.merge_zones:
    merged_zones = merge_lace_and_detected_zones(detected_zones, lace_zones, args)














