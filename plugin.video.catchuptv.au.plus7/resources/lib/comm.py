import urllib2
import config
import classes
import utils
import re
import datetime
import time

from BeautifulSoup import BeautifulStoneSoup
import simplejson as json

try:
	import xbmc, xbmcgui, xbmcplugin
except ImportError:
	pass # for PC debugging

cache = False

def fetch_url(url):
	"""	Simple function that fetches a URL using urllib2.
		An exception is raised if an error (e.g. 404) occurs.
	"""
	utils.log("Fetching URL: %s" % url)
	http = urllib2.urlopen(urllib2.Request(url, None))
	return http.read()


def get_index():
	"""	This function pulls in the index, which contains the TV series
	"""
	series_list = []
	data = fetch_url(config.index_url)
	data = data.replace('\n','')
	token = re.findall(r"<!-- Body Content  -->(.*)<!-- //Body Content -->", data)[0]
	token2 = re.findall(r'<div class="bd" id="atoz">(.*)</div>', token)[0]

	urls = re.findall(r'<a href="(.*?)"', token2)
	titles = re.findall(r'alt="(.*?)"', token2)
	imgs = re.findall(r'src="(.*?)\?', token2)

	for i in xrange(len(urls)):
		series = classes.Series()
		series.title = titles[i]
		series.thumbnail = imgs[i]
		series.url = urls[i]
		series_list.append(series)

	return series_list

def get_series(series_id):
	""" 
        <li class="clearfix">
          <a href="/plus7/felix-the-cat/-/watch/12698938/getting-rid-of-sniffer-series-1-episode-9/?play=1" class="vidimg">
              <img class="listimg" src="http://l.yimg.com/ea/img/-/120123/kids_felix_s1ep9_lrg_17hqg69-17hqg6o.jpg?x=118&y=66&xc=1&yc=2&wc=629&hc=352&sig=9aw7XqRoa4GRA2aCvHR2GQ--" alt="Felix The Cat" />
              <span class="vidimg-play">
                  <span class="txt">Play Video</span>
                  <span class="matte"></span>
              </span>
          </a>
          <div class="itemdetails">
            <h3><a href="/plus7/felix-the-cat/-/watch/12698938/getting-rid-of-sniffer-series-1-episode-9/">
              <span class="title">Felix The Cat</span>
              <span class="subtitle"> Getting Rid of Sniffer, series 1 episode 9</span>
            </a></h3>
            <p>Rock Bottom and the Professor need $10,000 for a vacation, which Felix won't lend them.</p>
          </div>
                              <a class="myshows-link" rel="autv-plus7-felix-the-cat"></a>        </li>



<span class="subtitle"> Thu 22 Mar, series 6 episode 7</span>

	"""




	program_list = []
	url = config.series_url % series_id

	data = fetch_url(url)	
	data = data.replace('\n','')

	#title = re.findall(r'<h2>(.*?)</h2>', data)[0]
	programs_data = re.findall(r'<ul id="related-episodes" class="featlist">(.*?)</ul>', data)[0]

	# ['John Safran's Race Relations', 'John Safran's Race Relations']
	titles = re.findall(r'<span class="title">(.*?)</span>', programs_data)

	# ['Episode desc', 'Episode desc']
	descs = re.findall(r'<p>(.*?)</p>', programs_data)

	# [' Wed 14 July, series 4 episode 2', ' Wed 14 July, series 4 episode 1']
	subtitles = re.findall(r'<span class="subtitle">(.*?)</span>', programs_data)

	# ['http://l.yimg.com/ea/img/-/100714/0714_city_homicide_ep56v2_sml-163qgka.jpg', 'http://l.yimg.com/ea/img/-/100714/0714_city_homicide_ep55v2_sml-163qgjl.jpg']	
	thumbs = re.findall(r'<img class="listimg" src="(.*?)\?', programs_data)

	# ['/plus7/city-homicide/-/watch/7583800/wed-14-july-series-4-episode-2/', '/plus7/city-homicide/-/watch/7583794/wed-14-july-series-4-episode-1/']
	urls = re.findall(r'<h3><a href="(.*?)">', programs_data)

	num_episodes = len(urls)

	for i in xrange(num_episodes):
		program = classes.Program()
		program.title = titles[i]
		program.description = descs[i]
		program.thumbnail = thumbs[i]
		program.url_path = urls[i]

		# season 4 episode 2
		program.episode_title = subtitles[i].split(',')[-1].lstrip(" ").rstrip(" ")

		date_string = subtitles[i].split(',')[0].lstrip(" ").rstrip(" ")
		try:
			date = "%s %s" % (date_string, program.get_year())
			timestamp = time.mktime(time.strptime(date, '%a %d %b %Y'))
			program.date = datetime.date.fromtimestamp(timestamp)
		except:
			utils.log("Didn't find a valid date from : %s" % date_string)

		program_list.append(program)

	return program_list


def get_program(path):

	# This stuff needs to go into parser
	index = fetch_url("http://au.tv.yahoo.com%s" % path) 

	program = classes.Program()

	program.id = re.findall("vid : '(.*?)'", index)[0]
	program.title = re.findall("<h1>(.*?)</h1>", index)[0]

	try:
		program.category = re.findall("Genre: <strong>(.*?)</strong>", index)[0]
	except:
		utils.log_error("Unable to parse program category")

	try:
		# Classified is now seperated by a newline
		program.rating = re.findall("Classified:.*?<strong>(.*?)</strong>", index, re.DOTALL)[0]
	except:
		utils.log_error("Unable to parse program classification")

	# Get the URL, but split it from the '?', to get the high-res image
	try:
		program.thumbnail = re.findall('<img class="listimg" src="(.*?)" alt', index)[0].split("?")[0]
	except:
		print "Unable to find thumbnail"

	# Get metadata
	url = "http://cosmos.bcst.yahoo.com/rest/v2/pops;id=%s;lmsoverride=1" % program.id
	index = fetch_url(url)

	try:
		program.episode_title = re.findall("<title><!\[CDATA\[(.*?)\]\]></title>", index)[0].split(": ")[1]
	except:
		utils.log_error("Unable to parse episode title")

	try:
		program.description = re.findall("<description><!\[CDATA\[(.*?)\]\]></description>", index)[0]
	except: 
		utils.log_error("Unable to parse episode description")

	try:
		program.thumbnail = re.findall('<media:content medium="image" url="(.*?)" name=', index)[0]
	except:
		utils.log_error("Unable to parse program thumbnail")

	# Parsing the date is a nightmare
	date_string = re.findall("<media:pubStart><!\[CDATA\[(.*?)\]\]></media:pubStart>", index)[0]
	date_parts = date_string.split()
	
	try:
		date_without_tz = " ".join(date_parts[:-1])
		timestamp = time.mktime(time.strptime(date_without_tz, '%m/%d/%Y %I:%M:%S %p')) # 05/18/2011 04:30:00 AM
		program.date = datetime.date.fromtimestamp(timestamp)
	except:
		date_without_tz = " ".join(date_parts[:-2])
		timestamp = time.mktime(time.strptime(date_without_tz, '%m/%d/%Y %I:%M:%S')) # 05/18/2011 04:30:00 AM
		program.date = datetime.date.fromtimestamp(timestamp)

	return program


def get_program_id(path):
	index = fetch_url("http://au.tv.yahoo.com%s" % path) 
	return re.findall("vid : '(.*?)'", index)[0]


def get_stream(program_id):

	# Get stream
	url = "http://cosmos.bcst.yahoo.com/rest/v2/pops;id=%s;lmsoverride=1;element=stream;bw=1200" % program_id
	index = fetch_url(url)

	result = {}
	
	try:
		result['rtmp_host'] = re.findall('url="(.*?)"', index)[0]
		result['rtmp_path'] = re.findall('path="(.*?)"', index)[0]
	except:
		# No RTMP given - probably not in AUS
		utils.log_error("Unable to find video URL. Is it usually because you're not in Australia.")
		
	try:
		result['error'] = re.findall("<media:error.*?<!\[CDATA\[(.*?)\]\]></media:error>", index)[0]
	except:
		pass

	return result
