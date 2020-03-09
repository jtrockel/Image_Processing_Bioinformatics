import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
from boxDrawer import BoxDrawer
from tqdm import tqdm
import sys
import random
import json
import multiprocess

class TemplateMatch:

    def __init__(self,img1Path, img2Path,stepSize,winSize,threshold,pathOut,pathOut2,outputJsonFile,maxItter = 6, lineWidth = 3, color=[],backgroundColor=[],parallel=False):
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
        self.boxes1 = []
        self.boxes2 = []
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
        self.backgroundColor = backgroundColor
        self.outputJsonFile = outputJsonFile
        self.parallel = parallel
        if img1Path == img2Path:
            self.compareToSelf = True
        else:
            self.compareToSelf = False

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

    def findMatchesWithSelf(self):
        print("finding with self matches")
        imgToMatchWith = self.img2Gray
        for el in tqdm(self.arr):
            template = el[2]
            w,h = template.shape[::-1]
            if self.backgroundColor!=[]: blank_image = self.backgroundColor[0] *np.ones([h*2,w*2], np.uint8)
            cv.rectangle(imgToMatchWith, (el[0], el[1]), (el[0] + w, el[1] + h), (0,0,255), -1)
            if w < .7*self.winSize[0] or h < .7*self.winSize[0]:continue
            imgToMatchWithSquares = imgToMatchWith
            maxVal = 1
            i = 0
            while maxVal> self.threshold:
                if self.backgroundColor!=[]:
                    if sum([1 for x in template.flatten() if x == 255])/ len(template.flatten()) > 0.4:
                        break
                i += 1
                res = cv.matchTemplate(imgToMatchWith,template,cv.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)


                if max_val<=self.threshold:break
                if self.backgroundColor!=[]:
                    crop_img = imgToMatchWith[max_loc[1]:max_loc[0]+h, max_loc[0]:max_loc[0]+w]
                    if sum([1 for x in crop_img.flatten() if x == 255])/ len(crop_img.flatten()) > 0.4:
                        break
                cv.rectangle(imgToMatchWithSquares, (max_loc[0], max_loc[1]), (max_loc[0] + w, max_loc[1] + h), (0,0,255), -1)
                if self.color == []:
                    color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
                else:
                    color = self.color
                cv.rectangle(self.img2, (el[0]-self.lineWidth, el[1]-self.lineWidth), (el[0] + w+self.lineWidth, el[1] + h+self.lineWidth), color, self.lineWidth)
                cv.rectangle(self.img2, (max_loc[0]-self.lineWidth, max_loc[1]-self.lineWidth), (max_loc[0] + w+self.lineWidth, max_loc[1] + h+self.lineWidth), color, self.lineWidth)
                if i >self.maxItter: break


    def findMatchesSingle(self, i):
        imgToMatchWith = self.img2Gray
        template = self.arr[i][2]
        w,h = template.shape[::-1]
        if w < .7*self.winSize[0] or h < .7*self.winSize[0]:return [[],[]]
        imgToMatchWithSquares = imgToMatchWith
        maxVal = 1
        j = 0
        boxes1 = []
        boxes2 = []
        while maxVal> self.threshold:
            j += 1
            res = cv.matchTemplate(imgToMatchWith,template,cv.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
            if max_val<=self.threshold:break
            cv.rectangle(imgToMatchWithSquares, (max_loc[0], max_loc[1]), (max_loc[0] + w, max_loc[1] + h), (0,0,255), -1)
            boxes1.append([[self.arr[i][0],self.arr[i][1]],[self.arr[i][0]+w,self.arr[i][1]+h]])
            boxes2.append([[max_loc[0],max_loc[1]],[max_loc[0]+w,max_loc[1]+h]])
            if j >self.maxItter: break
        return [boxes1, boxes2]


    def findMatchesParallel(self):
        p = multiprocess.Pool(multiprocess.cpu_count() -1)
        boxes = p.map(self.findMatchesSingle, range(len(self.arr)))
        p.close()
        p.join()
        for pair in boxes:
            if pair[0]==[] or pair[1] ==[]: continue
            one = pair[0][0]
            two = pair[1][0]
            self.boxes1.append(one)
            self.boxes2.append(two)
            if self.color == []:
                color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
            else:
                color = self.color
            cv.rectangle(self.img1, (one[0][0]-self.lineWidth, one[0][1]-self.lineWidth), (one[1][0] +self.lineWidth, one[1][1] +self.lineWidth), color, self.lineWidth)
            cv.rectangle(self.img2, (two[0][0]-self.lineWidth, two[0][1]-self.lineWidth), (two[1][0] +self.lineWidth, two[1][1] +self.lineWidth), color, self.lineWidth)



    def findMatches(self):
        """

        :return:
        """
        print("finding matches between images")
        imgToMatchWith = self.img2Gray
        for el in tqdm(self.arr):
            template = el[2]
            w,h = template.shape[::-1]
            if w < .7*self.winSize[0] or h < .7*self.winSize[0]:continue
            imgToMatchWithSquares = imgToMatchWith
            maxVal = 1
            i = 0
            while maxVal> self.threshold:
                i += 1
                res = cv.matchTemplate(imgToMatchWith,template,cv.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
                if max_val<=self.threshold:break
                cv.rectangle(imgToMatchWithSquares, (max_loc[0], max_loc[1]), (max_loc[0] + w, max_loc[1] + h), (0,0,255), -1)
                if self.color == []:
                    color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
                else:
                    color = self.color
                self.boxes1.append([[el[0],el[1]],[el[0]+w,el[1]+h]])
                self.boxes2.append([[max_loc[0],max_loc[1]],[max_loc[0]+w,max_loc[1]+h]])
                cv.rectangle(self.img1, (el[0]-self.lineWidth, el[1]-self.lineWidth), (el[0] + w+self.lineWidth, el[1] + h+self.lineWidth), color, self.lineWidth)
                cv.rectangle(self.img2, (max_loc[0]-self.lineWidth, max_loc[1]-self.lineWidth), (max_loc[0] + w+self.lineWidth, max_loc[1] + h+self.lineWidth), color, self.lineWidth)
                if i >self.maxItter: break

    def findAndDrawMatches(self):
        """

        :return:
        """

        print("drawing boxes")
        if self.compareToSelf:
            self.findMatchesWithSelf()
            cv.imwrite(self.pathOut, self.img1)
            cv.imwrite(self.pathOut2, self.img2)
        else:
            if self.parallel: self.findMatchesParallel()
            else: self.findMatches()
            cv.imwrite(self.pathOut, self.img1)
            cv.imwrite(self.pathOut2, self.img2)

        d = {"img1": self.boxes1, "img2":self.boxes2}
        with open(self.outputJsonFile, 'w') as fp:
            json.dump(d, fp)



def hconcat_resize_min(im_list, interpolation=cv.INTER_CUBIC):
    w_min = min(im.shape[1] for im in im_list)
    im_list_resize = [cv.resize(im, (w_min, int(im.shape[0] * w_min / im.shape[1])), interpolation=interpolation)
        for im in im_list]
    return cv.hconcat(im_list_resize)


if __name__ == "__main__":

    img1Path = "figure_1_input/cells_2_1.png"
    img2Path = "figure_1_input/cells_2_2.png"
    stepSize = 20
    winSize = (100,100)
    threshold = 0.7
    pathOut = 'joshImages/cells_2_1_template.jpg'
    pathOut2 = 'joshImages/cells_2_2_template.jpg'
    tm = TemplateMatch(img1Path,img2Path,stepSize,winSize,threshold,pathOut,pathOut2, outputJsonFile='joshImages/cells_2_template.json' )
    tm.findAndDrawMatches()

