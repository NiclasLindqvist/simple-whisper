# Simple Whisper

## Build Setup

``` bash
docker build -t simple-whisper .
```

## Download models
Follow instructions on [https://github.com/ggerganov/whisper.cpp/blob/master/models/README.md](https://github.com/ggerganov/whisper.cpp/blob/master/models/README.md)
For the default settings, download this model: [https://huggingface.co/ggerganov/whisper.cpp/blob/main/ggml-large-v3-q5_0.bin](ggml-large-v3-q5_0.bin)
Put the model in the `models` folder

## Run
- Put your audio files in the `audios` folder
- Run the application `./process.sh audios/your_audio_file.mp3`
- The output will be in the `output` folder

