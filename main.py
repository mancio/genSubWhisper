import glob
import os
import sys

import torch
from moviepy.editor import VideoFileClip
import whisper
from whisper.utils import get_writer

import srt

import names

model_size = "tiny"  # tiny,base,small,medium,large


def truncate_long_subs(srt_file_path, max_chars):
    """
    Truncates subtitles that exceed a certain number of characters in an SRT file.

    Args:
    srt_file_path (str): Path to the SRT file.
    max_chars (int): Maximum allowed characters in a subtitle.
    """
    with open(srt_file_path, 'r', encoding='utf-8') as file:
        subtitles = list(srt.parse(file.read()))

    adjusted_subs = []
    for sub in subtitles:
        if len(sub.content) > max_chars:
            # Truncate the content to the max allowed characters
            sub.content = sub.content[:max_chars]
        adjusted_subs.append(sub)

    # Write the adjusted subtitles back to the SRT file
    with open(srt_file_path, 'w', encoding='utf-8') as file:
        file.write(srt.compose(adjusted_subs))


def get_subs(audio_path, device, model=None):
    if device == names.CPU:
        model = whisper.load_model(model_size).to("cpu")
    elif device == names.GPU_GEFORCE_CUDA:
        torch.cuda.init()
        model = whisper.load_model(model_size).to("cuda")
    result = model.transcribe(audio_path, verbose=False, condition_on_previous_text=False)
    return result


def make_srt(result, audio_path, main_folder):
    # Define the options dictionary
    options = {
        "output_format": "srt",  # Specify the desired output format
        "max_line_width": None,
        "max_line_count": None,
        "highlight_words": False,
    }

    srt_file_name = os.path.basename(audio_path).rsplit('.', 1)[0] + ".srt"
    srt_file_path = os.path.join(main_folder, srt_file_name)

    srt_writer = get_writer(options["output_format"], main_folder)
    srt_writer(result, audio_path, options)

    return srt_file_path


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
    # Check if the folder name is provided
    if len(sys.argv) < 2:
        print("Error: No folder name specified.")
        sys.exit(1)  # Exit the script with an error code

    device_to_translate = names.GPU_GEFORCE_CUDA
    # device_to_translate = names.CPU

    folder = sys.argv[1]

    # Get a list of video files in the folder with .avi and .mkv extensions
    video_files = glob.glob(os.path.join(folder, '*.avi')) + glob.glob(os.path.join(folder, '*.mkv')) + \
                  glob.glob(os.path.join(folder, '*.mp4'))

    total_videos = len(video_files)

    for i, video_file in enumerate(video_files, start=1):
        print(f"Processing video {i}/{total_videos}")
        extract_audio(video_file)
        audio_path = replace_extension_with_mp3(video_file)
        transcription = get_subs(audio_path, device_to_translate)
        srt_file_path = make_srt(transcription, audio_path, folder)
        print("truncate too long sentences")
        truncate_long_subs(srt_file_path, 80)
        remove_all_mp3(folder)


if __name__ == "__main__":
    main()
