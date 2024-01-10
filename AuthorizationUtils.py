from google.cloud.secretmanager import SecretManagerServiceAsyncClient, AccessSecretVersionResponse, SecretPayload
from constants import PROJECT_ID, SECRET_NAME, SECRET_VERSION
from google_crc32c import Checksum
from connexion.exceptions import Unauthorized

class AuthorizationUtils:
    _client: SecretManagerServiceAsyncClient = None

    """Checks whether the provided api key is valid.

    Args:
        api_key: The api key to be checked.

    Raises:
        Unauthorized if the api key is not valid or the data retrieved from the secret is corrupt.
    """
    async def check_api_key(self, api_key: str) -> None:
        self._prepare()
        #https://cloud.google.com/secret-manager/docs/access-secret-version#access_a_secret_version
        name: str = self._client.secret_version_path(PROJECT_ID, SECRET_NAME, SECRET_VERSION)
        response: AccessSecretVersionResponse = await self._client.access_secret_version(name=name)
        payload: SecretPayload = response.payload
        crc32c = Checksum()
        crc32c.update(payload.data)
        if payload.data_crc32c != int(crc32c.hexdigest(), 16):
            raise Unauthorized("Data corruption detected")
        expected_key = payload.data.decode("UTF-8")
        if api_key != expected_key:
            raise Unauthorized("Wrong API key")
        
    def _prepare(self):
        """Intitializes the SecretManagerServiceClient if not yet done."""
        if self._client is None:
            print("instantiating SecretManagerServiceClient")
            self._client = SecretManagerServiceAsyncClient()
            print("instantiated SecretManagerServiceClient")
        else:
            print("SecretManagerServiceClient was already instantiated")


