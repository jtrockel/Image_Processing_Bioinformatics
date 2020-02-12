import cv2 as cv

class BoxDrawer:

    def __init__(self,kp,winSize,img,color, lineWidth):
        """
        Initializer function for box drawing class
        :param kp: array of key points from one of the images that have already been matched
        :param winSize: distance between points to call a new cluster of points a new cluster
        :param img: image being drawn on
        :param color: color of line in rgb for example (0,0,0)
        :param lineWidth: width of line to be drawn
        """
        self.kp = kp
        self.winSize = winSize
        self.img = img
        self.color = color
        self.lineWidth = lineWidth
        self.drawBoxes()

    def get_x_y_and_index(self):
        """
        Function that returns array of [x,y,i] where x is the x coordinate, y
            is the y coordinate and i is the index of point in keypoint array
        :return: array of [x,y,i] for all points in key points
        """
        arr = []
        for i in range(len(self.kp)):
            toApp = [self.kp[i].pt[0], self.kp[i].pt[1], i]
            arr.append(toApp)
        return arr

    def findBoxes(self):
        """
        Function to find clusters
        :return: return array of clusters
        """
        arr = self.get_x_y_and_index()
        points = self.partitionInADirection(arr,0,[])
        finalPoints = []
        for j in range(len(points)):
            p = points[j]
            finalPoints = self.partitionInADirection(p,1,finalPoints)

        return finalPoints

    def partitionInADirection(self,arr,indToSort,points):
        """
        Function to partition the points into clusters in a specific direction
        :param arr: array to be partitioned
        :param indToSort: index of which direction to partition in (x=0,y=1)
        :param points: array to be returned
        :return: return clustered points in direction indicated by indToSort
        """
        toApp = []
        srtd = sorted(arr, key=lambda x: x[indToSort])
        for i in range(1,len(srtd)):
            if srtd[i][indToSort] - srtd[i-1][indToSort] > self.winSize:
                points.append(toApp)
                toApp = []
            else:
                toApp.append(srtd[i-1])
        toApp.append(srtd[-1])
        points.append(toApp)

        return points


    def drawBoxes(self):
        """
        Function to draw boxes on self.img
        :return: None, updated image is stored in self.img
        """
        p = self.findBoxes()
        print(len(p))
        for points in p:
            xSorted = sorted(points, key=lambda x: x[0])
            ySorted = sorted(points, key=lambda x: x[1])
            x0 = xSorted[0][0]
            x1 = xSorted[-1][0]
            y0 = ySorted[0][1]
            y1 = ySorted[-1][1]
            cv.line(self.img, (int(x0), int(y0)), (int(x0), int(y1)), self.color,self.lineWidth)
            cv.line(self.img, (int(x1), int(y0)), (int(x1), int(y1)), self.color,self.lineWidth)
            cv.line(self.img, (int(x0), int(y0)), (int(x1), int(y0)), self.color,self.lineWidth)
            cv.line(self.img, (int(x0), int(y1)), (int(x1), int(y1)), self.color,self.lineWidth)
