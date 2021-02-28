Annotation_helper performs the following tasks :

1. Converting Lace-annotations (.svg) to VIA2 annotations (.csv)
2. Detecting zones in image-files
3. Adding detected zones to Lace-annotations. 


# Setup

Please install annotation_helper from source, using `git clone https://github.com/sven-nm/annotation_helper`. 
`environment.yml` specifies requirements for a conda environment. 

# Run

Go to the annotation_helper directory : `cd annotation_helper`.

Activate environment : `conda activate myenv`. 

Run `python3 annotation_helper` with the following arguments : 

```shell script
optional arguments:
  -h, --help            show this help message and exit
  --IMG_DATA_DIR IMG_DATA_DIR
                        Absolute path to the directory where the image-files
                        are stored
  --SVG_DATA_DIR SVG_DATA_DIR
                        Absolute path to the directory where the svg-files are
                        stored
  --OUTPUT_DIR OUTPUT_DIR
                        Absolute path to the directory in which output images,
                        csvs or jsons files are to be stored
  --dilation_kernel_size DILATION_KERNEL_SIZE
                        Dilation kernel size, preferably an odd number. Tweak
                        this parameter and `--dilation_iterations` to improve
                        automatic boxing.
  --dilation_iterations DILATION_ITERATIONS
                        Number of iterations in dilation, default 1
  --artifacts_size_threshold ARTIFACTS_SIZE_THRESHOLD
                        Size-threshold under which contours are to be
                        considered as artifacts and removed, expressed as a
                        percentage of image height. Default is 0.01
  --draw_rectangles     Whether to output images with both shrinked and
                        dilated rectangles.This is usefull if you want to have
                        a look at images, e.g. to test dilation parameters.
  --merge_zones         Whether to add automatically detected zones to Lace-
                        zones before exporting annotation file 
```

For example : 
```shell script
python3 annotation_helper --IMG_DATA_DIR "data/test_png" \
--SVG_DATA_DIR "data/test_svg" \
--OUTPUT_DIR "output" \
--dilation_kernel_size 51 \
--dilation_iterations 1 \
--artifacts_size_threshold 0.01 \
--draw_rectangles \
--merge_zones
```

# Transfering the project to VIA2

- Download VIA2 from : https://www.robots.ox.ac.uk/~vgg/software/via/ 
- Open a new VIA2 project and import your images
- In the `project`-menu, chose import file/region attributes and import `default_via_attributes.json` from
the annotation_helper directory. 
- In the `annotation`-menu, chose import annotations from csv, and import the annotations you want from the 
annotation_helper output. 


# A few words on the code

As mentionned above, Annotation_helper performs the following tasks :

1. Converting Lace-annotations (.svg) in VIA2 annotations (.csv)
2. Detecting zones in image-files
3. Adding detected zones to Lace-annotations. 


**Converting Lace-annotations (.svg) in VIA2 annotations (.csv)** is done in `svg_converter.py`. The idea is to
transform svg-annotation into VIA2 annotations by converting the vectorial coordinates of rectangles 
into pixel-coordinates. 

**Detecting zones in image-files** is done using `cv2.dilation`. This dilates recognized letters-contours to recognize 
wider structures. The retrieved rectangles are then shrinked back to their original size. This can be seen
when drawing rectangles on images. 

**Adding detected zones to Lace-annotations** is done by comparing detected rectangles to lace-rectangles. If a 
detected rectangle does not match any Lace-rectangles, it is added to the final list. 

