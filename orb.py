import numpy as np
import cv2 as cv
from boxDrawer import BoxDrawer
import sys
from matplotlib import pyplot as plt

class OrbAlgorithm:
    def __init__(self):
        pass

    def filterMatches(self, ratioThresh, matches):
        #-- Filter matches using the Lowe's ratio test
        # Changing the ratio_thresh variable allows more/fewer matches
        good_matches = []

        #-- Loop through matches and only allow those that meet the threshold
        # append those values to good_matches array
        for m,n in matches:
            if m.distance < ratioThresh * n.distance:
                good_matches.append(m)
        return good_matches

    def findKeypointsForSingleImage(self, imgPath, numfeatures=1000):
        img = cv.imread(imgPath)
        orb = cv.ORB_create(nfeatures=numfeatures)
        #kp = orb.detect(img, None)
        #kp, des = orb.compute(img, kp)

        kp, des = orb.detectAndCompute(img, None)
        # img2 = cv.drawKeypoints(img,kp,None,color=(0,255,0), flags=0)
        # plt.imshow(img2),plt.show

        return kp, des, img

    def findSimilaritiesBetweenTwoImages(self, img1path, img2path, a_outPathOriginal,
                                         a_outPathNew, numfeatures=10000, a_ratioThresh = 0.7):

        kp1, des1, img1 = self.findKeypointsForSingleImage(img1path, numfeatures)
        kp2, des2, img2 = self.findKeypointsForSingleImage(img2path, numfeatures)

        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=70) # or pass empty dictionary

        flann = cv.FlannBasedMatcher(index_params, search_params)
        des1 = np.float32(des1)
        des2 = np.float32(des2)

        matches = flann.knnMatch(des1, des2, k=2)
        goodmatches = self.filterMatches(a_ratioThresh, matches)

        kp1Matched = [kp1[m.queryIdx] for m in goodmatches]
        kp2Matched = [kp2[m.trainIdx] for m in goodmatches]

        self.drawMatches(kp1Matched, kp2Matched, img1, img2, a_outPathOriginal, a_outPathNew)

    def drawMatches(self, kp1, kp2, img1, img2, outPathOriginal, outPathNew):
        # Draw boxes around key matches
        bd = BoxDrawer(kp1,100,img1,(0,255,0),5)
        img1 = bd.img
        bd = BoxDrawer(kp2,100,img2,(0,255,0),5)
        img2 = bd.img

        # write out images
        cv.imwrite(outPathOriginal,img1)
        cv.imwrite(outPathNew, img2)

        """         matchesMask = [[0,0] for i in range(len(matches))]

        for i,(m,n) in enumerate(matchesMask):
            if m.distance < 0.7*n.distance:
                matchesMask[i] = [1,0]"""

        """        draw_params = dict(matchColor = (0,225,0),
                   singlePointColor = (255,0,0),
                   matchesMask = None,
                   flags = 0)"""

        # cv.drawMatchesKnn(img1, kp1, img2, kp2, matches, None, **draw_params)

        #plt.imshow(img3,), plt.show()



# detect the key points of an image

# Compare the key points of 2 images

"""img2 = cv.imread('images\\cellTest.jpg', 1)
img = cv.imread('images\\cellTestCrop4.jpg', 1)

# Initiate ORB detector
orb = cv.ORB_create(nfeatures=10000)

# find the keypoints with ORB
kp1, des1 = orb.detectAndCompute(img, None)
kp2, des2 = orb.detectAndCompute(img2, None)

# FLANN params
FLANN_INDEX_KDTREE = 0
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
search_params = dict(checks=70) # or pass empty dictionary

flann = cv.FlannBasedMatcher(index_params, search_params)
des1 = np.float32(des1)
des2 = np.float32(des2)

matches = flann.knnMatch(des1, des2, k=2)

matchesMask = [[0,0] for i in range(len(matches))]

for i,(m,n) in enumerate(matches):
    if m.distance < 0.7*n.distance:
        matchesMask[i] = [1,0]

draw_params = dict(matchColor = (0,225,0),
                   singlePointColor = (255,0,0),
                   matchesMask = matchesMask,
                   flags = 0)

img3 = cv.drawMatchesKnn(img, kp1, img2, kp2, matches, None, **draw_params)

plt.imshow(img3,), plt.show()

"""
'''_____________________________________________'''

"""img2 = cv.imread('images\\cellTest.jpg', 0)
img = cv.imread('images\\cellTest.jpg', 0)

training_image = cv.cvtColor(img, cv.COLOR_BGR2RGB)
training_gray = cv.cvtColor(training_image, cv.COLOR_RGB2GRAY)
test_image = cv.pyrDown(training_image)
test_image = cv.pyrDown(test_image)
num_rows, num_cols = test_image.shape[:2]

rotation_matrix = cv.getRotationMatrix2D((num_cols/2, num_rows/2), 30, 1)
test_image = cv.warpAffine(test_image, rotation_matrix, (num_cols, num_rows))

test_gray = cv.cvtColor(test_image, cv.COLOR_RGB2GRAY)

orb2 = cv.ORB_create()

train_keypoints, train_descriptor = orb.detectAndCompute(training_gray, None)
test_keypoints, test_descriptor = orb.detectAndCompute(test_gray, None)

keypoints_without_size = np.copy(training_image)
keypoints_with_size = np.copy(training_image)

cv.drawKeypoints(training_image, train_keypoints, keypoints_without_size, color = (0, 255, 0))
cv.drawKeypoints(training_image, train_keypoints, keypoints_with_size, flags = cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

# Display image with and without keypoints size
fx, plots = plt.subplots(1, 2, figsize=(20,10))

plots[0].set_title("Train keypoints With Size")
plots[0].imshow(keypoints_with_size, cmap='gray')

plots[1].set_title("Train keypoints Without Size")
plots[1].imshow(keypoints_without_size, cmap='gray')

# Print the number of keypoints detected in the training image
print("Number of Keypoints Detected In The Training Image: ", len(train_keypoints))

# Print the number of keypoints detected in the query image
print("Number of Keypoints Detected In The Query Image: ", len(test_keypoints))
"""


if __name__ == "__main__":

    # Paths for images to be compared

    imgPath1 = "images/test_images/figure1/cells_19_1.png"
    imgPath2 = "images/test_images/figure1/cells_19_2.png"
    #imgPath1 = "images/figure1/cells2.1.png"
    #imgPath2 = "images/figure1/cells2.2.png"
    outPathOriginal = "images/test_images/figure1/cells_19_1_matchedOrb.png"
    outPathNew = "images/test_images/figure1/cells_19_2_matchedOrb.png"

    # Create instance of class
    orbObj = OrbAlgorithm()
    # kp, des, img = orbObj.findKeypointsForSingleImage(imgPath1)

    # img2 = cv.drawKeypoints(img,kp,None,color=(0,255,0), flags=0)
    # plt.imshow(img2),plt.show()

    orbObj.findSimilaritiesBetweenTwoImages(imgPath1, imgPath2, numfeatures=100000,
                                            a_outPathOriginal=outPathOriginal, a_outPathNew=outPathNew)
