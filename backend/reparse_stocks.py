import re
from scraper import MyNetaScraper
from database import get_supabase

def reparse_all_stocks():
    scraper = MyNetaScraper()
    supabase = get_supabase()
    
    print("Fetching all stock-related investments from Supabase...")
    
    # Fetch investments that might be stocks
    # We look for common keywords in the 'type' column
    try:
        # Get all investments first (filtering in Python for flexibility)
        res = supabase.table('investments').select('*').execute()
        all_investments = res.data
        
        print(f"Found {len(all_investments)} total investments. Filtering for stocks...")
        
        stock_investments = [
            inv for inv in all_investments 
            if any(x in (inv['type'] or '') for x in ['Shares', 'Bonds', 'Debentures'])
        ]
        
        print(f"Identified {len(stock_investments)} stock-related records to re-parse.")
        
        # Group by politician to clear their stocks efficiently
        politician_ids = list(set(inv['politician_id'] for inv in stock_investments))
        
        print(f"Clearing old stock data for {len(politician_ids)} politicians...")
        for p_id in politician_ids:
            supabase.table('stocks').delete().eq('politician_id', p_id).execute()
            
        # Re-parse and insert
        new_stocks = []
        for inv in stock_investments:
            parsed = scraper.parse_stock_details(inv['description'], inv['amount'])
            
            new_stocks.append({
                'politician_id': inv['politician_id'],
                'company_name': parsed['company_name'],
                'quantity': parsed['quantity'],
                'rate': parsed['rate'],
                'total_value': parsed['total_value']
            })
            
        if new_stocks:
            # Insert in batches of 100
            for i in range(0, len(new_stocks), 100):
                batch = new_stocks[i:i+100]
                supabase.table('stocks').insert(batch).execute()
                print(f"  Inserted batch {i//100 + 1}...")
                
        print(f"\nSuccess! Re-parsed and updated {len(new_stocks)} stock records.")
        
    except Exception as e:
        print(f"Error during re-parsing: {e}")
    finally:
        scraper.close()

if __name__ == '__main__':
    reparse_all_stocks()
