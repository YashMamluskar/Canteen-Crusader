# app/routes.py

import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app
from app import db, bcrypt
# Add UpdateProfileForm to this import line
from app.forms import RegistrationForm, LoginForm, ReviewForm, AddItemForm, UpdateProfileForm
from app.models import User, Item, Review
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import func
from datetime import datetime, timedelta
from collections import defaultdict
from textblob import TextBlob

main = Blueprint('main', __name__)


# --- Helper Function for Saving Pictures ---
def save_picture(form_picture, type='review'):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    
    if type == 'profile':
        # Correctly join path from the app's root_path
        upload_path = os.path.join(current_app.root_path, 'static/profile_pics')
        output_size = (150, 150)
    else: # review
        upload_path = os.path.join(current_app.root_path, 'static/uploads')
        output_size = (500, 500)

    # Ensure the upload directory exists
    os.makedirs(upload_path, exist_ok=True)
    picture_path = os.path.join(upload_path, picture_fn)
    
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

# --- Helper function for recommendations ---
def get_recommendations(user):
    reviewed_item_ids = [review.item_id for review in user.reviews]
    category_ratings = defaultdict(lambda: {'total': 0, 'count': 0})
    for review in user.reviews:
        category = review.item.category
        category_ratings[category]['total'] += review.rating
        category_ratings[category]['count'] += 1
    if not category_ratings:
        return None, None
    favorite_category = max(category_ratings, key=lambda cat: category_ratings[cat]['total'] / category_ratings[cat]['count'])
    recommendations = Item.query.filter(Item.category == favorite_category, Item.id.notin_(reviewed_item_ids)).all()
    recommendations.sort(key=lambda item: item.avg_rating, reverse=True)
    return recommendations[:3], favorite_category

# --- Main Routes ---
@main.route("/")
@main.route("/home")
def home():
    top_items_query = db.session.query(Item, func.avg(Review.rating).label('average_rating')).join(Review).group_by(Item.id).order_by(func.avg(Review.rating).desc()).limit(3).all()
    top_items = [item for item, avg_rating in top_items_query]
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    trending_items_query = db.session.query(Item, func.count(Review.id).label('review_count')).join(Review).filter(Review.date_posted >= seven_days_ago).group_by(Item.id).order_by(func.count(Review.id).desc()).limit(3).all()
    trending_items = [item for item, count in trending_items_query]
    top_reviewers_query = db.session.query(User, func.count(Review.id).label('review_count')).join(Review).group_by(User.id).order_by(func.count(Review.id).desc()).limit(5).all()
    top_reviewers = top_reviewers_query
    recommendations = None
    recommended_for_category = None
    if current_user.is_authenticated:
        recommendations, recommended_for_category = get_recommendations(current_user)
    return render_template('index.html', top_items=top_items, trending_items=trending_items, recommendations=recommendations, recommended_for_category=recommended_for_category, top_reviewers=top_reviewers)

@main.route("/menu")
def menu():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q')
    category_filter = request.args.get('category')
    items_query = Item.query.order_by(Item.name.asc())
    if search_query:
        items_query = items_query.filter(Item.name.ilike(f'%{search_query}%'))
    if category_filter:
        items_query = items_query.filter(Item.category == category_filter)
    items = items_query.paginate(page=page, per_page=6)
    categories = db.session.query(Item.category).distinct().all()
    return render_template('menu.html', title='Menu', items=items, categories=[c[0] for c in categories], search_query=search_query, category_filter=category_filter)

@main.route("/item/<int:item_id>", methods=['GET', 'POST'])
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    form = ReviewForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('You must be logged in to submit a review.', 'warning')
            return redirect(url_for('main.login', next=request.path))
        image_filename = None
        if form.picture.data:
            image_filename = save_picture(form.picture.data)
        review_text = form.text.data
        sentiment_score = TextBlob(review_text).sentiment.polarity
        review = Review(rating=form.rating.data, text=review_text, author=current_user, item=item, image_file=image_filename, sentiment=sentiment_score)
        db.session.add(review)
        db.session.commit()
        flash('Your review has been submitted!', 'success')
        return redirect(url_for('main.item_detail', item_id=item.id))
    reviews = Review.query.filter_by(item_id=item.id).order_by(Review.date_posted.desc()).all()
    return render_template('item_detail.html', title=item.name, item=item, reviews=reviews, form=form)

# --- Favorite Routes ---
@main.route("/favorite/<int:item_id>", methods=['POST'])
@login_required
def favorite_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item not in current_user.favorited_items:
        current_user.favorited_items.append(item)
        db.session.commit()
        flash(f'"{item.name}" has been added to your favorites!', 'success')
    return redirect(url_for('main.item_detail', item_id=item.id))

@main.route("/unfavorite/<int:item_id>", methods=['POST'])
@login_required
def unfavorite_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item in current_user.favorited_items:
        current_user.favorited_items.remove(item)
        db.session.commit()
        flash(f'"{item.name}" has been removed from your favorites.', 'success')
    return redirect(url_for('main.item_detail', item_id=item.id))

@main.route("/favorites")
@login_required
def favorites():
    items = current_user.favorited_items
    return render_template('favorites.html', title='My Favorites', items=items)

# --- Profile Routes ---
@main.route("/profile")
@login_required
def profile():
    return redirect(url_for('main.user_profile', username=current_user.username))

@main.route("/profile/edit", methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, type='profile')
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.bio.data = current_user.bio
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@main.route("/user/<string:username>")
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    reviews = Review.query.filter_by(author=user).order_by(Review.date_posted.desc()).all()
    return render_template('user_profile.html', user=user, reviews=reviews, title=f"{user.username}'s Profile")

# --- Auth Routes ---
@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

# --- Admin Routes ---
@main.route("/add_item", methods=['GET', 'POST'])
@login_required
def add_item():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.home'))
    form = AddItemForm()
    if form.validate_on_submit():
        item = Item(name=form.name.data, category=form.category.data, description=form.description.data)
        db.session.add(item)
        db.session.commit()
        flash(f'Item "{item.name}" has been added!', 'success')
        return redirect(url_for('main.menu'))
    return render_template('add_item.html', title='Add New Item', form=form)

@main.route("/admin")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.home'))
    reviews = Review.query.order_by(Review.date_posted.desc()).all()
    return render_template('admin.html', title='Admin Dashboard', reviews=reviews)

@main.route("/admin/delete_review/<int:review_id>", methods=['POST'])
@login_required
def delete_review(review_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('main.home'))
    review_to_delete = Review.query.get_or_404(review_id)
    db.session.delete(review_to_delete)
    db.session.commit()
    flash('The review has been deleted.', 'success')
    return redirect(url_for('main.admin_dashboard'))
