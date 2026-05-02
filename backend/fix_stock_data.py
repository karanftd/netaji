import re
from database import get_supabase

def parse_stock_details(description, total_amount):
    """
    The definitive parsing logic for politician stock holdings.
    Handles: 
    - "Company Name Q. 100, Rate 50"
    - "Reliance 1000 Shares"
    - "SBI Units 500"
    - "Company Name @ 45.5"
    """
    try:
        # Normalize description for value extraction
        desc = description.replace(',', '').replace('Rs.', '').replace('Rs', '')
        
        # 1. Try to find Quantity (Prefixes and Suffixes)
        q_match = re.search(r'(?:Q(?:ty)?\.?|Quantity|Units?|Shares?|Nos\.?)\s*([\d.]+)', desc, re.IGNORECASE)
        q_suffix_match = re.search(r'([\d.]+)\s*(?:Shares?|Units?|Qty|Nos\.?)', desc, re.IGNORECASE)
        
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
        
        # 3. Handle Fallbacks (if no keywords found)
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

        # 4. Clean Company Name: Remove the parts we identified as data
        company_name = description
        if q_str_to_remove:
            company_name = re.sub(re.escape(q_str_to_remove), '', company_name, flags=re.IGNORECASE)
        if r_str_to_remove:
            company_name = re.sub(re.escape(r_str_to_remove), '', company_name, flags=re.IGNORECASE)
        
        # Remove leftovers like "Rate", "Qty", "Units", "@", "Shares"
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
    except:
        return {'company_name': description, 'quantity': None, 'rate': None, 'total_value': total_amount}

def run_fix():
    supabase = get_supabase()
    print("🚀 Starting one-time stock data fix...")
    
    # 1. Fetch all stock-related investments
    res = supabase.table('investments').select('*').execute()
    stock_investments = [
        inv for inv in res.data 
        if any(x in (inv['type'] or '') for x in ['Shares', 'Bonds', 'Debentures'])
    ]
    
    print(f"Found {len(stock_investments)} records to process.")
    
    # 2. Clear current stocks table
    # We do this to ensure we have a clean slate with the new logic
    politician_ids = list(set(inv['politician_id'] for inv in stock_investments))
    for p_id in politician_ids:
        supabase.table('stocks').delete().eq('politician_id', p_id).execute()
    
    # 3. Re-parse and Insert
    new_stocks = []
    for inv in stock_investments:
        parsed = parse_stock_details(inv['description'], inv['amount'])
        new_stocks.append({
            'politician_id': inv['politician_id'],
            'company_name': parsed['company_name'],
            'quantity': parsed['quantity'],
            'rate': parsed['rate'],
            'total_value': parsed['total_value']
        })
        
    if new_stocks:
        # Insert in chunks
        chunk_size = 100
        for i in range(0, len(new_stocks), chunk_size):
            batch = new_stocks[i:i+chunk_size]
            supabase.table('stocks').insert(batch).execute()
            print(f"✅ Updated batch {i//chunk_size + 1}")
            
    print(f"\n🎉 Success! All {len(new_stocks)} stock records have been fixed.")

if __name__ == '__main__':
    run_fix()
