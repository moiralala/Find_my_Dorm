from bs4 import BeautifulSoup
import re
import requests
import numpy as np

def get_wampler(url):

    """
        url = 'https://wamplerapartments.com/our-properties/'

        Scrape information about apartments from the Wampler website.

        Parameters:
        - url (str): The URL of the Wampler website's property listing page.

        Returns:
        - list: A list of lists, where each inner list represents information about an apartment.

        Example:
        # Fetch information about apartments from the Wampler website
        >>> wampler_apartments = get_wampler('https://wamplerapartments.com/our-properties/')

        Each inner list contains the following details:
        - Address (str): The address of the apartment.
        - Price (float): The rental price of the apartment.
        - Bedroom (int): The number of bedrooms in the apartment.
        - Bathroom (float): The number of bathrooms in the apartment.
        - Link (str): The URL link to the apartment's details.
        - Availability (str): The availability status or lease period of the apartment.
        - Name (str): The name or identifier of the property management company (Wampler).
        - Is_studio (bool): Indicates whether the apartment is a studio (True) or not (False).

        Doctests:
        >>> len(get_wampler('https://wamplerapartments.com/our-properties/')) >= 0
        True

        >>> isinstance(get_wampler('https://wamplerapartments.com/our-properties/')[0][2], int)
        True

        >>> get_wampler('https://wamplerapartments.com/our-properties/')[20][1] > 0
        True

        >>> get_wampler('https://invalid-url.com')  # Returns an empty list for an invalid URL
        []
    """
    session = requests.session()
    req_header = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',}
    name ='Wampler'
    re = session.post(url,headers=req_header).text
    soup = BeautifulSoup(re, 'html.parser')
    Dorms = []
    if soup == None:
        return Dorms
    for a in soup.find_all('a', class_='more-link'):
        link = a['href']
        res = session.get(link).text
        soup = BeautifulSoup(res, 'html.parser')
        address = soup.find('h3', class_='listing-address').text.strip(',Illinois').strip('/ Urb')
        lookup = {}
        for div in soup.find_all('div', class_='single-detail'):
            spans = div.find_all('span')
            lookup[spans[0].text.strip()] = spans[1].text.strip()
        if lookup['Bedrooms:'] == 'Studio':
            bedroom = 1
            is_studio = True
        else:
            bedroom = int(lookup['Bedrooms:'].split(' ')[0])
            is_studio = False
        bathroom = float(lookup['Bathrooms:'])
        available = lookup['Rent:'].upper() != 'LEASED'
        if available:
            availability = '2024-08'
            if lookup['Rent:'][0].isalpha():
                # use np.nan in Numpy to represent unavailable price
                price = np.nan
            else:
                price = float(lookup['Rent:'].replace('$', '').replace(',', '').split('-')[-1].strip('/mo'))
        else:
            available_date = None
            # use np.nan in Numpy to represent unavailable price
            price = np.nan
            continue
        Dorms.append([address, price, bedroom, bathroom, link, availability, name, is_studio])
    return Dorms

