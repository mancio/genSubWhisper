import glob
import os

import torch
from moviepy.editor import VideoFileClip
import whisper
from whisper.utils import get_writer

import names


def get_subs(audio_path, device, model=None):
    if device == names.CPU:
        model = whisper.load_model("base").to("cpu")
    elif device == names.GPU_GEFORCE_CUDA:
        torch.cuda.init()
        model = whisper.load_model("base").to("cuda")
    result = model.transcribe(audio_path, verbose=False)
    return result


def make_srt(result, audio_path, main_folder):
    # Define the options dictionary
    options = {
        "output_format": "srt",  # Specify the desired output format
        "max_line_width": None,
        "max_line_count": None,
        "highlight_words": False
    }

    # Save as an SRT file
    srt_writer = get_writer(options["output_format"], main_folder)
    srt_writer(result, audio_path, options)  # Pass the options dictionary to the writer


def extract_audio(path):
    # Load the video clip
    video_clip = VideoFileClip(path)

    # Extract the audio from the video clip
    audio_clip = video_clip.audio

    # Set the codec and write the audio as an MP3 file
    audio_clip.write_audiofile(replace_extension_with_mp3(path), codec='mp3')

    # Close the video and audio clips
    audio_clip.close()
    video_clip.close()


def replace_extension_with_mp3(file_path):
    # Get the directory path and the file's base name (without extension)
    directory_path, base_name = os.path.split(file_path)
    base_name_without_extension, _ = os.path.splitext(base_name)

    # Create and return the new file path with ".mp3" extension
    new_file_path = os.path.join(directory_path, base_name_without_extension + ".mp3")

    return new_file_path


def remove_all_mp3(path):
    for file in os.listdir(path):
        if file.endswith(".mp3"):
            file_path = os.path.join(path, file)
            os.remove(file_path)


def main():
    device_to_translate = names.GPU_GEFORCE_CUDA
    # device_to_translate = names.CPU

    folder = r'D:\torrent\Less.Than.Perfect.s01.DVDRip\output_folder\test'

    # Get a list of video files in the folder with .avi and .mkv extensions
    video_files = glob.glob(os.path.join(folder, '*.avi')) + glob.glob(os.path.join(folder, '*.mkv'))
    total_videos = len(video_files)

    for i, video_file in enumerate(video_files, start=1):
        print(f"Processing video {i}/{total_videos}")
        extract_audio(video_file)
        audio_path = replace_extension_with_mp3(video_file)
        transcription = get_subs(audio_path, device_to_translate)
        make_srt(transcription, audio_path, folder)
        remove_all_mp3(folder)


if __name__ == "__main__":
    main()
