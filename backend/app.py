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
        if query:
            # Search by name, party, or state
            res = supabase.table('politicians').select('*').or_(
                f"name.ilike.%{query}%,party.ilike.%{query}%,state.ilike.%{query}%"
            ).execute()
        else:
            res = supabase.table('politicians').select('*').limit(20).execute()
        
        return jsonify(res.data)
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
            return jsonify(politician)
        
        return jsonify({"error": "Politician not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
