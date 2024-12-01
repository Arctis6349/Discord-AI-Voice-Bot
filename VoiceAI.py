import discord
from discord.ext import commands, tasks
from discord import FFmpegPCMAudio
import random
from discord.ext import voice_recv
import wave
import asyncio
import os
import time
import tempfile



initial_extensions = []

Lists = []

Token = ''


intents = discord.Intents.default()

intents.all()

intents.members = True

intents.messages = True

intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)







server_id = discord.Object(id = 912368508808073227)



from transformers import pipeline

import whisper
from concurrent.futures import ThreadPoolExecutor
import pyttsx3
# Preload Whisper model
model = whisper.load_model("base")  # Load the Whisper model once at startup
executor = ThreadPoolExecutor()  # Thread pool for non-blocking transcription
from gtts import gTTS

from langchain_ollama import OllamaLLM
from llm_axe import OnlineAgent
from langchain_core.prompts import ChatPromptTemplate
class CustomAudioSink(voice_recv.AudioSink):
    def __init__(self,target_user_id):
        super().__init__()
        self.audio_buffer = bytearray()
        self.sample_rate = 48000  # Discord uses 48kHz PCM audio
        self.channels = 2  # Stereo audio
        self.last_packet_time = time.time()  # Initialize the timestamp
        self.target_user_id = target_user_id
        self.tts_engine = pyttsx3.init()

    def write(self, user_id, packet):
        """Buffer incoming audio packets."""
        if user_id == self.target_user_id and packet and packet.pcm:
            self.audio_buffer.extend(packet.pcm)
            self.last_packet_time = time.time()


    def wants_opus(self):
        """Specify PCM audio (not Opus)."""
        return False

    def cleanup(self):
        """Cleanup resources."""
        self.audio_buffer.clear()

    async def transcribe(self):
        """Transcribe buffered audio using Whisper."""
        if not self.audio_buffer:
            return None

        # Save audio to WAV
        file_path = "temp_audio.wav"
        with wave.open(file_path, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit PCM
            wf.setframerate(self.sample_rate)
            wf.writeframes(self.audio_buffer)

        # Transcribe audio using Whisper in a separate thread
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, lambda: model.transcribe(file_path))

        # Clean up the temporary file
        os.remove(file_path)

        return result["text"]

    def query_ollama(self, prompt):
        """Send a prompt to the Hugging Face Inference API and get the response."""

        model= OllamaLLM(model="llama3")
        result = model.invoke(input=prompt)
        print(result)
        return result




    def generate_response(self, user_input):
        """Generate a response using the Hugging Face Inference API."""
        prompt = f"{user_input}"
        return self.query_ollama(prompt)

    def Text_to_speech(self,text,vc):
        language = "en"
        file_path = "temp_text_to_speech.wav"


        speech = gTTS(text,lang=language)








        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_file_path = temp_file.name  # Get the file path
            speech.save(temp_file_path)  # Save the speech to this file

            # Step 3: Play the audio from the temporary file
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(temp_file_path))
            vc.play(source, after=lambda e: print("Playback finished"))






@bot.tree.command(name="voice", guild=server_id)
async def voice(interaction: discord.Interaction):
    try:
        # Ensure the user is in a voice channel
        voice_channel = interaction.user.voice.channel
        if not voice_channel:
            await interaction.response.send_message("You're not in a voice channel.")
            return

        # Send an initial response
        await interaction.response.send_message("Listening to voice channel audio...")

        # Connect to the voice channel
        voice_client = await voice_channel.connect(cls=voice_recv.VoiceRecvClient)

        # Attach a custom sink

        sink = CustomAudioSink(target_user_id=interaction.user)
        voice_client.listen(sink=sink)

        # Monitor silence and trigger transcription
        while True:
            await asyncio.sleep(1)  # Check every second
            current_time = time.time()
            silence_duration = current_time - sink.last_packet_time

            if silence_duration >= 3 and sink.audio_buffer:
                # Silence detected, trigger transcription
                transcript = await sink.transcribe()

                sink.cleanup()  # Clear the buffer after transcription
                voice_client.stop_listening()


                if transcript:
                    # Generate a response using LLaMA
                    if "bot" in transcript.lower():

                        response = sink.generate_response(transcript)
                        print(f"Transcribed: {transcript}")
                        print(f"LLaMA Response: {response}")
                        sink.Text_to_speech(response, voice_client)

                        # Send the response back to the user in the text channel
                        await interaction.followup.send(f"User: {transcript}\nBot: {response}")
                        await asyncio.sleep(20)
                        voice_client.listen(sink=sink)






    except Exception as e:
        # Handle exceptions and notify the user
        try:
            await interaction.followup.send(f"An error occurred: {e}")
        except discord.errors.InteractionResponded:
            pass  # Interaction was already responded to
    finally:
        # Cleanup resources on exit
        if voice_client:
            await voice_client.disconnect(force=True)
        sink.cleanup()



@bot.tree.command(name="ask", guild=server_id)
async def ask(interaction: discord.Interaction, message:str):
    await interaction.response.defer()
    sink = CustomAudioSink(target_user_id=interaction.user)
    response = sink.generate_response(message)
    await interaction.followup.send(response)

@bot.event
async def on_ready():
    try:
        guild = discord.Object(id = 912368508808073227)
        synced = await bot.tree.sync(guild=guild)
        print("Synced")
    except Exception as e:
        print(e)


if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)



bot.run(Token)
