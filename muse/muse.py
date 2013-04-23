import cgi, jinja2, webapp2, os, json, random
from settings import *
from google.appengine.api import users, memcache
import apis
from apis.pyechonest import config as enconfig
from apis.pyechonest import *
from apis.rdio import Rdio

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

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
		memcache.add(key='hot_list', value=artist.top_hottt(results=10), time=3600)
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
		
		# Put artist object from Echo Nest in memcache if it's not there already
		memcache.add(key=query, value=artist.Artist(query), time=3600)
		en_artist = client.gets(query)
		if en_artist is None:
			en_artist = artist.Artist(query)
			memcache.add(key=query, value=en_artist, time=3600)
			
		song_list = None
		
		if not section:
			# Find artist on EchoNest
			images = en_artist.get_images(results=15)
			image_url = images[random.randint(0,14)]['url']
			
			template_values = {
				'image_url': image_url,
				'artist_name': en_artist.name,
				'tracking': TRACKING,
			}
			
			template = JINJA_ENVIRONMENT.get_template('templates/artist.html')
			self.response.write(template.render(template_values))
		
		elif section is 'overview':
			self.response.headers['Content-Type'] = 'application/json'
			
			hotttnesss = en_artist.hotttnesss * 50
			familiarity = en_artist.familiarity * 50
			similar_list = artist.similar(ids=en_artist.id, results=7)
			if song_list is None:
				song_list = en_artist.get_songs(results=15)
			
			# Calculate average danceability
			total_danceability = 0
			for song in song_list:
				total_danceability += song.get_audio_summary()['danceability']
			danceability = (total_danceability / num_songs) * 100
			response = {
				'hotttnesss': hotttnesss,
				'familiarity': familiarity,
				'danceability': danceability,
				'term_list': en_artist.terms,
				'similar_list': similar_list,
			}
			
			self.response.write(json.dumps(response))

		
		elif section is 'song_length':
			if song_list is None:
				song_list = en_artist.get_songs(results=15)
			num_songs = len(song_list)
			
			# Calculate total and average song length
			total_song_length = 0
			for song in song_list:
				total_song_length += song.get_audio_summary()['duration']
			total_song_length = total_song_length / 60
			avg_song_length = total_song_length / num_songs
			
			response = {
				'total_songs': num_songs,
				'total_song_length': total_song_length,
				'avg_song_length': avg_song_length,
			}
			
			self.response.headers['Content-Type'] = 'application/json'
			self.response.write(response)
		
		elif section is 'blogs':
			doc_counts = en_artist.get_doc_counts()
			blog_list = en_artist.get_blogs(results=5, high_relevance=True)
			
			response = {
				'blog_count': doc_counts['blogs'],
				'blog_list': blog_list,
			}
			
			self.response.headers['Content-Type'] = 'application/json'
			self.response.write(response)
			
		else:
			self.response.headers['Content-Type'] = 'text/plain'
			self.response.write('uh oh')

app = webapp2.WSGIApplication([('/', MainPage),
								('/about', AboutPage),
								('/artist', GetArtist)],
								debug=True)