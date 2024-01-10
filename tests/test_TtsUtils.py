from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from TtsUtils import TtsUtils
from google.cloud.texttospeech import SsmlVoiceGender, VoiceSelectionParams, AudioConfig, AudioEncoding, SynthesisInput
from connexion.exceptions import InternalServerError


TEXT = "some text"
AUDIO = bytes(TEXT, "utf-8")
AUDIO_CONFIG = AudioConfig(audio_encoding=AudioEncoding.MP3)

@patch("google.cloud.texttospeech.TextToSpeechAsyncClient.list_voices")
@patch("google.cloud.texttospeech.TextToSpeechAsyncClient.synthesize_speech")
@pytest.mark.asyncio
async def test_synthesize_no_voice(synthesize_mock: AsyncMock, list_voices_mock: AsyncMock):
    tts_utils = TtsUtils()
    synthesize_mock.assert_not_called()
    list_voices_mock.assert_not_called()
    language = "xy"
    list_voices_mock.return_value = MagicMock(voices=[])
    with pytest.raises(InternalServerError):
        await tts_utils.synthesize(TEXT, language, SsmlVoiceGender.FEMALE)
    list_voices_mock.assert_called_once_with(language_code = language)
    synthesize_mock.assert_not_called()

@patch("google.cloud.texttospeech.TextToSpeechAsyncClient.list_voices")
@patch("google.cloud.texttospeech.TextToSpeechAsyncClient.synthesize_speech")
@pytest.mark.asyncio
async def test_synthesize_ok_hq_voice_matching_gender(synthesize_mock: AsyncMock, list_voices_mock: AsyncMock):
    tts_utils = TtsUtils()
    synthesize_mock.assert_not_called()
    list_voices_mock.assert_not_called()
    language = "en"
    voices = [mock_voice(language, SsmlVoiceGender.MALE, "Neural_Male"),
              mock_voice(language, SsmlVoiceGender.MALE, "Other_Male"),
              mock_voice(language, SsmlVoiceGender.FEMALE, "Other_Female"),
              mock_voice(language, SsmlVoiceGender.FEMALE, "Neural_Female")]
    list_voices_mock.return_value = MagicMock(voices=voices)
    synthesize_mock.return_value = MagicMock(audio_content = AUDIO)
    
    result = await tts_utils.synthesize(TEXT, language, "female")
    list_voices_mock.assert_called_once_with(language_code = language)
    synthesize_mock.assert_awaited_once_with(input = SynthesisInput(text=TEXT), voice = VoiceSelectionParams(language_code=language, name="Neural_Female"), audio_config=AUDIO_CONFIG)
    assert result == AUDIO

@patch("google.cloud.texttospeech.TextToSpeechAsyncClient.list_voices")
@patch("google.cloud.texttospeech.TextToSpeechAsyncClient.synthesize_speech")
@pytest.mark.asyncio
async def test_synthesize_ok_non_hq_voice_matching_gender(synthesize_mock: AsyncMock, list_voices_mock: AsyncMock):
    tts_utils = TtsUtils()
    synthesize_mock.assert_not_called()
    list_voices_mock.assert_not_called()
    language = "en"
    voices = [mock_voice(language, SsmlVoiceGender.MALE, "Neural_Male"),
              mock_voice(language, SsmlVoiceGender.MALE, "Other_Male"),
              mock_voice(language, SsmlVoiceGender.FEMALE, "Other_Female")]
    list_voices_mock.return_value = MagicMock(voices=voices)
    synthesize_mock.return_value = MagicMock(audio_content = AUDIO)
    
    result = await tts_utils.synthesize(TEXT, language, "female")
    list_voices_mock.assert_called_once_with(language_code = language)
    synthesize_mock.assert_awaited_once_with(input = SynthesisInput(text=TEXT), voice = VoiceSelectionParams(language_code=language, name="Other_Female"), audio_config=AUDIO_CONFIG)
    assert result == AUDIO

@patch("google.cloud.texttospeech.TextToSpeechAsyncClient.list_voices")
@patch("google.cloud.texttospeech.TextToSpeechAsyncClient.synthesize_speech")
@pytest.mark.asyncio
async def test_synthesize_ok_non_hq_voice_not_matching_gender(synthesize_mock: AsyncMock, list_voices_mock: AsyncMock):
    tts_utils = TtsUtils()
    synthesize_mock.assert_not_called()
    list_voices_mock.assert_not_called()
    language = "en"
    voices = [mock_voice(language, SsmlVoiceGender.MALE, "Neural_Male"),
              mock_voice(language, SsmlVoiceGender.MALE, "Other_Male")]
    list_voices_mock.return_value = MagicMock(voices=voices)
    synthesize_mock.return_value = MagicMock(audio_content = AUDIO)
    
    result = await tts_utils.synthesize(TEXT, language, "female")
    list_voices_mock.assert_called_once_with(language_code = language)
    synthesize_mock.assert_awaited_once_with(input = SynthesisInput(text=TEXT), voice = VoiceSelectionParams(language_code=language, name="Neural_Male"), audio_config=AUDIO_CONFIG)
    assert result == AUDIO

@patch("google.cloud.texttospeech.TextToSpeechAsyncClient.list_voices")
@patch("google.cloud.texttospeech.TextToSpeechAsyncClient.synthesize_speech")
@pytest.mark.asyncio
async def test_synthesize_ok_non_hq_voice_not_matching_gender(synthesize_mock: AsyncMock, list_voices_mock: AsyncMock):
    tts_utils = TtsUtils()
    synthesize_mock.assert_not_called()
    list_voices_mock.assert_not_called()
    language = "en"
    voices = [mock_voice(language, SsmlVoiceGender.MALE, "Other_Male")]
    list_voices_mock.return_value = MagicMock(voices=voices)
    synthesize_mock.return_value = MagicMock(audio_content = AUDIO)
    
    result = await tts_utils.synthesize(TEXT, language, "female")
    list_voices_mock.assert_called_once_with(language_code = language)
    synthesize_mock.assert_awaited_once_with(input = SynthesisInput(text=TEXT), voice = VoiceSelectionParams(language_code=language, name="Other_Male"), audio_config=AUDIO_CONFIG)
    assert result == AUDIO

def mock_voice(language: str, gender: SsmlVoiceGender, name: str) -> MagicMock:
    mock = MagicMock(ssml_gender = gender, language_codes=[language])
    mock.name = name # cannot be given in constructor because then it's the name of the mock
    return mock

    
    
    