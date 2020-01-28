#!/usr/bin/python3
#-*- encoding: utf-8 -*-

import os
import time
import logging

from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options

# Constants
LINK = 'https://m.yangshipin.cn/video?type=2&pid=600016637' # 雷神山
COMMAND_TEMPLATE_FFMPEG = 'ffmpeg -i "{link}" -bsf:a aac_adtstoasc -vcodec copy -c copy -crf 50 "{filename}"'
FILENAME_TEMPLATE = '{index}.mp4'

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup Selenium
browser = webdriver.Firefox()
options = Options()
options.add_argument('-headless')

# Get m3u8 link with Selenium and Headless Firefox
def get_m3u8_link(url):
    logger.info('  >>> Starting Firefox...')
    driver = webdriver.Firefox(options=options)
    logger.info('  >>> Loading website...')
    driver.get(url)
    logger.info('  >>> Loading video...')
    play_button = None
    while not play_button:
        try:
            play_button = driver.find_element_by_css_selector('.txp_svg_play')
        except Exception:
            pass
    play_button.click()
    m3u8_url = None
    while not m3u8_url:
        for request in driver.requests:
            if request.path.startswith('https://mobilelive') and ('m3u8' in request.path):
                logger.debug('  >>> Got link: %s' % request.path)
                driver.quit()
                return request.path
        time.sleep(1)

# Record stream with FFmpeg
def record():
    logger.info('>>> Fetching m3u8 link...')
    m3u8_link = get_m3u8_link(LINK)

    # Generate FFmpeg command
    files = [f for f in os.listdir('.') if os.path.isfile(os.path.join('.', f))]
    index = 1
    while FILENAME_TEMPLATE.format(index=index) in files:
        index += 1
    command = COMMAND_TEMPLATE_FFMPEG.format(
        link=m3u8_link,
        filename=FILENAME_TEMPLATE.format(index=index)
    )
    logger.info('>>> Running command: %s' % command)
    os.system(command)

while True:
    record()
