import torch
import os

os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

def get_plates_in_image(img, feature_extractor, model, threshold=0.5):
    inputs = feature_extractor(img, return_tensors="pt")
    outputs = model(**inputs)
    img_size = torch.tensor([tuple(reversed(img.size))])
    processed_outputs = feature_extractor.post_process(outputs, img_size)

    keep = processed_outputs[0]["scores"] > threshold
    boxes = processed_outputs[0]["boxes"][keep].tolist()
    scores = processed_outputs[0]["scores"][keep].tolist()
    labels = processed_outputs[0]["labels"][keep].tolist()
    
    return boxes

def get_people_in_image(img, model, threshold):
    images = [ img ] # inference operates on a list of images
    model.conf = threshold
    model.eval()
    detections = model(images, size=640)
    predictions:torch.Tensor = torch.clone(detections.pred[0]) # the predictions for our single image
    boxes = predictions[:, 0:4]
    for i in range(0, len(boxes)):
        diff = boxes[i, 3]-boxes[i, 1]
        boxes[i, 1] += diff
        boxes[i, 3] += diff
    scores = predictions[:, 4]
    labels = predictions[:, 5]
    return boxes.cpu().tolist() # image and number of detections
