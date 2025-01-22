import os
import re
import shutil
import traceback
import subprocess
import json
import mimetypes
import time
import pandas as pd

from print_text3 import xprint

BIN_FOLDER = "./bin.tmp"
OUTPUT_FOLDER = "../Output.tmp"
VIDEOS_FOLDER = "../Video.tmp/input"
TEMP_FOLDER = "../Temp.tmp"

os.environ['FFMPEG_BINARY'] = "ffmpeg"
os.environ['IMAGEMAGICK_BINARY'] = "magick"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(VIDEOS_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

with open('../CONFIG.json') as f:
    config = json.load(f)

def get_codec():
    try:
        data = subprocess.check_output("lspci | grep -i vga", shell=True).decode().lower()
        if "nvidia" in data:
            return "h264_nvenc"
        elif "amd" in data or "radeon" in data:
            return "h264_amf"
        elif "intel" in data:
            return "h264_qsv"
        else:
            return "libx264"
    except Exception as e:
        print("Error detecting GPU:", e)
        return "libx264"

CODEC = get_codec()
print(f"Using {CODEC} codec")

def convert_to_mp4(video, output, vc=CODEC, ac="aac", bitrate=None, fps=None, audio_bitrate=None):
    print("\n\n=== Converting ===\n", video, output)
    more = []
    if bitrate:
        more.extend(["-b:v", str(bitrate)])
    if fps:
        more.extend(["-r", str(fps)])
    if audio_bitrate:
        more.extend(["-b:a", str(audio_bitrate)])

    subprocess.call([os.environ['FFMPEG_BINARY'], "-i", video, "-c:v", vc, "-c:a", ac, "-y", "-preset", "slow"] + more + [output])

def export_videos(image, audio, output, vc=CODEC, ac="aac", bitrate=None, fps=None, audio_bitrate=None):
    print("\n\n", output)
    time.sleep(1)

    ffmpeg_args = []
    ffmpeg_i_args = []

    if vc == 'h264_nvenc':
        ffmpeg_i_args = [
            '-hwaccel', 'cuda',
        ]
        ffmpeg_args = [
            '-pix_fmt', 'yuv420p',
            '-bufsize:v', '8M', 
            '-profile:v', 'main',
        ]

    more = [] + ffmpeg_args
    if bitrate:
        more.extend(["-b:v", str(bitrate)])
    if fps:
        more.extend(["-r", str(fps)])
    if audio_bitrate:
        more.extend(["-b:a", str(audio_bitrate)])

    print(more)

    subprocess.call([
        os.environ['FFMPEG_BINARY'],
        "-loop", "1",
        "-i", image,
        "-i", audio,
        "-c:v", vc,
        "-c:a", ac,
        "-strict", "experimental",
        "-shortest",
        "-y", 
        "-preset", "fast",
    ] + ffmpeg_i_args + more + [output])

def main():
    AUDIOS = [i for i in os.scandir(VIDEOS_FOLDER) if mimetypes.guess_type(i.name) and mimetypes.guess_type(i.name)[0].startswith("audio")]
    IMAGES = [i for i in os.scandir(VIDEOS_FOLDER) if mimetypes.guess_type(i.name) and mimetypes.guess_type(i.name)[0].startswith("image")]

    for audio in AUDIOS:
        code = re.search(r"(\d+)", audio.name).group(1)
        audio_name = audio.name
        audio_path = audio.path

        for image in IMAGES:
            i_code = re.search(r"(\d+)", image.name).group(1)
            if i_code == code:
                image_name = image.name
                image_path = image.path
                break
        else:
            xprint(f"Image not found for {audio_name}")
            continue

        xprint(f"Processing {audio_name} and {image_name}")

        output_name = image_name.rsplit(".", 1)[0] + ".mp4"
        output = f"{OUTPUT_FOLDER}/{output_name}"

        audio_bitrate = config["AUDIO_BITRATE"]
        if audio_bitrate == "0":
            audio_bitrate = None

        bitrate = config["BITRATE"]

        export_videos(image_path, audio_path, output, bitrate=bitrate, audio_bitrate=audio_bitrate)

if __name__ == "__main__":
    try:
        main()
        xprint("\n\n/g/All Parts are processed!/=/\n")
    except Exception:
        traceback.print_exc()

    shutil.rmtree(TEMP_FOLDER, ignore_errors=True)
    input("\n\nPress Enter to Exit...")
