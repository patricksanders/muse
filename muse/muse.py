import apis
import cgi
import jinja2
import webapp2
import os
import json
import random
from settings import *
from google.appengine.api import users, memcache
from apis.pyechonest import config as enconfig
from apis.pyechonest import *
from apis.rdio import Rdio

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

NUM_SONGS = 15

random.seed()
client = memcache.Client()
	
# Set EchoNest API credentials (values located in settings.py)
enconfig.ECHO_NEST_API_KEY = ECHONEST_API_KEY
enconfig.ECHO_NEST_CONSUMER_KEY = ECHONEST_CONSUMER_KEY
enconfig.ECHO_NEST_SHARED_SECRET = ECHONEST_SHARED_SECRET

# Initialize Rdio connection
rdio = Rdio((RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET))

class MainPage(webapp2.RequestHandler):
	def get(self):
		memcache.add(key='hot_list',
			value=artist.top_hottt(results=10), time=3600)
		hot_list = client.gets('hot_list')
		
		template_values = {
			'hot_list': hot_list,
			'tracking': TRACKING,
		}
		
		template = JINJA_ENVIRONMENT.get_template('templates/index.html')
		self.response.write(template.render(template_values))
		
class AboutPage(webapp2.RequestHandler):
	def get(self):
		template_values = {
			'tracking': TRACKING,
		}
		
		template = JINJA_ENVIRONMENT.get_template('templates/about.html')
		self.response.write(template.render(template_values))

class GetArtist(webapp2.RequestHandler):
	def get(self):
		query = self.request.get('name')
		section = self.request.get('section')
		
		""" Retrieve artist from Echo Nest
		Put artist object in memcache if it's not there already """
		memcache.add(key=query, value=artist.Artist(query), time=3600)
		en_artist = client.gets(query)
		if en_artist is None:
			en_artist = artist.Artist(query)
			memcache.add(key=query, value=en_artist, time=3600)
		
		""" Generate response
		
		Responses are based on request contents
		If no 'section' parameter is present, the generic artist page is
			generated and returned (using 'name' parameter)
		Subsequent AJAX calls are differentiated by the 'section' parameter
			being one of the following values:
				overview
				song_length
				blogs
			
		"""
		if not section:
			images = en_artist.get_images(results=15)
			image_url = images[random.randint(0,14)]['url']
			
			template_values = {
				'image_url': image_url,
				'artist_name': en_artist.name,
				'tracking': TRACKING,
			}
			
			template = JINJA_ENVIRONMENT.get_template('templates/artist.html')
			self.response.write(template.render(template_values))
		elif section == 'overview':
			data = self.getOverview(en_artist)
			self.response.headers['Content-Type'] = 'application/json'
			self.response.write(data)
		elif section == 'song_length':
			data = self.getSongLength(en_artist)
			self.response.headers['Content-Type'] = 'application/json'
			self.response.write(data)
		elif section == 'blogs':
			data = self.getBlogs(en_artist)
			self.response.headers['Content-Type'] = 'application/json'
			self.response.write(data)
		else:
			self.response.headers['Content-Type'] = 'text/plain'
			self.response.write('That section doesn\'t exist')
	
	""" Returns JSON with relevant blog entries """
	def getBlogs(self, en_artist):
		doc_counts = en_artist.get_doc_counts()
		blog_list = en_artist.get_blogs(results=5, high_relevance=True)
		blogs = []
		for blog in blog_list:
			blogs.append(
				{
					'name': blog['name'],
					'url': blog['url'],
				})
		
		data = {
			'blog_count': doc_counts['blogs'],
			'blog_list': blogs,
		}
		return data
	
	""" Returns JSON including general artist info """
	def getOverview(self, en_artist):
		hotttnesss = en_artist.hotttnesss * 50
		familiarity = en_artist.familiarity * 50
		similar_artists = en_artist.get_similar(results=7)
		terms = en_artist.get_terms()
		
		similar_list = []
		for item in similar_artists:
			similar_list.append(item.name)
		terms_list = []
		for item in terms:
			terms_list.append(item['name'])
		
		song_list = en_artist.get_songs(results=NUM_SONGS)
		
		""" Calculate average danceability """
		total_danceability = 0
		for song in song_list:
			total_danceability += song.get_audio_summary()['danceability']
		danceability = (total_danceability / NUM_SONGS) * 100
		data = {
			'hotttnesss': hotttnesss,
			'familiarity': familiarity,
			'danceability': danceability,
			'term_list': terms_list,
			'similar_list': similar_list,
		}
		return data
	
	""" Returns JSON including avg and total song length """
	def getSongLength(self, en_artist):
		song_list = en_artist.get_songs(results=NUM_SONGS)
		num_songs = len(song_list)
		
		""" Calculate total and average song length """
		total_song_length = 0
		for song in song_list:
			total_song_length += song.get_audio_summary()['duration']
		total_song_length = total_song_length / 60
		avg_song_length = total_song_length / num_songs
		
		data = {
			'total_songs': num_songs,
			'total_song_length': total_song_length,
			'avg_song_length': avg_song_length,
		}
		return data

app = webapp2.WSGIApplication([('/', MainPage),
								('/about', AboutPage),
								('/artist', GetArtist)],
								debug=True)