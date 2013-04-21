import cgi, jinja2, webapp2, os, json
from settings import *
from google.appengine.api import users
import apis
from apis.pyechonest import config as enconfig
from apis.pyechonest import *
from apis.rdio import Rdio

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
	
# Set EchoNest API credentials (values located in settings.py)
enconfig.ECHO_NEST_API_KEY = ECHONEST_API_KEY
enconfig.ECHO_NEST_CONSUMER_KEY = ECHONEST_CONSUMER_KEY
enconfig.ECHO_NEST_SHARED_SECRET = ECHONEST_SHARED_SECRET

# Initialize Rdio connection
rdio = Rdio((RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET))

class MainPage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		
		if user:
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'
		
		template_values = {
			'url': url,
			'url_linktext': url_linktext,
		}
		
		template = JINJA_ENVIRONMENT.get_template('templates/main.html')
		self.response.write(template.render(template_values))
		
class AboutPage(webapp2.RequestHandler):
	def get(self):
		# user = users.get_current_user()
		# 
		# if user:
		# 	url = users.create_logout_url(self.request.uri)
		# 	url_linktext = 'Logout'
		# else:
		# 	url = users.create_login_url(self.request.uri)
		# 	url_linktext = 'Login'
		# 
		# template_values = {
		# 	'url': url,
		# 	'url_linktext': url_linktext,
		# }

		template = JINJA_ENVIRONMENT.get_template('templates/about.html')
		self.response.write(template.render())

class GetArtist(webapp2.RequestHandler):
	# def post(self):
	# 	query = self.request.get('artist')
	# 	
	# 	# Find artist on Rdio
	# 	rdio = Rdio((RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET))
	# 	searchResults = rdio.call('search', {'query': query,
	# 									'types': 'Artist'
	# 									})
	# 	firstResult = searchResults['result']['results'][0]['key']
	# 	
	# 	# Find artist on EchoNest
	# 	en_artist = artist.Artist(query)
	# 	rdioalbums = rdio.call('getAlbumsForArtist', {'artist': firstResult})
	# 	
	# 	# Print results for EchoNest then Rdio
	# 	self.response.headers['Content-Type'] = 'text/plain'
	# 	self.response.write('First EchoNest result: ' + repr(en_artist) + '\n')
	# 	self.response.write('First Rdio search result key: ' + firstResult + '\n')
	# 	self.response.write('Albums for artist:\n')
	# 	self.response.write(json.dumps(rdioalbums, ensure_ascii=True, indent=2))
	
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
		images = en_artist.get_images(results=1)
		image_url = images[0]['url']
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
		
		# Print results for EchoNest then Rdio
		# self.response.headers['Content-Type'] = 'text/plain'
		# self.response.write('First EchoNest result: ' + repr(en_artist) + '\n')
		# self.response.write('First Rdio search result key: ' + firstResult + '\n')
		# self.response.write('Albums for artist:\n')
		# self.response.write(json.dumps(rdioalbums, ensure_ascii=True, indent=2))

app = webapp2.WSGIApplication([('/', MainPage),
								('/about', AboutPage),
								('/artist', GetArtist)],
								debug=True)