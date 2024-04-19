#! /bin/bash

# If the user has supplied --help or -h as any of the arguments, show the usage
if [[ "$@" == *"--help"* ]] || [[ "$@" == *"-h"* ]]; then
    echo "Usage: $0 <mp3_file>  [--model <model_name>] [--input_folder <input_folder>] [--output_folder <output_folder>] [--models_folder <models_folder>]"
    echo "  <mp3_file>          The MP3 file to transcribe"
    echo "  --model             The model to use for transcription (default: ggml-large-v3-q5_0.bin)"
    echo "  --input_folder      The folder where the MP3 file is located (default: ./audios)"
    echo "  --output_folder     The folder where the output files will be saved (default: ./outputs)"
    echo "  --models_folder     The folder where the models are located (default: ./models)"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Use defaults if some arguments are missing
# Model
if [[ "$@" == *"--model"* ]]; then
        model=$(echo "$@" | grep -oE -- "--model \K[^ ]+")
    else
    model="ggml-large-v3-q5_0.bin"
fi

# Input folder
if [[ "$@" == *"--input_folder"* ]]; then
    input_folder=$(echo "$@" | grep -oE -- "--input_folder \K[^ ]+")
else
    input_folder="./audios"
fi

# Output folder
if [[ "$@" == *"--output_folder"* ]]; then
    output_folder=$(echo "$@" | grep -oE -- "--output_folder \K[^ ]+")
else
    output_folder="./outputs"
fi

# Models folder
if [[ "$@" == *"--models_folder"* ]]; then
    models_folder=$(echo "$@" | grep -oE -- "--models_folder \K[^ ]+")
else
    models_folder="./models"
fi

docker run -it --rm -v ${models_folder}:/models -v ${input_folder}:/audios -v ${output_folder}:/outputs simple-whisper $1 sv $model