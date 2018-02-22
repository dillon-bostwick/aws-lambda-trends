import urllib2
import boto3
import time
from BeautifulSoup import BeautifulSoup
from boto3.dynamodb.conditions import Key, Attr

serp_table = boto3.resource('dynamodb').Table('serps')
serp_updates_topic = boto3.resource('sns').Topic('arn:aws:sns:us-east-1:995452415820:serp_updates')

QUERY = 'steak+restaurants+near+me'
LOCATION = 'new york'

def get_serp_urls(page_start):
	google_req = urllib2.Request('http://www.google.com/search?q=' + QUERY + '&near=' + LOCATION + '&uule=w+CAIQICINVW5pdGVkIFN0YXRlcw&start=' + str(page_start))
	
	# Google expects User-Agent or else 403
	google_req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.95 Safari/537.11')

	serp_html = urllib2.urlopen(google_req).read()
	res_soup = BeautifulSoup(serp_html)

	return [ cite_tag.string for cite_tag in res_soup.findAll('cite') ]

def get_most_recent_serps():
	global serp_table

	# Get item with highest timestamp (timestamp is already sort key of table)
	query_res = serp_table.query(
		KeyConditionExpression=Key('id').eq(':id'),
		ScanIndexForward=False,
		Limit=1
	)

	if len(query_res['Items']) == 0:
		return []

	return query_res['Items'][0]['urls']

def record_serp_change(new_serps):
	global serp_table
	global serp_updates_topic

	serp_table.put_item(
		Item={
			'id': ':id',	
			'timestamp': int(time.time()),
			'urls': new_serps
		}
	)

	# serp_updates_topic.publish(
	# 	Subject='SERP change observed',
	# 	Message='https://console.aws.amazon.com/dynamodb/home?region=us-east-1#tables:selected=serps'
	# )


# LAMBDA
def scrape_serps_and_update(event, context):
	most_recent_serps = get_most_recent_serps()
	new_serps = get_serp_urls(0) + get_serp_urls(10) # first 20 results (10 per page)

	if most_recent_serps != new_serps:
		record_serp_change(new_serps)
	


