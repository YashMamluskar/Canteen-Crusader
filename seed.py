# seed.py
from app import create_app, db, bcrypt
from app.models import User, Item, Review
from textblob import TextBlob

# Create an app context to interact with the database
app = create_app()
with app.app_context():
    # --- Clear and Recreate Database ---
    print("--> Dropping all tables and recreating...")
    db.drop_all()
    db.create_all()

    # --- Create Users with Bios ---
    hashed_pw_admin = bcrypt.generate_password_hash('password').decode('utf-8')
    admin_user = User(
        username='admin', 
        password=hashed_pw_admin, 
        is_admin=True,
        bio='The original Canteen Crusader. Finding the best food on campus.'
    )
    
    hashed_pw_user = bcrypt.generate_password_hash('1234').decode('utf-8')
    user_troy = User(
        username='Troy', 
        password=hashed_pw_user,
        bio='Just a student looking for a good lunch.'
    )
    
    db.session.add_all([admin_user, user_troy])
    db.session.commit() 
    print("--> Users 'admin' and 'Troy' created with bios.")

    # --- Create Items with Real Image URLs ---
    items_to_add = [
        Item(name='Veg Samosa', category='Snack', description='Classic crispy samosa with potato filling.', image_url='https://images.unsplash.com/photo-1625709372223-9807de738531?fit=crop&w=800&q=80'),
        Item(name='Paneer Butter Masala', category='Lunch', description='Creamy and rich paneer curry.', image_url='https://images.unsplash.com/photo-1631452180539-96aca7d4062a?fit=crop&w=800&q=80'),
        Item(name='Cold Coffee', category='Beverage', description='Refreshing and strong cold coffee.', image_url='https://images.unsplash.com/photo-1551030173-17d6a1ae25c3?fit=crop&w=800&q=80'),
        Item(name='Chicken Biryani', category='Lunch', description='Aromatic rice dish with tender chicken pieces.', image_url='https://images.unsplash.com/photo-1589302168068-964664d93dc0?fit=crop&w=800&q=80'),
        Item(name='Masala Dosa', category='Breakfast', description='A South Indian classic, crispy and savory.', image_url='https://images.unsplash.com/photo-1626501237233-31c0a7f134c2?fit=crop&w=800&q=80')
    ]
    db.session.add_all(items_to_add)
    db.session.commit()
    print("--> Menu items with real images created.")

    # --- Create Reviews (with sentiment) ---
    item1 = Item.query.filter_by(name='Veg Samosa').first()
    item2 = Item.query.filter_by(name='Paneer Butter Masala').first()
    item3 = Item.query.filter_by(name='Cold Coffee').first()
    item4 = Item.query.filter_by(name='Chicken Biryani').first()

    reviews_to_add = [
        {"rating": 5, "text": 'Absolutely the best samosa on campus!', "author": admin_user, "item": item1},
        {"rating": 4, "text": 'Really good, but a bit too oily sometimes.', "author": user_troy, "item": item1},
        {"rating": 5, "text": 'The Paneer Butter Masala is creamy and delicious.', "author": user_troy, "item": item2},
        {"rating": 2, "text": 'The cold coffee was terrible and watery.', "author": admin_user, "item": item3},
        {"rating": 3, "text": 'The biryani was just average.', "author": user_troy, "item": item4}
    ]
    for review_data in reviews_to_add:
        sentiment_score = TextBlob(review_data["text"]).sentiment.polarity
        new_review = Review(rating=review_data["rating"], text=review_data["text"], author=review_data["author"], item=review_data["item"], sentiment=sentiment_score)
        db.session.add(new_review)
    db.session.commit()
    print("--> Sample reviews with sentiment added.")

    # --- Add Favorite Items ---
    user_troy.favorited_items.append(item1) 
    user_troy.favorited_items.append(item2)
    admin_user.favorited_items.append(item4)
    db.session.commit()
    print("--> Favorite items assigned.")

    print("\n✅ Sample data has been successfully created!")
