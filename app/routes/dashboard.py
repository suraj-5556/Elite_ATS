import json
import os
from flask import Blueprint, render_template, jsonify

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def dashboard():
    return render_template('dashboard.html')

@dashboard_bp.route('/api/stats')
def api_stats():
    stats = {
        'total_analyses': 0,
        'avg_score': 0,
        'high_matches': 0,
        'recent': []
    }
    
    log_file = 'logs/predictions.jsonl'
    if os.path.exists(log_file):
        entries = []
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    entries.append(json.loads(line.strip()))
                except:
                    pass
        
        if entries:
            stats['total_analyses'] = len(entries)
            scores = [e.get('final_score', 0) for e in entries if e.get('final_score')]
            stats['avg_score'] = round(sum(scores) / len(scores), 1) if scores else 0
            stats['high_matches'] = sum(1 for e in entries if e.get('final_score', 0) >= 70)
            stats['recent'] = entries[-5:][::-1]
    
    return jsonify(stats)
