import os
from moviepy.editor import ImageClip, AudioFileClip
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Google Drive API setup
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'credentials.json'  # Path to your Google API credentials JSON

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

def combine_jpg_mp3_to_mp4(jpg_path, mp3_path, output_path):
    """Combine a JPG and MP3 file to create an MP4."""
    image_clip = ImageClip(jpg_path, duration=10)  # Duration can be modified
    audio_clip = AudioFileClip(mp3_path)
    video_clip = image_clip.set_audio(audio_clip)
    video_clip.write_videofile(output_path, codec='libx264')

def upload_to_drive(file_path, folder_id):
    """Upload file to Google Drive in the specified folder."""
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype='video/mp4')
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"File uploaded with ID: {file.get('id')}")

# Paths to JPG and MP3
jpg_path = "your_image.jpg"
mp3_path = "your_audio.mp3"
output_path = "output_video.mp4"

# Combine JPG and MP3
combine_jpg_mp3_to_mp4(jpg_path, mp3_path, output_path)

# Upload MP4 to Google Drive
folder_id = 'your_folder_id'  # Replace with your Google Drive folder ID
upload_to_drive(output_path, folder_id)