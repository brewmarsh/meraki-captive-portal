from app import create_app
import os
from dotenv import load_dotenv

load_dotenv()

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
    app.run(host='0.0.0.0', port=port, debug=debug)
