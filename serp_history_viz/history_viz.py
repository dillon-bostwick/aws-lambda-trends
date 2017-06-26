import boto3
import matplotlib.pyplot as plt
from matplotlib import ticker
from datetime import datetime

def show_graph(single_url_index):
	# TODO handle single url index for filtering out one url

	serp_table = boto3.resource('dynamodb').Table('serps')

	all_serp_entries = serp_table.scan(
		AttributesToGet=[ 'timestamp', 'urls' ]
	)['Items']

	urls_to_plot = []

	# generate the initial list of urls that will be plotted
	for entry in all_serp_entries:
		for url in entry['urls']:
			if not any(url_obj['name'] == url for url_obj in urls_to_plot):
				urls_to_plot.append({
					'name': url,
					'timestamps': [],
					'rankings': []
				})

	for entry in all_serp_entries:
		for ranking, url in enumerate(entry['urls']):
			url_obj_to_update = next( url_obj for url_obj in urls_to_plot if url_obj['name'] == url )

			if url_obj_to_update['rankings']:
				url_obj_to_update['timestamps'].append(datetime.fromtimestamp(entry['timestamp'] - 3600))
				url_obj_to_update['rankings'].append(url_obj_to_update['rankings'][-1])

			url_obj_to_update['timestamps'].append(datetime.fromtimestamp(entry['timestamp']))
			url_obj_to_update['rankings'].append(ranking + 1)

	ax = plt.subplot(1, 2, 1)

	for url_obj in urls_to_plot:
		plt.plot(url_obj['timestamps'], url_obj['rankings'], label=url_obj['name'])

	# ax.set_xticklabels([ unixToHuman(ts) for ts in ax.get_xticks() ])
	plt.xticks( rotation=25 )
	plt.gca().invert_yaxis()
	plt.legend(bbox_to_anchor=(1, 1))
	plt.show()

if __name__ == "__main__":
    import sys
    show_graph(sys.argv[1] if len(sys.argv) == 2 else None)