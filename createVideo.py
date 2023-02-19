import datetime
import logging
import random
import os
import shutil

test_mode = False
log_level = logging.DEBUG

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[logging.FileHandler('/home/pgregg/timelapse/tl.log'), logging.StreamHandler()])

def create_video(photo_path, srt_path):
    audio_track_list = ['tomorrow-llthat.m4a', 'brazilsamb-funkyelement.m4a', 'brazilsamb-happyrock.m4a',  'creativeminds-straight.m4a', 'dance-hipjazz.m4a', 'dance-littleplanet.m4a', 'deepblue-hipjazz.m4a', 'deepblue-sweet.m4a', 'downtown-dreams.m4a', 'downtown-hipjazz.m4a', 'dreams-happyrock.m4a', 'dreams-onceagain.m4a', 'elevate-hipjazz.m4a', 'elevate-newdawn.m4a', 'emories-brazilsamb.m4a', 'emories-house.m4a', 'funkyelement-creativeminds.m4a', 'funkyelement-groovyhiphop.m4a', 'groovyhiphop-dance.m4a', 'groovyhiphop-downtown.m4a', 'happyrock-downtown.m4a', 'happyrock-groovyhiphop.m4a', 'hipjazz-happyrock.m4a', 'hipjazz-photoalbu.m4a', 'house-happyrock.m4a', 'house-hipjazz.m4a', 'house-inspire.m4a', 'house-littleplanet.m4a', 'house-pianomoment.m4a', 'inspire-groovyhiphop.m4a', 'inspire-hipjazz.m4a', 'littleplanet-deepblue.m4a', 'littleplanet-hipjazz.m4a', 'littleplanet-photoalbu.m4a', 'llthat-emories.m4a', 'llthat-house.m4a', 'newdawn-dance.m4a', 'newdawn-house.m4a', 'onceagain-dance.m4a', 'onceagain-newdawn.m4a', 'photoalbu-dance.m4a', 'photoalbu-groovyhiphop.m4a', 'pianomoment-dance.m4a',  'psychedelic-downtown.m4a', 'psychedelic-tomorrow.m4a', 'straight-groovyhiphop.m4a', 'straight-happyrock.m4a', 'summer-funkyelement.m4a', 'summer-sweet.m4a', 'sweet-onceagain.m4a', 'sweet-sweet.m4a', 'tomorrow-downtown.m4a']
    audio_file_name = random.choice(audio_track_list)
    fps = 60 # frames per second
    now = datetime.datetime.now()
    current_date = now.strftime("%Y-%m-%d_%H%M%S")
    video_name = f"laketravis_{current_date}.mp4"
    video_path = f'/media/videos/daily_upload/{video_name}'
    json_path = f'/home/pgregg/timelapse/json/{video_name}.json'

    # Create video
    logging.info('Starting video creation')
    try:
        cmd = f'''ffmpeg -framerate {fps} -pattern_type glob -i "{photo_path}/*.jpg" -i /media/videos/tl_music/m4a_long/{audio_file_name} -s:v 3840x2160 -c:v libx264 -bf 2 -preset slow -crf 17 -pix_fmt yuv420p -shortest -movflags +faststart -vf "subtitles={srt_path}:force_style='PrimaryColour=&H999999,Fontsize=6,Fontname=Consolas,BackColour=&H80000000,Spacing=0.2,Outline=0,Shadow=0.75'" -y {video_path}'''
        logging.info('Executing command: ' + cmd)
        os.system(cmd)

        if os.path.exists(video_path):
            logging.info(f'Video created successfully: {video_path}')
            logging.info(f'Creating JSON file for upload')
            json_path = '/home/pgregg/timelapse/json/2023-02-16.json' 
            logging.info(f'JSON file created: {json_path}')
            return video_path, json_path
        else:
            logging.error('Error creating video')
            return None, None

        logging.info('Video complete.')
    except Exception as e:
        logging.error('Unknown error creating video', exc_info=e)
        return None, None

if test_mode == True:
    photo_path = '/media/photos/test99'
    srt_path = '/media/videos/srt/02142023_b.srt'
    create_video(photo_path, srt_path)
