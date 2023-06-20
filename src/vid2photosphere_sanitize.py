import os
import torch
import argparse

from mapillary_tools.mapillary_tools.commands.video_process import Command as ProcessVideoCommand

from datetime import datetime
from pathlib import Path
from alive_progress import alive_bar
from PIL import Image, ImageFilter, ImageDraw
from transformers import YolosImageProcessor, YolosForObjectDetection

from bbox_utils import union_overlapping_bounding_boxes, grow_bounding_boxes
from tile_utils import get_tiles, offset_bounding_box_by_tile_position
from sanitization_models import get_plates_in_image, get_people_in_image

def blur_image(img, boxes):
	for box in boxes:
		box_int = [int(i) for i in box]
		ic = img.crop(box_int).filter(ImageFilter.GaussianBlur(radius=10))
		img.paste(ic, box_int)
	return img

if __name__ == "__main__":
	#Create instances of the mapillary commands we need to work with
	pv = ProcessVideoCommand()

	#Create an argument parser to use.
	parser = argparse.ArgumentParser(prog='vid2photosphere_sanitize', description='Generate photospheres, align them, and sanitize them.')

	parser.add_argument('video_import_path', type=Path, help="The path to the video that is to be processed.")
	parser.add_argument('import_path', type=Path, help="The path destination where the frames are to be saved.")

	#Add all the command line arguments having to do with Mapillary's "process_video" command 
	pv.add_basic_arguments(parser)

	#Add all the arguments we need for our sanitization process.
	parser.add_argument('--tile_size', type=int, help="The dimension of the square image tiles on which the ML models will be run.", default=1024)
	parser.add_argument('--person_detector_threshold', type=float, help="If the confidence of the prediction is less than this value, it will be discarded.", default=0.1)
	parser.add_argument('--license_plate_detector_threshold', type=float, help="If the confidence of the prediction is less than this value, it will be discarded.", default=0.5)
	parser.add_argument('--person_detector_prediction_growth', type=float, help="The amount that the prediction of the person detectors will be expanded.", default=0.3)
	parser.add_argument('--license_plate_detector_prediction_growth', type=float, help="The amount that the prediction of the license plate detectors will be expanded.", default=1.0)

	#Parse all the args that we need
	args = parser.parse_args()

	#Run the process_video command on the passed args
	pv.run(vars(args))

	#Get the model for detecting people 
	people_model = torch.hub.load('ultralytics/yolov5', 'yolov5l')
	people_model.classes = [ 0 ] # only considering class 'person' and not the 79 other classes...

	#Get model and feature extractor for detecting license plates
	lp_model_name = "nickmuchi/yolos-small-finetuned-license-plate-detection"
	lp_feature_extractor = YolosImageProcessor.from_pretrained(lp_model_name)
	lp_model = YolosForObjectDetection.from_pretrained(lp_model_name)

	#Get all the files that we need to run the models on...
	files = []
	desc_path = ""
	for (dirpath, dirnames, filenames) in os.walk(args.import_path):
		for file in filenames:
			if(file.lower().endswith(".jpg")):
				files.append(os.path.join(dirpath, file))
			if(file.lower().endswith(".json")):
				desc_path = os.path.join(dirpath, file)

	#Then iterate over the files while keeping track with a progress bar.
	with alive_bar(len(files)) as bar:
		for file in files:
			#Load the image
			image = Image.open(file)

			#Generate the tiles that will be passed to the model
			tiles, tile_positions = get_tiles(image, args.tile_size, args.tile_size)
			
			#Build lists that will store the predictions for both of the models
			plate_bboxes = []
			people_bboxes = []

			#For each tile
			for tile, tile_pos in zip(tiles, tile_positions):
				#Run the plate model, and then the people model
				tile_plate_boxes = get_plates_in_image(tile["image"], lp_feature_extractor, lp_model, threshold=args.license_plate_detector_threshold)
				tile_people_boxes = get_people_in_image(tile["image"], people_model, threshold=args.person_detector_threshold)
				
				#Track the bounding boxes from each model
				plate_bboxes.extend(offset_bounding_box_by_tile_position(tile_plate_boxes, tile_pos))
				people_bboxes.extend(offset_bounding_box_by_tile_position(tile_people_boxes, tile_pos))

			#Grow the bounding boxes based on the hyperparameter
			grown_plate_bounding_boxes = grow_bounding_boxes(plate_bboxes, args.person_detector_prediction_growth)
			grown_people_bounding_boxes = grow_bounding_boxes(people_bboxes, args.license_plate_detector_prediction_growth)

			#Union any bounding boxes that are overlapping
			unioned_plate_bboxes, _ = union_overlapping_bounding_boxes(grown_plate_bounding_boxes, [1]*len(grown_plate_bounding_boxes))
			unioned_people_bboxes, _ = union_overlapping_bounding_boxes(grown_people_bounding_boxes, [1]*len(grown_people_bounding_boxes))

			#Blur the images based on the bounding boxes that have been generated
			scrubbed_image = blur_image(image, unioned_plate_bboxes)
			scrubbed_image = blur_image(scrubbed_image, unioned_people_bboxes)

			#Save the image by deleting the original and saving the scrubbed one in its place.
			os.remove(file)
			scrubbed_image.save(file)

			#Advance the progress bar
			bar()