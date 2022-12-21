
import requests	
from news import scrape
import news.summarization as summarization

def NewsFromAP():
	
	query_params = {
	"source": "associated-press",
	"sortBy": "top",
	"apiKey": "f58a31b8ccdb449f8bf038a5fac6282e"
	}
	main_url = " https://newsapi.org/v1/articles"

	# fetching data in json format
	res = requests.get(main_url, params=query_params)
	open_reuters_page = res.json()
	# print(open_reuters_page)
	# getting all articles in a string article
	article = open_reuters_page["articles"]
	articles = article[:5]	
	# for k in article[0].keys():
	# 	print(f"k {k}")
	# empty list which will contain all trending news
	results = []
	
	for ar in articles:
		print(ar['title'])

def NewsFromReuters():
	
	query_params = {
	"source": "reuters",
	"sortBy": "top",
	"apiKey": "f58a31b8ccdb449f8bf038a5fac6282e"
	}
	main_url = " https://newsapi.org/v1/articles"

	# fetching data in json format
	res = requests.get(main_url, params=query_params)
	open_reuters_page = res.json()

	# getting all articles in a string article
	article = open_reuters_page["articles"]
	# for k in article[0].keys():
	# 	print(f"k {k}")
	# empty list which will contain all trending news
	results = []
	articles = article[:5]	
	for ar in articles:
		print(ar['title'])
		# print(ar['publishedAt'])
		# try:
		# 	a = scrape.get_reuters_text(ar['url'])
		# 	a = " ".join(a)
		# 	# print(summarization.abstract_summary(a))
		# except:
		# 	print("article unable")
		results.append(ar["title"])
		
	# for i in range(len(results)):
		
	# 	# printing all trending news
	# 	print(i + 1, results[i])

		

# Driver Code
if __name__ == '__main__':
	# print(scrape.get_ap_text("https://apnews.com/article/2022-midterm-elections-house-control-nov15-0608a0c22be510cec983f605e6a305b3?utm_source=homepage&utm_medium=TopNews&utm_campaign=position_01"))
	# function call
	NewsFromAP()
	# print("dnwkdnjkwbndkjwsbndjksdnjksndskjdnsjkdnjks")
	# NewsFromReuters()
