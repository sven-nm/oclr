import cv2
import numpy as np
import os
import csv


# TODO : maybe add to  oclr_utils
def remove_artifacts(image, contours, artifacts_size_threshold):
    """Removes contours if the sum of their height and width is inferior to the user-selected threshold"""
    contours_denoised = []
    for contour in contours:
        _, _, w, h = cv2.boundingRect(contour)
        if h + w > round(image.shape[0] * artifacts_size_threshold):
            contours_denoised.append(contour)
    return contours_denoised


# TODO : maybe add to  oclr_utils
def find_contour_centroid(contour):
    """Finds the centroid of a contour to perform clustering algorithm"""
    moments = cv2.moments(contour)
    centroid_x = int(moments["m10"] / moments["m00"])
    centroid_y = int(moments["m01"] / moments["m00"])
    centroid = np.array([centroid_x, centroid_y])
    return centroid


# TODO : maybe add to  oclr_utils
def get_bounding_rectangles(contours):
    contours_rectangles = []
    for i, contour in enumerate(contours):  # TODO : remove
        x, y, w, h = cv2.boundingRect(contour)
        contours_rectangles.append(np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]]))
    return contours_rectangles


def shrink_dilation_contours_rectangles(dilation_contours_rectangles, contours_rectangles):
    """Selects contours_rectangles contained in dilation_contours_rectangles and shrink dilation to minimum size"""

    dilation_contours_rectangles_shrinked = []

    for dilation_contour_rectangle in dilation_contours_rectangles:
        contours_in_dilation = []

        for contours_rectangle in contours_rectangles:
            if np.min(contours_rectangle[:, 0]) > np.min(dilation_contour_rectangle[:, 0]) and \
                    np.min(contours_rectangle[:, 1]) > np.min(dilation_contour_rectangle[:, 1]) and \
                    np.max(contours_rectangle[:, 0]) < np.max(dilation_contour_rectangle[:, 0]) and \
                    np.max(contours_rectangle[:, 1]) < np.max(dilation_contour_rectangle[:, 1]):
                contours_in_dilation.append(contours_rectangle)

        # Shrink dilation_contour_rectangle to min
        if contours_in_dilation != []:
            contours_in_dilation = np.stack(contours_in_dilation, axis=0)

            dilation_contours_rectangles_shrinked.append(np.array([
                [np.min(contours_in_dilation[:, :, 0]), np.min(contours_in_dilation[:, :, 1])],
                [np.max(contours_in_dilation[:, :, 0]), np.min(contours_in_dilation[:, :, 1])],
                [np.max(contours_in_dilation[:, :, 0]), np.max(contours_in_dilation[:, :, 1])],
                [np.min(contours_in_dilation[:, :, 0]), np.max(contours_in_dilation[:, :, 1])]
            ]))

    return dilation_contours_rectangles_shrinked


def correct_csv_manually(csv_filename, args):
    """manually corrects quoting error in output csv-files"""

    os.system("""sed -ia 's/ //g' """ + csv_filename)
    os.system("""sed -ia "s/'/ /g" """ + csv_filename)
    os.system("""sed -ia 's/ /""/g' """ + csv_filename)
    os.system("""sed -ia 's/},/}",/g' """ + csv_filename)
    os.system("""sed -ia 's/,{/,"{/g' """ + csv_filename)
    os.system("""sed -ia 's/""}/""}"/g' """ + csv_filename)


def write_csv_manually(csv_filename, csv_dict, args):
    """Writes a dictionnary a csv-file with custom quoting corresponding to via expectations"""

    pwd = os.getcwd()
    os.chdir(args.OUTPUT_DIR)

    with open(csv_filename, 'w') as csv_file:
        spamwriter = csv.writer(csv_file, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(list(csv_dict.keys()))
        for line in range(len(csv_dict["filename"])):
            to_append = []
            for k in list(csv_dict.keys()):
                to_append.append(csv_dict[k][line])
            spamwriter.writerow(to_append)

    correct_csv_manually(csv_filename, args)
    os.remove(csv_filename + "a")
    os.chdir(pwd)
