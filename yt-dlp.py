import yt_dlp 
import os
import ffmpeg
import gspread
from google.oauth2.service_account import Credentials
from mutagen.mp3 import MP3

SERVICE_ACCOUNT_FILE = "service_account.json"

creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
)
client = gspread.authorize(creds)

SHEET_ID = "1L5UcHvuLo3fFbz4XgXR2IDStG4PmP3FE_xOhVUvPDhs"
sheet = client.open_by_key(SHEET_ID).sheet1

SAVE_PATH = "C:/Users/happy/yt-dlp/bili/mp3"
COMPRESSED_PATH = "C:/Users/happy/yt-dlp/bili/mp3_compressed"
SPLIT_PATH = "C:/Users/happy/yt-dlp/bili/mp3_split"
DOWNLOADED_FILES_TRACKER = "downloaded_files.txt"

os.makedirs(SAVE_PATH, exist_ok=True)
os.makedirs(COMPRESSED_PATH, exist_ok=True)
os.makedirs(SPLIT_PATH, exist_ok=True)

def load_downloaded_files():
    if not os.path.exists(DOWNLOADED_FILES_TRACKER):
        return set()
    
    with open(DOWNLOADED_FILES_TRACKER, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

def save_downloaded_file(file_id):
    with open(DOWNLOADED_FILES_TRACKER, "a", encoding="utf-8") as f:
        f.write(file_id + "\n")

def sanitize_filename(filename):
    sanitized = "".join(c if c.isalnum() or c in " _-" else "_" for c in filename)
    return sanitized.strip()

def compress_audio(input_file, output_file, bitrate="192k"):
    try:
        print(f"Compressing audio: {input_file} → {output_file} ({bitrate})")
        ffmpeg.input(input_file).output(output_file, audio_bitrate=bitrate).run(overwrite_output=True, quiet=True)

        file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        if file_size > 25 and bitrate == "192k":
            print(f"Warning: 192kbps compression still exceeds 25MB ({file_size:.2f} MB), compressing again to 128kbps...")
            return compress_audio(output_file, output_file, bitrate="128k")

        print(f"Compression complete: {output_file} ({file_size:.2f} MB)")
        return output_file
    except Exception as e:
        print(f"Compression failed: {e}")
        return None

def split_audio(input_file):
    print(f"Checking audio length: {input_file}")

    audio = MP3(input_file)
    duration = audio.info.length  # seconds

    if duration <= 600:
        print("Audio is less than 10 minutes, no splitting required")
        return [input_file]  # Return the original file path

    print(f"Audio duration {duration / 60:.1f} minutes, starting split...")

    segment_files = []
    filename = sanitize_filename(os.path.basename(input_file).replace(".mp3", ""))

    for i, start_time in enumerate(range(0, int(duration), 600)):  # Split every 600 seconds
        segment_output = os.path.join(SPLIT_PATH, f"{filename}_part{i+1}.mp3")
        
        ffmpeg.input(input_file, ss=start_time, t=600).output(segment_output).run(overwrite_output=True, quiet=True)
        segment_files.append(segment_output)

        file_size = os.path.getsize(segment_output) / (1024 * 1024)  # MB
        if file_size > 25:
            print(f"Warning: Segment {i+1} still exceeds 25MB, compressing...")
            compressed_file = os.path.join(COMPRESSED_PATH, f"{filename}_part{i+1}.mp3")
            compress_audio(segment_output, compressed_file)
            segment_files[-1] = compressed_file

    print(f"Splitting complete, {len(segment_files)} segments created")
    return segment_files

def download_audio(video_title, video_url):
    os.makedirs(SAVE_PATH, exist_ok=True)

    video_title = sanitize_filename(video_title)
    output_path = os.path.join(SAVE_PATH, f"{video_title}.%(ext)s")

    if video_title in load_downloaded_files():
        print(f"Warning: {video_title} already downloaded, skipping.")
        return None

    ydl_opts = {
        "outtmpl": output_path,
        "format": "bestaudio",
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
    }

    try:
        print(f"Starting download: {video_title} - {video_url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(video_url, download=True)
        
        raw_audio = os.path.join(SAVE_PATH, f"{video_title}.mp3")

        segment_files = split_audio(raw_audio)

        save_downloaded_file(video_title)

        return segment_files
    except Exception as e:
        print(f"Download failed: {e}")
        return None

def get_latest_videos():
    print("Fetching latest video information from Google Sheets...")

    existing_data = sheet.get_all_values()
    
    if len(existing_data) <= 1:
        print("No video data in Google Sheets, waiting for next check...")
        return []

    new_videos = []

    for row in existing_data[1:]:  # Skip header
        if len(row) < 2:
            continue  # Skip incomplete data
        
        video_title = sanitize_filename(row[0])
        video_url = row[1]

        if video_title not in load_downloaded_files():
            new_videos.append((video_title, video_url))
        else:
            print(f"Warning: {video_title} already downloaded, skipping.")

    return new_videos

def process_new_videos():
    new_videos = get_latest_videos()
    downloaded_files = []

    for video_title, video_url in new_videos:
        segment_files = download_audio(video_title, video_url)
        if segment_files:
            downloaded_files.extend(segment_files)

    return downloaded_files

if __name__ == "__main__":
    process_new_videos()
