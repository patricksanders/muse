import jinja2
import os
import json
import random
from settings import *
from flask import Flask
# TODO: new implementation on caching
from google.appengine.api import memcache
from apis.pyechonest import config as enconfig
from apis.pyechonest import *
from apis.rdio import Rdio

app = Flask('__name__')
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

@app.route('/')
def main_mage(self):
	memcache.add(key='hot_list',
		value=artist.top_hottt(results=10), time=3600)
	hot_list = client.gets('hot_list')
	
	template_values = {
		'hot_list': hot_list,
		'tracking': TRACKING,
	}
	
	template = JINJA_ENVIRONMENT.get_template('templates/index.html')
	self.response.write(template.render(template_values))
		
@app.route('/about')
def about_page(self):
	template_values = {
		'tracking': TRACKING,
	}
	
	template = JINJA_ENVIRONMENT.get_template('templates/about.html')
	self.response.write(template.render(template_values))

@app.route('/artist/<artist_name>')
def get_artist(artist_name):
	query = self.request.get('name')
	section = self.request.get('section')
	
	""" Retrieve artist from Echo Nest
	Put artist object and song list in memcache if they're
	not there already 
	"""
	memcache.add(key=query, value=artist.Artist(query), time=3600)
	en_artist = client.gets(query)
	song_list_key = 'song_list-' + en_artist.name
	memcache.add(key=song_list_key,
				value=en_artist.get_songs(results=NUM_SONGS), time=3600)
	song_list = client.gets(song_list_key)
	
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
	elif section == 'stats':
		data = self.getStats(en_artist, song_list)
		json.dump(data, self.response)
	elif section == 'overview':
		data = self.getOverview(en_artist)
		self.response.headers['Content-Type'] = 'application/json'
		json.dump(data, self.response)
	elif section == 'song_length':
		data = self.getSongLength(en_artist, song_list)
		self.response.headers['Content-Type'] = 'application/json'
		json.dump(data, self.response)
	elif section == 'blogs':
		data = self.getBlogs(en_artist, song_list)
		self.response.headers['Content-Type'] = 'application/json'
		json.dump(data, self.response)
	else:
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.write('That section doesn\'t exist')
	
""" Returns dict with relevant blog entries """
def getBlogs(self, en_artist, song_list):
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

""" Returns dict including general artist info """
def getOverview(self, en_artist):
	similar_artists = en_artist.get_similar(results=7)
	terms = en_artist.get_terms()
	
	similar_list = []
	for item in similar_artists:
		similar_list.append(item.name)
	terms_list = []
	for item in terms:
		terms_list.append(item['name'])
	
	data = {
		'term_list': terms_list,
		'similar_list': similar_list,
	}
	return data

""" Returns dict including avg and total song length """
def getSongLength(self, en_artist, song_list):
	""" Calculate total and average song length """
	total_song_length = 0
	for song in song_list:
		total_song_length += song.get_audio_summary()['duration']
	total_song_length = total_song_length / 60
	avg_song_length = total_song_length / NUM_SONGS
	
	data = {
		'total_songs': NUM_SONGS,
		'total_song_length': total_song_length,
		'avg_song_length': avg_song_length,
	}
	return data

def getStats(self, en_artist, song_list):
	hotttnesss = en_artist.hotttnesss * 50
	familiarity = en_artist.familiarity * 50
	
	""" Calculate average danceability """
	total_danceability = 0
	for song in song_list:
		total_danceability += song.get_audio_summary()['danceability']
	danceability = (total_danceability / NUM_SONGS) * 100
	data = {
		'hotttnesss': hotttnesss,
		'familiarity': familiarity,
		'danceability': danceability,
	}
	return data

if __name__ == '__main__':
	app.run(debug=DEBUG)