import helpers
import sys
import json
import cv2
import time


def processing(video, object_name, new_object_name, iter_count, threshold):

    continue_count = 100
    root_dir = 'data/'

    if video:
        sys.path.append('./object_detection')

        import object_detection_api

        helpers.check_or_create_dirs(root_dir, new_object_name)
        try:
            cap = cv2.VideoCapture(video)
        except Exception as e:
            print(e)
            sys.exit()
        x = 0
        iteration = 0
        while cap.isOpened():
            x += 1
            if (x % continue_count) != 0:
                continue

            ret, frame = cap.read()
            orig_height, orig_width, _ = frame.shape

            objects = object_detection_api.get_objects(frame, threshold)

            objects = json.loads(objects)

            if len(objects) > 1:
                for item in objects:
                    if item['name'] != 'Object':
                        continue

                    if item['class_name'] != object_name:
                        continue

                    iteration += 1
                    file_name = str(int(time.time())) + '-data'

                    x = int(orig_width * item['x'])
                    y = int(orig_height * item['y'])

                    width = int(orig_width * item['width'])
                    height = int(orig_height * item['height'])

                    cv2.imwrite(root_dir + 'images/' + new_object_name + '/' + file_name + '.jpg', frame)

                    helpers.create_annotation(root_dir, new_object_name, file_name, x, y, width, height, orig_width,
                                              orig_height)

            if iteration == iter_count:
                break