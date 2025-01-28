import glob
import os
import sys
import torch
from moviepy.editor import VideoFileClip
import whisper
from whisper.utils import get_writer
import srt
import subprocess

device_to_translate = "cuda" # or "cpu"

model_size = "tiny"  # tiny,base,small,medium,large

# sometimes Whisper is not able to sync the subtitles correctly,
# this is the maximum time in seconds that the subtitles can be shifted dynamically
max_time_resync_block = "240"


def rename_and_remove_old_srt(synced_srt_path):
    new_srt_path = synced_srt_path.replace("_sync.srt", ".srt")

    if os.path.exists(new_srt_path):
        os.remove(new_srt_path)

    os.rename(synced_srt_path, new_srt_path)

    return new_srt_path

def sync_subtitles(video_file, srt_file_path):
    """
    Synchronizes subtitles using autosubsync.

    Args:
    video_file (str): Path to the video file.
    srt_file_path (str): Path to the SRT file.
    """
    output_srt_path = srt_file_path.replace(".srt", "_sync.srt")
    print(f"Synchronizing subtitles for {video_file} with {srt_file_path}")
    try:
        subprocess.run(
            ["autosubsync", "--max_shift_secs", max_time_resync_block, video_file, srt_file_path, output_srt_path],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Warning: autosubsync failed with error: {e}")
    return output_srt_path


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


def get_subs(audio_path, model=None):
    if device_to_translate == "cpu":
        model = whisper.load_model(model_size).to("cpu")
    elif device_to_translate == "cuda":
        torch.cuda.init()
        model = whisper.load_model(model_size).to("cuda")
    result = model.transcribe(audio_path, verbose=False, condition_on_previous_text=True)
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


def replace_extension_with_mp3(path):
    return os.path.splitext(path)[0] + ".mp3"


def extract_audio(path):
    # Determine the path for the audio file
    audio_path = replace_extension_with_mp3(path)

    # Check if the audio file already exists
    if os.path.exists(audio_path):
        print(f"Audio file already exists: {audio_path}")
        return
    # Load the video clip
    video_clip = VideoFileClip(path)

    # Extract the audio from the video clip
    audio_clip = video_clip.audio

    # Set the codec and write the audio as an MP3 file
    audio_clip.write_audiofile(replace_extension_with_mp3(path), codec='mp3')

    # Close the video and audio clips
    audio_clip.close()
    video_clip.close()


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



    folder = sys.argv[1]

    # Get a list of video files in the folder with .avi and .mkv extensions
    video_files = glob.glob(os.path.join(folder, '*.avi')) + glob.glob(os.path.join(folder, '*.mkv')) + \
                  glob.glob(os.path.join(folder, '*.mp4'))

    total_videos = len(video_files)

    for i, video_file in enumerate(video_files, start=1):
        print(f"Processing video {i}/{total_videos}")
        extract_audio(video_file)
        audio_path = replace_extension_with_mp3(video_file)
        transcription = get_subs(audio_path)
        srt_file_path = make_srt(transcription, audio_path, folder)
        print("truncate too long sentences")
        truncate_long_subs(srt_file_path, 120)
        synced_srt_path = sync_subtitles(video_file, srt_file_path)
        remove_all_mp3(folder)
        new_sub = rename_and_remove_old_srt(synced_srt_path)
        print(f"Synchronized subtitles saved to {new_sub}")

if __name__ == "__main__":
    main()