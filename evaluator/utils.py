def get_id(segment):
    """ Retrieves id from a lace or an ocrd segment. Input :  a segment. Returns : id as str"""
    try:
        id = segment.getAttribute("id")
    except TypeError:
        id = segment["id"]
    return id


# todo change all coords in new format
def get_coords(segment):
    """ Retrieves coords from a lace or an ocrd segment. Input :  a segment. Returns : coors as a list of [x,y]-coords-lists,
    with the following order for rectangles : upper left, upper right, down right, down left """

    try:  # try for an ocrd-segment
        coords = segment.getElementsByTagName("pc:Coords")[0].getAttribute("points").split()
        coords = [(int(coord.split(",")[0]), int(coord.split(",")[1])) for coord in coords]

    except TypeError:  # exception raised if lace segment
        coords = segment["title"].split()
        coords = [(int(coords[1]), int(coords[2])), (int(coords[3], int(coords[2]))),
                  (int(coords[3]), int(coords[4])), (int(coords[1]), int(coords[4]))]

    return coords

def get_type(segment):
    try:
        type_ = segment.getElementsByTagName("pc:Coords")[0].getAttribute("class")
    except TypeError:
        type_ = segment["class"]

# TODO CONtinuer ici
# TODO add file 146 TO OCR FROM TRASH




def compute_levenshtein(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]



#%%

coords = "12,13 13,13 14,14".split()

for a,b in coords[0].split(","):
    print(a,b)

[(int(coord.split(",")[0]), int(coord.split(",")[1])) for coord in coords]

a,b = coords[0].split(",")
[coord.split(",") for coord in coords]

coords = [(int(a),int(b)) for coord in coords for a,b in coord.split(",")]