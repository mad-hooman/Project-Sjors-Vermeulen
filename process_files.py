import requests
import zipfile
import os
import glob
from moviepy.editor import ImageClip, AudioFileClip

# Function to get the direct download link from gofile.io
def get_direct_download_link(gofile_link, account_token):
    # Extract the file ID from the shared link
    file_id = gofile_link.split("/")[-1]
    
    # Make an API request to get file info
    response = requests.get(
        f"https://api.gofile.io/getContent?contentId={file_id}&token={account_token}"
    )
    
    try:
        response_data = response.json()
    except ValueError:
        print("Error: Unable to parse JSON response from Gofile API")
        print("Response status code:", response.status_code)
        print("Response text:", response.text)
        raise

    if response_data['status'] == 'ok':
        # Extract direct download link from API response
        return response_data['data']['contents'][file_id]['link']
    else:
        raise ValueError("Failed to retrieve direct download link from gofile.io")

# Download and unzip files from gofile.io
def download_and_unzip(gofile_link, account_token, extract_to="input_files"):
    # Get the direct download link using the API
    direct_link = get_direct_download_link(gofile_link, account_token)
    
    # Download the zip file
    response = requests.get(direct_link, stream=True)
    zip_path = "input_files.zip"
    with open(zip_path, "wb") as file:
        file.write(response.content)

    # Unzip the file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    os.remove(zip_path)  # Clean up the zip file
    print("Downloaded and unzipped the input files.")

# Process JPG + MP3 to MP4
def process_files(input_dir="input_files", output_dir="output_videos"):
    os.makedirs(output_dir, exist_ok=True)

    jpg_files = sorted(glob.glob(f"{input_dir}/*.jpg"))
    mp3_files = sorted(glob.glob(f"{input_dir}/*.mp3"))

    for jpg, mp3 in zip(jpg_files, mp3_files):
        image_clip = ImageClip(jpg).set_duration(AudioFileClip(mp3).duration)
        audio_clip = AudioFileClip(mp3)
        video_clip = image_clip.set_audio(audio_clip)

        # Output file name
        output_file = os.path.join(output_dir, f"{os.path.basename(jpg).split('.')[0]}.mp4")
        video_clip.write_videofile(output_file, codec="libx264", fps=24)
        print(f"Created {output_file}")

# Zip the output files
def zip_output_files(output_dir="output_videos", output_zip="output_videos.zip"):
    with zipfile.ZipFile(output_zip, 'w') as zipf:
        for root, _, files in os.walk(output_dir):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), output_dir))
    print("Output files zipped successfully.")

# Main execution
if __name__ == "__main__":
    gofile_link = os.getenv("GOFILE_LINK")
    account_token = os.getenv("GOFILE_API_TOKEN")
    download_and_unzip(gofile_link, account_token)
    process_files()
    zip_output_files()