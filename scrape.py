#!/usr/bin/env python
from pathlib import Path
from toppreise import Scraper

SPECS_DIR = Path('spec')
DATA_DIR = Path('data')


def main():
    for spec in SPECS_DIR.iterdir():
        if spec.stem in ['fan']:
            scraper = Scraper.from_yaml(spec)
            scraper.scrape(max_products=2)
            scraper.to_csv(DATA_DIR / f'{spec.stem}.csv')


if __name__ == "__main__":
    main()
