import os
import requests
import logging
import time
from datetime import datetime, timedelta
import csv

csv_copy_path = 'root@ha.local:/config/laketraviswx.csv'
csv_save_path = '/media/videos/'


# setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[logging.FileHandler('/home/pgregg/timelapse/tl.log'), logging.StreamHandler()])

# retry decorator with maximum number of retries
def retry_on_exception(max_retries):
    def decorator(func):
        def wrapper(*args, **kwargs):
            tries = 0
            while tries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.warning(f'Retrying... ({tries + 1}/{max_retries})')
                    logging.error(str(e))
                    tries += 1
            raise Exception(f'Maximum number of retries ({max_retries}) exceeded')
        return wrapper
    return decorator

# decorate take_photo function with retry decorator
@retry_on_exception(5)
def take_photo(url, photo_path):
    response = requests.get(url)
    if response.status_code == 200:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f"laketravis_{timestamp}.jpg"
        with open(os.path.join(photo_path, filename), "wb") as f:
            f.write(response.content)
        logging.debug(f"Photo saved: {filename}")
    else:
        raise Exception(f"Error taking photo: {response.status_code}")

def write_srt(srt_path, srt_start_time, srt_end_time, temperature, pressure, humidity, wind_speed, wind_dir, visability, daily_rain, srt_date, srt_row_count):
    with open(srt_path, 'a') as f_srt:
        f_srt.writelines(f"{srt_row_count}\r\n0{srt_start_time},000 --> 0{srt_end_time},000\r\n{srt_date}  temp:{temperature}F  pres:{pressure}inHg  hum:{humidity}%  wind:{wind_speed}mph {wind_dir}\r\n\r\n")
    logging.info(f'SRT file updated {srt_path}')
def take_photos(num_photos, delay_sec, photo_path):
    dateraw= datetime.now()
    timestamp = dateraw.strftime("%Y-%m-%d_%H%M%S")
    # srt_path = '/media/videos/srt/02162023_b.srt'
    srt_row_count = 1
    srt_path = f'/media/videos/srt/{timestamp}_v2.srt'
    srt_elapsed_seconds = 0
    logging.info(f'srt save path: {srt_path}')
    url = "http://10.0.30.100/cgi-bin/api.cgi?cmd=Snap&channel=md=Snap&channel=0&rs=123&user=admin&password=pg12345678"
    if not os.path.exists(photo_path):
        os.makedirs(photo_path)
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=num_photos*delay_sec)
    image_count = 0
    logging.info(f"Photo taking started. Estimated end time: {end_time}")
    for i in range(num_photos):
        srt_now = datetime.now()
        srt_date = srt_now.strftime("%a, %b %d, %Y  %-l:%M %p: ")
        try:
            take_photo(url, photo_path)
        except Exception as e:
            logging.error(str(e))
        image_count += 1
        remaining_photos = num_photos - (i + 1)
        remaining_time = timedelta(seconds=remaining_photos*delay_sec)
        completion_time = datetime.now() + remaining_time
        if image_count % 100 == 0: # set to 500? for prod
            logging.info(f"Photos taken: {i+1}, Remaining: {remaining_photos}, Estimated completion time: {completion_time}")
        if image_count % 50 == 0: #set to 50 for prod.
            try:
                os.system(f'scp {csv_copy_path} {csv_save_path}')
                logging.info(f'WX CSV copied from {csv_copy_path}')
            except Exception as e:
                logging.error(str(e))
        if image_count % 55 == 0: # set to 55 for prod if 60 fps per second
            #get latest wx
            line_num = -1
            with open('/media/videos/laketraviswx.csv', "r", encoding="utf-8", errors="ignore") as csv_file:
                mycsv = csv.reader(csv_file)
                mycsv = list(mycsv)
                temperature = mycsv[line_num][1]
                humidity = mycsv[line_num][2]
                pressure = mycsv[line_num][3]
                wind_speed = mycsv[line_num][4]
                wind_dir = mycsv[line_num][6]
                daily_rain = mycsv[line_num][7]
                visability = mycsv[line_num][8]
                w_time = timestamp
            # srt calcs
            srt_start_time = timedelta(seconds=srt_elapsed_seconds)
            srt_end_calc = srt_elapsed_seconds + 1
            srt_end_time = timedelta(seconds=srt_end_calc)
            
            write_srt(srt_path, srt_start_time, srt_end_time, temperature, pressure, humidity, wind_speed, wind_dir, visability, daily_rain, srt_date, srt_row_count)
            srt_elapsed_seconds += 1
            srt_row_count += 1
            
            
        time.sleep(delay_sec)
    end_time = datetime.now()
    duration = end_time - start_time
    duration_str = str(timedelta(seconds=duration.total_seconds()))
    logging.info(f"Photo taking complete. Duration: {duration_str}")
    return photo_path, srt_path
