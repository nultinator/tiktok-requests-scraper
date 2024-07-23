import os
import csv
import requests
import json
import logging
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import concurrent.futures
from dataclasses import dataclass, field, fields, asdict

API_KEY = ""

with open("config.json", "r") as config_file:
    config = json.load(config_file)
    API_KEY = config["api_key"]


## Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_channel(channel_name, location, retries=3):
    url = f"https://www.tiktok.com/@{channel_name}"
    tries = 0
    success = False
    
    while tries <= retries and not success:
        try:
            response = requests.get(url)
            logger.info(f"Recieved [{response.status_code}] from: {url}")
            if response.status_code == 200:
                success = True
            
            else:
                raise Exception(f"Failed request, Status Code {response.status_code}")
                
                ## Extract Data

            soup = BeautifulSoup(response.text, "html.parser")            
            script_tag = soup.select_one("script[id='__UNIVERSAL_DATA_FOR_REHYDRATION__']")

            json_data = json.loads(script_tag.text)
            user_info = json_data["__DEFAULT_SCOPE__"]["webapp.user-detail"]["userInfo"]
            stats = user_info["stats"]


            follower_count = stats["followerCount"]
            likes = stats["heartCount"]
            video_count = stats["videoCount"]

            user_data = user_info["user"]
            unique_id = user_data["uniqueId"]
            nickname = user_data["nickname"]
            verified = user_data["verified"]
            signature = user_data["signature"]

            profile_data = {
                "name": unique_id,
                "follower_count": follower_count,
                "likes": likes,
                "video_count": video_count,
                "nickname": nickname,
                "verified": verified,
                "signature": signature
            }

            print(profile_data)        
                    
        except Exception as e:
            logger.error(f"An error occurred while processing page {url}: {e}")
            logger.info(f"Retrying request for page: {url}, retries left {retries-tries}")
            tries+=1
    if not success:
        raise Exception(f"Max Retries exceeded: {retries}")



def start_scrape(channel_list, location, max_threads=5, retries=3):
    for channel in channel_list:
        scrape_channel(channel, location, data_pipeline=data_pipeline, retries=retries)


if __name__ == "__main__":

    MAX_RETRIES = 3
    MAX_THREADS = 5
    LOCATION = "uk"

    logger.info(f"Scrape starting...")

    ## INPUT ---> List of keywords to scrape
    channel_list = [
        "paranormalpodcast",
        "theparanormalfiles",
        "jdparanormal",
        "paranormal.com7",
        "paranormal064",
        "marijoparanormal",
        "paranormal_activityghost",
        "youtube_paranormal",
        "paranormal140",
        "paranormal.51"
        ]

    ## Job Processes
    start_scrape(channel_list, LOCATION, retries=MAX_RETRIES)
    logger.info(f"Scrape complete.")