import requests
from bs4 import BeautifulSoup


url = 'https://www.franksonnenbergonline.com/blog/are-you-grateful/'
response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'lxml')
title_tag = soup.find('main').find('header').find('h1')
title_tag = title_tag.text
print(title_tag)

image = soup.find('img', class_='attachment-post-image')['src']
print(image)

article = soup.find('article').find('div')
print(article.text)
