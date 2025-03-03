import gspread
from google.oauth2.service_account import Credentials
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

SERVICE_ACCOUNT_FILE = "service_account.json"
creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
)
client = gspread.authorize(creds)

CHANNEL_SHEET_ID = "1APMZW2wb5B-FmyLkWo0ZXR4EB6bXMKm3aGvDhekMs8w"
VIDEO_SHEET_ID = "1L5UcHvuLo3fFbz4XgXR2IDStG4PmP3FE_xOhVUvPDhs"

CHANNEL_SHEET_NAME = "关注频道"
VIDEO_SHEET_NAME = "视频列表"

channel_sheet = client.open_by_key(CHANNEL_SHEET_ID).worksheet(CHANNEL_SHEET_NAME)
video_sheet = client.open_by_key(VIDEO_SHEET_ID).worksheet(VIDEO_SHEET_NAME)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
print(f"Current API Key: {YOUTUBE_API_KEY}") 

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_DETAILS_URL = "https://www.googleapis.com/youtube/v3/videos"

def get_existing_channels():
    existing_channels = set()
    video_data = video_sheet.get_all_values()

    for row in video_data[1:]:
        if len(row) > 2:
            existing_channels.add(row[2])

    return existing_channels

def get_channel_id_from_url(channel_url):
    if "youtube.com/@" in channel_url:
        channel_handle = channel_url.split("@")[-1]
        url = f"https://www.googleapis.com/youtube/v3/channels?part=id&forHandle=@{channel_handle}&key={YOUTUBE_API_KEY}"
        response = requests.get(url)
        data = response.json()

        if "items" in data and len(data["items"]) > 0:
            channel_id = data["items"][0]["id"]
            print(f"Retrieved: {channel_handle} → {channel_id}")
            return channel_id
        else:
            print(f"Channel ID not found: {channel_url}")
            return None

    elif "youtube.com/channel/" in channel_url:
        return channel_url.split("channel/")[-1]
    else:
        print(f"Unable to parse channel URL: {channel_url}")
        return None

def update_channel_ids():
    channels_data = channel_sheet.get_all_values()
    for index, row in enumerate(channels_data[1:], start=2):
        if len(row) < 4:
            continue
        
        channel_url, channel_id = row[0], row[1]

        if not channel_id:
            print(f"Fetching Channel ID: {channel_url}")
            channel_id = get_channel_id_from_url(channel_url)

            if channel_id:
                channel_sheet.update_cell(index, 2, channel_id)
                print(f"Channel ID updated in Google Sheets: {channel_id}")

def get_tracked_channels():
    channels_data = channel_sheet.get_all_values()
    channels = []

    for row in channels_data[1:]:
        if len(row) < 4:
            continue

        channel_id, min_views, min_likes = row[1], row[2], row[3]

        if not channel_id:
            continue

        try:
            min_views = int(min_views)
            min_likes = int(min_likes)
        except ValueError:
            print(f"Invalid min views/likes for channel {channel_id}, skipping...")
            continue

        channels.append((channel_id, min_views, min_likes))

    return channels

def get_latest_videos(channel_id, full_scan=False):
    max_results = 50 if full_scan else 5
    
    params = {
        "part": "snippet",
        "channelId": channel_id,
        "maxResults": max_results,
        "order": "date",
        "type": "video",
        "key": YOUTUBE_API_KEY
    }
    response = requests.get(YOUTUBE_SEARCH_URL, params=params)
    data = response.json()

    if "items" not in data or len(data["items"]) == 0:
        print(f"No videos found for channel {channel_id}")
        return []

    video_list = []
    for video in data["items"]:
        video_id = video["id"]["videoId"]
        title = video["snippet"]["title"]
        publish_time = video["snippet"]["publishedAt"]
        video_list.append((video_id, title, publish_time))

    return video_list

def get_video_stats(video_id):
    params = {
        "part": "statistics",
        "id": video_id,
        "key": YOUTUBE_API_KEY
    }
    response = requests.get(YOUTUBE_VIDEO_DETAILS_URL, params=params)
    data = response.json()

    if "items" not in data or len(data["items"]) == 0:
        print(f"Failed to retrieve stats for video {video_id}")
        return None, None

    stats = data["items"][0]["statistics"]
    views = int(stats.get("viewCount", 0))
    likes = int(stats.get("likeCount", 0)) if "likeCount" in stats else 0
    return views, likes

def video_already_tracked(video_url):
    existing_data = video_sheet.get_all_values()
    video_urls = [row[1] for row in existing_data[1:] if len(row) > 1]
    return video_url in video_urls

def track_new_videos():
    channels = get_tracked_channels()
    existing_channels = get_existing_channels()

    for channel_id, min_views, min_likes in channels:
        is_new_channel = channel_id not in existing_channels
        
        print(f"Checking latest videos for channel {channel_id}... {'(New Channel - Full Scan)' if is_new_channel else '(Existing Channel - Recent Only)'}")

        video_list = get_latest_videos(channel_id, full_scan=is_new_channel)
        
        for video_id, title, publish_time in video_list:
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            if video_already_tracked(video_url):
                print(f"Video already exists, skipping: {title}")
                continue

            views, likes = get_video_stats(video_id)
            if views is None or likes is None:
                continue

            print(f"{title} - {views} views, {likes} likes")

            if views >= min_views and likes >= min_likes:
                print(f"Meets criteria, adding to Google Sheets: {title}")
                video_sheet.append_row([title, video_url, channel_id, publish_time, views, likes])
            else:
                print(f"Does not meet minimum requirements, skipping: {title}")

if __name__ == "__main__":
    print("\n==================== Updating Channel IDs ====================")
    update_channel_ids()
    
    print("\n==================== Checking YouTube Channels ====================")
    track_new_videos()
    
    print("\nMonitoring complete!")
