




# %% DRAWING

for rectangle in gt_words:
    coords = utils.get_coords(rectangle)
    ocrd_word_rectangles_draw = cv2.rectangle(image.copy,
                                              (coords["x1"], coords["y1"]),
                                              (coords["x3"],coords["y3"]),
                                              (0, 255, 0),
                                              2)
for rectangle in ocr_words:
    coords = utils.get_coords(rectangle)
    ocrd_word_rectangles_draw = cv2.rectangle(image.copy,
                                              (coords["x1"]+1, coords["y1"]+1),
                                              (coords["x3"]+1,coords["y3"]+1),
                                              (0, 0, 255),
                                              2)
# %% Draw single word

rectangle = word
coords = utils.get_coords(rectangle)
ocrd_word_rectangles_draw = cv2.rectangle(image.copy,
                                          (coords["x1"], coords["y1"]),
                                          (coords["x3"], coords["y3"]),
                                          (0, 255, 0),
                                          2)
# %%
for polygon in ocrd_word_rectangles:
    _ = cv2.polylines(image.copy, [polygon], True, (0, 0, 255), 3)

cv2.imwrite("boxes.tif", image.copy)

# %%
