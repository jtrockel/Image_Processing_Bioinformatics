#TODO: consider breaking removeOverlap and others into two functions, one for finding overlap boxes and one for finding non-overlap boxes, for speed.

class Cost:
	def getCost(self, x, y, answer, guess):
		self.removeOverlap(answer[1:], [answer[0]])
#		print(answer)
		answer_area = self.getTotalArea(answer)
		self.removeOverlap(guess[1:], [guess[0]])
#		print(guess)
		guess_area = self.getTotalArea(guess)
		overlap_boxes = self.removeOverlap(answer, guess)
#		print(overlap_boxes)
		overlap_area = self.getTotalArea(overlap_boxes)

#		print(answer_area)
#		print(guess_area)
#		print(overlap_area)		
		wrong_pixels = answer_area + guess_area - (2 * overlap_area)
		pic_size = x*y
		cost = wrong_pixels/pic_size*100
		return cost

	def getTotalArea(self, a):
		area = 0
		for box in a:
			area += self.getBoxArea(box)
		return area
	
	def getBoxArea(self, box):
		dx = box[1][0] - box[0][0]
		dy = box[0][1] - box[1][1]
		return dx*dy

	def removeOverlap(self, a, temp):	
		overlap = []
		for i, box_a in enumerate(a):
			append_a = False
			for j, box_t in enumerate(temp[::-1]):
				xy = self.getOverlapPositions(box_a, box_t)
#				print("xy:")
#				print(xy)
				x_y_sum = xy[0] + xy[1] + xy[2] + xy[3]
				if x_y_sum == 0:
					xy2 = self.getOverlapPositions(box_t, box_a)
					x_y_sum2 = xy2[0] + xy2[1] + xy2[2] + xy2[3]
					#need to check one value of t in/out of a
					# if t is in: keep only a
					# if out, keep both
					if x_y_sum2 > 0 or box_a == box_t:
						temp.remove(box_t)
						overlap.append(box_t)
				elif x_y_sum == 1:
					overlap.append(self.shiftBox(a[i], temp[j], xy, 1))
					append_a = True
					#keep a, keep t but shift on the value that == 1
				elif x_y_sum == 3:
					#keep t, keep a but shift on the value that == 0
					overlap.append(self.shiftBox(temp[j], a[i], xy, 0))
					append_a = True
				elif x_y_sum == 2:
					#keep t, keep a but in two pieces, shift on the values that == 1
					m,n,l = self.makeTwoBoxes(temp[j], a[i], xy, 1)
					a.append(m)
					a.append(n)
					overlap.append(l)
					break
				else: #x_y_sum == 4:  Only keep t	
					overlap.append(box_a)
					break
			if append_a:
				temp.append(box_a)
		a = temp	
		return overlap




	def getOverlapPositions(self, a, t):
		x1 = x2 = y1 = y2 = 0
		if a[0][0] > t[0][0] and a[0][0] < t[1][0]:
			x1 = 1	
		if a[1][0] > t[0][0] and a[1][0] < t[1][0]:
			x2 = 1	
		if a[1][1] > t[1][1] and a[1][1] < t[0][1]:
			y1 = 1
		if a[0][1] > t[1][1] and a[0][1] < t[0][1]:
			y2 = 1
		return [x1, x2, y1, y2]

	# makes the "new" box into the portion that does not overlap with reference, and returns the overlap box.
	def shiftBox(self, reference, new, xy, toShift):
		overlap = []
		if xy[0] == toShift:
			overlap = [[reference[0][0],new[0][1]], new[1]]
			new[1][0] = reference[0][0]
		elif xy[1] == toShift:
			overlap = [new[0], [reference[1][0], new[1][1]]]
			new[0][0] = reference[1][0]
		elif xy[2] == toShift:
			overlap = [new[0],[new[1][0],reference[1][1]]]
			new[0][1] = reference[1][1]
		elif xy[3] == toShift:
			overlap = [[new[0][0],reference[0][1]],new[1]]
			new[1][1] = reference[0][1]
		return overlap



	def makeTwoBoxes(self, reference, new, xy, toShift):
		box1 = new.copy()
		overlap = self.shiftBox(reference, box1, xy, toShift)
		#print(overlap)
		box2 = []
		if xy == [1,0,0,1]:
			box2 = [[new[0][0],reference[1][1]],[reference[1][0],new[1][1]]]
		elif xy == [0,1,0,1]:
			box2 = [new[0],[reference[0][0],reference[1][1]]]
		elif xy == [0,1,1,0]:
			box2 = [[new[0][0],reference[0][1]],[reference[0][0],new[1][1]]]
		elif xy == [1,0,1,0]:
			box2 = [new[0],[reference[1][0],reference[0][1]]]
		return[box1,box2,overlap]


cost = Cost()
answer = [ [[1,5],[5,1]]  ]
guess = [   [[2,5],[5,2]] ]
print(cost.getCost(10,10, answer, guess))

