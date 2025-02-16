#!/usr/bin/env python
from pathlib import Path
from toppreise import Scraper

SPECS_DIR = Path('spec')
DATA_DIR = Path('data/complete')


def main():
    for spec in SPECS_DIR.iterdir():
        print(f'=== {spec.stem} ===')
        scraper = Scraper.from_yaml(spec)
        scraper.scrape(max_products=400)
        DATA_DIR.mkdir(exist_ok=True, parents=True)
        scraper.to_csv(DATA_DIR / f'{spec.stem}.csv')


if __name__ == "__main__":
    main()
