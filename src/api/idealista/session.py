import requests
from requests.exceptions import RequestException
import base64

class APISession:
    _session = None

    def __init__(
        self,
        base_url: str = 'https://api.idealista.com',
        auth_token: str = None,
        api_key: str = None,
        api_secret: str = None
    ) -> None:
        """
        Initializes the API session.

        Args:
        - base_url (str): The base URL of the API.
        - auth_token (str): The authentication token.
        - api_key (str): The API key for OAuth token retrieval.
        - api_secret (str): The API secret for OAuth token retrieval.

        Raises:
        - ValueError: If neither auth_token nor api_key and api_secret are provided.
        """
        self.base_url = base_url
        self.api_key = api_key
        self.api_secret = api_secret
        self.auth_token = auth_token

    @property
    def session(self) -> requests.Session:
        """
        Returns the API session, creating a new one if necessary and updating it with the authentication token.
        """
        if not self._session:
            self._create_session()
        elif self.auth_token:
            self._update_session_with_token()
        return self._session

    def _create_session(self) -> None:
        """
        Creates a new session and updates it with the authentication token if available.
        """
        self._session = requests.Session()

        if self.auth_token:
            self._update_session_with_token()
        elif self.api_key and self.api_secret:
            self.auth_token = self._get_oauth_token()
            self._update_session_with_token()
        else:
            raise ValueError('Either auth_token or api_key and api_secret must be provided')

    def _update_session_with_token(self) -> None:
        """
        Updates the session with the provided authentication token.
        """
        self._session.headers.update({'Authorization': f'Bearer {self.auth_token}'})

    def _get_oauth_token(self) -> str:
        """
        Retrieves and returns the OAuth token using the provided API key and secret.
        """
        token_url = f'{self.base_url}/oauth/token'
        auth_string = f"{self.api_key}:{self.api_secret}"
        encoded_auth_string = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
        headers = {
            "Authorization": f"Basic {encoded_auth_string}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            'grant_type': 'client_credentials',
            'scope': 'read'
        }
        try:
            response = requests.post(token_url, headers=headers, data=data)
            response.raise_for_status()
            token_info = response.json()
            access_token = token_info.get('access_token')
            if not access_token:
                raise ValueError('Access token not found in the response')
            return access_token
        except (requests.RequestException, ValueError) as e:
            raise ValueError(f'Failed to retrieve OAuth token: {e}') from e
