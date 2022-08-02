
import requests	
from news import scrape
import news.summarization as summarization
def NewsFromReuters():
	
	# BBC news api
	# following query parameters are used
	# source, sortBy and apiKey
	query_params = {
	"source": "reuters",
	"sortBy": "top",
	"apiKey": "f58a31b8ccdb449f8bf038a5fac6282e"
	}
	main_url = " https://newsapi.org/v1/articles"

	# fetching data in json format
	res = requests.get(main_url, params=query_params)
	open_bbc_page = res.json()

	# getting all articles in a string article
	article = open_bbc_page["articles"]

	# empty list which will
	# contain all trending news
	results = []
	
	for ar in article:
		print(ar['url'])
		try:
			a = scrape.get_reuters_text(ar['url'])
			a = " ".join(a)
			print(summarization.abstract_summary(a))
		except:
			print("article unable")
		results.append(ar["title"])
		
	for i in range(len(results)):
		
		# printing all trending news
		print(i + 1, results[i])

		

# Driver Code
if __name__ == '__main__':
	
	# function call
	NewsFromBBC()
