from unittest.mock import AsyncMock, patch, MagicMock
from PoemUtils import PoemUtils
from connexion.exceptions import InternalServerError
from constants import PROJECT_ID, GENERATIVE_MODEL_LOCATION
import google.cloud.aiplatform_v1beta1.types.content as types
import pytest


POEM = "Some poem."

@patch("vertexai.init")
@patch("vertexai.preview.generative_models.GenerativeModel.generate_content_async")
@pytest.mark.asyncio
async def test_generate_poem_ok(generate_content_mock: AsyncMock, init_mock: MagicMock):
    poem_utils = PoemUtils()
    init_mock.assert_not_called()
    generate_content_mock.assert_not_called()

    candidate = MagicMock(text = POEM, finish_reason = types.Candidate.FinishReason.STOP)
    generate_content_mock.return_value  = MagicMock(candidates = [candidate])

    result = await poem_utils.generate_poem("en", "12", "flowers")
    generate_content_mock.assert_called_once_with("Generate a poem about 'flowers' that rhymes in the language represented by the IETF language tag 'en' with the maximum length of 12 lines.")
    init_mock.assert_called_once_with(project=PROJECT_ID, location=GENERATIVE_MODEL_LOCATION)
    assert result == POEM  

    result = await poem_utils.generate_poem("de", "10", None)
    generate_content_mock.assert_called_with("Generate a poem that rhymes in the language represented by the IETF language tag 'de' with the maximum length of 10 lines.")
    init_mock.assert_called_once()
    assert result == POEM 

@patch("vertexai.init")
@patch("vertexai.preview.generative_models.GenerativeModel.generate_content_async")
@pytest.mark.asyncio
async def test_generate_poem_no_candidates(generate_content_mock: AsyncMock, _: MagicMock):
    poem_utils = PoemUtils()
    generate_content_mock.assert_not_called()

    generate_content_mock.return_value  = MagicMock(candidates = [])
    with pytest.raises(InternalServerError):
        await poem_utils.generate_poem("en", "12", "flowers")
    generate_content_mock.assert_called_once_with("Generate a poem about 'flowers' that rhymes in the language represented by the IETF language tag 'en' with the maximum length of 12 lines.")

@patch("vertexai.init")
@patch("vertexai.preview.generative_models.GenerativeModel.generate_content_async")
@pytest.mark.asyncio
async def test_generate_poem_wrong_finish_reason(generate_content_mock: AsyncMock, _: MagicMock):
    poem_utils = PoemUtils()
    generate_content_mock.assert_not_called()

    candidate = MagicMock(text = POEM, finish_reason = types.Candidate.FinishReason.SAFETY)
    generate_content_mock.return_value  = MagicMock(candidates = [candidate])
    with pytest.raises(InternalServerError):
        await poem_utils.generate_poem("en", "12", "flowers")
    generate_content_mock.assert_called_once_with("Generate a poem about 'flowers' that rhymes in the language represented by the IETF language tag 'en' with the maximum length of 12 lines.")
