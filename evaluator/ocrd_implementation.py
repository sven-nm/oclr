# ========================= FOR LATER OCRD INTEGRATION ========================================================
# FOR OCRD  #TODO CONTINUE/UPDATE HERE

# ocrd lines
ocrd_lines = ocrd.getElementsByTagName("pc:TextLine")
ocrd_line_polygons = []
for line in ocrd_lines:
# line = ocrd_lines[0]
    coords = line.getElementsByTagName("pc:Coords")[0].getAttribute("points").split()
    coords = [coord.split(",") for coord in coords]
    coords = [[int(coord[0]), int(coord[1])] for coord in coords]
    coords = np.array(coords)
    coords = coords.reshape((-1,1,2))
    ocrd_line_polygons.append(coords)
# TODO : Add for loop over ocrd words
# ==============================================================================================================
