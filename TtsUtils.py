
from google.cloud.texttospeech import TextToSpeechClient, SynthesisInput, VoiceSelectionParams, AudioConfig, AudioEncoding, SynthesizeSpeechResponse, SsmlVoiceGender, Voice
from connexion.exceptions import InternalServerError

class TtsUtils:
    """
    Provides means to synthesize a text via the google cloud TTS service.
    """
    _tts_client: TextToSpeechClient = None
    _audio_config: AudioConfig = None

    def synthesize(self, text: str, language: str, gender: str) -> bytes:
        """
        Synthesizes the provided text with a voice matching the provided language and gender.

        Args:
            text: The text to be synthesized.
            language: The language as IETF language tag.
            gender: The gender of the TTS voice to use ("female", "male" or "unspecified").
                    This is not a hard constraint, if a voice of the specified gender is not found, 
                    a voice of another gender might be used as fallback.
        
        Returns:
            The poem as bytes representing the mp3 data.

        Raises:
            InternalServerError if no voice can be found for the provided language.
        """
        self._prepare_tts()
        ssml_voice_gender = self._map_gender(gender)
        print(f"synthesizing the following text in language {language} with voice of gender {ssml_voice_gender}")
        print(text)
        voice: Voice = self._find_voice(language, ssml_voice_gender)
        if voice is not None:
            print(f"found voice {voice.name}")
            voice: VoiceSelectionParams = VoiceSelectionParams(language_code=voice.language_codes[0], name=voice.name)
        else:
            raise InternalServerError(f"didn't find voice for language {language}")
        synthesis_input = SynthesisInput(text=text)
        response: SynthesizeSpeechResponse = self._tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=self._audio_config)
        return response.audio_content
    
    def _prepare_tts(self) -> None:
        """Intitializes the TextToSpeechClient and AudioConfig if not yet done."""
        if self._tts_client is None:
            print("initializing TTS")
            self._tts_client = TextToSpeechClient()
            self._audio_config: AudioConfig = AudioConfig(audio_encoding=AudioEncoding.MP3)
            print("TTS initialized")
        else:
            print("TTS was already initialized")

    def _map_gender(self, gender: str) -> SsmlVoiceGender:
        """Maps a gender string ("female", "male" or "unspecified") to the corresponding SsmlVoiceGender.
        
        Args:
            gender: The gender string to be mapped.

        Returns:
            The corresponding SsmlVoiceGender.
        """
        if gender == "female":
            return SsmlVoiceGender.FEMALE
        elif gender == "male":
            return SsmlVoiceGender.MALE
        else:
            return SsmlVoiceGender.SSML_VOICE_GENDER_UNSPECIFIED
    

    def _find_voice(self, language: str, gender: SsmlVoiceGender) -> Voice | None:
        """
        Finds a TTS Voice matching the provided language and potentially the provided gender.
        
        If available, Neural or Wavenet voices are preferred due to their better quality.
        Voices are ranked by the fact whether they are for the requested gender and whether they are Neural/Wavenet voices, in that order.

        Args:
            language: The language as IETF language tag
            gender: The gender of the TTS voice to use.
                    This is not a hard constraint, if a voice of the specified gender is not found, 
                    a voice of another gender might be used as fallback.
        
        Returns:
            The voice best that matches the requirements explained above, or None if no voice for the provided language is available.
        """
        voices: list[Voice] = list(self._tts_client.list_voices(language_code=language).voices)
        voices_matching_gender: list[Voice] = list(filter(lambda voice: gender == SsmlVoiceGender.SSML_VOICE_GENDER_UNSPECIFIED or voice.ssml_gender == gender, voices))
        hq_voices: list[Voice] = list(filter(lambda voice: "Neural" in voice.name or "Wavenet" in voice.name, voices))
        hq_voices_matching_gender: list[Voice] = list(filter(lambda voice: voice in voices_matching_gender, hq_voices))
        if hq_voices_matching_gender:
            return hq_voices_matching_gender[0]
        elif voices_matching_gender:
            return voices_matching_gender[0]
        elif hq_voices:
            return hq_voices[0]
        elif voices:
            return voices[0]
        else:
            return None
