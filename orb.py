import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

img = cv.imread('images\\rotated.jpg', 0)
img2 = cv.imread('images\\original_golden_bridge.jpg', 0)

# Initiate ORB detector
orb = cv.ORB_create(nfeatures=1000)

# find the keypoints with ORB
kp1, des1 = orb.detectAndCompute(img, None)
kp2, des2 = orb.detectAndCompute(img2, None)

#kp = orb.detect(img, None)

# compute the descriptors with ORB
#kp, des = orb.compute(img, kp)

# draw only keypoints location,not size and orientation
#img3 = cv.drawKeypoints(img, kp1, None, color=(0,255,0), flags=0)
#plt.imshow(img2), plt.show()

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

plt.imshow(img3,),plt.show()

