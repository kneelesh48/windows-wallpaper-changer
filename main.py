import random
import requests
import os
import ctypes
import logging
import platform
import winsound
from config import wallpaper_subs

cd=os.path.dirname(os.path.abspath(__file__))

def logger_config():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

    file_handler = logging.FileHandler(f'{cd}/logfile.log',encoding = "UTF-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    logger.addHandler(stream_handler)
    return logger
logger=logger_config()

def wallpaper_changer():
    headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'}
    break_loop=False
    for _ in range(5): #if no image found, try another subreddit
        if break_loop: break
        sub=random.choice(wallpaper_subs)[0]
        logger.info(f"Subreddit: {sub}")
        data=requests.get(f"https://www.reddit.com/r/{sub}/top.json?t=day&limit=5",headers=headers).json()
        returned_len=len(data['data']['children'])
        n=random.randint(0,returned_len-1)
        for i in range(returned_len): #<returned_len> retries
            submission=data['data']['children'][(n+i)%returned_len]
            img_url=submission['data']['url']
            logger.info(img_url)
            if img_url in open(f'{cd}/downloaded_links.txt').read().split('\n'): #File already downloaded
                logger.info('File already downloaded')
                continue
            if submission['data']['post_hint']!='image': #url not image
                logger.info('File not image')
                continue
            if img_url[-3:]=='gif': #Image is gif
                logger.info('File is a gif')
                continue
            width=submission['data']['preview']['images'][0]['source']['width']
            height=submission['data']['preview']['images'][0]['source']['height']
            if width<=height: #vertical image
                logger.info('Vertical')
                continue
            if not (width>=1280 and height>=720): #Low resolution
                logger.info('Low resolution image')
                continue
            logger.info('Downloading file...')
            filepath=f"Images/{img_url.split('/')[-1]}"
            with open(filepath,'wb') as f:
                f.write(requests.get(img_url).content)
            with open(f'{cd}/downloaded_links.txt','a') as f:
                print(img_url,file=f)
            logger.info('File downloaded!')

            abs_img_path=f"{os.getcwd()}/{filepath}"
            if platform.system()=='Windows':
                ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_img_path, 0)
                winsound.MessageBeep()
            else:
                logger.info('Not implemented')
            logger.info('Wallpaper Changed!\n')
            break_loop=True
            break

if __name__ == '__main__':
    try:
        wallpaper_changer()
    except Exception as exception:
        logger.exception(f"{type(exception).__name__}: {exception}")
