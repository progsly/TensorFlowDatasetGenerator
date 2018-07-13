import helpers
import sys
import json
import cv2
import time
import zipfile
import os
from youtube_dl import YoutubeDL
from youtube_dl.utils import (
    DownloadError
)
import urllib.request


def download_file(url):
    file_name = 'data/tmp/' + str(int(time.time())) + '-video.mp4'
    urllib.request.urlretrieve(url, file_name)
    return file_name


def get_video(app, url):
    ydl_opts = {
        'format': 'best',
        'cachedir': False,
        'skip_download': True,
        'quiet': True
    }
    ydl = YoutubeDL(ydl_opts)
    try:
        download_url = ydl.extract_info(url, download=False)
        app.logger.info('Success')

    except DownloadError as e:
        app.logger.error('Error {}'.format(e))
        return False, ''
    except Exception as e:
        app.logger.error('Error 2 {}'.format(e))
        return False, ''

    for item in download_url['formats']:
        if int(item['format_id']) == 22:
            return True, item['url']

    return False, ''


def processing(app, chat_id, video, object_name, new_object_name, iter_count, threshold):
    chat_id = str(chat_id)
    continue_count = 500
    root_dir = 'data/' + chat_id + '/'

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
            app.logger.info(objects)
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

        zip_file = 'data/' + str(int(time.time())) + '_' + chat_id + '.zip'
        zf = zipfile.ZipFile(zip_file, "w")
        for dirname, subdirs, files in os.walk(root_dir):
            if dirname == 'data':
                continue
            zf.write(dirname)
            for filename in files:
                zf.write(os.path.join(dirname, filename))
        zf.close()

        deleteFiles = []
        deleteDirs = []
        for root, dirs, files in os.walk(root_dir):
            if root == 'data':
                continue
            for f in files:
                deleteFiles.append(os.path.join(root, f))
            for d in dirs:
                deleteDirs.append(os.path.join(root, d))
        for f in deleteFiles:
            os.remove(f)
        for d in deleteDirs:
            if d == 'data':
                continue
            os.rmdir(d)

        return True, zip_file
    else:
        return False, ''