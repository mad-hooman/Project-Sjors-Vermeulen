import os
import pickle
import subprocess
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# If modifying these SCOPES, delete the token.pickle file
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate_user():
    creds = None
    # The token.pickle file stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no valid credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_id.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('drive', 'v3', credentials=creds)

# Download file from Google Drive
def download_file(drive_service, file_id, file_name):
    request = drive_service.files().get_media(fileId=file_id)
    with open(file_name, 'wb') as f:
        request.execute(f)
    print(f"Downloaded {file_name} from Google Drive.")

# Upload file to Google Drive
def upload_file(drive_service, file_name, folder_id):
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_name, mimetype='video/mp4')
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Uploaded {file_name} to Google Drive with ID: {file.get('id')}")

# Combine JPG and MP3 to MP4 using ffmpeg
def combine_jpg_mp3_to_mp4(jpg_file, mp3_file, output_file):
    command = [
        "ffmpeg",
        "-loop", "1",
        "-i", jpg_file,
        "-i", mp3_file,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_file
    ]
    subprocess.run(command, check=True)
    print(f"Combined {jpg_file} and {mp3_file} into {output_file}")

if __name__ == "__main__":
    # Initialize Google Drive service
    drive_service = authenticate_user()

    # File IDs and folder IDs from Google Drive (update these environment variables in GitHub Actions)
    jpg_file_id = os.environ['JPG_FILE_ID']
    mp3_file_id = os.environ['MP3_FILE_ID']
    output_folder_id = os.environ['OUTPUT_FOLDER_ID']

    # Define file names for local use
    jpg_file = "input.jpg"
    mp3_file = "input.mp3"
    output_file = "output.mp4"

    # Download JPG and MP3 files
    download_file(drive_service, jpg_file_id, jpg_file)
    download_file(drive_service, mp3_file_id, mp3_file)

    # Combine JPG and MP3 into MP4
    combine_jpg_mp3_to_mp4(jpg_file, mp3_file, output_file)

    # Upload the MP4 file back to Google Drive
    upload_file(drive_service, output_file, output_folder_id)