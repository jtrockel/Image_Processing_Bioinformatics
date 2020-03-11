from PIL import Image
from PIL import ImageOps

class createImageDataset():

    # TODO: NOTE THAT I SORTA REMEMBER SOMETHING BEING SAID
    # TODO: ABOUT A PIXEL NOT BEING INCLUDED IN SOMETHING,
    # TODO: I THINK IT HAD TO DO WITH THE CUTTING

    """
    Possible URL for changing colors?? might not really work though https://python-forum.io/Thread-Change-color-pixel-in-an-image
    """

    def __init__(self):
        pass

    """
    code for cutting found at this URL:
    https://note.nkmk.me/en/python-pillow-image-crop-trimming/
    
    :param img: gives the image after it's been open with Image.open()
    :param coords: gives the coordinates of the box to cut in the format 
        (left, bottom, right, top)
    :return the cut selection from the image
    """
    def cutPieceFromImage(self, img, coords):
        box = [(coords[0], coords[3]), (coords[2], coords[1])]
        cutImg = img.crop(box)
        return cutImg

    """
    :param img: gives the image (NOT a filepath)
    :param angle: the angle at which to rotate the image (counter clockwise)
    """
    def rotateImage(self, img, angle, stretchBy):
        return img.rotate(angle, expand=True)

    """
    :param img: gives the image (NOT a filepath)
    :param stretchBy: a constant to be multiplied by the original size of the image
        (a decimal between .3 and 1.7) !!we can discuss these values!!
    URL: https://www.geeksforgeeks.org/python-pil-image-resize-method/
    """
    def resizeImage(self, img, stretchBy):
        resizeX = img.width * stretchBy
        resizeY = img.height * stretchBy
        return img.resize(resizeX, resizeY)

    """ URL: https://note.nkmk.me/en/python-pillow-flip-mirror/ """
    def mirrorImage(self, img):
        return ImageOps.mirror(img)

    def pasteImage(self, imgBase, imgPaste, topLCoord):
        imgToReturn = imgBase.copy()
        pasteCopy = imgPaste.copy()
        imgToReturn.paste(pasteCopy, topLCoord)
        return imgToReturn


    def createRandomPixelCoords(self, numToCreate):
        # todo randomize
        # todo - make sure the pixels will be
        # return [left,upper,right,lower]
        return 56, 34, 67, 8


def main():
    cid = createImageDataset()
    cid.cutPieceFromImage('image_datasets/training_set_edited/pair49/P9 B27-20913-9107.jpg')


if __name__ == '__main__':
    main()



