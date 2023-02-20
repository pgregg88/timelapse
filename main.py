import os
import logging
import concurrent.futures
from takePhotos import take_photos
from createVideo import create_video
from pubVideo import publish_video
from datetime import datetime

# setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[logging.FileHandler('/home/pgregg/timelapse/tl.log'), logging.StreamHandler()])

# define function for starting a task
def start_task(task_func, task_name):
    logging.info(f'Starting task {task_name}')
    try:
        task_func()
        logging.info(f'Finished task {task_name}')
    except Exception as e:
        logging.error(f'Error in task {task_name}: {e}')
        raise ValueError(f'Error in task {task_name}: {e}')

# define main function
def main():
    current_time = datetime.now()
    dir_name = current_time.strftime("%Y-%m-%d_%H%M%S")

    run_hours = 7
    #photo_count = run_hours * 1200 #1200 per hour
    photo_count = 16400
    delay_sec = 3
    photo_path = f"/media/photos/2/{dir_name}"

    if not os.path.exists(photo_path):
        os.makedirs(photo_path)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # submit take_pictures task to the thread pool and get its future object
        tp_future = executor.submit(take_photos, photo_count, delay_sec, photo_path)

        # wait for the take_pictures future to complete
        try:
            photo_path, srt_path = tp_future.result()
            logging.debug(f'take_photos: Received photo_path: {photo_path}, srt_path: {srt_path}')
        except Exception as e:
            logging.error(f'Error receiving result from take_photos: {e}')
            raise ValueError(f'Error receiving result from take_photos: {e}')

        # submit create_video task to the thread pool and get its future object
        cv_future = executor.submit(create_video, photo_path, srt_path)

        # wait for the create_video future to complete
        try:
            video_path, json_path = cv_future.result()
            logging.debug(f'create_video: Received video_path: {video_path}, json_path: {json_path}')
        except Exception as e:
            logging.error(f'Error receiving result from create_video: {e}')
            raise ValueError(f'Error receiving result from create_video: {e}')

        # submit publish_video task to the thread pool
        pv_future = executor.submit(publish_video, video_path, json_path)

        # wait for the publish_video future to complete
        try:
            pv_future.result()
        except Exception as e:
            logging.error(f'Error in publish_video task: {e}')
            raise ValueError(f'Error in publish_video task: {e}')

# run main function
if __name__ == '__main__':
    main()
