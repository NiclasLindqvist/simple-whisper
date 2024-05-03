.DEFAULT: run

ARGS := audios/niclas_babblar.m4a
run: install
	@pipenv run python app $(ARGS)

install: install_homebrew install_dependencies download_models
	@pipenv install

download_models:
	@mkdir -p models
	@wget -O https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-q5_0.bin models/ggml-large-v3-q5_0.bin

install_homebrew:
	@if ! command -v brew > /dev/null; then \
		echo "Installing Homebrew"; \
		/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"; \
	else \
		echo "Updating Homebrew"; \
		brew update; \
	fi

install_dependencies:
	@if ! command -v ffmpeg > /dev/null; then \
		echo "Installing ffmpeg"
		brew install ffmpeg
	fi
	@if ! command -v python > /dev/null; then \
		echo "Installing python"
		brew install python
	fi
	@if ! command -v pipenv > /dev/null; then \
		echo "Installing pipenv"
		pip install pipenv
	fi
	@if ! command -v wget > /dev/null; then \
		echo "Installing wget"
		brew install wget
	fi