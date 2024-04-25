#! /bin/bash

# Take an MP3 file and convert it to a 16 kHz WAV file

# Set default values
language="sv"
model="ggml-large-v3-q5_0.bin"
input_folder="/audios"
output_folder="/outputs"
models_folder="/models"
whisper_path="../whisper.cpp/main"

# Parse command line arguments
while getopts i:l:m:f:o:n:w: flag
do
    case "${flag}" in
        i) input_file=${OPTARG};;
        l) language=${OPTARG};;
        m) model=${OPTARG};;
        f) input_folder=${OPTARG};;
        o) output_folder=${OPTARG};;
        n) models_folder=${OPTARG};;
        w) whisper_path=${OPTARG};;
    esac
done

# Check if the user provided _NO_ arguments
if [ -z "$input_file" ]; then
    echo "Usage: $0 -i <mp3_file> [-l language] [-m model] [-f input_folder] [-o output_folder] [-m models_folder] [-w whisper_path]" 
    exit 1
fi

# Create the output file name by replacing the extension
# take only file name without extension or path
x_input_file=$(basename "$input_file")
# take only file name without extension
x_input_file="${x_input_file%.*}"

output_file="/tmp/${x_input_file}.wav"

# Check if the input file exists
if [ ! -f "$input_folder/$input_file" ]; then
    echo "File not found: $input_folder/$input_file"
    exit 1
fi

echo "Converting $input_folder/$input_file to $output_file"
trap "rm -f $output_file" EXIT
# Use ffmpeg to convert the file
ffmpeg -i "$input_folder/$input_file" -ar 16000 "$output_file" -v quiet

# Check if the conversion was successful
if [ $? -eq 0 ]; then
    echo "Conversion successful. Output file: $output_file"
else
    echo "Conversion failed."
    exit 1
fi

echo "Transcribing $output_file"
echo "Running: $whisper_path -m ${models_folder}/${model} -f $output_file -l ${language} -ovtt -otxt -of ${output_folder}/${x_input_file}"
$whisper_path -m ${models_folder}/${model} -f $output_file -l ${language} -ovtt -otxt -of ${output_folder}/${x_input_file} >> ${output_folder}/${x_input_file}.log 2>&1
echo "Transcription finished. Output files: ${x_input_file}.vtt, ${x_input_file}.txt"