Codename muse
====

## Overview ##
Muse is a cloud-based web application designed to help users get the most out of their music. Using The Echo Nest’s API, Muse gathers information about artists to present interesting statistics in a beautiful way.

Codename Muse works with The Echo Nest. See LICENSE.md for more licensing information.

## Location ##
Site: [http://muse.patricksanders.net/](http://muse.patricksanders.net/)

## Current Features ##
* Artist Information
	* Overview
		* Popularity
			* Combined metric of ‘hotttnesss’ and ‘familiarity’ presented graphically
		* Average Danceability
			* Based on danceability measure of the artist’s 15 most popular songs, presented graphically
		* Genres
			* A list of genres to which the artist’s music belongs, sorted by relevance
		* Similar
			* A list of links to pages for similar artists, sorted by similarity
	* Average song length
		* Average length of songs based on the artist’s 15 most popular songs
	* Blogs
		* Number of people blogging about the artist
		* List of five links to recent blog posts

## Future Features ##
* More artist information
	* Popular songs
		* “Listen Now” links for popular services (Spotify, Rdio, YouTube, etc.)
	* Metrics
		* Song length, tempo, energy, loudness, time signature, etc.
		* Other interesting information (based on community feedback)

## Technical Details ##
Platform: Google App Engine
Language: Python 2.7.x
External Dependencies:
	App Engine API
	The Echo Nest API (requires API key)
	Twitter Bootstrap front-end framework (accessed via CDN)
	jQuery 2.0.0 (accessed via CDN)

## Known Issues ##
* Exception handling - need to handle these exceptions gracefully
	* Artist not found causes HTTP 500
		* Suggest artists similar to search term
	* Echo Nest API call timeout causes HTTP 500
		* Retry API call, present friendly message if call still times out
* Special characters in artist name can give unexpected results
	* Need to properly escape special characters, or change the way queries are handled