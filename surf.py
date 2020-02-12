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
                         a_outPathNew, a_minHessian = 400, a_ratioThresh = 0.2):
        """
        Function using feature detection to find similarities between images
        :param a_imgPath1: path to first image
        :param a_imgPath2: path to second image
        :param a_minHessian: threshold for feature detection; the higher this value the fewer
            features will be detected. 300-500 is a good range
        :param a_ratioThresh: threshold for matching key features. 0-1. The closer to 1, the more features
            will be matched. The closer to 0, the fewer
        """

        #-- Stop 0: Read images; convert to grayscale
        img1 = cv.imread(a_imgPath1)
        # img1= cv.cvtColor(img1,cv.COLOR_BGR2GRAY)

        img2 = cv.imread(a_imgPath2)
        # img2= cv.cvtColor(img2,cv.COLOR_BGR2GRAY)


        #-- Step 1: Detect the keypoints using SURF Detector, compute the descriptors
        # minHessian is a threshold for the features detected; increasing this value
        # allows fewer features. 300-500 is a good default but feel free to play around with it
        minHessian = a_minHessian
        detector = cv.xfeatures2d_SURF.create(hessianThreshold=minHessian)
        keypoints1, descriptors1 = detector.detectAndCompute(img1, None)
        keypoints2, descriptors2 = detector.detectAndCompute(img2, None)


        #-- Match descriptor vectors with a FLANN based matcher
        # Since SURF is a floating-point descriptor NORM_L2 is used
        # Finds matches between key points in two images
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
        bd = BoxDrawer(kp1Matched,30,img1,(0,0,0),10)
        img1 = bd.img
        bd = BoxDrawer(kp2Matched,30,img2,(0,0,0),10)
        img2 = bd.img

        # write out images
        cv.imwrite(a_outPathMatches, img_matches)
        cv.imwrite(a_outPathOriginal,img1)
        cv.imwrite(a_outPathNew, img2)


if __name__ == "__main__":

    # Paths for images to be compared
    imgPath1 = "images/original_golden_bridge.jpg"
    imgPath2 = "images/copy_paste.jpg"

    #outputPaths
    outPathMatches = 'images/mappedMatches.jpg'
    outPathOriginal = 'images/matchesOnOriginal.jpg'
    outPathNew = 'images/matchesOnNew.jpg'

    # Create instance of class
    simDet = SimilarityDetector()

    # Show similarities
    simDet.findSimilarities(imgPath1, imgPath2,outPathMatches,outPathOriginal,outPathNew)

