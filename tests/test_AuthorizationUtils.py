from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from AuthorizationUtils import AuthorizationUtils
from google_crc32c import Checksum
from connexion.exceptions import Unauthorized
from google.cloud.secretmanager import SecretManagerServiceAsyncClient
from constants import PROJECT_ID, SECRET_NAME, SECRET_VERSION

SECRET_NAME = SecretManagerServiceAsyncClient.secret_version_path(PROJECT_ID, SECRET_NAME, SECRET_VERSION)

@patch("google.cloud.secretmanager.SecretManagerServiceAsyncClient.access_secret_version")
@pytest.mark.asyncio
async def test_generate_poem_ok(mock: AsyncMock):
    authorization_utils = AuthorizationUtils()
    mock.assert_not_called()

    key = "correct key"
    data = bytes(key, "utf-8")
    checksum = compute_checksum(data)
    secret_payload = MagicMock(data = data, data_crc32c=checksum)
    mock.return_value  = MagicMock(payload=secret_payload)

    await authorization_utils.check_api_key(key)
    mock.assert_called_once_with(name=SECRET_NAME)

@patch("google.cloud.secretmanager.SecretManagerServiceAsyncClient.access_secret_version")
@pytest.mark.asyncio
async def test_generate_poem_checksum_error(mock: AsyncMock):
    authorization_utils = AuthorizationUtils()
    mock.assert_not_called()

    key = "correct key"
    data = bytes(key, "utf-8")
    secret_payload = MagicMock(data = data, data_crc32c=0)
    mock.return_value  = MagicMock(payload=secret_payload)

    with pytest.raises(Unauthorized):
        await authorization_utils.check_api_key(key)
    mock.assert_called_once_with(name=SECRET_NAME)


@patch("google.cloud.secretmanager.SecretManagerServiceAsyncClient.access_secret_version")
@pytest.mark.asyncio
async def test_generate_poem_wrong_key(mock: AsyncMock):
    authorization_utils = AuthorizationUtils()
    mock.assert_not_called()

    key = "correct key"
    data = bytes(key, "utf-8")
    checksum = compute_checksum(data)
    secret_payload = MagicMock(data = data, data_crc32c=checksum)
    mock.return_value  = MagicMock(payload=secret_payload)
    
    with pytest.raises(Unauthorized):
        await authorization_utils.check_api_key("wrong key")  
    mock.assert_called_once_with(name=SECRET_NAME)

def compute_checksum(data):
    crc32c = Checksum()
    crc32c.update(data)
    return int(crc32c.hexdigest(), 16)