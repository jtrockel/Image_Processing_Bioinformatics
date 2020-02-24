import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
from boxDrawer import BoxDrawer
from tqdm import tqdm
import sys
import random

class TemplateMatch:

    def __init__(self,img1Path, img2Path,stepSize,winSize,threshold,pathOut,pathOut2,maxItter = 6, lineWidth = 3, color=[]):
        """

        :param img1Path:
        :param img2Path:
        :param stepSize:
        :param winSize:
        :param threshold:
        :param pathOut:
        :param pathOut2:
        :param maxItter:
        :param lineWidth:
        """
        self.threshold = threshold
        self.pathOut = pathOut
        self.pathOut2 = pathOut2
        self.img1 = cv.imread(img1Path)
        self.img1Gray = cv.cvtColor(self.img1, cv.COLOR_BGR2GRAY)
        self.img2 = cv.imread(img2Path)
        self.img2Gray = cv.cvtColor(self.img2, cv.COLOR_BGR2GRAY)
        self.stepSize = stepSize
        self.winSize = winSize
        self.arr = self.slidingWindow()
        self.shape1 = self.img1.shape
        self.shape2 = self.img2.shape
        self.maxItter = maxItter
        self.lineWidth = lineWidth
        self.color = color

    def slidingWindow(self):
        """

        :return:
        """
        # slide a window across the image
        arr = []
        print("sliding window")
        for y in tqdm(range(0, self.img1Gray.shape[0], self.stepSize)):
            for x in range(0, self.img1Gray.shape[1], self.stepSize):
                # yield the current window
                arr.append([x, y, self.img1Gray[y:y + self.winSize[1], x:x + self.winSize[0]]])
        return arr

    def getAllxy(self,x,y,w,h,points):
        """

        :param x:
        :param y:
        :param w:
        :param h:
        :param points:
        :return:
        """
        for i in range(0,w,1):
            for j in range(0,h,1):
                points.append([x+i,y+j])
        return points

    def findMatches(self):
        """

        :return:
        """
        points = []
        pointsOriginal = []
        print("finding matches")
        imgToMatchWith = self.img2Gray
        j=0
        for el in tqdm(self.arr):
            template = el[2]
            w,h = template.shape[::-1]
            if w < .7*self.winSize[0] or h < .7*self.winSize[0]:continue
            imgToMatchWithSquares = imgToMatchWith
            maxVal=1
            i = 0
            while maxVal> self.threshold:
                i+=1
                res = cv.matchTemplate(imgToMatchWith,template,cv.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
                if max_val<=self.threshold:break
                points = self.getAllxy(max_loc[0],max_loc[1],w,h,points)
                pointsOriginal = self.getAllxy(el[0],el[1],w,h,pointsOriginal)

                # cv.rectangle(imgToMatchWithSquares, (max_loc[0], max_loc[1] + int(h/2)), (max_loc[0] + int(w/2), max_loc[1]), (0,0,255), -1)
                cv.rectangle(imgToMatchWithSquares, (max_loc[0], max_loc[1]), (max_loc[0] + w, max_loc[1] + h), (0,0,255), -1)
                if self.color == []: color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
                else: color = self.color
                cv.rectangle(self.img1, (el[0]-self.lineWidth, el[1]-self.lineWidth), (el[0] + w+self.lineWidth, el[1] + h+self.lineWidth), color, self.lineWidth)
                cv.rectangle(self.img2, (max_loc[0]-self.lineWidth, max_loc[1]-self.lineWidth), (max_loc[0] + w+self.lineWidth, max_loc[1] + h+self.lineWidth), color, self.lineWidth)
                if i >self.maxItter: break
                # cv.rectangle(self.img1,(el[0], el[1]), (el[0] + w, el[1] + h), (0,0,255), 2)
                # cv.imwrite(f"joshImages/test_{j}.jpg",self.img1)
                # j+=1
            # loc = np.where(res >=self.threshold)
            # for pt in zip(*loc[::-1]):
            #     x= pt[0]
            #     y = pt[1]
            #     points = self.getAllxy(x,y,w,h,points)
        return points,pointsOriginal

    def findAndDrawMatches(self):
        """

        :return:
        """
        points,pointsOriginal = self.findMatches()
        print("drawing boxes")

        # bd = BoxDrawer(pointsOriginal,100,self.img1,(0,255,0),5)
        # self.boxedImageOriginal = bd.img
        cv.imwrite(self.pathOut, self.img1)



        # bd = BoxDrawer(points, 100, self.img2,(0,255,0),5)
        # self.boxedImage = bd.img

        cv.imwrite(self.pathOut2, self.img2)




if __name__ == "__main__":
    img1Path = "joshImages/cells_19_3.png"
    img2Path = "joshImages/cells_19_4.png"
    stepSize = 4
    winSize = (50,50)
    threshold = 0.9
    pathOut = 'joshImages/cells_19_3_template.jpg'
    pathOut2 = 'joshImages/cells_19_4_template.jpg'
    tm = TemplateMatch(img1Path,img2Path,stepSize,winSize,threshold,pathOut,pathOut2)
    tm.findAndDrawMatches()

