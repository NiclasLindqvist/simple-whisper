#! /bin/bash

# If the user has supplied --help or -h as any of the arguments, or no arguments at all, show the usage
if [[ "$@" == *"--help"* ]] || [[ "$@" == *"-h"* ]] || [ "$#" -eq 0 ]; then
    echo "Usage: $0 <transcription_file>"
    echo "  <transcription_file>          The file to summarize"
    exit 1
fi

# Check that ollama is running on 127.0.0.1:11434 using "lsof -i :11434"
if ! lsof -i :11434 &> /dev/null; then
    echo "Ollama is not running. Starting in the background..."
    ollama serve &
    # ollama run phi3 &
    sleep 5 # Wait for the server to start
fi

file_content=$(cat $1)

# Replace all new lines with pipes and escape double quotes
file_content=$(echo $file_content | sed 's/\n/|/g')
echo "Summarizing transcription: '$file_content'"

curl -X POST -H "Content-Type: application/json" -d '{
  "model": "mistral",
  "messages": [
    {
      "role": "user",
      "content": "Summarize this transcription: '"$file_content"'"
    }
  ],
  "stream": false
}' "http://localhost:11434/api/chat" | jq '.message.content' | sed 's/^"\(.*\)"$/\1/' > $2