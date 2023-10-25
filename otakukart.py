from crawler import get_soup_url, check_latest_news, insert_db, download_img, get_basic_info, update_idx
from database import db_connect
from dateutil.parser import parse
from datetime import datetime
from database import MangaAnimeNews
import os

today = datetime.today().date()
print(f'***************** {today}')
year = today.year
month = today.month
day = today.day


def get_news_links(page_url):
    soup = get_soup_url(page_url)
    print(soup)
    news_links = []
    
    list_news = soup.find_all('article', {'class': 'post'})
    for news in list_news:
        news_url = news.find('header',{'class':'entry-header'}).find('h2',{'class':'entry-title'}).find('a')['href']
        news_soup = get_soup_url(page_url=news_url)
        publish_time = news_soup.find('meta',{'property':'article:published_time'})['content']
        update_time_obj = parse(publish_time).date()
        if check_latest_news(update_time_obj):
            news_links.append(news_url)
    
    return news_links                                                                                                                            


def scrape_news_links(base_url):
    page_number = 1
    all_news_links = []
    
    while True:
        page_url = f"{base_url}page/{page_number}"
        news_links = get_news_links(page_url)
        print(news_links)
        
        if page_number == 1 and len(news_links) == 0:
            break
        
        if not news_links:
            break
        
        print(f"Page {page_number} - Total news links: {len(news_links)}")
        all_news_links.extend(news_links)
        page_number += 1
    
    return all_news_links

def get_news(news_url):
    db = db_connect()
    print(news_url)
    list_download_imgs = []
    img_count = 0
    news_soup = get_soup_url(news_url)
    news_title, news_thumb_url, news_description  = get_basic_info(news_soup=news_soup)
    news_slug = news_url.split('/')[-2]
    img_name = f'{news_slug}_{img_count}.jpg'
    formatted_thumb = os.path.join('images/news', str(year), str(month), str(day), img_name)
    news_author = news_soup.find('a',{'rel':'author'}).text
    list_download_imgs.append({'url':news_thumb_url,'path':formatted_thumb})
    content_div = news_soup.find('div',{'class':'entry-content'})
    
    # Remove ez_toc
    ez_toc_container = content_div.find('div',{'id':'ez-toc-container'})
    ez_toc_container.decompose()
    
    # Remove clear div
    clear_divs = content_div.find_all('div',{'style':'clear:both; margin-top:0em; margin-bottom:1em;'})
    for div in clear_divs:
        div.decompose()
        
    # Remove ad box
    ad_boxes = content_div.find_all('div',{'class':'mv-ad-box'})
    for ads in ad_boxes:
        ads.decompose()
        
    # Remove source href
    a_link_source = content_div.find_all('a')
    for link in a_link_source:
        link.unwrap()
    
    # Get list images
    figure_images = content_div.find_all('figure',{'class':'wp-caption'})
    # src_key = 'src'
    for figure in figure_images:
        if figure.has_attr('style'):
            del figure['style']
        print(figure)
        img_count += 1
        img = figure.find('img')
        print(img)
        img_src = img['data-lazy-src']
        print(f'======================== {img_src}')
        new_img_name = f'{news_slug}_{img_count}.jpg'
        formatted_img_name = os.path.join('images/news', str(year), str(month), str(day), new_img_name)
        # Change name
        img['src'] = f'https://static.animeranku.com/i/{formatted_img_name}'
        # Add to download list
        list_download_imgs.append({'url':img_src,'path':formatted_img_name})
        
    download_img(list_download_imgs)
    # Insert to DB
    news = {
        'slug': news_slug,
        'name': news_title.replace('- OtakuKart',''),
        'thumb': formatted_thumb,
        'description': news_description,
        'content': str(content_div),
        'original': news_url,
        'author': news_author,
        'featured': 1,
        'type': 'CRAWL',
        'ordinal': 0,
        'status': 1,
        'news_category_id': 4,
        'manga_ids': '',
        'anime_ids': '',
        'total_comment': 0,
        'total_view': 0,
        'total_like': 0,
        'published_by': 1,
        'meta_tag_id': None,
        'created_by': 1,
        'updated_by': 1,
        'deleted_by': 0,
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
        'deleted_at': None,
    }
    news_obj = MangaAnimeNews(**news)
    insert_db(db=db, news_obj=news_obj)
    update_idx(db=db, slug=news_slug)
    db.close()

if __name__ == "__main__":  
    url = 'http://otakukart.com/manga/'
    all_links = scrape_news_links(url)
    
    for link in all_links:
        get_news(link)
    