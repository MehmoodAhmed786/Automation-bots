import yt_dlp
import os
import csv

def download_youtube_video(video_url, username, save_path='/home/student/Documents/youtube_bot_downloads'):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    ydl_opts = {
        'outtmpl': os.path.join(save_path, f'{username}.%(ext)s'),
        'format': 'best',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',  # Convert videos to mp4 format
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            print(f"Video successfully downloaded: {filename}")
    except Exception as e:
        print(f"Error downloading video: {str(e)}")


def download_videos_from_file(file_path='youtube_video_urls.csv'):
    try:
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            
            for row in reader:
                if len(row) >= 2:
                    url = row[0].strip()  # URL is the first column
                    username = row[1].strip()  # Username is the second column
                    
                    if url and username:
                        print(f"Downloading video from URL: {url}")
                        download_youtube_video(url, username)
    except FileNotFoundError:
        print(f"File {file_path} not found. Please check the file path.")

# URL file path
url_file_path = '/home/student/Documents/youtube.csv'

# Call function to start downloading
download_videos_from_file(url_file_path)
