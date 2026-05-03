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

    def parse_stock_details(self, description, total_amount):
        """
        Tries to parse company name, quantity, and rate from description.
        Example: "3I Infotech Ltd Q. 200, Rate.40.05"
        Example: "Reliance Communication 1000 Shares"
        Example: "State Bank of India Units 1000"
        """
        print(f"  [DEBUG] Parsing stock: {description[:50]}...")
        try:
            # Normalize description for value extraction
            desc = description.replace(',', '').replace('Rs.', '').replace('Rs', '')
            
            # 1. Try to find Quantity (Prefixes and Suffixes)
            q_match = re.search(r'(?:Q(?:ty)?\.?|Quantity|Units?|Shares?)\s*([\d.]+)', desc, re.IGNORECASE)
            q_suffix_match = re.search(r'([\d.]+)\s*(?:Shares?|Units?|Qty|Nos)', desc, re.IGNORECASE)
            
            # 2. Try to find Rate
            r_match = re.search(r'(?:Rate\.?|@|at)\s*([\d.]+)', desc, re.IGNORECASE)
            
            quantity = None
            q_str_to_remove = ""
            if q_match:
                quantity = float(q_match.group(1))
                q_str_to_remove = q_match.group(0)
            elif q_suffix_match:
                quantity = float(q_suffix_match.group(1))
                q_str_to_remove = q_suffix_match.group(0)
            
            rate = float(r_match.group(1)) if r_match else None
            r_str_to_remove = r_match.group(0) if r_match else ""
            
            # 3. Handle Fallbacks
            matches = re.findall(r'[\d.]+', desc)
            if quantity is None and len(matches) >= 1:
                if len(matches) >= 2:
                    quantity = float(matches[0])
                    rate = float(matches[1])
                    q_str_to_remove = matches[0]
                    r_str_to_remove = matches[1]
                else:
                    if any(x in desc.lower() for x in ['share', 'unit', 'qty', 'nos']):
                        quantity = float(matches[0])
                        q_str_to_remove = matches[0]

            # Company name extraction: Remove the parts we identified as data
            company_name = description
            if q_str_to_remove:
                # Use escaped regex to remove the exact string
                company_name = re.sub(re.escape(q_str_to_remove), '', company_name, flags=re.IGNORECASE)
            if r_str_to_remove:
                company_name = re.sub(re.escape(r_str_to_remove), '', company_name, flags=re.IGNORECASE)
            
            # Remove leftovers like "Rate", "Qty", "Units", "@"
            company_name = re.sub(r'\b(?:Q(?:ty)?\.?|Quantity|Rate\.?|Units?|Shares?|Nos\.?|at|@)\b', '', company_name, flags=re.IGNORECASE)
            # Remove trailing/leading punctuation and whitespace
            company_name = company_name.replace(',', '').replace('()', '').strip()
            company_name = re.sub(r'^[ivx.\s]+', '', company_name).strip()
            
            if not company_name: company_name = description
            
            return {
                'company_name': company_name,
                'quantity': quantity,
                'rate': rate,
                'total_value': total_amount
            }
        except Exception as e:
            print(f"  [DEBUG] Parsing error: {e}")
            return {
                'company_name': description,
                'quantity': None,
                'rate': None,
                'total_value': total_amount
            }

    def get_all_candidate_urls(self, max_pages=5):
        print(f"Fetching candidate URLs from Analyzed summary (up to {max_pages} pages)...")
        all_candidate_urls = set()
        
        for page in range(1, max_pages + 1):
            print(f"  Fetching page {page}...")
            # MyNeta pagination often uses &page=X
            summary_page_url = f"{self.base_url}index.php?action=summary&sub_action=candidates_analyzed&page={page}"
            self.driver.get(summary_page_url)
            try:
                time.sleep(3)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                # Find all links
                links = soup.find_all('a', href=True)
                page_links_count = 0
                for link in links:
                    href = link['href']
                    if 'candidate.php?candidate_id=' in href:
                        # Extract the query part
                        query_part = href.split('candidate.php')[1]
                        full_url = f"{self.base_url}candidate.php{query_part}"
                        if full_url not in all_candidate_urls:
                            all_candidate_urls.add(full_url)
                            page_links_count += 1
                
                if page_links_count == 0:
                    print("  No more candidates found on this page. Stopping.")
                    break
                    
            except Exception as e:
                print(f"Error fetching candidate URLs on page {page}: {e}")
        
        print(f"Found {len(all_candidate_urls)} unique candidate URLs.")
        return list(all_candidate_urls)

    def is_already_scraped(self, url):
        try:
            res = self.supabase.table('politicians').select('id').eq('source_url', url).execute()
            return len(res.data) > 0
        except:
            return False

    def scrape_candidate(self, url):
        print(f"Scraping {url}...")
        self.update_status() # Refresh count frequently
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
                    # Track current category for rowspan rows
                    current_category = ""
                    for tr in table.find_all('tr')[1:]:
                        tds = tr.find_all('td')
                        if not tds or len(tds) < 2: continue
                        
                        # Detect category and identify columns
                        if tds[0].has_attr('rowspan'):
                            current_category = tds[1].get_text(strip=True)
                            description_td = tds[1]
                            self_td = tds[2] if len(tds) > 2 else None
                        elif len(tds) >= 8:
                            current_category = tds[1].get_text(strip=True)
                            description_td = tds[1]
                            self_td = tds[2]
                        else:
                            description_td = tds[0]
                            self_td = tds[1] if len(tds) > 1 else None

                        if not self_td: continue
                        
                        type_label = description_td.get_text(strip=True)
                        if any(x in type_label for x in ['Total', 'Gross', 'Calculated']):
                            continue

                        # Extract sub-investments by splitting on <br><br>
                        cell_html = str(self_td)
                        # Standardize br tags for easier splitting
                        cell_html = re.sub(r'<br\s*/?>', '<br>', cell_html)
                        item_blocks = cell_html.split('<br><br>')
                        
                        for block in item_blocks:
                            if not block.strip(): continue
                            block_soup = BeautifulSoup(block, 'html.parser')
                            
                            # Extract description from span.desc if it exists
                            desc_span = block_soup.find('span', class_='desc')
                            item_description = desc_span.get_text(strip=True) if desc_span else type_label
                            
                            # To get the amount, we remove all span tags
                            for s in block_soup.find_all('span'):
                                s.decompose()
                            
                            amount_text = block_soup.get_text(strip=True)
                            if amount_text.lower() == 'nil' or not amount_text:
                                continue
                                
                            amount = self.clean_amount(amount_text)
                            if amount > 0:
                                inv_type = current_category if current_category else type_label
                                # Clean up type (remove indices like i, ii, (a), (b))
                                inv_type = re.sub(r'^[ivx\(\)a-z.]+\s*', '', inv_type).strip()
                                
                                inv_item = {
                                    'type': inv_type,
                                    'description': item_description,
                                    'amount': amount
                                }
                                
                                # Stock specific parsing
                                if any(x in inv_type for x in ['Shares', 'Bonds', 'Debentures']):
                                    inv_item['stock_details'] = self.parse_stock_details(item_description, amount)
                                
                                investments.append(inv_item)
            
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

            # If politician existed, clear old investments and stocks before inserting new ones
            self.supabase.table('investments').delete().eq('politician_id', politician_id).execute()
            
            try:
                self.supabase.table('stocks').delete().eq('politician_id', politician_id).execute()
            except:
                print("Note: 'stocks' table not found in Supabase. Skipping stock-specific storage.")

            if data['investments']:
                inv_list = []
                stock_list = []
                for inv in data['investments']:
                    inv_list.append({
                        'politician_id': politician_id,
                        'type': inv['type'],
                        'description': inv['description'],
                        'amount': inv['amount']
                    })
                    
                    if 'stock_details' in inv:
                        s = inv['stock_details']
                        stock_list.append({
                            'politician_id': politician_id,
                            'company_name': s['company_name'],
                            'quantity': s['quantity'],
                            'rate': s['rate'],
                            'total_value': s['total_value']
                        })
                
                if inv_list:
                    self.supabase.table('investments').insert(inv_list).execute()
                
                if stock_list:
                    try:
                        self.supabase.table('stocks').insert(stock_list).execute()
                        print(f"Successfully saved {len(stock_list)} stocks.")
                    except Exception as e:
                        print(f"Could not save stocks to table: {e}")
            
            print(f"Successfully saved {data['name']} to Supabase.")
        except Exception as e:
            print(f"Supabase error for {data.get('name', 'Unknown')}: {e}")

    def update_status(self, page=None, status='running'):
        try:
            update_data = {
                'id': 'loksabha_2024',
                'status': status,
                'last_updated': 'now()',
                'total_pages': 167,
                'total_politicians': 8338
            }
            
            # If page is not provided, try to preserve the existing one from the DB
            if not page:
                try:
                    curr = self.supabase.table('scraping_status').select('current_page').eq('id', 'loksabha_2024').single().execute()
                    if curr.data:
                        update_data['current_page'] = curr.data.get('current_page')
                except:
                    pass
            else:
                update_data['current_page'] = page
                
            # Count total politicians in DB to get processed count
            try:
                res = self.supabase.table('politicians').select('id', count='exact').execute()
                update_data['processed_politicians'] = res.count or 0
            except:
                pass
                
            # Use upsert to ensure the row exists
            self.supabase.table('scraping_status').upsert(update_data).execute()
            print(f"  [STATUS] Page: {update_data.get('current_page', 'N/A')}, Status: {status}")
        except Exception as e:
            print(f"Error updating status: {e}")

    def close(self):
        self.update_status(status='idle')
        self.driver.quit()


if __name__ == '__main__':
    scraper = MyNetaScraper()
    try:
        # 167 total pages for Lok Sabha 2024
        TOTAL_PAGES = 167
        
        # --- AUTO-RESUME LOGIC ---
        start_page = 1
        try:
            status_res = scraper.supabase.table('scraping_status').select('current_page').eq('id', 'loksabha_2024').single().execute()
            if status_res.data and status_res.data.get('current_page'):
                start_page = status_res.data['current_page']
                print(f"Resuming from last known page: {start_page}")
        except Exception as e:
            print(f"Could not fetch resume point, starting from 1: {e}")

        print(f"Starting FULL LOK SABHA 2024 SCRAPE ({TOTAL_PAGES} pages)...")
        scraper.update_status(status='running')
        
        for page_num in range(start_page, TOTAL_PAGES + 1):
            print(f"\n--- PROCESSING PAGE {page_num}/{TOTAL_PAGES} ---")
            
            # Retry entire page on major network failure
            max_page_retries = 5
            unique_links = []
            
            for page_attempt in range(max_page_retries):
                try:
                    summary_page_url = f"{scraper.base_url}index.php?action=summary&sub_action=candidates_analyzed&page={page_num}"
                    scraper.driver.get(summary_page_url)
                    time.sleep(5)
                    scraper.update_status(page=page_num)
                    
                    soup = BeautifulSoup(scraper.driver.page_source, 'html.parser')
                    links = [l['href'] for l in soup.find_all('a', href=True) if 'candidate.php?candidate_id=' in l['href']]
                    
                    unique_links = []
                    for l in links:
                        q = l.split('candidate.php')[1]
                        full = f"{scraper.base_url}candidate.php{q}"
                        if full not in unique_links: unique_links.append(full)
                    
                    if len(unique_links) > 0:
                        break
                    print(f"  [PAGE RETRY] No candidates found on page {page_num}, attempt {page_attempt+1}...")
                    time.sleep(10)
                except Exception as e:
                    print(f"  [NETWORK ERROR] Failed to load page {page_num}: {e}")
                    scraper.driver.quit()
                    time.sleep(20) # Cool down
                    scraper.driver = scraper.setup_driver()
            
            if not unique_links:
                print(f"CRITICAL: Failed to load page {page_num} after {max_page_retries} attempts. Skipping.")
                continue

            print(f"Found {len(unique_links)} candidates on this page.")
            
            for index, url in enumerate(unique_links):
                # Inner loop error handling (per candidate)
                candidate_retries = 2
                for cand_attempt in range(candidate_retries):
                    try:
                        if scraper.is_already_scraped(url):
                            scraper.update_status() # Keep progress bar moving even on skip
                            break # Success (already done)

                        print(f"  [{index+1}/{len(unique_links)}] Processing {url}...")
                        data = scraper.scrape_candidate(url)
                        if data:
                            scraper.save_to_supabase(data)
                            scraper.update_status() # Update record count
                        break # Success
                    except Exception as e:
                        print(f"  [CANDIDATE ERROR] attempt {cand_attempt+1} for {url}: {e}")
                        # Network recovery
                        scraper.driver.quit()
                        time.sleep(10)
                        scraper.driver = scraper.setup_driver()
                        if cand_attempt == candidate_retries - 1:
                            print(f"  Failed to scrape {url} after {candidate_retries} attempts.")
                
                time.sleep(1) # Base delay
        
        scraper.update_status(status='idle')
                
    finally:
        scraper.close()
        print("\n--- Full election scraping process ended ---")
