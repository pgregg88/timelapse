import os
import logging
import concurrent.futures
from takePhotos import take_photos
from createVideo import create_video
from pubVideo import publish_video
from datetime import datetime
from logger import setup_logging
from mqtt import publish_mqtt_status

now = datetime.now()

# define main function
def main():
    timestamp = now.strftime("%Y-%m-%d_%H%M%S")
    titledate = now.strftime("%m/%d/%Y")
    project_name = 'lt_day'
    instance_name = f'{project_name}_{timestamp}'
    title = f"{titledate}: Lake Travis, Texas (Austin, TX): 4K, 60fps Daily Weather & Boat Traffic Timelapse Video"
    description  = '4K, 60fps Daily Weather & Boat Traffic Timelapse Video taken near Lakeway, Texas (Austin, Texas)\n \n Lake Travis is a large recreational lake and the crown jewel of the Central Texas Highland Lakes chain. It sits just west of Austin, TX in the Texas Hill Country and is the most visited freshwater recreational vacation destination in the state. The Lake Travis limestone bottom results in its unique crystal-clear blue waters, making it a freshwater haven for water enthusiasts of all kinds. \n \nThe lake is 63.75 miles long, has over 271 miles of shoreline and its maximum width is 4.5 miles. The lake covers 18,929 acres. \n \nMusic by Bensound.com\n \nAbout this channel:\nWe publish a daily 4K timelapse movie illustrating the weather around Lake Travis, Texas. The images are taken near Lakeway, Texas. \n \nIn addition to being visually interesting, we create these videos as a resource archive anyone can use to study local environmental changes over time.'
    categoryId = '28'
    playlistIds = 'PLFN-n1UuTGMFbSg3XSun34o3expxUWD-4' #daily timelapse
    tags = ["laketravis", "austin" ,"weather", "wx", "timelapse", "photography", "boating", "lake", "lakeway", "4K", "storms", "sunrise", "sunset", "heavyweather", "time-lapse", "clouds", "Meteorology", "wind", "sublimation", "deposition", "condensation", "saturation", "humidification", "60fps", "videoblog"]
    photo_count = 16400 # lt day prod count
    #photo_count = 3600 # 1 min video at 3 second delay
    #photo_count = 130
    fps = 60
    delay_sec = 3
    photo_path = f"/media/photos/2/{instance_name}"
    video_start_fade_time = round((photo_count/fps)-5, 1)

    if not os.path.exists(photo_path):
        os.makedirs(photo_path)
        
    # Set up the logger with the log path
    log_path = f'/home/pgregg/timelapse/logs/tl_{instance_name}.log'
    logger = setup_logging(log_path, instance_name)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # submit take_pictures task to the thread pool and get its future object
        tp_future = executor.submit(take_photos, photo_count, delay_sec, photo_path, logger, timestamp, now, instance_name)

        # wait for the take_pictures future to complete
        try:
            photo_path, srt_path = tp_future.result()
            logger.info(f'take_photos: Received photo_path: {photo_path}, srt_path: {srt_path}')
            publish_mqtt_status("timelapse/status",f'take_photos: Received photo_path: {photo_path}, srt_path: {srt_path}')
        except Exception as e:
            logger.error(f'Error receiving result from take_photos: {e}')
            publish_mqtt_status("timelapse/error",f'Error receiving result from take_photos: {e}')
            raise ValueError(f'Error receiving result from take_photos: {e}')

        # submit create_video task to the thread pool and get its future object
        cv_future = executor.submit(create_video, photo_path, srt_path, logger, timestamp, now, instance_name, fps, title, description, categoryId, playlistIds, tags, video_start_fade_time)

        # wait for the create_video future to complete
        try:
            video_path, json_path = cv_future.result()
            logger.info(f'create_video: Received video_path: {video_path}, json_path: {json_path}')
            publish_mqtt_status("timelapse/status",f'create_video: Received video_path: {video_path}, json_path: {json_path}')
        except Exception as e:
            logger.error(f'Error receiving result from create_video: {e}')
            publish_mqtt_status("timelapse/error",f'Error receiving result from create_video: {e}')
            raise ValueError(f'Error receiving result from create_video: {e}')

        # submit publish_video task to the thread pool
        pv_future = executor.submit(publish_video, video_path, json_path, logger)

        # wait for the publish_video future to complete
        try:
            pv_future.result()
            logger.info(f'published_video to YouTube and archived.')
            publish_mqtt_status("timelapse/status",f'published_video to YouTube and archived.')
        except Exception as e:
            logger.error(f'Error in publish_video task: {e}')
            publish_mqtt_status("timelapse/error",f'Error in publish_video task: {e}')
            raise ValueError(f'Error in publish_video task: {e}')
    # shutdown the executor after all tasks have completed
    executor.shutdown()
# run main function
if __name__ == '__main__':
    main()
