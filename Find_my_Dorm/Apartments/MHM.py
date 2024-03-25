import numpy as np
from bs4 import BeautifulSoup
import re
import requests

def get_MHM(url):
    """
        url = 'https://www.mhmproperties.com/apartments/?_sft_types=apartments'

        Scrape information about apartments listed on the MHM Properties website.

        Parameters:
        - url (str): The URL of the MHM Properties website's apartment listings.

        Returns:
        - list: A list of lists, where each inner list represents information about an apartment.

        Example:
        # Fetch information about MHM apartments from the provided URL
        >>> apartments_info = get_MHM('https://www.mhmproperties.com/apartments/?_sft_types=apartments')

        # Display details of each apartment
        Each inner list contains the following details:
        - Address (str): The address of the apartment.
        - Price (str): The rental price of the apartment.
        - Bedroom (int): The number of bedrooms in the apartment.
        - Bathroom (int): The number of bathrooms in the apartment.
        - Link (str): The URL link to the apartment's details.
        - Availability (str/bool): The availability status or lease period of the apartment.
        - Name (str): The name or identifier of the property management company (MHM in this case).
        - Is_studio (bool): Indicates whether the apartment is a studio (True) or not (False).

        Doctests:
        >>> len(get_MHM('https://www.mhmproperties.com/apartments/?_sft_types=apartments'))>=0
        True

        >>> isinstance(get_MHM('https://www.mhmproperties.com/apartments/?_sft_types=apartments')[10][2], int)
        True

        >>> get_MHM('https://www.mhmproperties.com/apartments/?_sft_types=apartments')[14][3] >= 0
        True

        >>> get_MHM('https://invalid-url.com')  # Returns an empty list for an invalid URL
        []
    """
    session = requests.session()
    req_header = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',}
    name = 'MHM'
    res = session.get(url,headers = req_header).text
    soup = BeautifulSoup(res, 'html.parser')
    units = soup.find_all('div', class_='propgridc')
    Dorms = []
    for unit in units:
        link = unit.find('a')['href']
        address = unit.find('h2').text
        #class_='ppricebox' include more information about each unit
        items = unit.find_all('p', class_='ppricebox')
        is_studio = False
        for item in items:
            item = item.text 
            #1 Bed format:1 Bed: 2024-2025  LEASED!
            if int(item[0][0]) == 1:
                bedroom = 1
                bathroom = 1
                is_studio = True
                if item[-7:] == 'LEASED!':
                    availability = False
                    # use np.nan in Numpy to represent unavailable price
                    price = np.nan
                
            #other format is 2 Bed/2 Bath: 2024-2025  LEASED!
            else:
                item = item.split("/")
                #['2 Bed', '2 Bath: 2024-2025  LEASED!']
                bedroom = int(item[0][0].strip(' '))
                bathroom = int(item[1].strip(' ')[0])
                last_letters = item[-1][-7:].strip(' ')
                #There are lots of typo on mhmproperties website
                if last_letters == 'LEASED!' or last_letters == 'LSESED!' or last_letters == 'LEASED':
                    availability = False
                    #use np.nan in Numpy to represent unavailable price
                    price = np.nan
                
                else:
                    availability = '2024-2025'
                    price = int(item[1].split(':')[1].strip(' ').strip('$'))
            Dorms.append([address, price, bedroom, bathroom, link, availability, name, is_studio])
    return Dorms

