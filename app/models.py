from . import db
from datetime import datetime

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mac_address = db.Column(db.String(17), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)
    user_agent = db.Column(db.String(255), nullable=True)
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Client {self.mac_address}>'
