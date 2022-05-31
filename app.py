#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from babel.dates import format_date, format_datetime, format_time
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate= Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

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

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []
    results = Venue.query.distinct(Venue.city, Venue.state).all()
    for result in results:
        city_state_data = {
            "city": result.city,
            "state": result.state
        }
        venues = Venue.query.filter_by(city=result.city, state=result.state).all()
        view_venues = []
        for venue in venues:
            view_venues.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), venue.show)))
            })
        
        city_state_data["venues"] = view_venues
        data.append(city_state_data)
   
    return render_template('pages/venues.html', areas=data)
  
#  Search Venues
#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get("search_term", "")
  data = {}
  venues = list(Venue.query.filter(
        Venue.name.ilike(f"%{search_term}%") |
        Venue.state.ilike(f"%{search_term}%") |
        Venue.city.ilike(f"%{search_term}%") 
    ).all())
  data["count"] = len(venues)
  data["data"] = []
  retrieve = {}

  for venue in venues:
        retrieve = {
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), venue.show)))
        }
  data["data"].append(retrieve)
  return render_template('pages/search_venues.html', results=data, search_term=search_term)
  

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  setattr(venue, "genres", venue.genres.split(",")) 

  past_shows = list(filter(lambda show: show.start_time < datetime.now(), venue.show))
  portray_shows = []
  for show in past_shows:
        portray = {}
        portray["artist_name"] = show.artist.name
        portray["artist_id"] = show.artist.id
        portray["artist_image_link"] = show.artist.image_link
        portray["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        portray_shows.append(portray)

  setattr(venue, "past_shows", portray_shows)
  setattr(venue,"past_shows_count", len(past_shows))

  upcoming_shows = list(filter(lambda show: show.start_time > datetime.now(), venue.show))
  portray_shows = []
  for show in upcoming_shows:
        portray = {}
        portray["artist_name"] = show.artist.name
        portray["artist_id"] = show.artist.id
        portray["artist_image_link"] = show.artist.image_link
        portray["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        portray_shows.append(portray)

  setattr(venue, "upcoming_shows", portray_shows)    
  setattr(venue,"upcoming_shows_count", len(upcoming_shows))

  return render_template('pages/show_venue.html', venue=venue)
  

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  if form.validate():
    try:

            new_venue = Venue(
            name = form.name.data,
            city = form.city.data,
            state = form.state.data,
            address=form.address.data,
            phone = form.phone.data,
            image_link = form.image_link.data,
            genres = ',' .join(form.genres.data),
            facebook_link = form.facebook_link.data,
            website_link= form.website_link.data,
            seeking_talent = form.seeking_talent.data,
            seeking_description=form.seeking_description.data
            )
            db.session.add(new_venue)
            db.session.commit()
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
          db.session.rollback()
          flash('An error occurred. Venue' + ' could not be listed.')
    finally:
          db.session.close()
    return render_template('pages/home.html')

#  Delete Venue
#  ----------------------------------------------------------------
@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash("Venue " + venue.name+ " ,with id " +venue_id+  " was deleted successfully!")
  except:
    db.session.rollback()
    flash('Error, Venue belongs to a show or venue does not exist')
  finally:
    db.session.close()
  return redirect(url_for('index'))

#  Update Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form= VenueForm(request.form)
  if form.validate():
    try:
      venue = Venue.query.get(venue_id)
      venue.name=form.name.data
      venue.city=form.city.data
      venue.state=form.state.data
      venue.address=form.address.data
      venue.phone=form.phone.data
      venue.image_link=form.image_link.data
      venue.genres= ','.join(form.genres.data)
      venue.facebook_link=form.facebook_link.data
      venue.website_link=form.website_link.data
      venue.seeking_talent=form.seeking_talent.data
      venue.seeking_description=form.seeking_description.data
      db.session.add(venue)
      db.session.commit()
      flash("Venue " + venue.name + " was successfully edited!")
    except:
      db.session.rollback()
      flash('Venue was not edited successfully!')
    finally:
      db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#                        Artists
#  ----------------------------------------------------------------
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form= ArtistForm(request.form)
  if form.validate():
    try:
      new_artist = Artist(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        image_link = form.image_link.data,
        genres = ','.join(form.genres.data),
        facebook_link = form.facebook_link.data,
        website_link = form.website_link.data,
        seeking_venue = form.seeking_venue.data,
        seeking_description = form.seeking_description.data
      )
      db.session.add(new_artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occurred. Artist ' + new_artist.name + ' could not be listed.')
    finally:
      db.session.close()
  return render_template('pages/home.html')

#  Artist Page
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
  data = db.session.query(Artist.id, Artist.name). all()
  return render_template('pages/artists.html', artists=data)


#  Search Artist
#  ----------------------------------------------------------------

@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    artists = Artist.query.filter(
        Artist.name.ilike(f"%{search_term}%") |
        Artist.city.ilike(f"%{search_term}%") |
        Artist.state.ilike(f"%{search_term}%")
    ).all()
    response = {
        "count": len(artists),
        "data": []
    }

    for artist in artists:
        portray = {}
        portray["name"] = artist.name
        portray["id"] = artist.id

        upcoming_shows = 0
        for show in artist.show:
            if show.start_time > datetime.now():
                upcoming_shows = upcoming_shows + 1
        portray["upcoming_shows"] = upcoming_shows

        response["data"].append(portray)

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
 

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  setattr(artist, "genres", artist.genres.split(","))

#Retrieve Past Shows
  past_shows = list(filter(lambda show: show.start_time < datetime.now(), artist.show))
  portray_shows = []
  for show in past_shows:
        portray = {}
        portray["venue_name"] = show.venue.name
        portray["venue_id"] = show.venue.id
        portray["venue_image_link"] = show.venue.image_link
        portray["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

        portray_shows.append(portray)
  setattr(artist, "past_shows", portray_shows)
  setattr(artist, "past_shows_count", len(past_shows))

#The upcoming Shows

  upcoming_shows = list(filter(lambda show: show.start_time > datetime.now(), artist.show))
  portray_shows = []
  for show in upcoming_shows:
        portray = {}
        portray["venue_name"] = show.venue.name
        portray["venue_id"] = show.venue.id
        portray["venue_image_link"] = show.venue.image_link
        portray["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

        portray_shows.append(portray)

  setattr(artist, "upcoming_shows", portray_shows)
  setattr(artist, "upcoming_shows_count", len(upcoming_shows))
  return render_template('pages/show_artist.html', artist=artist)

#  Update Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  if form.validate():
        try:
            artist = Artist.query.get(artist_id)
            artist.name = form.name.data
            artist.city= form.city.data
            artist.state= form.state.data
            artist.phone= form.phone.data
            artist.image_link= form.image_link.data
            artist.genres= ",".join(form.genres.data)
            artist.facebook_link= form.facebook_link.data
            artist.website_link = form.website_link.data
            artist.seeking_venue= form.seeking_venue.data
            artist.seeking_description= form.seeking_description.data
            db.session.add(artist)
            db.session.commit()
            flash("Artist " + artist.name + " was successfully edited!")
        except:
            db.session.rollback()
            flash("Artist was not edited successfully.")
        finally:
            db.session.close() 
        return redirect(url_for('show_artist', artist_id=artist_id))

#  Delete Artist
#  ----------------------------------------------------------------
@app.route('/artists/<artist_id>/delete', methods=['GET'])
def delete_artist(artist_id):
  try:
    artist = Artist.query.get(artist_id)
    db.session.delete(artist)
    db.session.commit()
    flash("Artist " + artist.name+ " ,with id " +artist_id+  " was deleted successfully!")
  except:
    db.session.rollback()
    flash('Error, Artist has  a show or artist does not exist')
  finally:
    db.session.close()
  return redirect(url_for('index'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  shows = Show.query.all()
  for show in shows:
        portray = {}
        portray["venue_id"] = show.venue.id
        portray["venue_name"] = show.venue.name
        portray["artist_id"] = show.artist.id
        portray["artist_name"] = show.artist.name
        portray["artist_image_link"] = show.artist.image_link
        portray["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        
        data.append(portray)

  return render_template('pages/shows.html', shows=data)

#  Create Shows
#  ----------------------------------------------------------------
@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  if form.validate():
    try:
      new_show = Show(
        artist_id = form.artist_id.data,
        venue_id = form.venue_id.data,
        start_time = form.start_time.data
        )
      db.session.add(new_show)
      db.session.commit()
      flash('Show was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
    finally:
      db.session.close()
  return redirect (url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
