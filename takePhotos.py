import os
import requests
import time
from datetime import datetime, timedelta
import logging

test_mode = False
log_level = logging.INFO

# setup logging
logging.basicConfig(
    level=log_level,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/pgregg/timelapse/tl.log'),
        logging.StreamHandler()
    ]
)


def take_photos(num_photos, delay_sec, photo_path):
    srt_path = '/media/videos/srt/02162023_b.srt'
    url = "http://10.0.30.100/cgi-bin/api.cgi?cmd=Snap&channel=md=Snap&channel=0&rs=123&user=admin&password=pg12345678"
    if not os.path.exists(photo_path):
        os.makedirs(photo_path)
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=num_photos*delay_sec)
    logging.info(f"Photo taking started. Estimated end time: {end_time}")
    for i in range(num_photos):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f"laketravis_{timestamp}.jpg"
        try:
            response = requests.get(url)
            with open(os.path.join(photo_path, filename), "wb") as f:
                f.write(response.content)
        except Exception as e:
            logging.error(str(e))
        time.sleep(delay_sec)
    end_time = datetime.now()
    duration = end_time - start_time
    duration_str = str(timedelta(seconds=duration.total_seconds()))
    logging.info(f"Photo taking complete. Duration: {duration_str}")
    return photo_path, srt_path



# def take_pictures(photo_count):
#     logging.info(f'Photo count is {photo_count}')
#     print(f'Photo count is {photo_count}')
#     photo_path = '/media/photos/move/02162023'
#     logging.info(f'Photo directory is {photo_path}')
#     print(f'Photo directory is {photo_path}')

#     srt_path = '/media/videos/srt/02162023_b.srt'
#     logging.info('Starting picture capture')
#     print('Starting picture capture')
#     time.sleep(5)
#     logging.info('Pictures captured')
#     print('Pictures captured')
    
#     time.sleep(5)  # wait for another 5 seconds before returning the results
    
#     logging.info(f'Returned: {photo_path}, {srt_path}')
#     print(f'Returned: {photo_path}, {srt_path}')
#     return photo_path, srt_path


if test_mode:
    num_photos = 10
    delay_sec = 3
    photo_path = "/media/photos/2/daily_photos"
    take_photos(num_photos, delay_sec, photo_path)


    