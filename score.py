

#this script compares how closely algorithms generated bounding boxes (boxes_gen) compared to the true positive. (boxes_sol)

#input is 2 lists of coordinate lists, each sublist representing a bounding box.
def scorer(boxes_gen, boxes_sol):
    false_positive = 0
    true_positive = 0
    false_negative = 0
    #generate all boxes by creating a set of all the pixels
    #generate pixel set in generated boxes
    tuples_gen = set()
    for box in boxes_gen:
        tuples_gen = tuples_gen.union(getBoxTuples(box))
    #do the same for solution boxes
    tuples_sol = set()
    for box in boxes_sol:
        tuples_sol = tuples_sol.union(getBoxTuples(box))

    #overlapping pixels will be included in true_positive
    true_positive = len(tuples_sol.intersection(tuples_gen))
    #pixels found in boxes_gen but not in boxes_sol will be included in false_positive
    false_positive = len(tuples_gen.difference(tuples_sol))
    #pixels found in boxes_sol but not in boxes_gen will be included in false_negative
    false_negative = len(tuples_sol.difference(tuples_gen))

    return [true_positive,false_positive,false_negative]


def getBoxTuples(box):
    tuples = set()
    p1 = box[0]
    p2 = box[1]
    for i in range(p1[0],p2[0]):
        for j in range(p1[1],p2[1]):
            tuples.add((i,j))
    return tuples

#example
#(1177,179),(1355,46)
boxes1 = [[(1,2),(5,5)],[(10,10),(12,12)]]
boxes2 = [[(1,2),(5,6)]]
print(scorer(boxes1,boxes2))