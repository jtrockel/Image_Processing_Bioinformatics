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
    def resizeImage(self, img, bounds):
        maxWidth = bounds[2] - bounds[0]
        maxHeight = bounds[3] - bounds[1]
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

    def getPasteCoords(self, imgPaste, bounds):
        potentialCoords = self.createRandomPixelCoords(bounds)

        if potentialCoords[0] + imgPaste.width > bounds[2]:
            shiftX = bounds[2] - (potentialCoords[0] + imgPaste.width)
            x1 = potentialCoords[0] + shiftX
            x2 = potentialCoords[0] + shiftX + imgPaste.width - 1

        else:
            x1 = potentialCoords[0]
            x2 = potentialCoords[0] + imgPaste.width - 1

        if potentialCoords[1] + imgPaste.height > bounds[3]:
            shiftY = bounds[3] - (potentialCoords[1] + imgPaste.width)
            y1 = potentialCoords[1] + shiftY
            y2 = potentialCoords[1] + shiftY + imgPaste.height - 1

        else:
            y1 = potentialCoords[1]
            y2 = potentialCoords[1] + imgPaste.height - 1

        return self.ptsWithinBounds(bounds, (x1, y1, x2, y2))

    def createRandomPixelCoords(self, bounds):
        x1 = random.randint(bounds[0], bounds[2])
        y1 = random.randint(bounds[1], bounds[3])

        x2 = random.randint(bounds[0], bounds[2])
        y2 = random.randint(bounds[1], bounds[3])

        if x1 == x2:
            print("THEY WERE EQUAL???")
            x2 = random.randint(bounds[0], bounds[2])

        if x1 < x2:
            if abs(x2-x1) < 50:
                x2 = x1+50
            if y1 == y2:
                y2 += random.randint(bounds[1], bounds[3])
            if y1 < y2:
                if abs(y2-y1) < 50:
                    y2 = y1+50
                return self.ptsWithinBounds(bounds, (x1, y1, x2, y2))
            else:
                if abs(y2-y1) < 50:
                    y1 = y2+50
                return self.ptsWithinBounds(bounds, (x1, y2, x2, y1))

        else:
            if abs(x2-x1) < 50:
                x1 = x2+50
            if y1 == y2:
                y2 += random.randint(bounds[1], bounds[3])
            if y1 < y2:
                if abs(y2-y1) < 50:
                    y2 = y1+50
                return self.ptsWithinBounds(bounds, (x2, y1, x1, y2))
            else:
                if abs(y2-y1) < 50:
                    y1 = y2+50
                return self.ptsWithinBounds(bounds, (x2, y2, x1, y1))

    def ptsWithinBounds(self, bounds, points):
        if bounds[2] < points[2]:
            tmp = bounds[2] - points[2]
            x1 = points[0] + tmp
            x2 = points[2] + tmp
        else:
            x1 = points[0]
            x2 = points[2]

        if bounds[3] < points[3]:
            tmp = bounds[3] - points[3]
            y1 = points[1] + tmp
            y2 = points[3] + tmp
        else:
            y1 = points[1]
            y2 = points[3]

        return x1, y1, x2, y2

    def createEditedPic(self, name1, name2, subdir):
        # open the images

        img1 = Image.open(subdir + "\\" + name1)
        img2 = Image.open(subdir + "\\" + name2)
        imgBase = img2.copy()

        # decide which edits to make
        hHeight = (img1.height-1)//2
        hWidth = (img1.width-1)//2
        height = img1.height-1
        width = img1.width-1

        hHeightb = (imgBase.height-1)//2
        hWidthb = (imgBase.width-1)//2
        heightb = imgBase.height-1
        widthb = imgBase.width-1

        availableBounds = [(0, 0, hWidth, hHeight), (0, hHeight, hWidth, height),
                           (hWidth, 0, width, hHeight), (hWidth, hHeight, width, height)]
        availableBoundsPaste = [(0, 0, hWidthb, hHeightb), (0, hHeightb, hWidthb, heightb),
                           (hWidthb, 0, widthb, hHeightb), (hWidthb, hHeightb, widthb, heightb)]

        random.shuffle(availableBounds)
        random.shuffle(availableBoundsPaste)

        coordsFromCuts = []
        coordsFromPastes = []

        mirror, rotate, stretch = self.randomizeEdits()

        # make edits
        if mirror:
            print("Mirror")
            # cut and mirror image
            mirrorCoord = self.createRandomPixelCoords(availableBounds[0])
            coordsFromCuts.append(mirrorCoord)
            cutMirror = self.cutPieceFromImage(img1, mirrorCoord)
            cutMirror = self.mirrorImage(cutMirror)

            if mirror > 1:
                # rotate or stretch
                mr, r, s = self.randomizeEdits()
                if r:
                    cutMirror = self.rotateImage(cutMirror)
                if s:
                    cutMirror = self.resizeImage(cutMirror, availableBoundsPaste[0])

            mirrorCoordPaste = self.getPasteCoords(cutMirror, availableBoundsPaste[0])
            coordsFromPastes.append(mirrorCoordPaste)
            imgBase = self.pasteImage(imgBase, cutMirror, (mirrorCoordPaste[0], mirrorCoordPaste[1]))

        if rotate:
            print("rotate")
            rotateCoord = self.createRandomPixelCoords(availableBounds[1])
            coordsFromCuts.append(rotateCoord)
            cutRotate = self.cutPieceFromImage(img1, rotateCoord)
            cutRotate = self.mirrorImage(cutRotate)

            if rotate > 1:
                mr, r, s = self.randomizeEdits()
                if mr:
                    cutRotate = self.mirrorImage(cutRotate)
                if s:
                    cutRotate = self.resizeImage(cutRotate, availableBoundsPaste[1])

            rotateCoordPaste = self.getPasteCoords(cutRotate, availableBoundsPaste[1])
            coordsFromPastes.append(rotateCoordPaste)
            imgBase = self.pasteImage(imgBase, cutRotate, (rotateCoordPaste[0], rotateCoordPaste[1]))

        if stretch:
            print("Stretch")
            stretchCoord = self.createRandomPixelCoords(availableBounds[2])
            coordsFromCuts.append(stretchCoord)
            cutStretch = self.cutPieceFromImage(img1, stretchCoord)
            cutStretch = self.resizeImage(cutStretch, availableBoundsPaste[2])

            if stretch > 1:
                mr, r, s = self.randomizeEdits()
                if mr:
                    cutStretch = self.mirrorImage(cutStretch)
                if r:
                    cutStretch = self.rotateImage(cutStretch)

            stretchCoordPaste = self.getPasteCoords(cutStretch, availableBoundsPaste[2])
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

        print(data)

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

    cid = createImageDataset()
    for subdir, dirs, files in os.walk(root2):
        if len(dirs) == 0:
            if os.path.exists(subdir + "\\correct.json"):
                os.remove(subdir + "\\correct.json")
            if os.path.exists(subdir + "\\edited.jpg"):
                os.remove(subdir + "\\edited.jpg")
            if os.path.exists(subdir + "\\truth.jpg"):
                os.remove(subdir + "\\truth.jpg")

    for subdir, dirs, files in os.walk(root2):
        if len(dirs) == 0:
            cid.createEditedPic(files[0], files[1], subdir)


if __name__ == '__main__':
    main()



