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
		# rdioalbums = rdio.call('getAlbumsForArtist', {'artist': firstResult})
		images = en_artist.get_images(results=15)
		image_url = images[random.randint(0,14)]['url']
		artist_name = en_artist.name
		hotttnesss = en_artist.hotttnesss * 50
		familiarity = en_artist.familiarity * 50
		
		template_values = {
			'image_url': image_url,
			'artist_name': artist_name,
			'hotttnesss': hotttnesss,
			'familiarity': familiarity,
		}
		
		template = JINJA_ENVIRONMENT.get_template('templates/artist.html')
		self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainPage),
								('/about', AboutPage),
								('/artist', GetArtist)],
								debug=True)