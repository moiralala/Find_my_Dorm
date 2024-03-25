from bs4 import BeautifulSoup
from public import Apartment, ApartmentScraper


class Bailey(ApartmentScraper):
    """
    A scraper class that inherits from ApartmentScraper to parse apartment listings
    from the Bailey Apartments Official website.
    """

    def parse_data(self):
        """
        Fetches and parses the HTML content to extract apartment data.
        Overrides the 'fetch_data' method from the parent class.

        Returns:
            list: A list of Apartment objects with the extracted data.
        """
        # Fetch the HTML data
        html = self.fetch_data()
        soup = BeautifulSoup(html, 'html.parser')

        # Find the table with apartment listings by ID
        table = soup.find('table', id='tablepress-2')
        header_cells = table.find('thead').find_all('th')
        keys = [cell.text.strip() for cell in header_cells]

        apartments = []
        # Iterate through each row in the table body
        for row in table.find('tbody').find_all('tr'):
            values = [cell.text.strip() for cell in row.find_all('td')]
            apartment_data = dict(zip(keys, values))
            apartments.append(self.create_apartment(apartment_data))
        return apartments

    def create_apartment(self, data):
        """
                Creates an Apartment object from a dictionary of apartment data.

                Args:
                    data (dict): A dictionary containing apartment data.

                Returns:
                    Apartment: An Apartment object initialized with the provided data.
                """
        # Extract individual data points from the dictionary
        address = data['Building']
        slug = self.slugify(address)
        bedrooms = self.get_bedrooms(data['# of Bedrooms'])
        is_studio = bedrooms == 0
        bathrooms = float(data['# of Baths'])
        price = self.get_price(data['Price (per month)'])
        link = f'http://baileyapartments.com/amenities/{slug}'
        available_date = self.get_available_date(data['Availability (AVAILABLE 2023-2024)'])
        return Apartment(address, price, bedrooms, bathrooms, link, available_date, self.agency_name, is_studio)

    @staticmethod
    def slugify(address):
        """
                Replace spaces and punctuation in an address with URL-friendly characters.

                >>> Bailey.slugify("123 Main St.")
                '123-main-st'
                """
        return address.lower().replace(' ', '-').replace('.', '').replace(',', '')

    @staticmethod
    def get_bedrooms(bedroom_text):
        """
        Return 0 for 'Efficiency' or convert text to integer.

        >>> from bs4 import BeautifulSoup
        >>> html = '<td class="column-1">1 Bedroom</td>'
        >>> bedroom_text = BeautifulSoup(html, 'html.parser').text.strip()
        >>> Bailey.get_bedrooms(bedroom_text)
        1
        >>> html = '<td class="column-1">Efficiency</td>'
        >>> bedroom_text = BeautifulSoup(html, 'html.parser').text.strip()
        >>> Bailey.get_bedrooms(bedroom_text)
        0
        """
        return 0 if 'Efficiency' in bedroom_text else int(bedroom_text.split()[0])

    @staticmethod
    def get_price(price_text):
        """
                Extract the price from text and convert to float.

                >>> Bailey.get_price('$1,200 - $1,500')
                1500.0
                """
        return float(price_text.split(' - ')[-1].replace('$', '').replace(',', ''))

    @staticmethod
    def get_available_date(availability_text):
        """
                Return a fixed date if available or None.

                >>> Bailey.get_available_date('Available')
                '2024-08-01'
                """
        return '2024-08-01' if availability_text == 'Available' else None


if __name__ == "__main__":
    import doctest
    doctest.testmod()


"""
# Usage
scraper = Bailey('http://baileyapartments.com/amenities/', 'Bailey')
apartments = scraper.parse_data()
for apt in apartments:
    print(apt.address, apt.price, apt.bedrooms, apt.bathrooms, apt.link, apt.available_date, apt.agency_name, apt.is_studio)
"""