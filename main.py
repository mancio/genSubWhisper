from moviepy.editor import VideoFileClip
import whisper
from whisper.utils import get_writer


def get_subs(path):
    model = whisper.load_model("base")
    result = model.transcribe(path, verbose=False)
    return result


def make_srt():
    # Save as an SRT file
    srt_writer = get_writer("srt", r'C:\Users\andma\Downloads\')
    srt_writer(result, audio)


def extract_audio(input_video_path, output_audio_path):
    # Load the video clip
    video_clip = VideoFileClip(input_video_path)

    # Extract the audio from the video clip
    audio_clip = video_clip.audio

    # Set the codec and write the audio as an MP3 file
    audio_clip.write_audiofile(output_audio_path, codec='mp3')

    # Close the video and audio clips
    audio_clip.close()
    video_clip.close()


def main():
    input_video_path = r'D:\torrent\Less.Than.Perfect.s01.DVDRip\output_folder\Less.Than.Perfect.s01e01.Pilot.DVDRip.rus.eng.Jetsam.avi'
    # output_audio_path = r'D:\torrent\Less.Than.Perfect.s01.DVDRip\output_folder\test.mp3'
    output_audio_path = r'C:\Users\andma\Downloads\sample-0.mp3'

    # extract_audio(input_video_path, output_audio_path)

    print(get_subs(output_audio_path))


if __name__ == "__main__":
    main()
