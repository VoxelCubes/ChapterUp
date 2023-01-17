# ChapterUp

This is a simple command line tool to upload a folder of images to imgur in a sensible order.
When sharing images, sometimes the order may be important, and this tool will ensure the album
contains all images in the order they are named.


## Installation

Get the .whl file from the releases page and install it with pip:

```
pip install chapterup-[latest release].whl
```
Requirements: Python 3.10 or later \
Dependencies are installed automatically by pip.

You will also need an access token from imgur.
Follow this official guide by imgur to get one: https://apidocs.imgur.com

(The access token specifically is acquired in step 5.)


## Example usage

```
$ chapterup test_images Demonstration 
The following test_images will be uploaded in order:
image0.png
image1.png
image2.png
image3.png
image4.png

Found 5 test_images.
Do you want to continue? [y/N] > y
100%|██████████| 5/5 [00:06<00:00,  1.33s/it]
--------------------------------------------------
Album created with id: 6We1mSd
Access the album here: https://imgur.com/a/6We1mSd
```
Note: The first time you run it, you need to provide an access token, but it will be saved in the config for future uses.