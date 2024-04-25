#! /bin/bash

# If the user has supplied --help or -h as any of the arguments, or no arguments at all, show the usage
if [[ "$@" == *"--help"* ]] || [[ "$@" == *"-h"* ]] || [ "$#" -eq 0 ]; then
    echo "Usage: $0 <mp3_file> [--whisper-path] [--use-docker] [--model <model_name>] [--input_folder <input_folder>] [--output_folder <output_folder>] [--models_folder <models_folder>]"
    echo "  <mp3_file>          The MP3 file to transcribe"
    echo "  --whisper-path      The path to the whisper executable (default: ../whisper.cpp/main)"
    echo "  --use-docker        Use Docker to run the script (default: false)"
    echo "  --model             The model to use for transcription (default: ggml-large-v3-q5_0.bin)"
    echo "  --input_folder      The folder where the MP3 file is located (default: ./audios)"
    echo "  --output_folder     The folder where the output files will be saved (default: ./outputs)"
    echo "  --models_folder     The folder where the models are located (default: ./models)"
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

# Whisper path
if [[ "$@" == *"--whisper-path"* ]]; then
    whisper_path=$(echo "$@" | grep -oE -- "--whisper-path \K[^ ]+")
else
    whisper_path="../whisper.cpp/main"
fi

# Check if the user wants to use Docker
if [[ "$@" == *"--use-docker"* ]]; then
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        echo "Docker is not running. Please start Docker and try again."
        exit 1
    fi

    # Check if the Docker image exists
    if ! docker image inspect simple-whisper &> /dev/null; then
        echo "Docker image simple-whisper not found. Building the image..."
        docker build -t simple-whisper .
    fi

    echo "Running with Docker: docker run -it --rm -v ${models_folder}:/models -v ${input_folder}:/audios -v ${output_folder}:/outputs simple-whisper -i $1  -l sv -m $model -f $input_folder  -o $output_folder -n $models_folder -w ./main"
    docker run -it --rm -v ${models_folder}:/models -v ${input_folder}:/audios -v ${output_folder}:/outputs simple-whisper -i $1  -l sv -m $model -f $input_folder  -o $output_folder -n $models_folder -w ./main
    exit 0
else
    echo "Running without Docker: ./transcribe_mp3.ph $1 sv $model $input_folder $output_folder $models_folder $whisper_path"
    ./transcribe_mp3.sh -i $1 -l sv -m $model -f $input_folder -o $output_folder -n $models_folder -w $whisper_path
    exit 0
fi