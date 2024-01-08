from google.cloud.secretmanager import SecretManagerServiceClient, AccessSecretVersionRequest, SecretVersion
from constants import PROJECT_ID, SECRET_NAME, SECRET_VERSION
from google_crc32c import Checksum
from connexion.exceptions import Unauthorized

class AuthorizationUtils:
    _client: SecretManagerServiceClient = None

    """Checks whether the provided api key is valid.

    Args:
        api_key: The api key to be checked.

    Raises:
        Unauthorized if the api key is not valid or the data retrieved from the secret is corrupt.
    """
    def check_api_key(self, api_key: str) -> None:
        self._prepare()
        #https://cloud.google.com/secret-manager/docs/access-secret-version#access_a_secret_version
        name: str = self._client.secret_version_path(PROJECT_ID, SECRET_NAME, SECRET_VERSION)
        #request = new AccessSecretVersionRequest(na)
        secret_version: SecretVersion = self._client.access_secret_version(name=name)
        crc32c = Checksum()
        data = secret_version.payload.data
        crc32c.update(data)
        if secret_version.payload.data_crc32c != int(crc32c.hexdigest(), 16):
            raise Unauthorized("Data corruption detected")
        expected_key = data.decode("UTF-8")
        if api_key != expected_key:
            raise Unauthorized("Wrong API key")
        
    def _prepare(self):
        """Intitializes the SecretManagerServiceClient if not yet done."""
        if self._client is None:
            print("instantiating SecretManagerServiceClient")
            self._client = SecretManagerServiceClient()
            print("instantiated SecretManagerServiceClient")
        else:
            print("SecretManagerServiceClient was already instantiated")


