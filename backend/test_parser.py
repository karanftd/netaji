import re

def parse_stock_details(description, total_amount):
    print(f"Parsing: '{description}'")
    try:
        desc = description.replace(',', '').replace('Rs.', '').replace('Rs', '')
        
        # 1. Try to find Quantity (Prefixes and Suffixes)
        q_match = re.search(r'(?:Q(?:ty)?\.?|Quantity|Units?|Shares?)\s*([\d.]+)', desc, re.IGNORECASE)
        q_suffix_match = re.search(r'([\d.]+)\s*(?:Shares?|Units?|Qty|Nos)', desc, re.IGNORECASE)
        
        # 2. Try to find Rate
        r_match = re.search(r'(?:Rate\.?|@|at)\s*([\d.]+)', desc, re.IGNORECASE)
        
        quantity = None
        if q_match:
            quantity = float(q_match.group(1))
        elif q_suffix_match:
            quantity = float(q_suffix_match.group(1))
        
        rate = float(r_match.group(1)) if r_match else None
        
        # 3. Handle Fallbacks
        matches = re.findall(r'[\d.]+', desc)
        if quantity is None and len(matches) >= 1:
            if len(matches) >= 2:
                quantity = float(matches[0])
                rate = float(matches[1])
            else:
                if any(x in desc.lower() for x in ['share', 'unit', 'qty', 'nos']):
                    quantity = float(matches[0])

        # Company name extraction
        company_name = description
        split_match = re.search(r'[\d\(]|Q(?:ty)?\.?|Rate\.?|@|at\s+\d|Units?|Shares?|Quantity', description, re.IGNORECASE)
        if split_match:
            company_name = description[:split_match.start()].strip()
        
        company_name = re.sub(r'^[ivx.\s]+', '', company_name).strip()
        if not company_name: company_name = description
        
        print(f"  Result -> Name: '{company_name}', Qty: {quantity}, Rate: {rate}")
        return {
            'company_name': company_name,
            'quantity': quantity,
            'rate': rate,
            'total_value': total_amount
        }
    except Exception as e:
        print(f"  Error: {e}")
        return None

test_cases = [
    ("Reliance Communication 1000 Shares", 10000),
    ("State Bank of India Units 1000", 50000),
    ("3I Infotech Ltd Q. 200, Rate.40.05", 8010),
    ("HDFC Bank 1500 Shares", 1500000)
]

for desc, val in test_cases:
    parse_stock_details(desc, val)
