import copy

class Cost:

#TODO: be able to handle any x,y ordering rather than just [x1,y2],[x2,y1] and [x1,y1],[x2,y2]
	def getCost(self, answer, guess):
		"""
		Function to quickly calculate both total pixel errors and binary errors.
		"""
		self.validateInput(answer)
		self.validateInput(guess)
		
		binaryResults = self.getBinaryCost(answer, guess)
		pixelResults = self.getPixelCost(answer, guess)

		return pixelResults + binaryResults


	def getPixelCost(self, answer, guess):
		"""
		Function for calculating overlap and non-overlap between two sets of boxes on a grid
		:param x: size of grid in x direction
		:param y: size of grid in y direction
		:param answer: Array of points in the form [[x1,y2],[x2,y1]] where x1 < x2 and y1 < y2, e.g.  [  [[0,3],[3,2]],   [[1,4],[2,1]]   ]
		:param guess: 3d array of points in the same format as param answer.
		:return percent_true_lost: the percentage of the grid covered by the answer boxes and not covered by the guess boxes (A complement B)
		:return percent_false_gained: the percentage of the grid covered by the guess boxes not covered by the answer boxes (B complement A)
		:return cost: the total percentage of the grid covered by answer or guess boxes but not by both (percent_true_lost + percent_false_gained) (A complement B + B complement A)
		:return percent_overlap: the percentage of the grid covered by both answer and guess boxes but not covered by one alone  (A intersect B)
		"""
		#clean answer boxes
		answer_area = 0
		if len(answer) > 0:
			answer, a_overlap = self.removeOverlap(answer, [])
			answer_area = self.getTotalArea(answer)

		#clean guess boxes
		guess_area = 0
		if len(guess) > 0:
			guess, g_overlap = self.removeOverlap(guess, [])
			guess_area = self.getTotalArea(guess)

		#find overlap between answer and guess boxes
		t, overlap_boxes = self.removeOverlap(answer, guess)
		overlap_area = self.getTotalArea(overlap_boxes)

		#calculate return values
		percent_true_lost = ( answer_area - overlap_area ) / answer_area * 100
		percent_false_gained = ( guess_area - overlap_area ) / answer_area * 100
		cost = percent_true_lost + percent_false_gained
		percent_overlap = overlap_area/answer_area * 100

		return [percent_true_lost, percent_false_gained, cost, percent_overlap]


	def getBinaryCost(self, answer, guess):
		"""Function for counting how many boxes we found (even if the areas aren't exactly the same)
		and how many boxes we made that do not overlap at all with an answer box.
		:param answer: same as getCost
		:param guess: same as getCost
		:return percent_ans_correct: the percent of answer boxes for which we found at least a partial match
		:return percent_guess_wrong: the percent of guess boxes which did not hit any part of an answer box
		"""

		ans_dict = {}
		guess_dict = {}
		if len(guess) == 0:
			return[0.0,0.0]
		if len(answer) == 0:
			return[0.0, 100.0]

		#This loop marks which answer boxes and guess boxes overlap
		for i, box in enumerate(answer):
			for j, box2 in enumerate(guess):
				arr = self.getOverlapPositions(box, box2)
				if arr[4] != -1:
					ans_dict[i] = 1
					guess_dict[j] = 1

		ans_total = float(sum(ans_dict.values()))
		guess_total = float(sum(guess_dict.values()))


		percent_ans_correct = ans_total/len(answer) * 100
		percent_guess_wrong = (1 - guess_total/len(guess)) * 100

		return[percent_ans_correct, percent_guess_wrong]


        
	def validateInput(self, array):
		for box in array:
			if len(box) != 2:
				print("error: bad box format: more or less than 2 points per box")
				sys.exit()
			if box[0][0] < box[1][0] and box[0][1] < box[1][1]:
				box[0][1], box[1][1] = box[1][1], box[0][1]
			elif box[0][0] > box[1][0] or box[0][1] < box[1][1]:
				print("error: bad box format: x and y coordinates not in right order: " \
					   "should be either [[x1,y2],[x2,y1]] or [[x1,y1],[x2,y2]] where x1 < x2 and y1 < y2")
				sys.exit()

	def getTotalArea(self, a):
		"""
		Function for finding the total area of a grid covered by a list of boxes
		:param a: Array of points in the form [[x1,y2],[x2,y1]] where x1 < x2 and y1 < y2
		:return: area of grid covered by array of points a.
        Note that if the boxes overlap, the overlapped area will be counted twice.
		"""
		area = 0
		for box in a:
			area += self.getBoxArea(box)
		return area
	
	def getBoxArea(self, box):
		"""
		Function for finding the area of a box
		:param box: a point of the form [[x1,y2],[x2,y1]] where x1 < x2 and y1 < y2
		:return: the area of the box
		"""
		dx = box[1][0] - box[0][0]
		dy = box[0][1] - box[1][1]
		return dx*dy

	def removeOverlap(self, a, temp):
		"""
		Function for taking one set or two sets of boxes on a grid and reducing it (or them) to a new set of boxes that cover the same
		area but do not overlap, plus a list of boxes covering the overlap regions removed.  If two lists are provided,
		neither individual list can contain overlapping regions, but boxes from one list may overlap with boxes from the other list.
		:param a: Array of points in the form [[x1,y2],[x2,y1]] where x1 < x2 and y1 < y2  (in other words, the bottom left and upper right corners)
		:param temp: Either an empty list [] or an array of points in the form [[x1,y2],[x2,y1]] where x1 < x2 and y1 < y2
		if an empty list is provided, the function will find overlaps within array a alone.  If an array of points is provided,
		then the function will find places where array a overlaps with array temp.
		:return temp: if one input array was provided, this is the "cleaned" version of the array.  If two were provided, this value is meaningless.
		Array of points in the form [[x1,y2],[x2,y1]] where x1 < x2 and y1 < y2
		:return overlap: Array of boxes that cover the area where "a" overlapped with itself if temp was empty, or where "a"
		overlapped with temp if temp was non empty.  Array of points in the form [[x1,y2],[x2,y1]] where x1 < x2 and y1 < y2
		"""
		reduce_a = False
		overlap = []
		if len(temp) == 0:
			temp.append(a.pop(0))
			reduce_a = True

		for i, box_a in enumerate(a):
			append_a = True
			j = 0
			while j < len(temp):
				box_t = temp[j]
				xy = self.getOverlapPositions(box_a, box_t)
				if xy[4] == -1: # The boxes do not overlap, so move on
					j += 1
					continue
				elif xy[4] == 0:  #t is inside a, so keep only a
					temp.remove(box_t)
					overlap.append(box_t)
					continue
				elif xy[4] == 1: #keep a, keep t but shift on the value that == 1
					overlap.append(self.shiftBox(a[i], temp[j], xy, 1))
				elif xy[4] == 3: #keep t, keep a but shift on the value that == 0
					overlap.append(self.shiftBox(temp[j], a[i], xy, 0))
				elif xy[4] == 2:  #keep t, keep a but in two pieces, shift on the values that == 0
					m,n,l = self.makeTwoBoxes(temp[j], a[i], xy, 0)
					if self.getBoxArea(l) > 0:
						overlap.append(l)
					if len(m) > 0 and self.getBoxArea(m) > 0:
						a.append(m)
					if len(n) > 0 and self.getBoxArea(n) > 0:
						a.append(n)
					append_a = False
					break
				else: #xy[4] == 4:  Only keep t
					overlap.append(box_a)
					break

				j += 1
			if reduce_a and append_a:
				temp.append(box_a)
		return [temp, overlap]


	def getOverlapPositions(self, a, t):
		"""
		Function to determine if two boxes overlap, and if so, whether the four lines x = x1, x = x2, y = y1, and y= y2 in the first box
		 cross through the second box.
		:param a: A box of the form [[x1,y2],[x2,y1]] where x1 < x2 and y1 < y2.  This is the box for which the values of lines will be calculated.
		:param t: A second box of the form [[x1,y2],[x2,y1].
		:return: A list of x1, x2, y1, y2, (which are 1 if the corresponding line from a passes through t, or 0 otherwise) and sum, which
		is -1 if the boxes a and t do not overlap, or the sum of x1 + x2 + y1 + y2 otherwise.
		"""
		x1 = x2 = y1 = y2 = 0
		in_out = [1,1,1,1]

		if a[0][0] > t[0][0] and a[0][0] < t[1][0]:
			x1 = 1
		elif a[0][0] >= t[1][0]:
			in_out[0] = 'g'
		else:  #a[0][0] <= t[0][0]
			in_out[0] = 'l'

		if a[1][0] > t[0][0] and a[1][0] < t[1][0]:
			x2 = 1
		elif a[1][0] >= t[1][0]:
			in_out[1] = 'g'
		else: #a[1][0] <= t[0][0]
			in_out[1] = 'l'

		if a[1][1] > t[1][1] and a[1][1] < t[0][1]:
			y1 = 1
		elif a[1][1] >= t[0][1]:
			in_out[2] = 'g'
		else: #a[1][1] <= t[1][1]
			in_out[2] = 'l'

		if a[0][1] > t[1][1] and a[0][1] < t[0][1]:
			y2 = 1
		elif a[0][1] >= t[0][1]:
			in_out[3] = 'g'
		else: #a[0][1] <= t[1][1]
			in_out[3] = 'l'

		sum = x1 + x2 + y1 + y2

		if (in_out[0] in ['l','g'] and in_out[0] == in_out[1]) or (in_out[2] in ['l','g'] and in_out[2] == in_out[3]):
			sum = -1

		return [x1, x2, y1, y2, sum]

	def shiftBox(self, reference, new, xy, toShift):
		"""
		Function to reduce a box into one that does not overlap with the other given box, and return the overlapping portion.
		The two boxes must relate in such a way that exactly three of the edges of one box are inside of the other.
		:param reference: A box of the form [[x1,y2],[x2,y1]] where x1 < x2 and y1 < y2.  This box will not change.
		:param new: A box of the form [[x1,y2],[x2,y1]] where x1 < x2 and y1 < y2. This is the box that has three edges inside of the reference box.
		 After running the function, its value will be only the portion that does not overlap with reference.
		:param xy: The return of running getOverlapPositions on a, t
		:param toShift: Integer 0 or 1, 1 meaning whether to cut a on the line that cuts through t, or 1 meaning
		to cut on the line that of t where the equivalient line of a does not cut through t.
		:return: a box that covers the overlapping portion of the two given boxes.
		"""
		overlap = []
		if xy[0] == toShift:
			overlap = [[reference[0][0],new[0][1]], new[1].copy()]
			new[1][0] = reference[0][0]
		elif xy[1] == toShift:
			overlap = [new[0].copy(), [reference[1][0], new[1][1]]]
			new[0][0] = reference[1][0]
		elif xy[2] == toShift:
			overlap = [new[0].copy(),[new[1][0],reference[1][1]]]
			new[0][1] = reference[1][1]
		elif xy[3] == toShift:
			overlap = [[new[0][0],reference[0][1]],new[1].copy()]
			new[1][1] = reference[0][1]
		return overlap



	def makeTwoBoxes(self, reference, new, xy, toShift):
		"""
		Function to take a box and reduce it to two new boxes that do not overlap with another given box.
		Also returns the area where the two given boxes overlapped.
		:param reference: This box will not change.
		:param new:  This box is split into two new boxes.
		:param xy: The return of running getOverlapPositions on two boxes a, t
		:param toShift: integer 0 or 1 that indicates how to cut param new.
		:return: list of [box1, box2, overlap]  where box1 and box2 are the reduced form of param new and overlap is
		the area where reference and new overlapped.
		"""
		box1 = []
		box2 = []
		if xy[0:4] == [1,0,0,1]:
			box2 = [[new[0][0],reference[1][1]], new[1].copy()]
			new[1][1] = reference[1][1]
		elif xy[0:4] == [0,1,0,1]:
			box2 = [[new[0][0],reference[1][1]], new[1].copy()]
			new[1][1] = reference[1][1]
		elif xy[0:4] == [0,1,1,0]:
			box2 = [new[0].copy(),[new[1][0],reference[0][1]]]
			new[0][1] = reference[0][1]
		elif xy[0:4] == [1,0,1,0]:
			box2 = [new[0].copy(),[new[1][0],reference[0][1]]]
			new[0][1] = reference[0][1]
		elif xy[0:4] == [1,1,0,0]:
			box1 = [new[0].copy(), [new[1][0], reference[0][1]]]
			box2 = [[new[0][0], reference[1][1]], new[1].copy()]
			overlap = [[new[0][0], reference[0][1]], [new[1][0], reference[1][1]]]
			return [box1, box2, overlap]
		elif xy[0:4] == [0,0,1,1]:
			box1 = [new[0].copy(), [reference[0][0], new[1][1]]]
			box2 = [[reference[1][0], new[0][1]], new[1].copy()]
			overlap = [[reference[0][0], new[0][1]], [reference[1][0], new[1][1]]]
			return [box1, box2, overlap]

		box1 = new.copy()
		overlap = self.shiftBox(reference, box1, xy, toShift)

		return[box1,box2,overlap]

	def splitBox(self, reference, new, xy):
		box1 = [new[0].copy(), new[1].copy()]
		box2 = [new[0].copy(), new[1].copy()]
		if xy[0:4] == [1,1,0,0]:
			box1[1][1] = reference[0][1]
			box2[0][1] = reference[0][1]
		else:  #xy[0:4] = [0,0,1,1]
			box1[1][0] = reference[0][0]
			box2[0][0] = reference[0][0]
		return [box1,box2]


if __name__ == '__main__':
	cost = Cost()

	answer = [[[77, 384], [323, 609]], [[363, 458], [534, 903]]]
	guess = [  ]

	#for i in range(len(answers)):
	#	print(cost.getCost(10,10, answers[i], guesses[i]))


	#print(cost.getCost(answer,guess))

	print(cost.getCost(answer, guess))

