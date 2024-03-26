import requests
import random
import time
import hashlib
import logging
from bs4 import BeautifulSoup
from tqdm import tqdm

class NewBuildingSpainScraper:
    def __init__(self, base_url):
        """
        Initialize the scraper with the base URL and a random user agent.
        """
        self.base_url = base_url
        self.headers = {'User-Agent': self.get_random_user_agent()}
        self.logger = logging.getLogger(__name__)
    
    def get_random_user_agent(self):
        """
        Return a random user agent from a list of user agents.
        """
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            # Add more user agents as needed
        ]
        return random.choice(user_agents)
    
    def get_search_data(self):
        """
        Extract all the links and their respective card data from the base URL.
        """
        all_card_data = []

        # Get all card links from the base URL
        card_links = self.get_card_links()

        # Scrape card data for each link
        for link in tqdm(card_links):
            card_data = self.scrape_card_data(link)
            if card_data:
                all_card_data.append(card_data)
        
        search_documents = {
        'base_url': self.base_url,
        'results': all_card_data
        }
        return search_documents
    
    def get_card_links(self):
        """
        Extract card links from the base URL and subsequent pages.
        """
        links = []
        next_page_link = self.base_url
        
        while next_page_link:
            response = self.send_request(next_page_link)
            if response is None:
                self.logger.warning("Failed to retrieve page: %s", next_page_link)
                break

            soup = BeautifulSoup(response.content, 'html.parser')
            card_links = soup.find_all(class_='card__link', href=True)
            links += [link['href'] for link in card_links]

            next_page_link = self.get_next_page_link(soup) if soup else None
            if next_page_link:
                next_page_link = self.base_url + next_page_link
            time.sleep(2)  # Add a small delay to respect the server
            
        self.logger.info(f'Detected {len(links)} property cards')
        return links
    
    def scrape_card_data(self, link):
        """
        Scrape data from a specific card link.
        """
        response = self.send_request(link)
        if response is None:
            self.logger.warning("Failed to retrieve page: %s", link)
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        ref = soup.find(lambda tag: tag.name == 'div' and tag.get('data-value', '').startswith('ON')).get('data-value')
        target_a = soup.find('a', text='See on the map')
        address = target_a.find_parent('div').text.strip()
        content_items = soup.find_all('div', class_='single__contents-item')
        property_info = {}
        for item in content_items:
            contents_name = item.find('div', class_='single__contents-name')
            contents_value = item.find('div', class_='single__contents-value')
            if contents_name and contents_value:
                property_info[contents_name.text.strip()] = contents_value.text.strip()
        icon_items = soup.find_all('li', class_='item')
        extra_information = [item.find('span', class_='single__icons-text').text for item in icon_items if item.find('span', class_='single__icons-text')]
        card_id = hashlib.sha256(link.encode()).hexdigest()
        
        document = {
            'id': card_id,
            'url': link,
            'site_ref': ref,
            'address': address,
            'property_information': property_info,
            'extra_information': extra_information
        }
        return document
        
    def send_request(self, url):
        """
        Send a GET request to the specified URL with custom headers.
        """
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response
            else:
                self.logger.warning("Failed to retrieve page: %s, Status code: %s", url, response.status_code)
                return None
        except requests.RequestException as e:
            self.logger.error("Exception while retrieving page: %s, Error: %s", url, e)
            return None

    def get_next_page_link(self, pagination_soup):
        """
        Extract the link for the next page from the pagination HTML.
        """
        next_page_element = pagination_soup.find('a', class_='pagination__item--next', href=True)
        return next_page_element.get('href') if next_page_element else None
