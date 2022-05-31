"""
Venue, Artis and Show models
"""
# Imports

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Models.
class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(300))
    genres = db.Column(db.String(), nullable=False)
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(200))
    seeking_talent=db.Column(db.Boolean,nullable=False, default=False)
    seeking_description=db.Column(db.String(120))
    show=db.relationship('Show', backref='venue', lazy=True, cascade= 'all, save-update, merge,delete, delete-orphan')

    def __repr__(self):
        return f"<Venue id={self.id} name={self.name} city={self.city} state={self.state}>"


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.String(120), nullable=False)
    facebook_link = db.Column(db.String(300))
    website_link =db.Column(db.String(300))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String())
    show= db.relationship('Show', backref='artist', lazy=True, cascade= 'all, save-update, merge,delete, delete-orphan')

    def __repr__(self):
        return f"<Artist id={self.id} name={self.name} city={self.city} state={self.state}>"

class Show(db.Model):
  __tablename__ = 'show'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)

  def __repr__(self):
        return f"<Show id={self.id} artist_id={self.artist_id} venue_id={self.venue_id} start_time={self.start_time}"
