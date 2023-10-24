## genSubWhisper

### Why:
to generate subtitles to multiple videos

### Is not working?
* Install pytorch with cuda from [here](https://pytorch.org/get-started/locally/)
* execute ``pip install ffmpeg-python``
* execute ``pip install -U openai-whisper``
* try if cuda is installed by executing this: `` python -c "import torch; print(torch.rand(2,3).cuda())"``