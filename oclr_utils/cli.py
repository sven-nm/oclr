import argparse
import sys

parser = argparse.ArgumentParser()


def general_args(parser):
    """Define general cli arguments"""

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

    return parser


def evaluator_args(parser):
    """Defines evaluator-specific cli arguments"""

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

    return parser


def annotation_helper_args(parser):
    """Defines annotation_helper-specific arguments"""

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
        help="Size-threshold under which contours are to be considered as artifacts and removed, expressed as a "
             "percentage of image height. Default is 0.01")

    parser.add_argument(
        "--draw_rectangles", action="store_true", help="Whether to output images with both shrinked and dilated "
                                                       "rectangles. This is usefull if you want to have a look at "
                                                       "images, e.g. to test dilation parameters. ")
    parser.add_argument(
        "--merge_zones", action="store_true", help="Whether to add automatically detected zones to Lace-zones before "
                                                   "exporting annotation file")

    return parser


if sys.argv[0] == "evaluator":
    parser = evaluator_args(general_args(parser))
    args = parser.parse_args()

elif sys.argv[0] == "annotation_helper":
    parser = annotation_helper_args(general_args(parser))
    args = parser.parse_args()


# For local testing
else:
    parser = evaluator_args(annotation_helper_args(general_args(parser)))
    args = parser.parse_args(["--IMG_DIR", "/Users/sven/oclr/evaluator/data/images",
                              "--SVG_DIR", "/Users/sven/oclr/evaluator/data/svg",
                              "--OUTPUT_DIR", "/Users/sven/oclr/evaluator/outputs/ocrd_jebb_eval",
                              "--GROUNDTRUTH_DIR", "/Users/sven/oclr/evaluator/data/groundtruth",
                              "--OCR_DIR", "/Users/sven/oclr/evaluator/data/ocr/ocrd_ocr/OCR-D-OCR_word",
                              "--dilation_kernel_size", "51",
                              "--dilation_iterations", "1",
                              "--artifacts_size_threshold", "0.01",
                              "--draw_rectangles",
                              "--merge_zones"
                              ])
