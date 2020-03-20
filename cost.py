#TODO: consider breaking removeOverlap and others into two functions, one for finding overlap boxes and one for finding non-overlap boxes, for speed.

#TODO:
class Cost:
	def getCost(self, x, y, answer, guess):
		answer, a_overlap = self.removeOverlap(answer, [], True)
#		print(answer)
		answer_area = self.getTotalArea(answer)
		guess, g_overlap = self.removeOverlap(guess, [], True)
#		print(guess)
		guess_area = self.getTotalArea(guess)
		t, overlap_boxes = self.removeOverlap(answer, guess, False)
#		print(overlap_boxes)
		overlap_area = self.getTotalArea(overlap_boxes)

#		print(answer_area)
#		print(guess_area)
#		print(overlap_area)

		pic_size = x * y
		percent_true_lost = ( answer_area - overlap_area ) / pic_size * 100
		percent_false_gained = ( guess_area - overlap_area ) / pic_size * 100
		cost = percent_true_lost + percent_false_gained
		return [percent_true_lost, percent_false_gained, cost]

	def getTotalArea(self, a):
		area = 0
		for box in a:
			area += self.getBoxArea(box)
		return area
	
	def getBoxArea(self, box):
		dx = box[1][0] - box[0][0]
		dy = box[0][1] - box[1][1]
		return dx*dy

	def removeOverlap(self, a, temp, reduce_a):
		overlap = []
		if len(temp) == 0:
			temp.append(a.pop(0))

		for i, box_a in enumerate(a):
			append_a = True
			j = 0
			while j < len(temp):
				#print(i,j)
				box_t = temp[j]
				xy = self.getOverlapPositions(box_a, box_t)
#				print("xy:")
#				print(xy)
				if xy[4] == -1: # The boxes do not overlap, so move on
					j += 1
					continue
				elif xy[4] == 0:  #t is inside a, so keep only a
					#xy2 = self.getOverlapPositions(box_t, box_a)
					#need to check one value of t in/out of a
					# if t is inside a, keep only a
					# if out, keep both
					#if xy2[4] > 0 or box_a == box_t:
					#	temp.remove(box_t)
					#	overlap.append(box_t)
					temp.remove(box_t)
					overlap.append(box_t)
					continue
				elif xy[4] == 1:
					overlap.append(self.shiftBox(a[i], temp[j], xy, 1))
					#append_a = True
					#keep a, keep t but shift on the value that == 1
				elif xy[4] == 3:
					#keep t, keep a but shift on the value that == 0
					overlap.append(self.shiftBox(temp[j], a[i], xy, 0))
					#append_a = True
				elif xy[4] == 2:
					#keep t, keep a but in two pieces, shift on the values that == 1
					#xy2 = self.getOverlapPositions(box_t, box_a)
					#if xy2[0:4] == [1,1,0,0] or xy2[0:4] == [0,0,1,1]:
					#	m,n = self.splitBox(temp[j], a[i], xy)
					#else:
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
		#a = temp
		return [temp, overlap]



	# Takes two boxes of the form [[x1,y1],[x2,y2]]
	# returns -1 if they do not overlap
	# else returns 1 if any of the lines x1, x2, y1, y2 in a pass through the box t, and the sum of x1 + x2 + y1 + y2
	def getOverlapPositions(self, a, t):
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

		#elif sum == 2 and x1 == 1 and x2 == 1 and in_out[2] != in_out[3]:
		#	sum = -2

		#elif sum == 2 and y1 == 1 and y2 == 1 and in_out[0] != in_out[1]:
		#	sum = -2

		return [x1, x2, y1, y2, sum]

	# makes the "new" box into the portion that does not overlap with reference, and returns the overlap box.
	#
	def shiftBox(self, reference, new, xy, toShift):
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
		#print(overlap)
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


cost = Cost()

answer = [    [[1,4],[4,1]], [[1,3],[5,2]]   ]  # tl 5 fg 10 cost 15
guess = [     [[0,6],[4,3]], [[2,5],[3,0]]  ]



#for i in range(len(answers)):
#	print(cost.getCost(10,10, answers[i], guesses[i]))

print(cost.getCost(10,10,answer,guess))

