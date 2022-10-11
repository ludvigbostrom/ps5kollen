from dataclasses import dataclass
from typing import Callable

import requests
from requests import Response
from bs4 import BeautifulSoup


@dataclass
class Page:
    name: str
    url: str
    msg: str
    check: Callable[[Response, bool], bool] = lambda x, y, z: False
    headers: dict = None
    visit_url: str = None
    is_digital: bool = False

    def check_stock(self):
        resp = requests.get(self.url, headers=self.headers, timeout=10)
        return self.check(resp, self.is_digital)


@dataclass
class PostPage(Page):
    post_data: dict = None

    def check_stock(self):
        resp = requests.post(self.url, headers=self.headers, data=self.post_data, timeout=10)
        return self.check(resp, self.is_digital)


def is_valid_ps5(title: str, is_digital: bool) -> bool:
    lower_title = title.lower()
    return ((not is_digital and 'playstation 5' in lower_title and 'digital' not in lower_title) or
            (is_digital and 'playstation 5' in lower_title and 'digital' in lower_title))


def webhallen(resp: Response, is_digital: bool) -> bool:
    data = resp.json()
    if resp.status_code != 200:
        return False
    if data['totalProductCount'] <= 0:
        return False
    in_stock = False
    for product in data['products']:
        name = product["name"]

        if is_valid_ps5(name, is_digital) and product['stock']['web'] > 0 and 9 not in product['statusCodes']:
            in_stock = True
    return in_stock


def ginza(resp: Response) -> bool:
    soup = BeautifulSoup(resp.content, "html.parser")
    price_area = soup.find('div', class_='price-area')
    link = price_area.find('a')

    return link.text.strip() != 'Bevaka'


def inet(resp: Response, is_digital: bool) -> bool:
    soup = BeautifulSoup(resp.content, "html.parser")
    buttons = soup.find_all('button', class_='btn')
    in_stock = False
    for b in buttons:
        if hasattr(b, 'attrs') and 'buy_button' in b.attrs.get('data-test-id', ''):
            name = b.parent.parent.parent.findChild('a').attrs.get('aria-label', '').lower()
            if is_valid_ps5(name, is_digital):
                if b.text.lower() == 'köp':
                    in_stock = True
    return in_stock


def netonnet(resp: Response, is_digital: bool) -> bool:
    soup = BeautifulSoup(resp.content, "html.parser")
    tracking_products = soup.find_all('div', class_='cProductItem')
    for t in tracking_products:
        title = t.find('div', class_='smallHeader').find('div', class_='shortText').text
        if is_valid_ps5(title, is_digital):
            if t.find('div', class_='warehouseStockStatusContainer').find('i', class_='check'):
                return True
    return False


def power(resp: Response, is_digital: bool) -> bool:
    data = resp.json()
    if data['totalProductCount'] <= 0:
        return False
    products = data['products']
    for product in products:
        title = product['title']
        if is_valid_ps5(title, is_digital):
            if product['stockCount'] > 0:
                if product.get('canAddToCart', False):
                    return True
    return False


def maxgaming(resp: Response, is_digital: bool) -> bool:
    soup = BeautifulSoup(resp.content, "html.parser")
    product_items = soup.find_all('div', class_='PT_Wrapper')
    in_stock = False
    for product in product_items:
        title = product.find('div', class_='PT_Beskr').text
        if is_valid_ps5(title, is_digital):
            if product.find('div', class_='PT_text_Lagerstatus').text.lower().strip() == 'i lager':
                in_stock = True
    return in_stock


def mediamarkt(resp: Response, is_digital: bool) -> bool:
    soup = BeautifulSoup(resp.content, "html.parser")
    product_list = soup.find('ul', class_='products-list')
    product_items = product_list.find_all('div', class_='product-wrapper')
    in_stock = False
    for product in product_items:
        content = product.find('div', class_='content')
        if not content:
            print('Content not found')
            continue
        title = content.find('h2').text
        if is_valid_ps5(title, is_digital):
            if product.find('meta', itemprop='availability', content='InStock'):
                in_stock = True

    return in_stock


def spelochsant(resp: Response, is_digital: bool) -> bool:
    data = resp.json()
    for product in data['products']:
        name = product['name']
        if is_valid_ps5(name, is_digital) and int(product['stock']['quantity']) > 0:
            return True
    return False


def amazon(resp: Response, is_digital: bool) -> bool:
    edition = 'edition_0' if is_digital else 'edition_10'
    soup = BeautifulSoup(resp.content, "html.parser")
    selected_edition = soup.find('li', class_='swatchSelect')
    if not selected_edition:
        print('seleted_edition is None')
        return False
    if selected_edition['id'] == edition:
        if soup.find('input', id='buy-now-button'):
            return True
    return False


WEBHALLEN_SE = Page(
    name='Webhallen standard edition',
    url='https://www.webhallen.com/api/search?query%5BsortBy%5D=sales&query%5Bfilters%5D%5B0%5D%5Btype%5D=category&query%5Bfilters%5D%5B0%5D%5Bvalue%5D=16279&query%5BminPrice%5D=0&query%5BmaxPrice%5D=999999&page=1',
    visit_url='https://www.webhallen.com/se/category/16279-Konsol',
    check=webhallen,
    is_digital=False,
    msg='Webhallen har nu Playstation 5 Standard edition i lager.',
)
WEBHALLEN_DE = Page(
    name='Webhallen digital edition',
    url='https://www.webhallen.com/api/search?query%5BsortBy%5D=sales&query%5Bfilters%5D%5B0%5D%5Btype%5D=category&query%5Bfilters%5D%5B0%5D%5Bvalue%5D=16279&query%5BminPrice%5D=0&query%5BmaxPrice%5D=999999&page=1',
    visit_url='https://www.webhallen.com/se/category/16279-Konsol',
    check=webhallen,
    is_digital=True,
    msg='Webhallen har nu Playstation 5 Digital edition i lager.',
)
INET_SE = Page(
    name='Inet standard edition',
    url='https://www.inet.se/kategori/751/konsoler/180/sony',
    check=inet,
    headers={
        'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Upgrade-Insecure-Requests': '1',
    },
    is_digital=False,
    msg='Inet har nu Playstation 5 Standard edition i lager.',
)
INET_DE = Page(
    name='Inet digital edition',
    url='https://www.inet.se/kategori/751/konsoler/180/sony',
    check=inet,
    headers={
        'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Upgrade-Insecure-Requests': '1',
    },
    is_digital=True,
    msg='Inet har nu Playstation 5 Digital edition i lager.',
)
NETONNET_SE = Page(
    name='Netonnet standard edition',
    url='https://www.netonnet.se/art/gaming/spel-och-konsol/playstation/playstation-konsol',
    check=netonnet,
    headers={
        'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Upgrade-Insecure-Requests': '1',
    },
    is_digital=False,
    msg='NetOnNet har nu Playstation 5 Standard edition i lager.',
)
NETONNET_DE = Page(
    name='Netonnet digital edition',
    url='https://www.netonnet.se/art/gaming/spel-och-konsol/playstation/playstation-konsol',
    check=netonnet,
    is_digital=True,
    headers={
        'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Upgrade-Insecure-Requests': '1',
    },
    msg='NetOnNet har nu Playstation 5 Digital edition i lager.',
)
POWER_SE = Page(
    name='Power standard edition',
    url='https://www.power.se/api/v2/productlists?cat=7416&size=36&s=5&from=0&o=false',
    visit_url='https://www.power.se/c/7416/gaming/playstation/playstation-konsoler/',
    check=power,
    is_digital=False,
    msg='Power har nu Playstation 5 Standard edition i lager.',
)
POWER_DE = Page(
    name='Power digital edition',
    url='https://www.power.se/api/v2/productlists?cat=7416&size=36&s=5&from=0&o=false',
    visit_url='https://www.power.se/c/7416/gaming/playstation/playstation-konsoler/',
    check=power,
    is_digital=True,
    msg='Power har nu Playstation 5 Digital edition i lager.',
)
MAXGAMING_SE = Page(
    name='Maxgaming standard edition',
    url='https://www.maxgaming.se/sv/konsol/playstation/playstation-5',
    check=maxgaming,
    is_digital=False,
    msg='MaxGaming har nu Playstation 5 Standard edition i lager.',
)
MAXGAMING_DE = Page(
    name='Maxgaming digital edition',
    url='https://www.maxgaming.se/sv/konsol/playstation/playstation-5',
    check=maxgaming,
    is_digital=True,
    msg='MaxGaming har nu Playstation 5 Digital edition i lager.',
)

MEDIAMARKT_SE = Page(
    name='Mediamarkt standard edition',
    url='https://www.mediamarkt.se/sv/category/_playstation-5-konsoler-766514.html',
    is_digital=False,
    check=mediamarkt,
    msg='MediaMarkt har nu Playstation 5 Standard edition i lager.',
)

MEDIAMARKT_DE = Page(
    name='Mediamarkt digital edition',
    url='https://www.mediamarkt.se/sv/category/_playstation-5-konsoler-766514.html',
    check=mediamarkt,
    is_digital=True,
    msg='MediaMarkt har nu Playstation 5 Digital edition i lager.',
)

SPELOCHSANT_SE = PostPage(
    name='Spel och Sånt Standard edition',
    url='https://www.spelochsant.se/products/json',
    post_data={'category': 369},
    check=spelochsant,
    is_digital=False,
    msg='Spel och Sånt har nu Playstation 5 Standard edition i lager.',
    visit_url='https://www.spelochsant.se/kategori/playstation5/konsol',
)

SPELOCHSANT_DE = PostPage(
    name='Spel och Sånt Digital edition',
    url='https://www.spelochsant.se/products/json',
    post_data={'category': 369},
    check=spelochsant,
    is_digital=True,
    msg='Spel och Sånt har nu Playstation 5 Digital edition i lager.',
    visit_url='https://www.spelochsant.se/kategori/playstation5/konsol',
)

AMAZON_SE = PostPage(
    name='Amazon Standard edition',
    url='https://www.amazon.se/dp/B08LLZ2CWD',
    check=amazon,
    headers={
        'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Upgrade-Insecure-Requests': '1',
    },
    is_digital=False,
    msg='Amazon har nu Playstation 5 Standard edition i lager.',
)

AMAZON_DE = Page(
    name='Amazon Digital edition',
    url='https://www.amazon.se/dp/B08LM3KW18',
    check=amazon,
    headers={
        'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Upgrade-Insecure-Requests': '1',
    },
    is_digital=True,
    msg='Amazon har nu Playstation 5 Digital edition i lager.',
)

PAGES = [
     WEBHALLEN_DE, WEBHALLEN_SE,
     INET_DE, INET_SE,
     NETONNET_SE, NETONNET_DE,
     POWER_DE, POWER_SE,
     MAXGAMING_DE, MAXGAMING_SE,
     MEDIAMARKT_DE, MEDIAMARKT_SE,
     SPELOCHSANT_DE, SPELOCHSANT_SE,
      AMAZON_DE, AMAZON_SE,
]
