"""
TalentAI Application Entry Point.
Run with: python run.py
Or with gunicorn: gunicorn "run:app" --bind 0.0.0.0:5000
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    import os
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '1') == '1'
    
    print(f"""
    ╔══════════════════════════════════════════════╗
    ║          TalentAI - AI Job Portal            ║
    ║   AI-Powered Resume Screening & Matching     ║
    ╠══════════════════════════════════════════════╣
    ║  Starting on http://localhost:{port}           ║
    ║  Debug mode: {'ON ' if debug else 'OFF'}                          ║
    ╚══════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
