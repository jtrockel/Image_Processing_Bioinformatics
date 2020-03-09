#!/usr/bin/python

# TODO future potential plans:
# allow ELA to run on png files?

from __future__ import print_function
from PIL import Image, ImageChops, ImageEnhance
import sys, os
import threading
import argparse
import glob

# USAGE: ela.py --dir directory/to/folder(or file) --quality qualityNum --brightness brightnessPercent
# both --quality and --brightness are optional and default to 90 and 100 respectively

parser = argparse.ArgumentParser(description="""
Performs Error Level Analysis over a single image or a directory of images
""")
parser.add_argument('--dir', dest='directory', required=True,
                    help='path to an image or a directory containing multiple images')
parser.add_argument('--quality', dest='quality',
                    help='quality used by the jpeg compression alg.',
                    default=90)
parser.add_argument('--brightness', dest='brightness',
                    help='percent brightness of result, with 100 as default',
                    default=100)

TMP_EXT = ".tmp_ela.jpg"
ELA_EXT = ".ela.png"
SAVE_REL_DIR = "generated"
threads = []


def ela(fname, orig_dir, save_dir, quality=90, brightness=100):
    """
    Generates an ELA image on save_dir.
    Params:
        fname:      filename w/out path
        orig_dir:   origin path
        save_dir:   save path
    """
    basename, ext = os.path.splitext(fname)

    org_fname = os.path.join(orig_dir, fname)
    tmp_fname = os.path.join(save_dir, basename + TMP_EXT)
    ela_fname = os.path.join(save_dir, basename + ELA_EXT)

    im = Image.open(org_fname)
    im.save(tmp_fname, 'JPEG', quality=quality)

    tmp_fname_im = Image.open(tmp_fname)
    ela_im = ImageChops.difference(im, tmp_fname_im)

    extrema = ela_im.getextrema()
    max_diff = max([ex[1] for ex in extrema])

    brightness = brightness * 2.55
    if brightness <= 0:
        brightness = 1
    print(brightness)
    scale = brightness / max_diff  # default scale is 255 with 100 percent brightness
    ela_im = ImageEnhance.Brightness(ela_im).enhance(scale)

    ela_im.save(ela_fname)
    os.remove(tmp_fname)


def main():
    args = parser.parse_args()
    dirc = args.directory
    # TODO: make this more robust
    quality = int(args.quality)
    brightness = int(args.brightness)
    print(brightness)
    if os.path.exists(dirc):
        if os.path.isfile(dirc):
            if not dirc.endswith(".jpg") and not dirc.endswith(".jpeg"):
                print("Your file is not a jpg or jpeg image!")
            else:
                print("Performing ELA on %s" % os.path.basename(dirc))

                fname = os.path.basename(dirc)
                dirname = os.path.dirname(dirc)
                thread = threading.Thread(target=ela, args=[fname, dirname, dirname, quality, brightness])
                threads.append(thread)
                thread.start()
                thread.join()

                print("Finished!")
                basename, ext = os.path.splitext(fname)

                print("Head to %s to check the results!" % (os.path.join(dirname, basename + ELA_EXT)))

        else:
            print("Performing ELA on images at %s" % dirc)

            # if the directory has jpg or jpeg images, run ela on them, otherwise print that nothing happened
            if len(glob.glob("*.jpg")) != 0 or len(glob.glob("*.jpeg")) != 0:

                ela_dirc = os.path.join(dirc, SAVE_REL_DIR)
                if not os.path.exists(ela_dirc):
                    os.makedirs(ela_dirc)

                for d in os.listdir(dirc):
                    if d.endswith(".jpg") or d.endswith(".jpeg"):
                        thread = threading.Thread(target=ela, args=[d, dirc, ela_dirc, quality, brightness])
                        threads.append(thread)
                        thread.start()

                for t in threads:
                    t.join()

                print("Finished!")
                print("Head to %s to check the results!" % (os.path.join(dirc, SAVE_REL_DIR)))
            else:
                print("Finished!")
                print("No jpg or jpeg images were detected in that directory, so nothing happened.")
    else:
        print("Path %s doesn't exist. Please check your path and try again." % dirc)


if __name__ == '__main__':
    main()
else:
    print("This should'nt be imported.", file=sys.stderr)
    sys.exit(1)
