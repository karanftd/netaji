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

            # NOTE: Investment parsing is complex and not fully implemented.
            investments = []

            return {
                'name': name, 'party': party, 'constituency': constituency.strip(), 'state': state.strip(),
                'total_assets': total_assets, 'total_liabilities': total_liabilities,
                'investments': investments, 'source_url': url
            }
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None