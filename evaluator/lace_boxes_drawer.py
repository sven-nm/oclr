import cv2
import numpy as np

# image = cv2.imread(os.path.join(args.IMG_DIR, filename))
copy = image.image_matrix.copy()
gray = cv2.cvtColor(image.image_matrix, cv2.COLOR_BGR2GRAY)
ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

cv2.drawContours(copy, contours, -1, (0,255,0), 1)
cv2.drawContours(copy, contours[:50], -1, (0,255,255), 1)
cv2.drawContours(copy, contours[100], -1, (255,0,0), 6)


cv2.imwrite("LEPET.png", copy)
#%%
overlap_matrix = np.ndarray((4, image.height, image.width), dtype=object)
overlap_matrix[:, :, :] = ''
overlap_matrix[3, :, :] = -1



for i, contour in enumerate(contours):
    for point in contour:
        overlap_matrix[3, point[0][1], point[0][0]] = i

#%%





#%%
for contour in contours:
    # print(np.squeeze(contour).shape)
    print(np.max(contour[:, :,1:2]))


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
