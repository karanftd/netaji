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
        # Firefox doesn't use the sandbox/shm arguments in the same way
        driver = webdriver.Firefox(options=options)
        return driver

    def clean_amount(self, text):
        if not text:
            return 0
        try:
            # Remove noise like 'Rs', commas, and the 'Crore+/Lacs+' part
            text = text.split('~')[0]
            text = text.replace('Rs', '').replace(',', '').replace('&nbsp;', '').replace('\xa0', '')
            
            # Use regex to find all numbers (including decimals)
            matches = re.findall(r'\d+(?:\.\d+)?', text)
            if not matches:
                return 0
            
            # Often the "Total" for that cell is at the end.
            return int(float(matches[-1]))
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

            name = main_info_div.find('h2').get_text(strip=True).split('(')[0].strip()
            party_tag = main_info_div.find('b', string=re.compile('Party:'))
            party = party_tag.next_sibling.strip() if party_tag and party_tag.next_sibling else "Unknown"
            
            constituency, state = "", ""
            h5_tag = main_info_div.find('h5')
            if h5_tag:
                match = re.search(r'(.+?)\s*\((.+?)\)', h5_tag.text.strip())
                if match:
                    constituency, state = match.groups()

            # Better parsing for Total Assets and Liabilities from the summary table
            total_assets = 0
            total_liabilities = 0
            summary_table = soup.find('table', class_='w3-table w3-striped')
            if summary_table:
                rows = summary_table.find_all('tr')
                for r in rows:
                    if 'Assets:' in r.text:
                        total_assets = self.clean_amount(r.find_all('td')[1].text)
                    elif 'Liabilities:' in r.text:
                        total_liabilities = self.clean_amount(r.find_all('td')[1].text)

            investments = []
            movable_assets_header = soup.find('h3', string=re.compile('Details of Movable Assets'))
            if movable_assets_header:
                table_div = movable_assets_header.find_parent('div').find_next_sibling('div')
                table = table_div.find('table')
                if table:
                    # We need to track the current category because of rowspans
                    current_category = ""
                    for tr in table.find_all('tr')[1:]: # Skip header
                        tds = tr.find_all('td')
                        if not tds or len(tds) < 2: continue
                        
                        # Handle rowspans for categories (i, ii, iii, iv...)
                        if tds[0].has_attr('rowspan'):
                            current_category = tds[1].get_text(strip=True)
                            description_td = tds[1]
                            self_td = tds[2] if len(tds) > 2 else None
                        elif len(tds) >= 8: # Normal row
                            current_category = tds[1].get_text(strip=True)
                            description_td = tds[1]
                            self_td = tds[2]
                        else: # Row inside a rowspan
                            description_td = tds[0]
                            self_td = tds[1] if len(tds) > 1 else None

                        if not self_td: continue
                        
                        type_name = description_td.get_text(strip=True)
                        if any(x in type_name for x in ['Total', 'Gross', 'Calculated']):
                            continue

                        # Extract sub-investments from the self_td
                        content_str = str(self_td)
                        # Normalize br tags
                        content_str = content_str.replace('<br/>', '<br>').replace('<br >', '<br>')
                        parts = content_str.split('<br>')
                        
                        for part in parts:
                            part_soup = BeautifulSoup(part, 'html.parser')
                            
                            # Ignore if it's just 'Nil' or empty
                            text_content = part_soup.get_text(strip=True)
                            if not text_content or text_content.lower() == 'nil' or len(text_content) < 2:
                                continue
                            
                            # The description for this specific item
                            item_desc_span = part_soup.find('span', class_='desc')
                            item_desc = item_desc_span.get_text(strip=True) if item_desc_span else type_name
                            
                            # Remove all spans from part_soup to get only the amount text
                            for span in part_soup.find_all('span'):
                                span.decompose()
                            
                            amount_text = part_soup.get_text(strip=True)
                            amount = self.clean_amount(amount_text)
                            
                            if amount > 0:
                                investments.append({
                                    'type': current_category if current_category else type_name,
                                    'description': item_desc,
                                    'amount': amount
                                })
            
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
            
            # Use upsert for cleaner logic
            upsert_res = self.supabase.table('politicians').upsert(politician_data, on_conflict='source_url').execute()
            if not upsert_res.data:
                print(f"Upsert failed for {data['name']}")
                return
                
            politician_id = upsert_res.data[0]['id']

            # If politician existed, clear old investments before inserting new ones
            self.supabase.table('investments').delete().eq('politician_id', politician_id).execute()

            if data['investments']:
                inv_list = []
                for inv in data['investments']:
                    inv_list.append({
                        'politician_id': politician_id,
                        'type': inv['type'],
                        'description': inv['description'],
                        'amount': inv['amount']
                    })
                self.supabase.table('investments').insert(inv_list).execute()
            
            print(f"Successfully saved {data['name']} to Supabase.")
        except Exception as e:
            print(f"Supabase error for {data.get('name', 'Unknown')}: {e}")

    def close(self):
        self.driver.quit()


if __name__ == '__main__':
    scraper = MyNetaScraper()
    try:
        # --- DEBUGGING SINGLE CANDIDATE ---
        test_url = "https://myneta.info/LokSabha2024/candidate.php?candidate_id=4427"
        data = scraper.scrape_candidate(test_url)
        if data:
            import json
            print("\n--- Scraped Data ---")
            print(json.dumps(data, indent=2))
            print("--- End Scraped Data ---\n")
            
            scraper.save_to_supabase(data)
    finally:
        scraper.close()
        print("\n--- Scraping complete ---")
