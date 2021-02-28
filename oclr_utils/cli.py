import argparse
#TODO centralize all this

parser = argparse.ArgumentParser()

# ==================================================================
# ==================== GENERAL ARGUMENTS ===========================
# ==================================================================
parser.add_argument(
    "--IMG_DIR",
    default=None,
    type=str,
    required=True,
    help="Absolute path to the directory where the image-files are stored")

parser.add_argument(
    "--SVG_DIR",
    default=None,
    type=str,
    required=True,
    help="Absolute path to the directory where the svg-files are stored")

parser.add_argument(
    "--OUTPUT_DIR",
    default=None,
    type=str,
    required=True,
    help="Absolute path to the directory in which outputs are to be stored")


# ==================================================================
# ==================== EVALUATOR ARGUMENTS =========================
# ==================================================================
parser.add_argument(
    "--GROUNDTRUTH_DIR",
    default=None,
    type=str,
    required=True,
    help="Absolute path to the directory in which groundtruth-files are stored")

parser.add_argument(
    "--OCR_DIR",
    default=None,
    type=str,
    required=True,
    help="Absolute path to the directory in which ocr-files are stored")


# ==================================================================
# ================ ANNOTATION_HELPER ARGUMENTS =====================
# ==================================================================
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








try:
    args = parser.parse_args()
except:
    args = parser.parse_args(["--IMG_DIR", "data/images",
                              "--SVG_DIR", "data/svg",
                              "--OUTPUT_DIR", "output",
                              "--GROUNDTRUTH_DIR", "data/groundtruth",
                              "--OCR_DIR", "data/ocr" #TODO complete this list with annotation_helper args
                              ])
