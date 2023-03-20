import requests
from bs4 import BeautifulSoup as bs

def get_bbc_text(url:str) -> list:
    """Parse bbc article and return text in list of strings"""
    
    article = requests.get(url)
    soup = bs(article.content, "html.parser")
    # print(soup)
    body = soup.find(class_="ssrcss-pv1rh6-ArticleWrapper e1nh2i2l6")
    text = [p.text for p in body.find_all("p")] 
    return text

def get_reuters_text(url:str) -> list:
    article = requests.get(url)
    soup = bs(article.content, "html.parser")
    # print(soup)
    body = soup.find(class_ = "article-body__content__17Yit paywall-article")
    # body = soup.find(class_="text__text__1FZLe text__dark-grey__3Ml43 text__medium__1kbOh text__heading_2__1K_hh heading__base__2T28j heading__heading_2__3Fcw5")
    text = [p.text for p in body.find_all("p")] 
    return text

def get_ap_text(url:str) -> list:
    article = requests.get(url)
    # print(article.content)
    soup = bs(article.content, "html.parser")
    # print("="*10)
    # print(soup)
    body = soup.find(class_ = "Article") # sometimes article 
    if body:
        text = [p.text for p in body.find_all("p")] 
        return text


