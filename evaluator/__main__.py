import csv
import os
import Levenshtein
import sys
sys.path.append(os.getcwd())
from oclr_utils import file_management, extracters
from oclr_utils.cli import args
import evaluator.utils
import cv2


# TODO : Update Logging
# TODO : Update html overlapping
# TODO : handle words that are in ocr but not in gt
# TODO : add safe check
# TODO : manage box sizes for ocrd
# TODO : see if word as already been evaulated
# TODO : see if overlap can be to another word
# TODO : all correction as a safety check

# Pre-loop declarations
analyzed_zonetypes = ["global", "commentary", "primary_text", "translation", "app_crit", "page_number", "title",
                      "no_zone"]
error_counts = {i: {j: 0 for j in ["chars", "distance", "words", "false_words"]} for i in analyzed_zonetypes}
editops_record = []
args.ocr_engine = "ocrd" if args.OCR_DIR.find("OCR-D") >= 0 else "lace"

for gt_filename in os.listdir(args.GROUNDTRUTH_DIR):  # GT-files LOOP

    if gt_filename[-5:] == ".html":
        print("Processing image " + gt_filename)
        gt_filename = gt_filename[:-5]  # Removes the extension

        # Import files
        image = file_management.Image(args, gt_filename)
        svg = file_management.ZonesMasks(args, gt_filename, image.image_format)
        groundtruth = file_management.OcrObject(args, image, gt_filename, data_type="groundtruth")
        ocr = file_management.OcrObject(args, image, gt_filename, data_type="ocr")

        soup = evaluator.utils.initialize_soup(image)  # Initialize html output
        image.overlap_matrix = evaluator.utils.actualize_overlap_matrix(args, image, svg, groundtruth, ocr)

        for gt_word in groundtruth.words:

            gt_word.zone_type = extracters.get_segment_zonetype(gt_word, image.overlap_matrix)
            ocr_word = extracters.get_corresponding_ocr_word(args, gt_word, ocr, image.overlap_matrix)

            # Compute and record distance and edit operation
            distance = Levenshtein.distance(ocr_word.content, gt_word.content)
            editops = Levenshtein.editops(ocr_word.content, gt_word.content)
            editops_record = evaluator.utils.record_editops(gt_word, ocr_word, editops, editops_record)
            error_counts = evaluator.utils.actualize_error_counts(error_counts, gt_word, distance)

            # Actualize soup and write comparison html file
            soup = evaluator.utils.insert_text(soup, image, gt_word, True, distance)
            soup = evaluator.utils.insert_text(soup, image, ocr_word, False, distance)
            image.copy = evaluator.utils.draw_rectangle(image.copy, gt_word, (0,255,0), 4)
            image.copy = evaluator.utils.draw_rectangle(image.copy, ocr_word, (0, 0, 255), 2)

        # Write final html-file
        with open(os.path.join(args.OUTPUT_DIR, gt_filename+".html"), "w") as html_file:
            html_file.write(str(soup))

        # Write boxes images
        cv2.imwrite(os.path.join(args.OUTPUT_DIR,gt_filename+".png"), image.copy)



# Compute CER and WER
cer = {}
wer = {}
for zone_type in error_counts.keys():
    try:
        cer[zone_type] = error_counts[zone_type]["distance"] / error_counts[zone_type]["chars"]
    except ZeroDivisionError:
        cer[zone_type] = 0

    try:
        wer[zone_type] = error_counts[zone_type]["false_words"] / error_counts[zone_type]["words"]
    except ZeroDivisionError:
        wer[zone_type] = 0


editops_record = {op: editops_record.count(op) for op in editops_record}
editops_record = {k: v for k, v in sorted(editops_record.items(), key=lambda item: item[1], reverse=True)}

# Write custom results.tsv
with open(os.path.join(args.OUTPUT_DIR, "results_{}.tsv".format(args.ocr_engine)), 'w') as csv_file:
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
with open(os.path.join(args.OUTPUT_DIR, "editops_record_{}.tsv".format(args.ocr_engine)), 'w') as csv_file:
    spamwriter = csv.writer(csv_file, delimiter='\t',
                            quotechar='"')
    for k, v in editops_record.items():
        spamwriter.writerow([k, v])

