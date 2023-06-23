from init import db
from flask import Blueprint, request, jsonify
from models.review import Review, ReviewSchema
from models.game import Game, GameSchema
from models.user import User, UserSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from datetime import date
from blueprints.auth_bp import admin_or_owner_required

reviews_bp = Blueprint('reviews', __name__, url_prefix='/reviews')

# Get all reviews of all games - no login required
@reviews_bp.route('/')
def all_reviews():
    stmt = db.select(Review).order_by(Review.id)
    games = db.session.scalars(stmt).all()
    return ReviewSchema(many=True).dump(games)

# Get a specific review 
@reviews_bp.route('/<int:review_id>')
def one_review(review_id):
    stmt = db.select(Review).filter_by(id=review_id)
    review = db.session.scalar(stmt)
    if review: 
        return ReviewSchema().dump(review)
    else:
        return {'error':'Review not found'}, 404

# #Get all reviews for a specific game - no login required
@reviews_bp.route('/game/<int:game_id>')
def get_reviews_by_game(game_id):
    game = Game.query.get(game_id)
    if game:
        reviews = Review.query.filter_by(game_id=game_id).all()
        if reviews:
            review_schema = ReviewSchema(many=True)
            return review_schema.dump(reviews)
        else:
            return {'error': 'No reviews found for the specified game ID.'}, 404
    else:
        return {'error': 'Game not found.'}, 404
    
# Get all reviews from a specific user 
@reviews_bp.route('/user/<int:user_id>')
def get_reviews_by_user(user_id):
    user = User.query.get(user_id)
    if user: 
        reviews = Review.query.filter_by(user_id=user_id).all()
        if reviews:
            review_schema = ReviewSchema(many=True)
            return review_schema.dump(reviews)
        else:
            return {'error': 'No reviews found for the specified user ID.'}, 404
    else:
        return {'error': 'User not found.'}, 404



# Add a review - must be logged in to do this 
@reviews_bp.route('/', methods=['POST'])
@jwt_required()
def add_review():
    try:
        review_info = ReviewSchema().load(request.json)
        review = Review(
            title=review_info['title'],
            rating=review_info['rating'],
            body=review_info['body'],
            date_created=date.today(),
            user_id = get_jwt_identity(),
            game_id = review_info['game_id']
        )
        db.session.add(review)
        db.session.commit()
        return ReviewSchema().dump(review), 201
    except IntegrityError:
        return {'error': 'Review already exists'}, 409
    except KeyError:
        return {'error':'please provide all details of the review'}, 400
    
# Update a review - only the review owner or an admin can do this 
@reviews_bp.route('/<int:review_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_review(review_id):
    stmt = db.select(Review).filter_by(id=review_id)
    review = db.session.scalar(stmt)
    review_info = ReviewSchema().load(request.json)
    if review:
        admin_or_owner_required(review.user_id)
        review.title = review_info.get('title', review.title),
        review.rating = review_info.get('rating', review.rating),
        review.body = review_info.get('body', review.body),
        db.session.commit()
        return ReviewSchema().dump(review)
    else: 
        return {'error': 'Review not found'}, 404
    
# Delete a review - only the review owner or an admin can do this 
@reviews_bp.route('/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    stmt = db.select(Review).filter_by(id=review_id)
    review = db.session.scalar(stmt)
    if review:
        admin_or_owner_required(review.user_id)
        db.session.delete(review)
        db.session.commit()
        return {'message':'Review deleted'}, 200
    else: 
        return {'error': 'Review not found'}, 404