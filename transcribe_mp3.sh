#! /bin/bash

# Take an MP3 file and convert it to a 16 kHz WAV file

# Check if the user provided _NO_ arguments
if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <mp3_file> [language] [model]" 
    exit 1
fi

# Check if language argument is provided, if not set to default
if [ "$#" -eq 2 ]; then
    language="$2"
else
    language="sv"
fi

# Check if model argument is provided, if not set to default
if [ "$#" -eq 3 ]; then
    model="$3"
else
    model="ggml-large-v3-q5_0.bin"
fi

# Get the input file from the command line argument
input_file="$1"

# Create the output file name by replacing the extension
# take only file name without extension or path
x_input_file=$(basename "$input_file")
# take only file name without extension
x_input_file="${x_input_file%.*}"

output_file="/tmp/${x_input_file}.wav"

# Check if the input file exists
if [ ! -f "/audios/$input_file" ]; then
    echo "File not found: $input_file"
    exit 1
fi

echo "Converting $input_file to $output_file"
# Use ffmpeg to convert the file
ffmpeg -i "/audios/$input_file" -ar 16000 "$output_file" -v quiet

# Check if the conversion was successful
if [ $? -eq 0 ]; then
    echo "Conversion successful. Output file: $output_file"
else
    echo "Conversion failed."
    exit 1
fi

echo "Transcribing $output_file"
./main -m /models/${model} -f $output_file -l ${language} -ovtt -otxt -of /outputs/${x_input_file} >> /outputs/${x_input_file}.log 2>&1
echo "Transcription finished. Output files: ${x_input_file}.vtt, ${x_input_file}.txt"