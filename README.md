# Presentation

`oclr` is python-package containing **Optical Character and Layout Recognition utilities**. 

It contains `annotation_helper` and `evaluator`. 
 
`Annotation_helper` performs the following tasks :

1. Converting Lace-annotations (.svg) to VIA2 annotations (.csv)
2. Detecting zones in image-files
3. Adding detected zones to Lace-annotations. 

`evaluator` performs regional and coordinates-based CER and WER evaluation between Lace groundtruth-files and Lace or OCR-D ocr-files.

This file is general presentation. More detailed information on the code can be found in each subpackage. 

# Setup

Please install `olcr` from source, using `git clone https://github.com/sven-nm/oclr`. 

# Run

In order to run `oclr` properly, you first need to create an environment. `environment.yml` 
specifies requirements for [creating a conda environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file). 

Once the environment is created, go to the annotation_helper directory : `cd annotation_helper`.

Activate your environment : `conda activate myenv`. 

Then follow the specific instructions of each program. 


# Run annotation_helper

Run `python3 annotation_helper` with the following arguments : 

```shell script
optional arguments:
  -h, --help            show this help message and exit
  --IMG_DIR IMG_DIR
                        Absolute path to the directory where the image-files
                        are stored
  --SVG_DIR SVG_DIR
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
python3 annotation_helper --IMG_DIR "data/test_png" \
--SVG_DIR "data/test_svg" \
--OUTPUT_DIR "output" \
--dilation_kernel_size 51 \
--dilation_iterations 1 \
--artifacts_size_threshold 0.01 \
--draw_rectangles \
--merge_zones
```

Then, to **transfer the project to VIA2**, please :

- [Download VIA2](https://www.robots.ox.ac.uk/~vgg/software/via/) 
- Open a new VIA2 project and import your images
- In the `project`-menu, chose import file/region attributes and import `default_via_attributes.json` from
the annotation_helper/data directory. 
- In the `annotation`-menu, chose import annotations from csv, and import the annotations you want from the 
annotation_helper output. 

# Run evaluator

Run `python3 evaluator` with the following arguments : 

```shell script
optional arguments:
  -h, --help            show this help message and exit
  --IMG_DIR IMG_DIR     Absolute path to the directory where the image-files
                        are stored
  --SVG_DIR SVG_DIR     Absolute path to the directory where the svg-files are
                        stored
  --OUTPUT_DIR OUTPUT_DIR
                        Absolute path to the directory in which outputs are to
                        be stored
  --GROUNDTRUTH_DIR GROUNDTRUTH_DIR
                        Absolute path to the directory in which groundtruth-
                        files are stored
  --OCR_DIR OCR_DIR     Absolute path to the directory in which ocr-files are
                        stored
```