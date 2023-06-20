import sys
import numpy as np

def bb_intersection_over_union(boxA, boxB):
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    # compute the area of intersection rectangle
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)
    # return the intersection over union value
    return iou

def grow_bounding_boxes(bounding_boxes, growth_rate=0.2):
    grown_boxes = []
    for xmin, ymin, xmax, ymax in bounding_boxes:
        width = xmax-xmin
        height = ymax-ymin
        grown_boxes.append([xmin-(width*growth_rate), ymin-(height*growth_rate), xmax+(width*growth_rate), ymax-(height*growth_rate)])
    return grown_boxes

def union_overlapping_bounding_boxes(bounding_boxes, confidences, iou_thr=0):
    unioned_bounding_boxes_confs = []
    unmatched_bounding_boxes_confs = list(zip(bounding_boxes, confidences))
    any_match = True
    while(any_match):
        any_match = False
        idx = 0
        while(idx < len(unmatched_bounding_boxes_confs) and idx >= 0):
            box_i, conf_i = unmatched_bounding_boxes_confs[idx]
            match = False
            for j in range(0, len(unioned_bounding_boxes_confs)):
                box_j, conf_j = unioned_bounding_boxes_confs[j]
                iou = bb_intersection_over_union(box_i, box_j)
                if(iou > iou_thr and len(unmatched_bounding_boxes_confs) > 0):
                    x_min = min(box_i[0], box_j[0])
                    y_min = min(box_i[1], box_j[1])
                    x_max = max(box_i[2], box_j[2])
                    y_max = max(box_i[3], box_j[3])
                    unioned_bounding_boxes_confs[j] = ([x_min, y_min, x_max, y_max], max(conf_i, conf_j))
                    unmatched_bounding_boxes_confs.pop(idx)
                    match = True
                    any_match = True
                    idx -= 1
                    
            if(not match):
                unioned_bounding_boxes_confs.append((box_i, conf_i))

            idx+=1
        unmatched_bounding_boxes_confs = unioned_bounding_boxes_confs[:]
        unioned_bounding_boxes_confs = []

    unmatched_bounding_boxes = [bb for bb, _ in unmatched_bounding_boxes_confs]
    unmatched_confidences = [c for _, c in unmatched_bounding_boxes_confs]

    return unmatched_bounding_boxes, unmatched_confidences