# coding=utf8
# importing packages
import urllib # get webpage
import robotexclusionrulesparser as rerp #get permission for webpages to crawl
from bs4 import BeautifulSoup # parse webpages
from urlparse import urlparse, urljoin # to get website information
import unicodedata
import MySQLdb #importing mysqldb

#helper functions

def crawl_web(seed, max_pages, max_depth): # returns index, graph of inlinks
	if is_tripadvisor(seed): #validation
		tocrawl = [[seed, 0]] # adding to valid list
	else: 
		print "This seed is not a tripadvisor site!"
		return
	crawled = []
	graph = {}  # <url>, [list of pages it links to]
	index = {} 
	# main logic
	while tocrawl: 
		page, depth = tocrawl.pop()
		print "CURRENT DEPTH: ", depth
		print "PAGES CRAWLED: ", len(crawled)
		# validation to avoid same web page crawl and to avoid infinite crawling
		if page not in crawled and len(crawled) < max_pages and depth <= max_depth:
			soup, url = get_page(page)
			add_page_to_index(index, page, soup)
			outlinks = get_all_links(soup, url)
			graph[page] = outlinks
			add_new_links(tocrawl, outlinks, depth)
			#print tocrawl
			crawled.append(page)
			#print crawled
	return index, graph

# return all crawlable links
def get_all_links(page, url):
	links = []
	page_url = urlparse(url)
	print "PAGE URL: " , page_url
	if page_url[0]:
		base = page_url[0] + '://' + page_url[1]
		print "BASE URL: " , base
		robots_url = urljoin(base, '/robots.txt')
		print "ROBOTS URL: " , robots_url
	else:
		robots_url = "http://www.tripadvisor.in/robots.txt"
	rp = rerp.RobotFileParserLookalike()
	rp.set_url(robots_url)
	rp.read()
	#print rp
	for link in page.find_all('a'):
		link_url = link.get('href') # get link information
		print "Found a link: ", link_url
		#Ignore links that are 'None'.
		if link_url == None: 
			pass
		elif not rp.can_fetch('*', link_url):
			print "Page off limits!" 
			pass		
		#Ignore links that are internal page anchors. 
		#Urlparse considers internal anchors 'fragment identifiers', at index 5. 
		elif urlparse(link_url)[5] and not urlparse(link_url)[2]: 
			pass
		elif urlparse(link_url)[1]:
			links.append(link_url)
		else:
			newlink = urljoin(base, link_url)
			links.append(newlink)
	return links

# add links if its not been crawled
def add_new_links(tocrawl, outlinks, depth):
    for link in outlinks:
        if link not in tocrawl:
        	if is_tripadvisor(link):
        		tocrawl.append([link, depth+1])

def add_page_to_index(index, url, content):
	try:
		text = content.get_text()
	except:
		return
	words = text.split()
	for word in words:
		add_to_index(index, word, url)
        
def add_to_index(index, keyword, url):
    if keyword in index:
        index[keyword].append(url)
    else:
        index[keyword] = [url]


def get_page(url):
	page_url = urlparse(url)
	base = page_url[0] + '://' + page_url[1]
	robots_url = base + '/robots.txt'
	rp = rerp.RobotFileParserLookalike()
	rp.set_url(robots_url)
	rp.read()
	if not rp.can_fetch('*', url):
		print "Page off limits!"
		return BeautifulSoup(""), ""
	if url in cache:
		return cache[url]
	else:
		print "Page not in cache: " + url
		try:
			content = urllib.urlopen(url).read()
			return BeautifulSoup(content), url
		except:
			return BeautifulSoup(""), ""

# page rank algorithm
# webpage has more rank if it has more innode compare to outnode
# p(innode/outnode)

def compute_ranks(graph):
    d = 0.8 # damping factor
    numloops = 10
    
    ranks = {}
    npages = len(graph)
    for page in graph:
        ranks[page] = 1.0 / npages
    
    for i in range(0, numloops):
        newranks = {}
        for page in graph:
            newrank = (1 - d) / npages
            for node in graph:
                if page in graph[node]:
                    newrank = newrank + d * (ranks[node] / len(graph[node]))
            
            newranks[page] = newrank
        ranks = newranks
    return ranks

def is_tripadvisor(url):
	tripadvisor_urls = ['http://www.tripadvisor.in']
	parsed_url = urlparse(url)
	if parsed_url[1] not in tripadvisor_urls:
		return True
	else:
		return True

# function to return information about Restaurant
def get_content(page):
	content = {}
	# parsing specific web page content
	soup, url = get_page(page)
	# print soup
	try:
		format_address_content = soup.find('span',attrs={"class" : "format_address"}).findAll(text=True)
		address = ', '.join([str(x) for x in format_address_content])
		content['address'] = address
	except:
		content['address'] = "";

	
	try:
		phoneNumber_content = soup.find('div',attrs={"class" : "phoneNumber"}).findAll(text=True)
		phoneNumber = phoneNumber_content[0]
		content['phoneNumber'] = phoneNumber
	except:
		content['phoneNumber'] = ""

	try:	
		name_content = soup.find('h1',attrs={"class" : "heading_name"}).findAll(text=True)
		name = ""
		name_str = ', '.join([str(x) for x in name_content])
		name = name_str.strip("\n").replace(",","").replace("\n","")
		content['name'] = name
	except:
		content['name'] = ""

	try:
		cuisine_content = soup.find('div',attrs={"class" : "detail separator"}).findAll(text=True)
		cuisine_str = ', '.join([str(x) for x in cuisine_content])
		content['cuisine'] = cuisine_str.strip("\n").replace(",","").replace("\n","")
	except:
		content['cuisine'] = ""

	try:
		user_review_content = soup.find('h3',attrs={"class" : "tabs_header reviews_header"}).findAll(text=True)
		review = user_review_content[0]
		content['review'] = review
	except:
		content['review'] = ""

	try:	
		top_review_content = soup.find('div',attrs={"class" : "isNew"}).findAll(text=True)
		top_review_content_arr = []
		top_review_content_str = ""
		for content in top_review_content:
			ascii_content = unicodedata.normalize('NFKD', content).encode('ascii','ignore')
			top_review_content_arr.append(ascii_content)
		top_review_content_arr_str = ', '.join([str(x) for x in top_review_content_arr])
		top_review = top_review_content_arr_str.strip("\n").replace(",","").replace("\n","")
		content['top_review'] = top_review
	except:
		content['top_review'] = ""

	return content

# code starts from here 

cache = {} # store key value pairs
max_pages = 1
max_depth = 1 # to stop infinite crawling
index, graph = crawl_web('https://www.tripadvisor.in/Restaurants',max_pages, max_depth)
ranks = compute_ranks(graph)

# print "INDEX: ", index
# print ""
# print "GRAPH: ", graph
# print ""
# print "RANKS: ", ranks

for url_key, url_val in graph.iteritems():
	expected_uls = filter(lambda k: 'Restaurant_Review' in k, url_val)

# print expected_uls

unique_expected_uls = list(set(expected_uls))

#applying filer for remove duplications

for review_url in unique_expected_uls:
	if '#REVIEWS' in review_url:
		unique_expected_uls.remove(review_url)

print unique_expected_uls

restraurants_content = []

for Restaurant in unique_expected_uls:
	try:
		content = get_content(Restaurant)
		restraurants_content.append(content)
	except:
		content = {}

# Open database connection
db = MySQLdb.connect("localhost","root","root","tripadvisor")

# prepare a cursor object using cursor() method
cursor = db.cursor()

for content_map in restraurants_content:
	try:
		cursor.execute('''INSERT into restraurants (name, address, phoneNumber, cuisine, review, top_review)
                  values (%s, %s, %s, %s, %s, %s, %s)''',
                  (content_map['name'],content_map['address'],content_map['phoneNumber_content'], content_map['cuisine'], content_map['review'], content_map['top_review']))
		db.commit()
	except:
	    print "rollback"
	    db.rollback()