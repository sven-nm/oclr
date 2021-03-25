# -----------------------------------------------------------
# `extracters.py` stores all the function used to extract data from hocr, html or PAGE-xml formats.
# -----------------------------------------------------------


def get_id(args, segment, data_type):
    """ Retrieves id from a lace or an ocrd segment. Input :  a segment. Returns : id as str"""
    if args.ocr_engine == "ocrd" and data_type == "ocr":
        id = segment.getAttribute("id")
    else:
        id = segment["id"]
    return id


def get_coords(args, segment, data_type):
    """ Retrieves coords from a lace or an ocrd segment.
        Input :  a segment.
        Returns : coords as a list of (x,y)-coords-tuples,
        with the following order for rectangles : upper left, upper right, down right, down left """

    if args.ocr_engine == "ocrd" and data_type == "ocr":
        coords = segment.getElementsByTagName("pc:Coords")[0].getAttribute("points").split()
        coords = [(int(coord.split(",")[0]), int(coord.split(",")[1])) for coord in coords]

    else :  # exception raised if lace segment
        coords = segment["title"].split()
        coords = [(int(coords[1]), int(coords[2])), (int(coords[3]), int(coords[2])),
                  (int(coords[3]), int(coords[4])), (int(coords[1]), int(coords[4]))]

        # Make sure the segment is at least one-pixel wide
        if coords[0][0] == coords[2][0]:
            coords[2] = (coords[2][0]+1, coords[2][1])
            coords[1] = (coords[1][0] + 1, coords[1][1])

        if coords[0][1] == coords[2][1]:
            coords[2] = (coords[2][0], coords[2][1]+1)
            coords[3] = (coords[3][0], coords[3][1]+1)

    return coords


def get_type(args, segment, data_type):
    if args.ocr_engine == "ocrd" and data_type == "ocr":
        type_ = segment.getElementsByTagName("pc:Coords")[0].getAttribute("class")
    else:
        type_ = segment["class"]




def get_content(args, segment, data_type):
    """Retrieves the content of a segment"""
    if args.ocr_engine == "ocrd" and data_type == "ocr":
        content = segment.getElementsByTagName("pc:TextEquiv")[0].getElementsByTagName("pc:Unicode")[
            0].firstChild.nodeValue
    else:
        try:
            content = segment.contents[0]
        except IndexError:
            content = ""

    return content