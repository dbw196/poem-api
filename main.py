from connexion import AsyncApp
from PoemUtils import PoemUtils
from TtsUtils import TtsUtils
from AuthorizationUtils import AuthorizationUtils

app = AsyncApp(__name__)

poem_utils = PoemUtils()
tts_utils = TtsUtils()
authorization_utils = AuthorizationUtils()

def print_poem(language: str, max_length: int, topic: str = None) -> tuple[str, int]:
    """Generates a poem and returns it as plain text.

    Args:
        language: The language as IETF language tag.
        max_length: The maximum length of the poem (in lines).
        topic: The topic the poem should be about.

    Returns:
        The generated poem as plain text and the response code.
    """
    return poem_utils.generate_poem(language, max_length, topic), 200

def read_poem(language: str, max_length: int, gender: str, topic: str | None = None) -> tuple[bytes, int]:
    """Generates a poem, synthesizes it via TTS and returns it as mp3.

    Args:
        language: The language as IETF language tag.
        max_length: The maximum length of the poem (in lines).
        gender: The gender of the TTS voice to use ("female", "male" or "unspecified").
        topic: The topic the poem should be about.

    Returns:
        The poem as bytes representing the mp3 data and the response code.
    """
    poem: str = poem_utils.generate_poem(language, max_length, topic)
    audio: bytes = tts_utils.synthesize(poem, language, gender)
    return audio, 200

def apikey_auth(api_key: str)-> None:
    """ Uses the provided api key to perform authorization.

    Args:
        api_key: The api key to be checked.

    Returns:
        A dict conterning minimal rfc7662 information.

    Raises:
        Unauthorized if the api key is not valid.
    """
    # will throw an exception if not authorized
    authorization_utils.check_api_key(api_key)
    return {"active": True}

app.add_api("poem_api.yaml")

if __name__  == "__main__":
    app.run()