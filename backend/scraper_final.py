import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from database import get_supabase


class MyNetaScraper:
    def __init__(self):
        self.supabase = get_supabase()
        self.base_url = "https://myneta.info/LokSabha2024/"
        self.driver = self.setup_driver()

    def setup_driver(self):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        driver = webdriver.Firefox(options=options)
        return driver

    def clean_amount(self, amount_str):
        if not amount_str:
            return 0
        try:
            val_part = amount_str.split('~')[0]
            clean_str = re.sub(r'[^\d]', '', val_part.replace('&nbsp;', '').replace('\xa0', ''))
            return int(clean_str) if clean_str else 0
        except:
            return 0

    def get_all_candidate_urls(self):
        print("Fetching all candidate URLs...")
        all_candidate_urls = set()
        main_page_url = f"{self.base_url}index.php?action=show"
        self.driver.get(main_page_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.w3-table"))
            )
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            main_table = None
            all_tables = soup.find_all('table')
            for table in all_tables:
                table_text = table.text
                if 'Candidate' in table_text and 'Party' in table_text and 'Criminal Cases' in table_text:
                    main_table = table
                    break
            if not main_table:
                return []
            
            candidate_rows = main_table.find_all('tr')[1:]
            for row in candidate_rows:
                cols = row.find_all('td')
                if len(cols) > 1:
                    link_tag = cols[1].find('a')
                    if link_tag and 'href' in link_tag.attrs:
                        candidate_profile_url = f"{self.base_url}{link_tag['href']}"
                        all_candidate_urls.add(candidate_profile_url)
        except Exception as e:
            print(f"Error fetching all candidate URLs: {e}")
        
        print(f"Found {len(all_candidate_urls)} unique candidate URLs.")
        return list(all_candidate_urls)

    def scrape_candidate(self, url):
        print(f"Scraping {url}...")
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.w3-twothird"))
            )
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            main_info_div = soup.find('div', class_='w3-twothird')
            if not main_info_div:
                return None

            name = main_info_div.find('h2').text.strip()
            party_tag = main_info_div.find('b', string=re.compile('Party:'))
            party = party_tag.next_sibling.strip() if party_tag and party_tag.next_sibling else "Unknown"
            
            constituency, state = "", ""
            h5_tag = main_info_div.find('h5')
            if h5_tag:
                match = re.search(r'(.+?)\s*\((.+?)\)', h5_tag.text.strip())
                if match:
                    constituency, state = match.groups()

            total_assets = 0
            assets_td = soup.find(lambda tag: tag.name == 'td' and 'Total Assets' in tag.text)
            if assets_td:
                value_cell = assets_td.find_next_sibling('td')
                if value_cell:
                    total_assets = self.clean_amount(value_cell.text)

            total_liabilities = 0
            liabilities_row = soup.find(lambda tag: tag.name == 'tr' and 'Grand Total of Liabilities' in tag.text)
            if liabilities_row:
                value_cell = liabilities_row.find_all('td')[-1]
                if value_cell:
                    total_liabilities = self.clean_amount(value_cell.text)

            # NOTE: Investment parsing is complex and has been skipped.
            investments = []

            return {
                'name': name, 'party': party, 'constituency': constituency.strip(), 'state': state.strip(),
                'total_assets': total_assets, 'total_liabilities': total_liabilities,
                'investments': investments, 'source_url': url
            }
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    def save_to_supabase(self, data):
        if not data:
            return
        
        try:
            politician_data = {
                'name': data['name'], 'party': data['party'],
                'constituency': data['constituency'], 'state': data['state'],
                'total_assets': data['total_assets'], 'total_liabilities': data['total_liabilities'],
                'source_url': data['source_url']
            }
            
            upsert_res = self.supabase.table('politicians').upsert(politician_data, on_conflict='source_url').execute()
            politician_id = upsert_res.data[0]['id']

            self.supabase.table('investments').delete().eq('politician_id', politician_id).execute()
            
            print(f"Successfully saved {data['name']} to Supabase.")
        except Exception as e:
            print(f"Supabase error for {data.get('name', 'Unknown')}: {e}")

    def close(self):
        self.driver.quit()


if __name__ == '__main__':
    scraper = MyNetaScraper()
    try:
        candidate_urls = scraper.get_all_candidate_urls()
        print(f"
--- Starting to scrape {len(candidate_urls)} candidates ---")
        
        for url in candidate_urls:
            data = scraper.scrape_candidate(url)
            if data:
                scraper.save_to_supabase(data)
    finally:
        scraper.close()
        print("
--- Scraping complete ---")
