import cv2
import os
import annotation_helper.utils
import pandas as pd
import logging


def detect_zones(args: "ArgumentParser", filename: str, csv_dict: dict) -> dict:

    """Automatically detects regions of interest for every image in `IMG_DIR`, using a simple dilation process.
    Returns a `'key':[values]`-like dictionnary containing all the generated rectangles for all the images"""

    # Preparing image
    image = cv2.imread(os.path.join(args.IMG_DIR, filename))
    copy = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(src=gray, ksize=(31, 31), sigmaX=0)
    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

    # Appplying dilation on the threshold image
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (args.dilation_kernel_size, args.dilation_kernel_size))
    dilation = cv2.dilate(thresh1, rect_kernel, iterations=args.dilation_iterations)

    # Finding contours
    contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours = annotation_helper.utils.remove_artifacts(image, contours, args.artifacts_size_threshold)

    # Finding dilation contours
    dilation_contours, dilation_hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    dilation_contours = annotation_helper.utils.remove_artifacts(image, dilation_contours, args.artifacts_size_threshold)

    # Get boundings rects of contours
    contours_rectangles = annotation_helper.utils.get_bounding_rectangles(contours)
    dilation_contours_rectangles = annotation_helper.utils.get_bounding_rectangles(dilation_contours)

    dilation_contours_rectangles_shrinked = annotation_helper.utils.shrink_dilation_contours_rectangles(dilation_contours_rectangles,
                                                                                           contours_rectangles)

    for i, rectangle in enumerate(dilation_contours_rectangles_shrinked):
        csv_dict["filename"].append(filename)
        csv_dict["file_size"].append(os.stat(os.path.join(args.IMG_DIR, filename)).st_size)
        csv_dict["file_attributes"].append("{}")
        csv_dict["region_count"].append(len(dilation_contours_rectangles_shrinked))
        csv_dict["region_id"].append(i)
        csv_dict["region_shape_attributes"].append({"name": "rect",
                                                    "x": rectangle[0, 0],
                                                    "y": rectangle[0, 1],
                                                    "width": rectangle[1, 0] - rectangle[0, 0],
                                                    "height": rectangle[2, 1] - rectangle[0, 1]})
        csv_dict["region_attributes"].append({"text": "undefined"})

    # Draws output rectangles
    if args.draw_rectangles :
        # for rectangle in dilation_contours_rectangles:
        #     dilation_rectangle = cv2.rectangle(copy, (rectangle[0, 0], rectangle[0, 1]),
        #                          (rectangle[2, 0], rectangle[2, 1]), (0, 0, 255), 4)

        for rectangle in dilation_contours_rectangles_shrinked:
            shrinked_rectangle = cv2.rectangle(copy, (rectangle[0, 0], rectangle[0, 1]),
                                        (rectangle[2, 0], rectangle[2, 1]), (0, 0, 255), 4)

    cv2.imwrite(os.path.join(args.OUTPUT_DIR, filename), copy)



def merge_lace_and_detected_zones(detected_zones, lace_zones, args):
    """Adds automatically detected regions to Lace-annotations if they are different"""
    dfd = pd.DataFrame.from_dict(detected_zones)
    dfl = pd.DataFrame.from_dict(lace_zones)

    added_rectangles = 0

    for filename in set(dfd["filename"]):

        dfd_ = dfd[dfd["filename"] == filename]
        dfl_ = dfl[dfl["filename"] == filename]

        temporary = pd.DataFrame.from_dict({"filename": [], "file_size": [], "file_attributes": [], "region_count": [],
                                            "region_id": [], "region_shape_attributes": [], "region_attributes": []})

        for rowl in dfl_.iterrows():
            for rowd in dfd_.iterrows():
                # if a detected rectangle is not within +/- 10 pixel of a lace rectangle then add it to annotations
                if rowl[1].loc["region_shape_attributes"]["x"] - 10 < rowd[1].loc["region_shape_attributes"]["x"] < \
                        rowl[1].loc["region_shape_attributes"]["x"] + 10 and \
                        rowl[1].loc["region_shape_attributes"]["y"] - 10 < rowd[1].loc["region_shape_attributes"]["y"] < \
                        rowl[1].loc["region_shape_attributes"]["y"] + 10 and \
                        rowl[1].loc["region_shape_attributes"]["height"] - 10 < rowd[1].loc["region_shape_attributes"][
                    "height"] < rowl[1].loc["region_shape_attributes"]["height"] + 10 and \
                        rowl[1].loc["region_shape_attributes"]["width"] - 10 < rowd[1].loc["region_shape_attributes"][
                    "width"] < rowl[1].loc["region_shape_attributes"]["width"] + 10:
                    pass
                else:
                    if rowd[0] not in temporary.index:
                        added_rectangles += 1
                        temporary = temporary.append(rowd[1], ignore_index=False)

        dfl = dfl.append(temporary, ignore_index=False)

    csv_dict = dfl.to_dict(orient='list')

    annotation_helper.utils.write_csv_manually("all_annotations.csv", csv_dict, args)

    print("{} automatically detected zones were added to lace annotations".format(added_rectangles))

    return csv_dict
