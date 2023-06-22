from init import db, ma 
from marshmallow import fields

# REVIEW MODEL 
class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    rating = db.Column(db.Integer, nullable=False)
    body = db.Column(db.Text())
    date_created = db.Column(db.Date())

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)

    user = db.relationship('User', back_populates='reviews')

class ReviewSchema(ma.Schema):
    user = fields.Nested('UserSchema', exclude=['password', 'reviews'])

    class Meta:
        fields = ('id', 'title', 'rating', 'body', 'date_created', 'user', 'game_id')