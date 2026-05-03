from flask import Flask, jsonify, request
from flask_cors import CORS
from database import get_supabase

app = Flask(__name__)
CORS(app)

supabase = get_supabase()

@app.route('/api/politicians', methods=['GET'])
def get_politicians():
    query = request.args.get('q', '').lower()
    
    try:
        # We only want politicians who have at least one entry in the stocks table.
        # Supabase/Postgrest handles this well with inner joins or filtering by associated table existence.
        # Here we select politicians and filter where stocks is not empty.
        
        # 'stocks!inner(id)' does an inner join, effectively filtering out 
        # politicians without any matching rows in stocks.
        select_query = "*, stocks!inner(id)"
        
        if query:
            # Search by name, party, or state
            res = supabase.table('politicians').select(select_query).or_(
                f"name.ilike.%{query}%,party.ilike.%{query}%,state.ilike.%{query}%"
            ).execute()
        else:
            res = supabase.table('politicians').select(select_query).limit(20).execute()
        
        # We clean the response to remove the nested stock IDs used for filtering
        cleaned_data = []
        for p in res.data:
            p.pop('stocks', None)
            cleaned_data.append(p)
            
        return jsonify(cleaned_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/politicians/<id>', methods=['GET'])
def get_politician(id):
    try:
        # Get politician details
        pol_res = supabase.table('politicians').select('*').eq('id', id).single().execute()
        
        if pol_res.data:
            politician = pol_res.data
            # Get associated investments
            inv_res = supabase.table('investments').select('*').eq('politician_id', id).execute()
            politician['investments'] = inv_res.data
            
            # Get associated stocks
            stock_res = supabase.table('stocks').select('*').eq('politician_id', id).execute()
            politician['stocks'] = stock_res.data
            
            return jsonify(politician)
        
        return jsonify({"error": "Politician not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/richest', methods=['GET'])
def get_richest_politicians():
    try:
        res = supabase.table('politicians').select('name, party, total_assets').order('total_assets', desc=True).limit(10).execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/party-wealth', methods=['GET'])
def get_party_wealth():
    try:
        # This is better done with a raw RPC or complex query, but we'll aggregate in Python for simplicity
        res = supabase.table('politicians').select('party, total_assets').execute()
        wealth_map = {}
        for p in res.data:
            party = p['party'] or 'Unknown'
            wealth_map[party] = wealth_map.get(party, 0) + float(p['total_assets'] or 0)
        
        # Sort and return as list of dicts
        sorted_wealth = sorted([{"party": k, "total_assets": v} for k, v in wealth_map.items()], key=lambda x: x['total_assets'], reverse=True)
        return jsonify(sorted_wealth[:10])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/popular-stocks', methods=['GET'])
def get_popular_stocks():
    try:
        # Fetch company name, total value, and politician id
        res = supabase.table('stocks').select('company_name, total_value, politician_id').execute()
        
        stock_stats = {}
        for s in res.data:
            name = s['company_name']
            if name not in stock_stats:
                stock_stats[name] = {
                    "company": name,
                    "count": 0,
                    "total_value": 0,
                    "politician_ids": set()
                }
            
            stock_stats[name]["total_value"] += float(s['total_value'] or 0)
            stock_stats[name]["politician_ids"].add(s['politician_id'])
            
        # Transform for JSON and count unique politicians
        result = []
        for name, stats in stock_stats.items():
            result.append({
                "company": name,
                "count": len(stats["politician_ids"]),
                "total_value": stats["total_value"]
            })
            
        # Sort by unique holder count primarily, then total value
        sorted_stocks = sorted(result, key=lambda x: (x['count'], x['total_value']), reverse=True)
        
        return jsonify(sorted_stocks[:20])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/party-stock-stats', methods=['GET'])
def get_party_stock_stats():
    try:
        # Join stocks with politicians to get party info
        # query format: table.select('*, other_table(column)')
        res = supabase.table('stocks').select('id, politician_id, politicians(party)').execute()
        
        party_counts = {}
        for item in res.data:
            # item['politicians'] is a dict because of the join
            party = item.get('politicians', {}).get('party') or 'Unknown'
            party_counts[party] = party_counts.get(party, 0) + 1
            
        # Sort by count
        sorted_stats = sorted([{"party": k, "count": v} for k, v in party_counts.items()], key=lambda x: x['count'], reverse=True)
        return jsonify(sorted_stats)
    except Exception as e:
        print(f"Error in party-stock-stats: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
