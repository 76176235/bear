import time
import azure.cognitiveservices.speech as speechsdk


speech_key, service_region = "6fb5a50eb92f426e92d0ddc2db11d5ce", "eastus"


def language_detection(langs, wav_path):
    auto_detect_source_language_config = \
        speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=langs)

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.output_format = speechsdk.OutputFormat.Detailed

    audio_config = speechsdk.audio.AudioConfig(filename=wav_path)

    source_language_recognizer = speechsdk.SourceLanguageRecognizer(
        speech_config=speech_config,
        auto_detect_source_language_config=auto_detect_source_language_config,
        audio_config=audio_config)

    result = source_language_recognizer.recognize_once()
    return result.json


def speech_recognize(lang, wav_path):
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.output_format = speechsdk.OutputFormat.Detailed
    audio_config = speechsdk.audio.AudioConfig(filename=wav_path)
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, language=lang, audio_config=audio_config)

    result = speech_recognizer.recognize_once()

    #print(result.text)
    result = eval(result.json)
    #print(result)
    #print(result["DisplayText"])

    if result['RecognitionStatus'] != 'Success':
        return None

    nbest = result["NBest"][0]
    assert nbest["Display"] == result["DisplayText"]

    return result["DisplayText"], nbest["Confidence"], nbest["Lexical"]


def speech_recognize_continuous(lang, wav_path):
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.output_format = speechsdk.OutputFormat.Detailed
    speech_config.set_profanity(speechsdk.ProfanityOption.Raw)
    audio_config = speechsdk.audio.AudioConfig(filename=wav_path)

    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, language=lang, audio_config=audio_config)

    done = False
    result = ""
    confidence = []

    def stop_cb(evt: speechsdk.SessionEventArgs):
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        nonlocal done
        done = True

    def recognition_cb(evt: speechsdk.SessionEventArgs):
        nonlocal result
        nonlocal confidence
        ret = eval(evt.result.json)["NBest"][0]
        confidence.append(ret["Confidence"])
        result += " " + ret["Lexical"]

    speech_recognizer.recognized.connect(recognition_cb)
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start continuous speech recognition
    speech_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(.5)

    speech_recognizer.stop_continuous_recognition()

    confidence = sum(confidence) / len(confidence) if confidence else 0.
    return result, confidence
