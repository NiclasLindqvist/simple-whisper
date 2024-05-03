FROM ghcr.io/ggerganov/whisper.cpp:main

RUN apt-get update && apt-get install -y \
    python3.12 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3.12 /usr/bin/python3
RUN ln -s /usr/bin/python3.12 /usr/bin/python

COPY transcribe_mp3.sh transcribe_mp3.py ./
RUN chmod +x transcribe_mp3.sh


ENTRYPOINT ["python", "-m", "transcribe_mp3"]
CMD ["--help"]