from flask import app
from app.config import config 
if __name__ == "__main__":
    app.run(port=5000, debug=True, host='0.0.0.0')