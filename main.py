import helpers
import sys
import json
import cv2
import time
import argparse


parser = argparse.ArgumentParser(add_help=True, description='TensorFlow Dataset Generator')

parser.add_argument('-s', '--show', type=bool, action='store', dest='show',
                    help='Show frames', default=True)
parser.add_argument('-i', '--iterations', type=int, action='store', dest='iterations',
                    help='Count images for dataset', default=500)
parser.add_argument('-t', '--threshold', type=float, action='store', dest='threshold',
                    help='threshold for detection, default - 0.5', default=0.5)

required_params = parser.add_argument_group('required arguments')

required_params.add_argument('-v', '--video', type=str, action='store', dest='video', help='Path to video file',
                             required=True)
required_params.add_argument('-o', '--object', type=str, action='store', dest='object_name',
                             help='object name for detection', required=True)
required_params.add_argument('-n', '--name', type=str, action='store', dest='new_name',
                             help='new object name for annotations', required=True)

if __name__ == '__main__':

    arguments = parser.parse_args()

    THRESHOLD = arguments.threshold
    CONTINUE_COUNT = 100
    OBJECT_NAME = arguments.object_name
    NEW_OBJECT_NAME = arguments.new_name
    ROOT_DIR = 'data/'
    ITER_COUNT = arguments.iterations
    VIDEO = arguments.video
    IS_SHOW = arguments.show

    if VIDEO:
        sys.path.append('./object_detection')

        import object_detection_api

        helpers.check_or_create_dirs(ROOT_DIR, NEW_OBJECT_NAME)

        cap = cv2.VideoCapture(VIDEO)
        x = 0
        iteration = 0
        while cap.isOpened():
            x += 1
            if (x % CONTINUE_COUNT) != 0:
                continue

            ret, frame = cap.read()
            orig_height, orig_width, _ = frame.shape

            objects = object_detection_api.get_objects(frame, THRESHOLD)

            objects = json.loads(objects)
            font = cv2.FONT_HERSHEY_SIMPLEX
            if IS_SHOW:
                show_frame = frame.copy()
            else:
                show_frame = None

            if len(objects) > 1:
                for item in objects:
                    if item['name'] != 'Object':
                        continue

                    if item['class_name'] != OBJECT_NAME:
                        continue

                    iteration += 1
                    file_name = str(int(time.time())) + '-data'

                    x = int(orig_width * item['x'])
                    y = int(orig_height * item['y'])

                    width = int(orig_width * item['width'])
                    height = int(orig_height * item['height'])

                    if IS_SHOW:
                        cv2.rectangle(show_frame, (x, y), (width, height), (0, 255, 0), 2)
                        scope = float('{:.2f}'.format(item['score'] * 100))
                        cv2.putText(show_frame, item['class_name'] + " - " + str(scope) + '%', (x + 5, y + 20), font, 1,
                                    (255, 255, 255), 2, cv2.LINE_AA)

                    cv2.imwrite(ROOT_DIR + 'images/' + NEW_OBJECT_NAME + '/' + file_name + '.jpg', frame)

                    helpers.create_annotation(ROOT_DIR, NEW_OBJECT_NAME, file_name, x, y, width, height, orig_width,
                                              orig_height)

            if iteration == ITER_COUNT:
                break

            if IS_SHOW and show_frame is not None:
                cv2.imshow('frame', show_frame)

                k = cv2.waitKey(1)
                if k == ord('q'):
                    break

        cap.release()
        cv2.destroyAllWindows()

        print('Done')
