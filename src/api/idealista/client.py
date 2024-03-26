from typing import Optional, Dict, Any
from .session import APISession

class IdealistaAPIClient:
    def __init__(self, api_key: str, api_secret:str):
        
        self.api_session = APISession(api_key=api_key, api_secret=api_secret)

    def get_json(
        self,
        country:str = 'es',
        api_version: str = '3.5',
        params:Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for properties using the Idealista API.

        Args:
        - country (str): The country code for the search (e.g., 'es' for Spain).
        - filters (dict): Optional filters for the property search.

        Returns:
        - dict: The response from the property search API.

        Raises:
        - ValueError: If the property search request fails.
        """
        endpoint = f'/{api_version}/{country}/search'
        url = self.api_session.base_url + endpoint
        response = self.api_session.session.post(url, params=params)
        response.raise_for_status()
        return response.json()

