# app/models.py

from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

# ... (favorites association table remains the same) ...
favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'), primary_key=True)
)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    # ... (no changes to the User model) ...
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    # Add new profile fields
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    bio = db.Column(db.String(255), nullable=True)
    reviews = db.relationship('Review', backref='author', lazy=True, cascade="all, delete-orphan")
    favorited_items = db.relationship('Item', secondary=favorites, backref=db.backref('favorited_by', lazy='dynamic'))

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    # Add the image_url column
    image_url = db.Column(db.String(255), nullable=False, default='https://placehold.co/600x400/CCCCCC/FFFFFF?text=No+Image')
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    reviews = db.relationship('Review', backref='item', lazy=True, cascade="all, delete-orphan")

    # ... (properties like avg_rating remain the same) ...
    @property
    def avg_rating(self):
        if not self.reviews: return 0
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)
    
    @property
    def review_count(self):
        return len(self.reviews)

    @property
    def avg_sentiment(self):
        if not self.reviews: return 0
        sentiments = [r.sentiment for r in self.reviews if r.sentiment is not None]
        if not sentiments: return 0
        return round(sum(sentiments) / len(sentiments), 2)


class Review(db.Model):
    # ... (no changes to the Review model) ...
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(120), nullable=True)
    sentiment = db.Column(db.Float, nullable=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
