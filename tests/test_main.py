import main
from httpx import Response
from unittest.mock import MagicMock
from PoemUtils import PoemUtils
from AuthorizationUtils import AuthorizationUtils
from connexion.exceptions import Unauthorized
from TtsUtils import TtsUtils


class MockPoemUtils(PoemUtils):
    async def generate_poem(self, language: str, max_length: int, topic: str | None) -> str:
        return f"This is a poem about {topic} in {language} with the maximum length {max_length}."
    
class MockAuthorizationUtils(AuthorizationUtils):
    async def check_api_key(self, api_key: str) -> None:
        if api_key != "correct":
            raise Unauthorized("Wrong API key")

class MockTtsUtils(TtsUtils):
    async def synthesize(self, text: str, language: str, gender: str) -> bytes:
        return bytes(f"{text} Synthesized with a {gender} voice in {language}.", "utf-8")
        
class TestMain:

    def setup_class(self):
        self.test_client = main.app.test_client()
        main.poem_utils = MockPoemUtils()
        main.authorization_utils = MockAuthorizationUtils()
        main.tts_utils = MockTtsUtils()

    def test_print_poem_ok(self):
        response = self.test_client.get("/print_poem?lang=en&max_length=12&topic=flowers&api_key=correct")
        assert response.status_code == 200
        assert response.text == "This is a poem about flowers in en with the maximum length 12."

    def test_print_poem_wrong_api_key(self):
        response = self.test_client.get("/print_poem?lang=en&max_length=12&topic=flowers&api_key=wrong")
        assert response.status_code == 401

    def test_read_poem_ok(self):
        response = self.test_client.get("/read_poem?lang=en&max_length=12&topic=flowers&gender=female&api_key=correct")
        assert response.status_code == 200
        assert response.content == bytes("This is a poem about flowers in en with the maximum length 12. Synthesized with a female voice in en.", "utf-8")

