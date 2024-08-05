import os
import urllib.request

from google.cloud import speech


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/tmp/livedata2019.json"


client = speech.SpeechClient()


def transcribe_file(lang, speech_file):

    with open(speech_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=lang,
        model="default",
    )

    operation = client.long_running_recognize(config=config, audio=audio)
    response = operation.result(timeout=90)

    ret = []
    for result in response.results:
        for a in result.alternatives:
            ret.append([a.transcript, a.confidence])

    return ret