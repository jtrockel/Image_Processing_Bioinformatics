'''import numpy as np
import cv2
import sys
from matplotlib import pyplot as plt

img1 = cv2.imread(sys.argv[1],0) # queryImage
img2 = cv2.imread(sys.argv[2],0) # trainImage

# Initiate SIFT detector
sift = cv2.xfeatures2d.SIFT_create()

# find the keypoints and descriptors with SIFT
kp1, des1 = sift.detectAndCompute(img1,None)
kp2, des2 = sift.detectAndCompute(img2,None)

# FLANN parameters
FLANN_INDEX_KDTREE = 0
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks=50)   # or pass empty dictionary

flann = cv2.FlannBasedMatcher(index_params,search_params)

matches = flann.knnMatch(des1,des2,k=2)

# Need to draw only good matches, so create a mask
matchesMask = [[0,0] for i in range(len(matches))]

# ratio test as per Lowe's paper (https://www.cs.ubc.ca/~lowe/papers/ijcv04.pdf)
# removes outliers
for i,(m,n) in enumerate(matches):
    if m.distance < 0.7*n.distance:
        matchesMask[i]=[1,0]

draw_params = dict(matchColor = (0,255,0),
                   singlePointColor = (255,0,0),
                   matchesMask = matchesMask,
                   flags = 0)

img3 = cv2.drawMatchesKnn(img1,kp1,img2,kp2,matches,None,**draw_params)

plt.imshow(img3,),plt.show()'''

import cv2 as cv
import sys
import numpy as np
from boxDrawer import BoxDrawer

"""
Script to find similarities in images. There's still a lot of cases that this does not find. 
For example if an images colors are inverted, the features won't be found. But it's a first step.

The SURF algorithm is protected by some copyright issues so in order to use it you must install previous
versions of opencv and contrib. 

I used the following commands (you may need to uninstall current versions if you already have them. Or
create a virtual environment for this):

pip install opencv-contrib-python==3.4.2.16
pip install opencv-python==3.4.2.16

Information and code from the following:

https://docs.opencv.org/2.4/modules/nonfree/doc/feature_detection.html?highlight=threshold
https://docs.opencv.org/3.4/d5/d6f/tutorial_feature_flann_matcher.html
https://docs.opencv.org/3.4/da/df5/tutorial_py_sift_intro.html
https://www.youtube.com/watch?v=WOH7hDXrfwc&list=PL6Yc5OUgcoTlQuAdhtnByty15Ea9-cQly&index=1
https://www.youtube.com/watch?v=9mQznoHk4mU&list=PL6Yc5OUgcoTlQuAdhtnByty15Ea9-cQly&index=2
https://www.youtube.com/watch?v=ND5vGDNvN0s&list=PL6Yc5OUgcoTlQuAdhtnByty15Ea9-cQly&index=3
https://www.youtube.com/watch?v=ADuHe4JNLXs&list=PL6Yc5OUgcoTlQuAdhtnByty15Ea9-cQly&index=4
"""
class SimilarityDetector:

    def __init__(self):
        """
        Empty initializer for now
        """
        pass

    def filterMatches(self,a_ratioThresh,matches):
        #-- Filter matches using the Lowe's ratio test
        # Changing the ratio_thresh variable allows more/fewer matches
        good_matches = []

        #-- Loop through matches and only allow those that meet the threshold
        # append those values to good_matches array
        for m,n in matches:
            if m.distance < a_ratioThresh * n.distance:
                good_matches.append(m)
        return good_matches

    def findSimilarities(self,a_imgPath1, a_imgPath2, a_outPathMatches,a_outPathOriginal,
                         a_outPathNew, a_outPathBoxes, a_minHessian = 200, a_ratioThresh = 0.6):
        """
        Function using feature detection to find similarities between images
        :param a_imgPath1: path to first image
        :param a_imgPath2: path to second image
        :param a_ratioThresh: threshold for matching key features. 0-1. The closer to 1, the more features
            will be matched. The closer to 0, the fewer
        """

        #-- Step 0: Read images; convert to grayscale
        img1 = cv.imread(a_imgPath1)
        # img1= cv.cvtColor(img1,cv.COLOR_BGR2GRAY)

        img2 = cv.imread(a_imgPath2)
        # img2= cv.cvtColor(img2,cv.COLOR_BGR2GRAY)


        #-- Step 1: Detect the keypoints using SIFT Detector, compute the descriptors
        detector = cv.xfeatures2d_SIFT.create()
        keypoints1, descriptors1 = detector.detectAndCompute(img1, None)
        keypoints2, descriptors2 = detector.detectAndCompute(img2, None)


        #-- Match descriptor vectors with a FLANN based matcher
        #currently configured to work best with SURF but also works well with SIFT
        matcher = cv.DescriptorMatcher_create(cv.DescriptorMatcher_FLANNBASED)
        matches = matcher.knnMatch(descriptors1, descriptors2, 2)

        good_matches = self.filterMatches(a_ratioThresh,matches)


        # Keep only key points that were matched
        kp1Matched = [keypoints1[m.queryIdx] for m in good_matches]
        kp2Matched = [keypoints2[m.trainIdx] for m in good_matches]

        #-- Draw matches
        img_matches = np.empty((max(img1.shape[0], img2.shape[0]), img1.shape[1]+img2.shape[1], 3), dtype=np.uint8)
        cv.drawMatches(img1, keypoints1, img2, keypoints2, good_matches, img_matches, flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        # matchOriginal = cv.drawKeypoints(img1,kp1Matched,None,(255,0,0),4)
        # matchTrain = cv.drawKeypoints(img2,kp2Matched,None,(255,0,0),4)

        # Draw boxes around key matches
        bd = BoxDrawer(kp1Matched,30,img1,(51,255,255),2)
        img1 = bd.img
        bd = BoxDrawer(kp2Matched,30,img2,(51,255,255),2)
        img2 = bd.img

        combinedimg = np.empty((max(img1.shape[0], img2.shape[0]), img1.shape[1]+img2.shape[1], 3), dtype=np.uint8)

        # write out images
        cv.imwrite(a_outPathMatches, img_matches)
        cv.imwrite(a_outPathOriginal,img1)
        cv.imwrite(a_outPathNew, img2)
        cv.imwrite(a_outPathBoxes, combinedimg)


if __name__ == "__main__":

    # # Paths for images to be compared
    imgPath1 = "images/test_images/figure1/cells2.1.png"
    imgPath2 = "images/test_images/figure1/cells2.2.png"
    
    # outputPaths
    outPathMatches = 'images/ike_ans/sift2.1map.jpg'
    outPathOriginal = 'images/ike_ans/sift2.2orig.jpg'
    outPathNew = 'images/ike_ans/sift2.2new.jpg'
    outPathBoxes = 'images/ike_ans/sift2.2boxes.jpg'

    # Create instance of class
    simDet = SimilarityDetector()

    # Show similarities
    simDet.findSimilarities(imgPath1, imgPath2,outPathMatches,outPathOriginal,outPathNew,outPathBoxes)

