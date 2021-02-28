import argparse
from zone_detector import detect_zones, merge_lace_and_detected_zones
from svg_converter import convert_svg

# Parameters
parser = argparse.ArgumentParser()

parser.add_argument(
    "--IMG_DATA_DIR",
    default=None,
    type=str,
    required=True,
    help="Absolute path to the directory where the image-files are stored")

parser.add_argument(
    "--SVG_DATA_DIR",
    default=None,
    type=str,
    required=True,
    help="Absolute path to the directory where the svg-files are stored")

parser.add_argument(
    "--OUTPUT_DIR",
    default=None,
    type=str,
    required=True,
    help="Absolute path to the directory in which output images, csvs or jsons files are to be stored")

parser.add_argument(
    "--dilation_kernel_size",
    default=51,
    type=int,
    help="Dilation kernel size, preferably an odd number. Tweak this parameter and `--dilation_iterations` "
         "to improve automatic boxing.")

parser.add_argument(
    "--dilation_iterations",
    default=1,
    type=int,
    help="Number of iterations in dilation, default 1")


parser.add_argument(
    "--artifacts_size_threshold",
    default=0.01,
    type=float,
    help="Size-threshold under which contours are to be considered as artifacts and removed, expressed as a percentage of image height. Default is 0.01")


parser.add_argument(
    "--draw_rectangles", action="store_true", help="Whether to output images with both shrinked and dilated rectangles."
                                                   "This is usefull if you want to have a look at images, e.g. to test "
                                                   "dilation parameters. ")
parser.add_argument(
    "--merge_zones", action="store_true", help="Whether to add automatically detected zones to Lace-zones before "
                                               "exporting annotation file")

args = parser.parse_args()

# merging Lace and detected zones
detected_zones = detect_zones(args)
lace_zones = convert_svg(args)
if args.merge_zones:
    merged_zones = merge_lace_and_detected_zones(detected_zones, lace_zones, args)














