import csv
import os
import numpy as np
import Levenshtein
import sys
sys.path.append(os.getcwd())
from oclr_utils import file_management
from oclr_utils.cli import args
import evaluator.utils


# TODO : Update Logging
# TODO : Update html overlapping
# TODO : Create dinglehopper like comparison files
# TODO : Warning, this loop only works if the files are named in a same way.
# TODO : handle words that are in ocr but not in gt
# TODO : add safe check
# TODO : manage box sizes for ocrd
# TODO : see if word as already been evaulated
# TODO : see if overlap can be to another word
# TODO : all correction as a safety check

# Warning : This is assuming no words are overlapping in a single ocr !

# Declarations
analyzed_zonetypes = ["global", "commentary", "primary_text", "translation", "app_crit", "page_number", "title", "no_zone"]
error_counts = {i: {j: 0 for j in ["chars", "distance", "words", "false_words"]} for i in analyzed_zonetypes}
error_traceback = []
args.ocr_engine = "ocrd" if args.OCR_DIR.find("OCR-D") >= 0 else "lace"



# Loop over all image-files
for image_filename in os.listdir(args.IMG_DIR):

    if image_filename[-3:] in ["png", "jpg", "tif", "jp2"]:

        print("Processing image " + image_filename)

        # Import files (FOR LACE)
        image = file_management.Image(args, image_filename)
        svg = file_management.ZonesMasks(args, image_filename[0:-3] + "svg")
        groundtruth = file_management.OcrObject(args, image_filename, data_type="groundtruth")
        ocr = file_management.OcrObject(args, image_filename, data_type="ocr")

        # Initialize html output
        soup = evaluator.utils.initialize_soup(image)

        # Creates a blank image matrix that we will use later
        image_matrix = np.ndarray((3, image.height, image.width), dtype=object)
        image_matrix[:, :, :] = ''

        # TODO : change this if ocr is not regionized
        # For each zone, fill matrix and add error dictionary
        for zone in svg.zones:
            zone = file_management.Segment.from_lace_svg(zone, image, svg)
            image_matrix[0, zone.coords[0][1]:zone.coords[2][1],zone.coords[0][0]:zone.coords[2][0]] = zone.type  # adds zone.type to matrix, eg. "primary_text"

        # For each word in ocr, fill matrix
        for word in ocr.words:
            word = file_management.Segment.from_ocr(args, word, "ocr")
            image_matrix[2, word.coords[0][1]:word.coords[2][1], word.coords[0][0]:word.coords[2][0]] = word.id

        # For each gt_word in gt, fill matrix, then find overlapping gt- and ocr-words
        for gt_word in groundtruth.words:
            gt_word = file_management.Segment.from_ocr(args, gt_word, "groundtruth")
            image_matrix[1, gt_word.coords[0][1]:gt_word.coords[2][1],gt_word.coords[0][0]:gt_word.coords[2][0]] = gt_word.id

            array = image_matrix[0, gt_word.coords[0][1]:gt_word.coords[2][1],gt_word.coords[0][0]:gt_word.coords[2][0]]

            # TODO : encore un code de cochon monsieur NM
            word_zone = None
            for e in set(array.flatten()):
                if e != '':
                    word_zone = e
            if word_zone is None:
                word_zone = "no_zone"

            # easy solution : get the most present element in ocr matrix for given gt coordinates
            overlap_scores = {}
            array = image_matrix[2, gt_word.coords[0][1]:gt_word.coords[2][1],gt_word.coords[0][0]:gt_word.coords[2][0]]

            for id in set(array.flatten()):
                overlap_scores[id] = len(array[array == id])

            # LIPSTICK ON A MUDDY PIG TO GET THE VALUE THAT HAS THE MAX SCORE # TODO change this horror
            good_id = list(overlap_scores.keys())[list(overlap_scores.values()).index(max(overlap_scores.values()))]

            # Retrieve word with good id
            if args.ocr_engine == "lace":
                ocr_word = file_management.Segment.from_ocr(args,
                                                            ocr.source.find_all("html:span", {"id": good_id})[0],
                                                            "ocr")
            else: # TODO change this to not reloop over words
                for word in ocr.words:
                    word = file_management.Segment.from_ocr(args, word, "ocr")
                    if word.id == good_id:
                        ocr_word = word


            # Compute edit distance
            distance = Levenshtein.distance(ocr_word.content, gt_word.content)
            editops = Levenshtein.editops(ocr_word.content, gt_word.content)

            for editop in editops:
                if editop[0] == "delete":
                    error_traceback.append("delete " + ocr_word.content[editop[1]])
                elif editop[0] == "insert":
                    error_traceback.append("insert " + gt_word.content[editop[2]])
                else:
                    error_traceback.append(
                        "{} {} -> {}".format(editop[0], ocr_word.content[int(editop[1])], gt_word.content[int(editop[2])]))

            # Register counts at global- and word_zone-level
            for key in ["global", word_zone]:
                error_counts[key]["chars"] += len(gt_word.content)
                error_counts[key]["distance"] += distance
                error_counts[key]["words"] += 1
                if distance > 0:
                    error_counts[key]["false_words"] += 1

            # Actualize and write soup
            soup = evaluator.utils.insert_text(soup, gt_word, True, distance)
            soup = evaluator.utils.insert_text(soup, ocr_word, False, distance)
            with open(os.path.join(args.OUTPUT_DIR, image.filename[:-3] + "html"), "w") as html_file:
                html_file.write(str(soup))


# Compute CER and WER
cer = {}
wer = {}
for zonetype in error_counts.keys():
    try:
        cer[zonetype] = error_counts[zonetype]["distance"] / error_counts[zonetype]["chars"]
    except ZeroDivisionError:
        cer[zonetype] = 0

    try:
        wer[zonetype] = error_counts[zonetype]["false_words"] / error_counts[zonetype]["words"]
    except ZeroDivisionError:
        wer[zonetype] = 0

# Histogramm of error traceback

error_traceback = {op: error_traceback.count(op) for op in error_traceback}
error_traceback = {k: v for k, v in sorted(error_traceback.items(), key=lambda item: item[1], reverse=True)}

# Write custom results.tsv
with open(os.path.join(args.OUTPUT_DIR, "results.tsv"), 'w') as csv_file:
    spamwriter = csv.writer(csv_file, delimiter='\t',
                            quotechar='"')
    spamwriter.writerow(["global_cer", "global_wer",
                         "commentary_cer", "commentary_wer",
                         "primary_text_cer", "primary_text_wer",
                         "translation_cer", "translation_wer",
                         "app_crit_cer", "app_crit_wer",
                         "page_number_cer", "page_number_wer",
                         "title_cer", "title_wer",
                         "no_zone_cer", "no_zone_wer"])

    spamwriter.writerow([cer["global"], wer["global"],
                         cer["commentary"], wer["commentary"],
                         cer["primary_text"], wer["primary_text"],
                         cer["translation"], wer["translation"],
                         cer["app_crit"], wer["app_crit"],
                         cer["page_number"], wer["page_number"],
                         cer["title"], wer["title"],
                         cer["no_zone"], wer["no_zone"]])

# Write custom editops_traceback
with open(os.path.join(args.OUTPUT_DIR, "error_traceback.tsv"), 'w') as csv_file:
    spamwriter = csv.writer(csv_file, delimiter='\t',
                            quotechar='"')
    for k, v in error_traceback.items():
        spamwriter.writerow([k, v])

# %%


#%%