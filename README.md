## genSubWhisper

### Why:
to generate subtitles to multiple videos

### Is not working?
* Install pytorch with cuda from [here](https://pytorch.org/get-started/locally/)
* install ffmpeg from [here](https://github.com/GyanD/codexffmpeg/releases/tag/2023-11-28-git-47e214245b)
* (on windows) add to path ``setx /m PATH "C:\ffmpeg\bin;%PATH%"``
* test if ffmpeg is working ``ffmpeg -version``
* execute ``pip install ffmpeg-python``
* execute ``pip install -U openai-whisper``
* try if cuda is installed by executing this: `` python -c "import torch; print(torch.rand(2,3).cuda())"``
* restart windows