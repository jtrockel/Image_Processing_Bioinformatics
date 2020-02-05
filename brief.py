import cv2 as cv
import numpy as np
#import contrib

"""
    Hannah's urls:
    
    https://answers.opencv.org/question/11209/unsupported-format-or-combination-of-formats-in-buildindex-using-flann-algorithm/
    https://docs.opencv.org/master/dc/d7d/tutorial_py_brief.html
    https://www.programcreek.com/python/example/89440/cv2.FlannBasedMatcher
    
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

    def findSimilarities(self,a_imgPath1, a_imgPath2, a_minHessian = 400, a_ratioThresh = 0.5):
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

        # Initiate FAST detector
        star = cv.xfeatures2d.StarDetector_create()
        # Initiate BRIEF extractor
        brief = cv.xfeatures2d.BriefDescriptorExtractor_create()

        # find the keypoints with STAR
        kp1 = star.detect(img1,None)
        kp2 = star.detect(img2,None)

        # compute the descriptors with BRIEF
        keypoints1, descriptors1 = brief.compute(img1, kp1)
        keypoints2, descriptors2 = brief.compute(img2, kp2)
        
        if len(descriptors1)==0:
            cvError(0,"MatchFinder","1st descriptor empty",__FILE__,__LINE__);
        if len(descriptors2)==0:
            cvError(0,"MatchFinder","2nd descriptor empty",__FILE__,__LINE__);

        #keypoints1, descriptors1 = detector.detectAndCompute(img1, None)
        #keypoints2, descriptors2 = detector.detectAndCompute(img2, None)

#creates floats from binaries so standard FLANN can process them, if using  cv.NORM_HAMMING  or cv.DescriptorMatcher_FLANNBASED
#descriptors2 = np.float32(descriptors2)
#descriptors1 = np.float32(descriptors1)

        # If you want to visualize what is being done in finding keypoints, uncomment the lines below

        """
        kp1Image = cv.drawKeypoints(img1,keypoints1, img1)
        cv.imshow('showKeypoints',cv.resize(kp1Image,None, fx=0.3,fy=0.3))
        cv.waitKey()

        kp2Image = cv.drawKeypoints(img2,keypoints2, img2)
        cv.imshow('showKeypoints2',cv.resize(kp2Image, None, fx=0.3, fy=0.3))
        cv.waitKey()
        """

        #-- Match descriptor vectors with a FLANN based matcher
        # Since SURF is a floating-point descriptor NORM_L2 is used
        # Finds matches between key points in two images

#FlannBasedMatcher matcher(new flann::LshIndexParams(20, 10, 2));

        #norm_hashing makes a brute force matcher  or use cv.DescriptorMatcher_FLANNBASED   for FLANN
#matcher = cv.DescriptorMatcher_create(cv.NORM_HAMMING)  #


#or use the following three lines instead
        index_params = dict(
                    algorithm = 6,
                    table_number = 12,
                    key_size = 20,
                    multi_probe_level = 2)
        search_params = dict(checks = 600)
        matcher = cv.FlannBasedMatcher(index_params, search_params)
        
        
        matches = matcher.knnMatch(descriptors1, descriptors2, 2)

        #-- Filter matches using the Lowe's ratio test
        # Changing the ratio_thresh variable allows more/fewer matches
        ratio_thresh = a_ratioThresh
        good_matches = []

        #-- Loop through matches and only allow those that meet the threshold
        # append those values to good_matches array
        for m,n in matches:
            if m.distance < ratio_thresh * n.distance:
                good_matches.append(m)

        #-- Draw matches
        # removing the flags on line 96 will allow you to once again see all the features in both images
        img_matches = np.empty((max(img1.shape[0], img2.shape[0]), img1.shape[1]+img2.shape[1], 3), dtype=np.uint8)
        cv.drawMatches(img1, keypoints1, img2, keypoints2, good_matches, img_matches, flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

        #-- Show detected matches
        # I've resized the image so that it's easier to see
        print("Number of good matches:" + str(len(good_matches)))
        cv.imshow('Good Matches', cv.resize(img_matches,None, fx=0.3,fy=0.3))

        cv.waitKey(0)


if __name__ == "__main__":

    # Paths for images to be compared
    imgPath1 = "original_golden_bridge.jpg"
    imgPath2 = "copy_paste.jpg"

    # Create instance of class
    simDet = SimilarityDetector()

    # Show similarities
    simDet.findSimilarities(imgPath1, imgPath2)
