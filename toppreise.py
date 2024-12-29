#!/usr/bin/env python
import argparse
from bs4 import BeautifulSoup
import pandas as pd
from playwright.sync_api import sync_playwright
import re
from tqdm import tqdm
import yaml

ungrouped_variants_query = '1299760721062_fi_pcds_v=0'


def scrape_website(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        html_content = page.content()
        browser.close()
        return html_content


def get_number_of_products(search_results_url):
    html = scrape_website(search_results_url)
    soup = BeautifulSoup(html, "html.parser")
    hits_string = soup.find('span', class_='f_hits').text
    return int(re.match(r"^([\d']+) hits$", hits_string).group(1).replace("'", ""))


def get_product_list(search_results_url):
    html = scrape_website(search_results_url)
    soup = BeautifulSoup(html, "html.parser")
    matching_nodes = soup.find_all(id=re.compile(r"^Plugin_Product_.*"))
    matching_nodes += soup.find_all(id=re.compile(r"^Plugin_Offer_.*"))
    return matching_nodes


def get_product_link(product_node):
    return 'https://www.toppreise.ch' + product_node.find_all('a')[0]['href']


def get_product_features(product_url, filter=None):
    # Some Toppreise URLs point to external sites, we filter these together with any other
    # possibly unexpected URLs.
    if not product_url.startswith('https://www.toppreise.ch/price-comparison'):
        print(f'Discarding product {product_url} at unsupported URL')
        return None
    else:
        html = scrape_website(product_url)
        try:
            # Parse product page HTML
            soup = BeautifulSoup(html, "html.parser")

            # Get generic product features (price, manufacturer, name)
            price = float(soup.find('div', class_="Plugin_Price").text.strip().replace("'", ""))
            manufacturer = soup.find('span', class_="manu").text.strip()
            title = soup.find('span', class_="title break")
            if title is None:
                title = soup.find('span', class_="title")
            name = title.text.strip().split(',')[0]
            features = {
                'manufacturer': manufacturer,
                'name': name,
                'price': price,
                'link': product_url
            }

            # Get product feature categories
            category_nodes = soup.find_all(id=re.compile(r"^Plugin_ProductNgfFeatureCategory_.*"))

            # Iterate feature categories
            for category_node in category_nodes:
                category_name = category_node.find('div', class_='featureCatName').text.strip()
                features[category_name] = {}

                # Get features in category
                feature_nodes = category_node.find_all(id=re.compile(r"^Plugin_ProductNgfFeature_.*"))

                # Iterate features in category
                for feature_node in feature_nodes:
                    key = feature_node.find('div', class_='name').text.strip()
                    value = feature_node.find('div', class_='value').text.strip()
                    features[category_name][key] = value

            # Filter features if requested
            if filter is not None:
                filtered_features = {}
                try:
                    # Iterate entries in filter structure
                    for entry in filter:
                        # If entry is a category, feature is found in subkeys
                        if isinstance(entry, dict):
                            category = list(entry.keys())[0]
                            for feature in list(entry.values())[0]:
                                filtered_features[feature] = features[category][feature]
                        else:
                            filtered_features[entry] = features[entry]
                    return filtered_features
                except KeyError as e:
                    print(f'Discarding product {product_url} missing required features: {e}')
                    return None
            else:
                return features

        except Exception as e:
            raise Exception(f"Error while scraping {product_url}: {e}")


class Scraper():

    def __init__(self, url, features=None):
        self.url = url + '?' + ungrouped_variants_query
        self.features = features

    @classmethod
    def from_yaml(cls, path):
        with open(path, 'r') as file:
            config = yaml.safe_load(file)
        return cls(config['url'], config['features'])

    def scrape(self, max_products=float('inf')):
        num_products = get_number_of_products(self.url)
        num_products = int(min(num_products, max_products))

        products = []
        remaining_products = num_products
        discarded_products = 0

        # Create progress bar
        with tqdm(total=num_products, desc="Scraping Products") as pbar:

            # Iterate search pages until we went through all products
            while remaining_products > 0:

                # Get links to all products in search page
                product_list = get_product_list(self.url + f'&sfh=o~{len(products)}')
                product_links = [get_product_link(product) for product in product_list]

                # Iterate products in page
                for link in product_links:

                    # Break when we processed maximum number of products
                    if remaining_products > 0:

                        product = get_product_features(link, self.features)

                        # Check if a valid product was returned, else count it as discarded
                        if product is not None:
                            products.append(product)
                        else:
                            discarded_products += 1

                        remaining_products -= 1
                        pbar.update(1)

                    else:
                        break

        print(f"Discarded {discarded_products} products")
        self.products = products
        return self.products

    def to_csv(self, path):
        df = pd.DataFrame(self.products)
        df.to_csv(path, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape a Toppreise results webpage')
    parser.add_argument('url', type=str, help='URL of the results page')
    parser.add_argument('features', type=str, nargs='+', help='Features to scrape')
    parser.add_argument('--max-products', type=int, default=float('inf'), help='Maximum number of products to scrape')
    parser.add_argument('--output', type=str, default='output.csv', help='Output file path')
    args = parser.parse_args()
    scraper = Scraper(args.url, args.features)
    scraper.scrape(args.max_products)
    scraper.to_csv(args.output)
