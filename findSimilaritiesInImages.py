import cv2 as cv
import sys
import numpy as np
from boxDrawer_version2 import BoxDrawer
import json
from pprint import pprint
import random
from template import TemplateMatch
from writeDefaultJson import WriteDefaultJson


class FindSimilarities:

    def __init__(self, algorithm, dictValues, inputPath1, inputpath2):
        """
        Initializer function
        :param algorithm: name of algorithm to be used (surf, sift, orb, template)
        :param dictValues: parameters needed to run that algorithm (see writeDefaults.py)
        :param inputPath1: input image 1
        :param inputpath2: input image 2
        """
        self.algorithm = algorithm
        self.params = dictValues
        self.compareToSelf = False
        if inputPath1 == inputpath2:
            self.compareToSelf = True
        self.inputPath1 = inputPath1
        self.inputPath2 = inputpath2
        self.color = self.params["color"]
        self.boxes1 = []
        self.boxes2 = []

    def readInImages(self):
        """
        Function to read in images and save them as member variables
        :return: None
        """
        self.img1 = cv.imread(self.inputPath1)
        self.img2 = cv.imread(self.inputPath2)
        if self.params["b_w"]:
            self.img1 = cv.cvtColor(self.img1,cv.COLOR_BGR2GRAY)
            self.img2 = cv.cvtColor(self.img2,cv.COLOR_BGR2GRAY)

    def findSurfKP(self):
        """
        Function to find key features using surf
        :return: None
        """
        minHessian = self.params["min_hess"]
        detector = cv.xfeatures2d_SURF.create(hessianThreshold=minHessian)
        self.kp1, self.desc1 = detector.detectAndCompute(self.img1, None)
        self.kp2, self.desc2 = detector.detectAndCompute(self.img2, None)

    def findSiftKP(self):
        """
        Function to find key features using sift
        :return: None
        """
        detector = cv.xfeatures2d_SIFT.create()
        self.kp1, self.desc1 = detector.detectAndCompute(self.img1, None)
        self.kp2, self.desc2 = detector.detectAndCompute(self.img2, None)

    def findOrbKP(self):
        """
        Function to find key features using orb
        :return: None
        """
        numFeatures = self.params["num_features"]
        detector = cv.ORB_create(nfeatures=numFeatures)
        self.kp1, self.desc1 = detector.detectAndCompute(self.img1, None)
        self.kp2, self.desc2 = detector.detectAndCompute(self.img2, None)
        self.desc1 = np.float32(self.desc1)
        self.desc2 = np.float32(self.desc2)

    def performTemplate(self):
        """
        Function to perform template matching. If algorithm is template, this
            is the only function that need be run.
        :return: None
        """
        stepSize = self.params["step_size"]
        winSize = self.params["win_size"]
        threshold = self.params["cor_thresh"]
        pathOut = self.params["outputPath1"]
        pathOut2 = self.params["outputPath2"]
        tm = TemplateMatch(self.inputPath1,self.inputPath2,stepSize,winSize,threshold,pathOut,pathOut2,outputJsonFile=self.params["outputFile"], color = self.color, lineWidth=self.params["line_width"])
        tm.findAndDrawMatches()

    def findKeyPoints(self):
        """
        Function to find key points based on algorithm specified
        :return:
        """
        if self.algorithm == "surf":
            self.findSurfKP()
        elif self.algorithm == "sift":
            self.findSiftKP()
        elif self.algorithm == "orb":
            self.findOrbKP()
        elif self.algorithm == "template":
            self.performTemplate()

    def findMatches(self):
        """
        Function to find matches in key points using flann. Based on params passed in
            either defaults will be used or params saved in self.params
        :return:
        """
        if self.algorithm=="template":return
        if self.params["flann"]["default"]:
            matcher = cv.DescriptorMatcher_create(cv.DescriptorMatcher_FLANNBASED)
        else:
            FLANN_INDEX_KDTREE = self.params["flann"]["flann_index_kdtree"]
            numTrees = self.params["flann"]["num_trees"]
            numChecks = self.params["flann"]["num_checks"]
            index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = numTrees)
            search_params = dict(checks = numChecks)
            matcher = cv.FlannBasedMatcher(index_params, search_params)

        matches1 = matcher.knnMatch(self.desc1, self.desc2, self.params["num_matches"])
        trainMatches1, testMatches1,dictMatches1 = self.makeArrayOfMatches(matches1,self.kp1,self.kp2)

        # # -- below is an idea for how to know which image has one copy of thing and which has multiple.
        # # -- Doesn't work.
        # matches2 = matcher.knnMatch(self.desc2, self.desc1, self.params["num_matches"])
        # trainMatches2, testMatches2,dictMatches2 = self.makeArrayOfMatches(matches2,self.kp2,self.kp1)
        # print(sum([len(v) for k,v in dictMatches1.items() if len(v)!=1]))
        # print(sum([len(v) for k,v in dictMatches2.items() if len(v)!=1]))
        # if len(testMatches2) > len(testMatches1):
        #     print("Switching")
        #     self.matches = matches2
        #     trainMatches = trainMatches2
        #     testMatches = testMatches2
        #     img1,img2 = self.img1, self.img2
        #     self.img1, self.img2 = img2,img1
        #     kp1,desc1,kp2,desc2 = self.kp1,self.desc1,self.kp2,self.desc2
        #     self.kp1,self.desc1,self.kp2,self.desc2 = kp2, desc2, kp1, desc1
        #     self.dictMatches = dictMatches2
        # else:
        self.matches = matches1
        trainMatches = trainMatches1
        testMatches = testMatches1
        self.dictMatches = dictMatches1

        self.kp1_matched = np.take(self.kp1,trainMatches)
        self.kp2_matched = np.take(self.kp2,testMatches)

    def addToDict(self,d1,d2):
        """
        Function to add matches from temp dict to permanent dict
        :param d1: temp dict
        :param d2: permanent dict
        :return: updated permanent dict
        """
        for k,v in d1.items():
            if k not in d2:
                d2[k] = v
            else:
                d2[k] = d2[k] + v
        return d2


    def find_x_y_min_max(self,clust):
        sx = sorted(clust, key=lambda x: x[0])
        sy = sorted(clust, key=lambda x: x[1])

        minX = int(sx[0][0])
        maxX = int(sx[-1][0])
        minY = int(sy[0][1])
        maxY = int(sy[-1][1])
        return [[minX,minY], [maxX,maxY]]

    def addBounds(self, clust1,clust2):
        self.boxes1.append(self.find_x_y_min_max(clust1))
        for clust in clust2:
            self.boxes2.append(self.find_x_y_min_max(clust))

    def makeArrayOfMatches(self,matches,kp1,kp2):
        """
        Make arrays of all matched indeces in both images
        :param matches: list of matches
        :param kp1: key points in first image
        :param kp2: key points in second image
        :return: index of matches in training image and test image, dict of all matched key points
        """
        if self.algorithm=="template":return
        q_good_matches = []
        t_good_matches = []
        dictOfMatches = {}
        for match in matches:
            q_temp_matches = []
            t_temp_matches = []
            tempDict = {}
            for i in range(len(match)-1):
                if self.compareToSelf:
                    if kp1[match[i].queryIdx].pt == kp2[match[i].trainIdx].pt:
                        continue
                if match[i].distance < self.params["lowes_ratio"]*match[i+1].distance:
                    q_temp_matches.append(match[i].queryIdx)
                    t_temp_matches.append(match[i].trainIdx)
                    if kp1[match[i].queryIdx] not in tempDict:
                        tempDict[kp1[match[i].queryIdx]] = []
                    tempDict[kp1[match[i].queryIdx]].append(kp2[match[i].trainIdx])
                    dictOfMatches = self.addToDict(tempDict,dictOfMatches)
                    q_good_matches = q_good_matches + q_temp_matches
                    t_good_matches = t_good_matches + t_temp_matches
                    break
                else:
                    if kp1[match[i].queryIdx] not in tempDict:
                        tempDict[kp1[match[i].queryIdx]] = []
                    tempDict[kp1[match[i].queryIdx]].append(kp2[match[i].trainIdx])
                    q_temp_matches.append(match[i].queryIdx)
                    t_temp_matches.append(match[i].trainIdx)
        return q_good_matches, t_good_matches, dictOfMatches
    
    def getClusters(self):
        if self.algorithm=="template":return 0
        bd = BoxDrawer(self.params["cluster_gap"],self.img1,(0,0,0),self.params["line_width"],self.params["min_num_in_cluster_to_accept"])
        clusters1 = bd.get_x_y_and_index(self.kp1_matched)
        clusters1 = bd.findBoxes(clusters1)
        return len(clusters1)
    
    def drawMatches(self):
        """
        Function to draw matches onto images
        :return:
        """
        if self.algorithm=="template":return
        bd = BoxDrawer(self.params["cluster_gap"],self.img1,(0,0,0),self.params["line_width"],self.params["min_num_in_cluster_to_accept"])
        if self.compareToSelf:
            bd2 = BoxDrawer(self.params["cluster_gap"],self.img1,(0,0,0),self.params["line_width"],self.params["min_num_in_cluster_to_accept"])
        else:
            bd2 = BoxDrawer(self.params["cluster_gap"],self.img2,(0,0,0),self.params["line_width"],self.params["min_num_in_cluster_to_accept"])
        clusters1 = bd.get_x_y_and_index(self.kp1_matched)
        clusters1 = bd.findBoxes(clusters1)
        for clust in clusters1:
            clustFrom2 = []
            for val in clust:
                clustFrom2 = clustFrom2 + self.dictMatches[self.kp1_matched[val[2]]]

            clust2 = bd2.get_x_y_and_index(clustFrom2)
            clust2 = bd.findBoxes(clust2)
            self.addBounds(clust,clust2)
            if self.color == []: color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
            else: color = self.color
            bd.color = color
            bd2.color = color
            bd.drawBoxes([clust])
            bd2.drawBoxes(clust2)

        img1 = bd.img
        img2 = bd2.img

        # write out images
        cv.imwrite(self.params["outputPath1"],img1)
        cv.imwrite(self.params["outputPath2"], img2)
        d = {"img1": self.boxes1, "img2":self.boxes2}
        with open(self.params["outputFile"], 'w') as fp:
            json.dump(d, fp)


def writeDefaultJson(jsonPath):
    """
    Function to write default json file
    :param jsonPath: path to json file
    :return:
    """
    WriteDefaultJson(jsonPath)

def main(jsonPath):
    """
    Main function, calls class itteratively for all comparisons in json file
    :param jsonPath: path to json file
    :return:
    """
    writeDefaultJson(jsonPath)
    with open(jsonPath, 'r') as fp:
        data = json.load(fp)
    for key, dct in data.items():

        inputPath1 = dct["inputImg1"]
        inputPath2 = dct["inputImg2"]
        for k,v in dct["algorithms"].items():
            random.seed(0)
            algorithm = k
            params = v
            cp = FindSimilarities(algorithm,params,inputPath1,inputPath2)
            cp.readInImages()
            cp.findKeyPoints()
            cp.findMatches()
            len1 = cp.getClusters()
            
            cp2 = FindSimilarities(algorithm,params,inputPath2,inputPath1)
            cp2.readInImages()
            cp2.findKeyPoints()
            cp2.findMatches()
            len2 = cp2.getClusters()

            if len1 < len2:
                cp.drawMatches()
            else:
                cp2.drawMatches()

if __name__ == "__main__":
    jsonPath = "comparison.json"
    main(jsonPath)
