# Discord Voice Bot

## Overview

This is a powerful Discord bot that provides real-time voice recognition, transcription, and text-to-speech capabilities integrated with advanced natural language processing (NLP). The bot connects to voice channels, listens to audio input, transcribes it, and generates intelligent responses using the LLaMA language model. Additionally, it features direct text-based interaction via a `/ask` command.

---

## Features

- **Voice Recognition**: Captures and processes audio from voice channels.
- **Speech-to-Text**: Uses OpenAI Whisper for high-quality transcription.
- **Text-to-Speech**: Converts responses into audio using Google Text-to-Speech (gTTS).
- **Advanced NLP**: Integrates with the LLaMA model to generate context-aware responses.
- **Silent Detection**: Automatically triggers transcription after detecting silence in the audio stream.

### Command Interaction:
- `/voice`: Enables voice channel audio capture and intelligent response generation.
- `/ask [message]`: Generates text-based responses to queries.

---

## Requirements

### Dependencies

To run this bot, you will need to install the required Python packages:

```bash
pip install discord.py pyttsx3 whisper transformers gtts langchain langchain-core
