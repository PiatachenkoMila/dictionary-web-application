"""Synthesizes speech from the input string of text or ssml.

Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""
from google.cloud import texttospeech
from ..python_prog.splitter import TextSplitter


def determine_language(term):
    try:
        words = TextSplitter().split_text(term, 1)
        words = "".join(words)
        eng_abc_range = range(65, 123)
        ukr_abc_range = range(1028, 1170)
        chars_ukr = 0
        chars_eng = 0
        for c in words:
            if ord(c) in eng_abc_range:
                chars_eng += 1
            elif ord(c) in ukr_abc_range:
                chars_ukr += 1
        if chars_ukr > 0:
            return "uk-UA"
        else:
            return "en-US"
    except ValueError:
        return "en-US"


def convert_text_to_speech(text, output_file):
    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.types.SynthesisInput(text=text)

    # Build the voice request, select the language code and the ssml
    # voice gender ("neutral")
    language = determine_language(text)
    voice = texttospeech.types.VoiceSelectionParams(
        language_code=language,
        ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)

    # Select the type of audio file you want returned
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    # The response's audio_content is binary.
    with open(output_file, 'wb') as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print('Audio content written to file "{}"'.format(output_file))
