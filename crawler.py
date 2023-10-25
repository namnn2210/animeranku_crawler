from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from database import MangaAnimeNews
from hashids import Hashids

import config
import requests
import os

def get_soup_url(page_url):
    proxies = {
        'http': 'http://71.86.129.131:8080',
    }
    s = requests.Session()
    # s.proxies = proxies
    page_res = s.get(page_url).text
    # server_ip = page_res.raw._connection.sock.getpeername()[0]
    # print(f"Server IP Address: {server_ip}")
    return BeautifulSoup(page_res, 'html.parser')

def check_latest_news(update_time):
    today = datetime.today().date()
    return update_time >= (today - timedelta(days=3))

def get_basic_info(news_soup):
    news_title = news_soup.find('meta',{'property':'og:title'})['content']
    news_thumb_url = news_soup.find('meta',{'property':'og:image'})['content']
    news_description = news_soup.find('meta',{'property':'og:description'})['content']
    return news_title, news_thumb_url, news_description

def insert_db(db, news_obj):
    news_exists = db.query(MangaAnimeNews).filter(MangaAnimeNews.slug == news_obj.slug).count()
    if news_exists == 0:
        try:
            db.add(news_obj)
            db.commit()
        except Exception as ex:
            print(str(ex))
            db.rollback()

def update_idx(db, slug):
    db_news = db.query(MangaAnimeNews).filter(MangaAnimeNews.slug == slug).first()
    if db_news:
        news_id = db_news.id
        idx = hashidx(news_id)
        try:
            db.query(MangaAnimeNews).filter(MangaAnimeNews.id == news_id).update({'idx': idx})
            db.commit()
        except Exception as ex:
            print(str(ex))
            db.rollback()
        
    
def download_img(list_download_imgs):
    for download_img in list_download_imgs:
        url = download_img['url']
        path = download_img['path']
        print(f'download image url: {url}')
        response = requests.get(url)
        save_path = f'/www-data/animeranku.com/storage/app/public/{path}'
        if response.status_code == 200:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(response.content)
                
def hashidx(id):
    hashids = Hashids(salt='TIND', alphabet='abcdefghijklmnopqrstuvwxyz1234567890', min_length=7)
    return hashids.encode(id)

if __name__ == "__main__":
    proxies = {
        'http': 'http://71.86.129.131:8080',
    }
    # r = requests.get('http://www.example.com', proxies = proxies)
    # print (r.status_code, r.reason)
    s = requests.Session()
    # s.proxies = proxies
    
    url = 'http://api.ipify.org'

    try:
        response = s.get(url)
        print(response.text)
    except:
        print("Proxy does not work")