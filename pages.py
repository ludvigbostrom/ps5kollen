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
    check: Callable[[Response], bool] = lambda x: False
    headers: dict = None
    visit_url: str = None

    def check_stock(self):
        resp = requests.get(self.url, headers=self.headers, timeout=10)
        return self.check(resp)


def webhallen(resp: Response) -> bool:
    data = resp.json()
    if resp.status_code != 200:
        return False
    if 9 in data['product']['statusCodes']:
        return False
    return True


def ginza(resp: Response) -> bool:
    soup = BeautifulSoup(resp.content, "html.parser")
    price_area = soup.find('div', class_='price-area')
    link = price_area.find('a')

    return link.text.strip() != 'Bevaka'


def inet(resp: Response) -> bool:
    soup = BeautifulSoup(resp.content, "html.parser")
    qty_strings = soup.find_all('span', class_='qty-string')
    for s in qty_strings:
        if s.text != '- st':
            return True
    return False


def netonnet(resp: Response) -> bool:
    soup = BeautifulSoup(resp.content, "html.parser")
    tracking_products = soup.find_all('div', class_='cProductItem')
    for t in tracking_products:
        text = t.find('div', class_='smallHeader').find('div', class_='shortText').text
        if ('PlayStation 5' in text or 'Playstation 5' in text) and 'Digital' not in text:
            if t.find('div', class_='warehouseStockStatusContainer').find('i', class_='check'):
                return True
    return False


def netonnet_digital(resp: Response) -> bool:
    soup = BeautifulSoup(resp.content, "html.parser")
    tracking_products = soup.find_all('div', class_='cProductItem')
    for t in tracking_products:
        text = t.find('div', class_='smallHeader').find('div', class_='shortText').text
        if 'PlayStation 5 Digital' in text or 'Playstation 5 Digital' in text:
            if t.find('div', class_='warehouseStockStatusContainer').find('i', class_='check'):
                return True
    return False


def komplett(resp: Response) -> bool:
    soup = BeautifulSoup(resp.content, "html.parser")
    action_button = soup.find('div', class_='actionButton-completeGrid')
    if action_button.find('div', class_='buy-button'):
        return True
    return False


def power(resp: Response) -> bool:
    products = resp.json()
    if len(products) > 0 and products[0]['StockCount'] > 0:
        return True
    return False


def maxgaming(resp: Response) -> bool:
    soup = BeautifulSoup(resp.content, "html.parser")
    saldo_amount = soup.find('div', class_='saldoamount')
    if int(saldo_amount['data-saldo']) > 0:
        return True
    return False


def mediamarkt(resp: Response) -> bool:
    soup = BeautifulSoup(resp.content, "html.parser")
    price_sidebar = soup.find('div', class_='price-sidebar')
    if price_sidebar.find('a', class_='instockonline'):
        return True
    return False


WEBHALLEN_SE = Page(
    name='Webhallen standard edition',
    url='https://www.webhallen.com/api/product/300815',
    visit_url='https://www.webhallen.com/se/product/300815-Playstation-5-Konsol-PS5',
    check=webhallen,
    msg='Webhallen har nu Playstation 5 Standard edition i lager.',
)
WEBHALLEN_DE = Page(
    name='Webhallen digital edition',
    url='https://www.webhallen.com/api/product/320479',
    visit_url='https://www.webhallen.com/se/product/320479-Playstation-5-Digital-Edition',
    check=webhallen,
    msg='Webhallen har nu Playstation 5 Digital edition i lager.',
)

GINZA_SE = Page(
    name='Ginza standard edition',
    url='https://www.ginza.se/product/ps5-basenhet/406570/',
    check=ginza,
    msg='Ginza har nu Playstation 5 Standard edition i lager.',
)
GINZA_DE = Page(
    name='Ginza digital edition',
    url='https://www.ginza.se/product/ps5-basenhet-digital-edition/406571/',
    check=ginza,
    msg='Ginza har nu Playstation 5 Digital edition i lager.',
)
INET_SE = Page(
    name='Inet standard edition',
    url='https://www.inet.se/produkt/6609649/sony-playstation-5',
    check=inet,
    msg='Inet har nu Playstation 5 Standard edition i lager.',
)
INET_DE = Page(
    name='Inet digital edition',
    url='https://www.inet.se/produkt/6609862/sony-playstation-5-digital-edition',
    check=inet,
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
    msg='NetOnNet har nu Playstation 5 Standard edition i lager.',
)
NETONNET_DE = Page(
    name='Netonnet digital edition',
    url='https://www.netonnet.se/art/gaming/spel-och-konsol/playstation/playstation-konsol',
    check=netonnet_digital,
    headers={
        'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Upgrade-Insecure-Requests': '1',
    },
    msg='NetOnNet har nu Playstation 5 Digital edition i lager.',
)
POWER_SE = Page(
    name='Power standard edition',
    url='https://www.power.se/umbraco/api/product/getproductsbyids?ids=1077687',
    visit_url='https://www.power.se/gaming/playstation/playstation-konsoler/playstation-5/p-1077687/',
    check=power,
    msg='Power har nu Playstation 5 Standard edition i lager.',
)
POWER_DE = Page(
    name='Power digital edition',
    url='https://www.power.se/umbraco/api/product/getproductsbyids?ids=1101680',
    visit_url='https://www.power.se/gaming/playstation/playstation-konsoler/playstation-5-digital-edition/p-1101680/',
    check=power,
    msg='Power har nu Playstation 5 Digital edition i lager.',
)
KOMPLETT_SE = Page(
    name='Komplett standard edition',
    url='https://www.komplett.se/product/1111557/gaming/playstation/playstation-5',
    check=komplett,
    msg='Komplett har nu Playstation 5 Standard edition i lager.',
)
KOMPLETT_DE = Page(
    name='Komplett digital edition',
    url='https://www.komplett.se/product/1161553/gaming/playstation/playstation-5-digital-edition',
    check=komplett,
    msg='Komplett har nu Playstation 5 Digital edition i lager.',
)
MAXGAMING_SE = Page(
    name='Maxgaming standard edition',
    url='https://www.maxgaming.se/sv/playstation-5/playstation-5',
    check=maxgaming,
    msg='MaxGaming har nu Playstation 5 Standard edition i lager.',
)
MAXGAMING_DE = Page(
    name='Maxgaming digital edition',
    url='https://www.maxgaming.se/sv/playstation-5/playstation-5-digiatal-edition',
    check=maxgaming,
    msg='MaxGaming har nu Playstation 5 Digital edition i lager.',
)

MEDIAMARKT_SE = Page(
    name='Mediamarkt standard edition',
    url='https://www.mediamarkt.se/sv/product/_sony-playstation-5-ps5-1283580.html',
    check=mediamarkt,
    msg='MediaMarkt har nu Playstation 5 Standard edition i lager.',
)

# Mediamarkt Digital edition temporarily disabled. No actual listing on website.
MEDIAMARKT_DE = Page(
    name='Mediamarkt digital edition',
    url='https://www.mediamarkt.se/sv/product/_sony-playstation-5-ps5-digital-edition-1325322.html',
    check=mediamarkt,
    msg='MediaMarkt har nu Playstation 5 Digital edition i lager.',
)

PAGES = [WEBHALLEN_DE, WEBHALLEN_SE, INET_DE, INET_SE, NETONNET_SE, NETONNET_DE, POWER_DE, POWER_SE, KOMPLETT_DE,
         KOMPLETT_SE, MAXGAMING_DE, MAXGAMING_SE, MEDIAMARKT_SE, GINZA_SE, GINZA_DE]
