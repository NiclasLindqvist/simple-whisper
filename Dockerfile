FROM ghcr.io/ggerganov/whisper.cpp:main

COPY transcribe_mp3.sh .
RUN chmod +x transcribe_mp3.sh

ENTRYPOINT ["./transcribe_mp3.sh"]
CMD ["/tmp/input.mp3"]