import cgi, jinja2, webapp2, os, json, random
from settings import *
from google.appengine.api import users
import apis
from apis.pyechonest import config as enconfig
from apis.pyechonest import *
from apis.rdio import Rdio

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

random.seed()
	
# Set EchoNest API credentials (values located in settings.py)
enconfig.ECHO_NEST_API_KEY = ECHONEST_API_KEY
enconfig.ECHO_NEST_CONSUMER_KEY = ECHONEST_CONSUMER_KEY
enconfig.ECHO_NEST_SHARED_SECRET = ECHONEST_SHARED_SECRET

# Initialize Rdio connection
rdio = Rdio((RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET))

class MainPage(webapp2.RequestHandler):
	def get(self):
		hot_list = artist.top_hottt(results=10)
		
		template_values = {
			'hot_list': hot_list,
			'analytics': ANALYTICS_CODE,
		}
		
		template = JINJA_ENVIRONMENT.get_template('templates/index.html')
		self.response.write(template.render(template_values))
		
class AboutPage(webapp2.RequestHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('templates/about.html')
		self.response.write(template.render())

class GetArtist(webapp2.RequestHandler):
	def get(self):
		query = self.request.get('artist')
		
		# Find artist on Rdio
		# searchResults = rdio.call('search', {'query': query,
		# 								'types': 'Artist'
		# 								})
		# firstResult = searchResults['result']['results'][0]['key']
		
		# Find artist on EchoNest
		en_artist = artist.Artist(query)
		images = en_artist.get_images(results=15)
		image_url = images[random.randint(0,14)]['url']
		hotttnesss = en_artist.hotttnesss * 50
		familiarity = en_artist.familiarity * 50
		similar_list = artist.similar(ids=en_artist.id, results=7)
		song_list = en_artist.get_songs(results=25)
		doc_counts = en_artist.get_doc_counts()
		num_songs = len(song_list)
		blog_list = en_artist.get_blogs(results=5, high_relevance=True)
		
		# Calculate average danceability
		total_danceability = 0
		for song in song_list:
			total_danceability += song.get_audio_summary()['danceability']
		danceability = (total_danceability / num_songs) * 100
		
		# Calculate total and average song length
		total_song_length = 0
		for song in song_list:
			total_song_length += song.get_audio_summary()['duration']
		total_song_length = total_song_length / 60
		avg_song_length = total_song_length / num_songs
		
		
		template_values = {
			'image_url': image_url,
			'artist_name': en_artist.name,
			'hotttnesss': hotttnesss,
			'familiarity': familiarity,
			'danceability': danceability,
			'term_list': en_artist.terms,
			'similar_list': similar_list,
			'total_songs': num_songs,
			'total_song_length': total_song_length,
			'avg_song_length': avg_song_length,
			'blog_count': doc_counts['blogs'],
			'blog_list': blog_list,
			'analytics': ANALYTICS_CODE,
		}
		
		template = JINJA_ENVIRONMENT.get_template('templates/artist.html')
		self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainPage),
								('/about', AboutPage),
								('/artist', GetArtist)],
								debug=True)