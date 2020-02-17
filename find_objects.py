#TODO: in the lowe's test loop, iterate matches 'till i<7j, and include if dist = 0, remove  (likely means for same pic. to itself, always remove 1st match.

import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
import sys

from boxDrawer import BoxDrawer_version2

MIN_MATCH_PER_CLUMP = 10   #Number of matches that must be found to keep a match.  (to keep a clump of points, we want more than one feature to match, right?)
WINDOW_SIZE = 30   # how close matches need to be to each other to be considered part of a potential clump.
NUMBER_OF_CLUMPS = 10   #how many clumps we are hoping to find, e.g. this would find up to but no more than 9 matches from any one point.

imgPath1 = sys.argv[1]
imgPath2 = sys.argv[2]

#if I need to implement something different if they are the same; not being used right now
#sameImage = False
#if sys.argv[3] == "Y" or sys.argv[3] == "y":
#    sameImage = True

#TODO do the 0's make this B&W? is that bad?  should we do that to compare but print in color?
img1 = cv.imread(imgPath1) # queryImage
img2 = cv.imread(imgPath2) # trainImage
# Initiate SIFT detector
sift = cv.xfeatures2d.SIFT_create()

# find the keypoints and descriptors with SIFT
kp1, des1 = sift.detectAndCompute(img1,None)
kp2, des2 = sift.detectAndCompute(img2,None)

#print("first des1")


#iterate over pictures finding the next best clump until all clumps have been found:
all_clumps = []  #this will store key points of the query Image
foundClump = True  #this will run our loop
bd = BoxDrawer(WINDOW_SIZE,img1,(0,255,0),10)  #this will let us find, store, and draw clumps
    
    
    
#find matches with flann
FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks = 50)
flann = cv.FlannBasedMatcher(index_params, search_params)
matches = flann.knnMatch(des1,des2,k=NUMBER_OF_CLUMPS)
    #print(matches)


# store all the good matches as per Lowe's ratio test, store both for query and train images.
#TODO: store these matches in a way that groups test w/ query indices, then we can color code them.
q_good_matches = []
t_good_matches = []
for match in matches:
    q_temp_matches = []
    t_temp_matches = []
    for i in range(len(match)-1):
        if match[i].distance < 0.7*match[i+1].distance:
            q_good_matches = q_good_matches + q_temp_matches
            t_good_matches = t_good_matches + t_temp_matches
            break
        else:
            q_temp_matches.append(match[i].queryIdx)
            t_temp_matches.append(match[i].trainIdx)


            #np.delete(des1,m.queryIdx)
print(len(q_good_matches))  #I think if sys.argv[3] = y, run once with each picture as query and take the larger of len(q_good_matches  for each.

#keep only good points
kp1_temp = np.take(kp1,q_good_matches)
kp2_temp = np.take(kp2,t_good_matches)

#use the box class to turn good matches into clumps of matches rather than total matches so we can analyze them
modified_array = bd.get_x_y_and_index(kp1_temp)
curr_clumps = bd.findBoxes(modified_array)

#for each clump, we must decide if it is a valid object
for clump in curr_clumps:
    #remove key points in query image
    if len(clump) > MIN_MATCH_PER_CLUMP:
            all_clumps.append(clump)

#print(all_clumps)
#remove already-found matches
#des1 = np.delete(des1,matched_points_to_remove)
#kp1 = np.delete(kp1,matched_points_to_remove)
#print("des1:")
#   print(len(des1))
#   print("********************")

#TODO: reiterate through other image so we don't have to do this twice
#TODO: find a way to match clumps with traningimage clumps & group for box-drawing, color-coordinating purposes

#leftovers from a tutorial
'''if len(good)>MIN_MATCH_COUNT:
    src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
    dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
    M, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC,5.0)
    matchesMask = mask.ravel().tolist()
    h,w = img1.shape  #and ,d
    pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
    dst = cv.perspectiveTransform(pts,M)
    img2 = cv.polylines(img2,[np.int32(dst)],True,255,3, cv.LINE_AA)
    else:
    print( "Not enough matches are found - {}/{}".format(len(good), MIN_MATCH_COUNT) )
    matchesMask = None'''

'''draw_params = dict(matchColor = (0,255,0), # draw matches in green color
    singlePointColor = None,
    matchesMask = matchesMask, # draw only inliers
    flags = 2)
    img3 = cv.drawMatches(img1,kp1,img2,kp2,good,None,**draw_params)
    plt.imshow(img3, 'gray'),plt.show()'''


#prep boxes for img 1
bd.drawBoxes(all_clumps)
img1 = bd.img

#prep boxes for img 2
bd2 = BoxDrawer(WINDOW_SIZE,img2,(0,255,0),10)
clumps2 = bd2.findBoxes(bd2.get_x_y_and_index(kp2_temp))
bd2.drawBoxes(clumps2)
img2 = bd2.img

# write out images--ask Joshua abt these two lines?
#cv.imwrite(a_outPathMatches, img_matches)
#cv.imwrite(a_secondIterationOfMatchesImgPath, img_matches_2)


#TODO: add drawing images to screen
#TODO: make new names command line input
cv.imwrite(imgPath1[:-4] + "_v2_bw_query.jpg", img1)
cv.imwrite(imgPath2[:-4] + "_v2_bw_training.jpg", img2)

cv.waitKey(0)

#for clump in all_clumps:
# Draw boxes around key matches

