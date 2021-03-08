from bs4 import BeautifulSoup

divisor = 4


def initialize_soup(image):
    """Initializes a blank html page for comparisons"""

    soup = BeautifulSoup("""<!doctype html>
                         <html lang="en">
                         <head><meta charset="utf-8"><title>{}</title></head>
                         <body><p style="margin:auto;text-align:center"> 
                         <b>OCR/GROUNDTRUTH COMPARISON </b><br> 
                         Ocr is displayed on the left, groundtruth on the right.<br>
                         Missrecognized words are contoured in red. </p>
                         </body></html>""".format(image.filename), features="lxml")

    to_append = soup.new_tag(name="div",
                             attrs={"half_width": image.width / divisor,
                                    "style": "margin:auto;"
                                             "position:relative;"
                                             "width:{}px; "
                                             "height:{}px".format(image.width * 2 / divisor,
                                                                  image.height / divisor)})

    soup.html.body.append(to_append)

    return soup


def insert_text(soup, word, gt, distance):
    """Draws text and rectangles on html"""

    x_coord = word.coords[3][0]/divisor+soup.html.body.div["half_width"] if gt else word.coords[3][0]/divisor

    border = "1px solid red" if distance > 0 else "0px"

    to_append = soup.new_tag(name="div",
                             attrs={"style": "position:absolute;"
                                             "width:{}px;"
                                             "height:{}px;"
                                             "left:{}px;"
                                             "top:{}px;"
                                             "border:{}".format(word.width / divisor,
                                                                word.height / divisor,
                                                                x_coord,
                                                                word.coords[3][1] / divisor,
                                                                border)})


    to_append.string = word.content

    soup.html.body.div.append(to_append)

    return soup
