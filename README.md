# BigSys

A Discord bot that can play music from YouTube, search on Wikipedia and other basic functions all with a voice assistant mode.

## TODO

PRs are welcomed! 🙏

- [ ] Administration and moderation commands
- [ ] Slash commands integration
- [ ] BigSys Affection, a tradeable currency gained by good will
- [ ] Reports on the nicest, most toxic and etc users based on statistics.
- [ ] Documentation website for users and developers
- [ ] Music lyrics, looping and better listing
- [ ] Google Colab for quick bot testing

## Disclaimer

Depsite the permissive licensing, it is strongly suggested to not use this bot commercially nor abuse it as it currently violates the Terms of Service of YouTube (and Google Translate). This is an experiment, an attempt to make a voice assitant in Discord.

## Naming

BigSys stands for Big System. It is also a play of word as it sounds like Big Sis. This name is also a reference to Big Brother in 1984 by George Orwell.

This bot is quite computationally heavy as it uses all the following machine learning models when all functionalities are bootstraped.

## Models

Textual machine learning models:
- https://github.com/unitaryai/detoxify for toxicity detection
- https://huggingface.co/sentence-transformers for prompt embeddings
- https://huggingface.co/tasks/question-answering to query the arguments of the nearest intent
- https://huggingface.co/tasks/conversational for conversations
- https://huggingface.co/pranavpsv/gpt2-genre-story-generator for story generation

Voice assistant machine learning models:
- https://github.com/Picovoice/porcupine for wake call detection
- https://github.com/openai/whisper for transcribing
- https://huggingface.co/microsoft/speecht5_tts for voice synthesis
- https://huggingface.co/espnet/kan-bayashi_ljspeech_vits for voice synthesis (tts_old)

## External APIs

- Google Translate Text-to-Speech API for the voice assistant voice.
- YouTube via `youtube-dl`

## Commands (Tasks) 

Please see `bootstraps/command_bootstrap.py`
for a general idea of the commands available.

The commands can be triggered by pining the robot as follows: `@bigsys <command> [arguments...]`

## Intents (Tasks)

`bootstraps/intent_bootstrap.py`

The intents are triggered if intent embedding closest to the embedding the user prompt sentence embedding is smaller than `INTENT_THRESHOLD` defined in `params.py`.

## Conversations

If the commands and the intents are not matched, the conversational AI model will take over.

## Voice Assistant

The voice assistant mode uses the intent handler and the conversation model.

The voice assistant uses Picovoice's Porcupine to the detect the wake word Big Sys located at `models/ppn/bigsys-linux.ppn`. As the filename indicates, this only works on Linux machines. You can run this in a docker container or generate a new wake word file within the Picovoice console.

After a wake word detection, it will start transcribing the user's utterances using Whisper. However, before that, it is suggested to wait for the bot's confirmation that is it listening. Please note there may be issues when the username is too long. [gTTS](https://github.com/pndurette/gTTS) is used for the bot's voice. Therefore, the concerns related to gTTS are also present in this project.

## Running

To run this bot, the environment variables `DISCORD_BOT_TOKEN` and `PICOVOICE_ACCESS_SECRET` must be set. If you are running without the voice related commands bootstrapped, you do not need to set `PICOVOICE_ACCESS_SECRET`. Please note that you need an account to obtain the `PICOVOICE_ACCESS_SECRET`.

Running the following command in the repository is sufficient to boot the bot up.

```sh
python main.py
```

If you are running on a device with low GPU memory and it crashes, you may need to set `TORCH_DEVICE` to `cpu`. On the other hand, to enforce the use of the GPU, set it to `cuda` instead.

## License

MIT. Wei. For more information please read the `LICENSE` file.