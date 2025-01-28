## genSubWhisper

### Why:
to generate subtitles to multiple videos

### Is not working?
* Install pytorch with cuda from [here](https://pytorch.org/get-started/locally/)
* install ffmpeg from [here](https://github.com/GyanD/codexffmpeg/releases/tag/2023-11-28-git-47e214245b)
* (on windows) add to path `setx /m PATH "C:\ffmpeg\bin;%PATH%"`
* test if ffmpeg is working `ffmpeg -version`
* execute `pip install ffmpeg-python`
* execute `pip install -U openai-whisper`
* try if cuda is installed by executing this: `python -c "import torch; print(torch.rand(2,3).cuda())"`
* restart windows

### Usage:
1. Place your video files in a folder.
2. Run the script with the folder name as an argument:
   ```sh
   python main.py <folder_name>
   
### Configuration:
* ``max_time_resync_block``: This variable defines the maximum time in seconds that the subtitles can be shifted dynamically
to synchronize with the video. By default, it is set to 240 seconds (4 minutes). 
For example, to allow a maximum shift of 5 minutes, change it to:
``max_time_resync_block = "300``
* ``device_to_translate``: This variable defines the device to use for translation. By default, it is set to "cuda" to use the GPU.
* ``model_size = "tiny"``: This variable defines the model size to use for translation. By default, it is set to "tiny" to use the smallest model.