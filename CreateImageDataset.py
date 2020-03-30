from PIL import Image
from PIL import ImageOps
import random
import json
import os

class createImageDataset():

    """
    Possible URL for changing colors?? might not really work though https://python-forum.io/Thread-Change-color-pixel-in-an-image
    """

    def __init__(self):
        self.threshold = .25
        self.ogthreshhold = .50
        pass

    """
    code for cutting found at this URL:
    https://note.nkmk.me/en/python-pillow-image-crop-trimming/
    
    :param img: gives the image after it's been open with Image.open()
    :param coords: gives the coordinates of the box to cut in the format 
        (left, bottom, right, top)
        #IMPORTANT# the cut section does not include right and lower
        # I have accounted for this #
    :return the cut selection from the image
    """
    def cutPieceFromImage(self, img, coords):
        imgCopy = img.copy()
        box = coords[0], coords[1], coords[2]+1, coords[3]+1  # keep an eye on this
        cutImg = imgCopy.crop(box)
        return cutImg

    """
    :param img: gives the image (NOT a filepath)
    :param angle: the angle at which to rotate the image (counter clockwise)
    """
    def rotateImage(self, img):
        angles = [90, 180, 270, 360]
        random.shuffle(angles)
        return img.rotate(angles[0], expand=True)

    """
    :param img: gives the image (NOT a filepath)
    :param stretchBy: a constant to be multiplied by the original size of the image
        (a decimal between .4 and 1.7) !!we can discuss these values!!
    URL: https://www.geeksforgeeks.org/python-pil-image-resize-method/
    """
    def resizeImage(self, img):
        maxWidth = 475
        maxHeight = 475
        stretchBy = random.randint(4, 17)/10
        resizeX = int(img.width * stretchBy)
        resizeY = int(img.height * stretchBy)

        if resizeX > maxWidth:
            return img
        if resizeY > maxHeight:
            return img

        resized = img.resize((resizeX, resizeY))
        return resized

    """ URL: https://note.nkmk.me/en/python-pillow-flip-mirror/ """
    def mirrorImage(self, img):
        return ImageOps.mirror(img)

    def pasteImage(self, imgBase, imgPaste, topLCoord):
        imgToReturn = imgBase.copy()
        pasteCopy = imgPaste.copy()
        imgToReturn.paste(pasteCopy, topLCoord)
        return imgToReturn

    def chooseRandomWidth(self):
        width = random.randint(75, 300)
        height = random.randint(75, 300)
        return width, height


    def createRandomPixelCoords(self, bounds, width, height):
        x1 = random.randint(bounds[0], bounds[2])
        y1 = random.randint(bounds[1], bounds[3])
        x2 = x1+width
        y2 = y1+height

        return x1, y1, x2, y2


    def determinePixelHomogeneity(self, picture):
        # print("indeterminePixelHomogeneity")
        pixelMap = picture.load()
        mapOPix = {}
        for i in range(picture.size[0]):
            for j in range(picture.size[1]):
                key = pixelMap[i,j]
                if key in mapOPix:
                    mapOPix[key] += 1
                else:
                    mapOPix[key] = 1

        maxVal = 0

        for val in mapOPix.values():
            if val > maxVal:
                maxVal = val

        # print(maxVal)
        homogeneity = maxVal/(picture.size[0]*picture.size[1])
        return homogeneity

    def filterOGPics(self, subdir, images):
        counter = 0
        for image in images:
            counter += 1
            # print(counter)
            img = Image.open(subdir + "\\" + image)
            homogeneity = self.determinePixelHomogeneity(img)
            if homogeneity > self.ogthreshhold:
                if not os.path.exists(subdir + '\\discards'):
                    os.makedirs(subdir + '\\discards')
                os.replace(subdir + '\\' + image, subdir + '\\discards\\' + image)

    def createEditedPic(self, name1, name2, subdir):
        # open the images

        img1 = Image.open(subdir + "\\" + name1)
        img2 = Image.open(subdir + "\\" + name2)
        imgBase = img2.copy()

        boundsImg1 = (0, 0, img1.width-300, img1.height-300)
        boundsImg2 = (0, 0, img2.width-300, img2.height-300)

        coordsFromCuts = []
        coordsFromPastes = []

        mirror, rotate, stretch = self.randomizeEdits()

        # make edits
        if mirror:
            # print("Mirror")
            homogeneity = 1
            cutMirror = None
            mirrorCoord = None
            # cut and mirror image
            while homogeneity > self.threshold:
                width, height = self.chooseRandomWidth()
                mirrorCoord = self.createRandomPixelCoords(boundsImg1, width, height)
                cutMirror = self.cutPieceFromImage(img1, mirrorCoord)
                homogeneity = self.determinePixelHomogeneity(cutMirror)

            coordsFromCuts.append(mirrorCoord)
            cutMirror = self.mirrorImage(cutMirror)

            if mirror > 1:
                # rotate or stretch
                mr, r, s = self.randomizeEdits()
                if r:
                    cutMirror = self.rotateImage(cutMirror)
                if s:
                    cutMirror = self.resizeImage(cutMirror)

            mirrorCoordPaste = self.createRandomPixelCoords(boundsImg2, cutMirror.width, cutMirror.height)
            coordsFromPastes.append(mirrorCoordPaste)
            imgBase = self.pasteImage(imgBase, cutMirror, (mirrorCoordPaste[0], mirrorCoordPaste[1]))

        if rotate:
            # print("rotate")
            homogeneity = 1
            cutRotate = None
            rotateCoord = None

            while homogeneity > self.threshold:
                width, height = self.chooseRandomWidth()
                rotateCoord = self.createRandomPixelCoords(boundsImg1, width, height)
                cutRotate = self.cutPieceFromImage(img1, rotateCoord)
                homogeneity = self.determinePixelHomogeneity(cutRotate)

            coordsFromCuts.append(rotateCoord)
            cutRotate = self.rotateImage(cutRotate)

            if rotate > 1:
                mr, r, s = self.randomizeEdits()
                if mr:
                    cutRotate = self.mirrorImage(cutRotate)
                if s:
                    cutRotate = self.resizeImage(cutRotate)

            rotateCoordPaste = self.createRandomPixelCoords(boundsImg2, cutRotate.width, cutRotate.height)
            coordsFromPastes.append(rotateCoordPaste)
            imgBase = self.pasteImage(imgBase, cutRotate, (rotateCoordPaste[0], rotateCoordPaste[1]))

        if stretch:
            # print("Stretch")
            homogeneity = 1
            cutStretch = None
            stretchCoord = None

            while homogeneity > self.threshold:
                width, height = self.chooseRandomWidth()
                stretchCoord = self.createRandomPixelCoords(boundsImg1, width, height)
                cutStretch = self.cutPieceFromImage(img1, stretchCoord)
                homogeneity = self.determinePixelHomogeneity(cutStretch)

            coordsFromCuts.append(stretchCoord)
            cutStretch = self.resizeImage(cutStretch)

            if stretch > 1:
                mr, r, s = self.randomizeEdits()
                if mr:
                    cutStretch = self.mirrorImage(cutStretch)
                if r:
                    cutStretch = self.rotateImage(cutStretch)

            stretchCoordPaste = self.createRandomPixelCoords(boundsImg2, cutStretch.width, cutStretch.height)
            coordsFromPastes.append(stretchCoordPaste)
            imgBase = self.pasteImage(imgBase, cutStretch, (stretchCoordPaste[0], stretchCoordPaste[1]))

        # save edited pic
        imgOG = img1.save(subdir + "\\" + "truth.jpg")
        imgBase = imgBase.save(subdir + "\\" + "edited.jpg")

        # save json
        self.saveJson(coordsFromCuts, coordsFromPastes, subdir)

    def saveJson(self, cutCoords, pasteCoords, subdir):

        for i in range(len(cutCoords)):
            coords = cutCoords[i]
            cutCoords[i] = [[coords[0], coords[1]],[coords[2], coords[3]]]
        for i in range(len(pasteCoords)):
            coords = pasteCoords[i]
            pasteCoords[i] = [[coords[0], coords[1]],[coords[2], coords[3]]]
        data = {
            "truth" : cutCoords,
            "edited" : pasteCoords
        }

        with open(subdir + "\\" + "correct.json", 'w') as fp:
            json.dump(data, fp)

        return data

    def randomizeEdits(self):
        doMirror, doRotate, doStretch = 0, 0, 0

        while not (doMirror or doRotate or doStretch):
            doMirror = random.randint(0,2)
            doRotate = random.randint(0,2)
            doStretch = random.randint(0,2)

        return doMirror, doRotate, doStretch


# https://stackoverflow.com/questions/19587118/iterating-through-directories-with-python
# to iterate over files in a directory
def main():
    root = 'image_datasets\\training_set_edited'
    root2 = 'image_datasets\\testing_set_edited'

    root1 = 'image_datasets_random\\train'

    cid = createImageDataset()

    # for subdir, dirs, files in os.walk(root1):
    #     cid.filterOGPics(subdir, files)

    # for subdir, dirs, files in os.walk(root1):
    #     random.shuffle(files)
    #     for i in range(len(files)//2):
    #         if not os.path.exists(subdir + '\\pair' + str(i)):
    #             os.makedirs(subdir + '\\pair' + str(i))
    #         os.replace(subdir + '\\' + files[i], subdir + '\\pair' + str(i) + '\\' + files[i])
    #         os.replace(subdir + '\\' + files[-(i + 1)], subdir + '\\pair' + str(i) + '\\' + files[-(i + 1)])
    #     break


    for subdir, dirs, files in os.walk(root1):
        if len(dirs) == 0:
            if os.path.exists(subdir + "\\correct.json"):
                os.remove(subdir + "\\correct.json")
            if os.path.exists(subdir + "\\edited.jpg"):
                os.remove(subdir + "\\edited.jpg")
            if os.path.exists(subdir + "\\truth.jpg"):
                os.remove(subdir + "\\truth.jpg")

    counter = 0
    for subdir, dirs, files in os.walk(root1):
        counter += 1
        print(subdir)
        if len(dirs) == 0:
            cid.createEditedPic(files[0], files[1], subdir)


if __name__ == '__main__':
    main()



