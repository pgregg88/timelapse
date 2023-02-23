import datetime
import logging
import random
import os
import shutil
import json
# from main import log_path
from logger import setup_logging
from mqtt import publish_mqtt_status

# Set up the logger with the log path
# log_path = '/home/pgregg/timelapse/logs/shouldnotbehere.log'
# logger = setup_logging(log_path)

def create_video(photo_path, srt_path, logger, timestamp, now, instance_name, fps, title, description, categoryId, playlistIds, tags):
    audio_track_list = ['tomorrow-llthat.m4a', 'brazilsamb-funkyelement.m4a', 'brazilsamb-happyrock.m4a',  'creativeminds-straight.m4a', 'dance-hipjazz.m4a', 'dance-littleplanet.m4a', 'deepblue-hipjazz.m4a', 'deepblue-sweet.m4a', 'downtown-dreams.m4a', 'downtown-hipjazz.m4a', 'dreams-happyrock.m4a', 'dreams-onceagain.m4a', 'elevate-hipjazz.m4a', 'elevate-newdawn.m4a', 'emories-brazilsamb.m4a', 'emories-house.m4a', 'funkyelement-creativeminds.m4a', 'funkyelement-groovyhiphop.m4a', 'groovyhiphop-dance.m4a', 'groovyhiphop-downtown.m4a', 'happyrock-downtown.m4a', 'happyrock-groovyhiphop.m4a', 'hipjazz-happyrock.m4a', 'hipjazz-photoalbu.m4a', 'house-happyrock.m4a', 'house-hipjazz.m4a', 'house-inspire.m4a', 'house-littleplanet.m4a', 'house-pianomoment.m4a', 'inspire-groovyhiphop.m4a', 'inspire-hipjazz.m4a', 'littleplanet-deepblue.m4a', 'littleplanet-hipjazz.m4a', 'littleplanet-photoalbu.m4a', 'llthat-emories.m4a', 'llthat-house.m4a', 'newdawn-dance.m4a', 'newdawn-house.m4a', 'onceagain-dance.m4a', 'onceagain-newdawn.m4a', 'photoalbu-dance.m4a', 'photoalbu-groovyhiphop.m4a', 'pianomoment-dance.m4a',  'psychedelic-downtown.m4a', 'psychedelic-tomorrow.m4a', 'straight-groovyhiphop.m4a', 'straight-happyrock.m4a', 'summer-funkyelement.m4a', 'summer-sweet.m4a', 'sweet-onceagain.m4a', 'sweet-sweet.m4a', 'tomorrow-downtown.m4a']
    audio_file_name = random.choice(audio_track_list)
    video_name = f"{instance_name}.mp4"
    video_path = f'/media/videos/daily_upload/{video_name}'
    json_path = f'/home/pgregg/timelapse/json/{video_name}.json'

    #create json
    try:
        logger.info(f'Creating JSON file for upload')
        recordingdate = now.strftime("%Y-%m-%d")
        madeForKids = False
        embeddable = True
        publicStatsViewable = True

        # Data to be written

        youTubeMetaData = {
            "madeForKids": madeForKids,
            "embeddable": embeddable,
            "license": "creativeCommon",
            "publicStatsViewable": publicStatsViewable,
            "recordingdate": recordingdate,
            "title": title,
            "tags": tags,
            "privacyStatus": "public",
            "description": description,
            "categoryId": categoryId,
            #"secrets": "/root/.config/youtubeuploader/client_secrets.json",
            "secrets": "/home/pgregg/timelapse-1/client_secrets.json",
            "playlistIds": [playlistIds],
            #"playlistTitles": ["Lake Travis Daily 4K Timelapse"]
        }

        with open(json_path, "w") as outfile:
            json.dump( youTubeMetaData, outfile)
            logger.info('YouTube Metadata file created')
            logger.info(f'JSON file created: {json_path}')
            publish_mqtt_status(f'JSON file created: {json_path}')
        
    except Exception as e:
            logger.error('Error creating JSON', exc_info=e)
            publish_mqtt_status('Error creating JSON', exc_info=e)

    # Create video
    logger.info('Starting video creation')
    publish_mqtt_status('Starting video creation')
    try:
        cmd = f'''ffmpeg -framerate {fps} -pattern_type glob -i "{photo_path}/*.jpg" -i /media/videos/tl_music/m4a_long/{audio_file_name} -s:v 3840x2160 -c:v libx264 -bf 2 -preset slow -crf 17 -pix_fmt yuv420p -shortest -movflags +faststart -vf "subtitles={srt_path}:force_style='PrimaryColour=&H999999,Fontsize=6,Fontname=Consolas,BackColour=&H80000000,Spacing=0.2,Outline=0,Shadow=0.75'" -y {video_path}'''
        logger.info(f'Executing command: {cmd}')
        publish_mqtt_status(f'Executing command: {cmd}')
        os.system(cmd)

        if os.path.exists(video_path):
            logger.info(f'Video created successfully: {video_path}')
            publish_mqtt_status(f'Video created successfully: {video_path}')

            #archive pictures
            try:
                archive_dir_path = '/media/timelapse_storage/photos'
                isExist = os.path.exists(archive_dir_path)
                if not isExist:
                    os.makedirs(archive_dir_path)
                    logger.info('Archive path directory created')
                    publish_mqtt_status('Archive path directory created')
                try:
                    archive_path = f'{archive_dir_path}/{instance_name}.tar.gz'
                    os.system(f"tar --directory {photo_path} --create --verbose --file {archive_path} .")
                    logger.info(f'Image archive created: {archive_path}' )
                    publish_mqtt_status(f'Image archive created: {archive_path}' )
                except Exception as e:
                    logger.error('Error at %s', 'division', exc_info=e)
                if os.path.exists(archive_path):
                    shutil.rmtree(photo_path)
                    logger.info(f'Local copy of photos deleted: {photo_path}' )
                    publish_mqtt_status(f'Local copy of photos deleted: {photo_path}' )
                else:
                    logger.error(f'Error: Could not delete local copy of photos: {photo_path}', exc_info=e)
                    publish_mqtt_status(f'Error: Could not delete local copy of photos: {photo_path}', exc_info=e)
                    
            except Exception as e:
                logger.error('Error creating photo archive', exc_info=e)
                publish_mqtt_status('Error creating photo archive', exc_info=e)
            return video_path, json_path
        else:
            logger.error('Error creating video')
            publish_mqtt_status('Error creating video')
            return None, None
        logger.info('Video complete.')
    except Exception as e:
        logger.error('Unknown error creating video', exc_info=e)
        publish_mqtt_status('Unknown error creating video', exc_info=e)
        return None, None
