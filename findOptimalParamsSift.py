from scipy.optimize import minimize, dual_annealing
import random
import numpy as np
import json
import glob
import sys
from findSimilaritiesInImages import FindSimilarities
import cv2 as cv
from cost import Cost
import time
import multiprocess
import os
from tqdm import tqdm

class OptimizeParams:

    def __init__(self, filePath, testPath):
        self.listOfFiles = glob.glob(filePath+"*")
        self.testFiles = glob.glob(testPath+"*")
        self.listOfFiles.sort()
        self.testFiles.sort()
        self.setBounds()
        self.cst = Cost()
        self.optimizing=False

    def setBounds(self):
        self.setBoundsSurf()
        self.setBoundsSift()
        self.setBoundsOrb()

    def getRandomSubset(self,n=10):
        if n >= len(self.listOfFiles) or n ==-1:
            return self.listOfFiles
        subset = random.sample(self.listOfFiles, n)
        return subset

    def setBoundsSurf(self):
        self.surfBounds = [
            [200,700],[0.3,0.85],[1,15],[1,100],[3,15]
        ]
        self.surfBoundsStand = [[0,1],[0,1],[0,1],[0,1],[0,1]]
        self.bestGuessSurf = [400,0.7,1,40,8]
        self.bestGuessSurfStand = self.toStandard(self.bestGuessSurf, self.surfBounds)

    def setBoundsSift(self):
        self.siftBounds = [
            [0.3,0.85],[1,15],[1,100],[3,15]
        ]
        self.siftBoundsStandard = [[0,1],[0,1],[0,1],[0,1]]
        self.bestGuessSift = [0.7,1,40,8]

    def setBoundsOrb(self):
        self.orbBounds = [
            [100,10000],[0.3,0.85],[1,15],[1,100],[3,15]
        ]
        self.orbBoundsStand = [[0,1],[0,1],[0,1],[0,1],[0,1]]
        self.bestGuessOrb = [1000, 0.7,1,40,8]
        self.bestGuessOrbStand = self.toStandard(self.bestGuessOrb, self.orbBounds)

    def fillParamsDictSurf(self, params, img1outPath, img2outPath, jsonOutPath):
        return {
                "min_hess": int(round(params[0])),
                "lowes_ratio": params[1],
                "min_num_in_cluster_to_accept": int(round(params[2])),
                "cluster_gap": int(round(params[3])),
                "num_matches": int(round(params[4])),
                "b_w": 0,
                "outputPath1":img1outPath,
                "outputPath2": img2outPath,
                "outputFile": jsonOutPath,
                "color":[],
                "flann":{"default":True},
                "line_width":10
                }

    def fillParamsDictSift(self, params, img1outPath, img2outPath, jsonOutPath):
        return {
                "lowes_ratio": params[0],
                "min_num_in_cluster_to_accept": int(round(params[1])),
                "cluster_gap": int(round(params[2])),
                "num_matches": int(round(params[3])),
                "b_w":0,
                "outputPath1":img1outPath,
                "outputPath2": img2outPath,
                "outputFile": jsonOutPath,
                "color":[],
                "flann":{"default":True},
                "line_width":10
                }

    def fillParamsDictOrb(self, params, img1outPath, img2outPath, jsonOutPath):
        return {
                "num_features":int(round(params[0])),
                "lowes_ratio": params[1],
                "min_num_in_cluster_to_accept": int(round(params[2])),
                "cluster_gap": int(round(params[3])),
                "num_matches": int(round(params[4])),
                "b_w":0,
                "outputPath1":img1outPath,
                "outputPath2": img2outPath,
                "outputFile": jsonOutPath,
                "color":[],
                "flann":{"default":True},
                "line_width":10
                }

    def fillerCost(self,arr1,arr2):
        return len(arr1) - len(arr2)

    def findCostFromJson(self,jsonPathTrue,jsonPathPred, all=False):
        with open(jsonPathTrue, 'r') as fp:
            true = json.load(fp)
        with open(jsonPathPred, 'r') as fp:
            pred = json.load(fp)
        costArr = []
        for k,v in true.items():
            xas = self.cst.getCost(v,pred[k])
            if not all: costArr.append(xas[2])
            else: costArr.append(xas)
        if not all: return np.mean(costArr)
        else: return costArr

    def getPathsFromPair(self,pair):
        if pair[-1] !="/": pair+='/'
        # pair = 'image_datasets/training_set_edited/pair42/'
        truth = pair+"truth.jpg"
        edited = pair+"edited.jpg"
        json_in = pair+"correct.json"
        outPutTruth = pair+"truth_boxed.jpg"
        outPutEdited = pair+"edited_boxed.jpg"
        json_out = pair+"boxed.json"
        return [truth,edited,outPutTruth,outPutEdited,json_in,json_out]


    def callSingleMatch(self,pair):
        inPath1, inPath2, outPath1, outPath2, jsonPathTrue, jsonPathPred = self.getPathsFromPair(pair)
        paramDict = self.currentFunc(self.currentParams, outPath1,outPath2, jsonPathPred)
        self.performMatch(self.currentAlg,paramDict,inPath1,inPath2)
        if self.findAllCosts:
            return self.findCostFromJson(jsonPathTrue, jsonPathPred, all=True)
        return self.findCostFromJson(jsonPathTrue, jsonPathPred)

    def performMatch(self, algorithm, paramDict, inputPath1, inputPath2):
        cp = FindSimilarities(algorithm,paramDict,inputPath1,inputPath2)
        cp.readInImages()
        cp.findKeyPoints()
        cp.findMatches()
        cp.drawMatches()

    def optimizeSurf(self,params,n=50, test=False):
        print(params)
        st = time.time()
        self.currentParams = params
        self.currentAlg = "SURF"
        self.currentFunc = self.fillParamsDictSurf
        if not test:
            pairedFoulders = self.getRandomSubset(n)
            self.findAllCosts = False
        else:
            pairedFoulders = self.testFiles
            self.findAllCosts = True

        cost = [self.callSingleMatch(f) for f in pairedFoulders]
        # p = multiprocess.Pool()
        # cost = p.map(self.callSingleMatch, pairedFoulders)
        # p.close()
        # p.join()
        print(f"params used: {params}")
        print(f"Time for one itteration: {time.time()-st}")
        if not test: print(f"cost of this iteration: {np.mean(cost)}\n")
        else: print(f"cost of this iteration: {np.mean([np.mean([c[0][2], c[1][2]]) for c in cost])}\n")
        if not test:
            return np.mean(cost)
        return cost

    def optimizeSift(self,params,n=5, test=False):
        st = time.time()
        self.currentParams = params
        self.currentAlg = "SIFT"
        self.currentFunc = self.fillParamsDictSift
        if not test:
            pairedFoulders = self.getRandomSubset(n)
            self.findAllCosts = False
        else:
            pairedFoulders = self.testFiles
            self.findAllCosts = True
        
        p = multiprocess.Pool()
        cost = p.map(self.callSingleMatch, pairedFoulders)
        p.close()
        p.join()
        print(len(cost))
        print(f"params used: {params}")
        print(f"Time for one itteration: {time.time()-st}")
        if not test: print(f"cost of this iteration: {np.mean(cost)}\n")
        else: print(f"cost of this iteration: {np.mean([np.mean([c[0][2], c[1][2]]) for c in cost])}\n")
        if not test:
            return np.mean(cost)
        return cost

    def optimizeOrb(self,params,n=50, test=False):
        st = time.time()
        self.currentParams = params
        self.currentAlg = "ORB"
        self.currentFunc = self.fillParamsDictOrb
        if not test:
            pairedFoulders = self.getRandomSubset(n)
            self.findAllCosts = False
        else:
            pairedFoulders = self.testFiles
            self.findAllCosts = True
        p = multiprocess.Pool()
        cost = p.map(self.callSingleMatch, pairedFoulders)
        p.close()
        p.join()
        print(f"params used: {params}")
        print(f"Time for one itteration: {time.time()-st}")
        if not test: print(f"cost of this iteration: {np.mean(cost)}\n")
        else: print(f"cost of this iteration: {np.mean([np.mean([c[0][2], c[1][2]]) for c in cost])}\n")
        if not test:
            return np.mean(cost)
        return cost

    def optimizeAFunction(self, func, bestGuess, bounds):
        st = time.time()
        res = dual_annealing(func, bounds, maxiter=5)
        print(res)
        print(f"Total Time Elapsed: {time.time()-st}")
        return res.x

    def fromStandard(self, params, bounds):
        toReturn = []
        for p, b in zip(params, bounds):
            temp = ((b[1]-b[0]) * p) + b[0]
            if b[0]%1 == 0:
                temp = round(temp)
            toReturn.append(temp)
        return toReturn

    def toStandard(self, params, bounds):
        toReturn = []
        for p,b in zip(params, bounds):
            temp = ((p - b[0]) / (b[1] - b[0]))
            toReturn.append(temp)
        return toReturn

    def minimizeAll(self):
        self.optimizing = True
        self.finalSiftParams = self.optimizeAFunction(self.optimizeSift, self.bestGuessSift, self.siftBounds)
        siftParams = list(self.finalSiftParams)
        d = {
            'sift':siftParams,
        }
        with open('finalParamsSift.json', 'w') as fp:
            json.dump(d, fp)
        res_sift = self.optimizeSift(siftParams,-1,test=True)
        d = {
            'siftRes': res_sift
        }

        with open('finalTestCostsSift.json','w') as fp:
            json.dump(d,fp)

if __name__ == "__main__":
    # op = OptimizeParams('image_datasets_random/train/', 'image_datasets_random/test/')
    op = OptimizeParams('/fslhome/itaylor3/BIO465/Image_Processing/image_datasets_random/train/', '/fslhome/itaylor3/BIO465/Image_Processing/image_datasets_random/test/')
    op.minimizeAll()
