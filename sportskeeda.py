from datetime import datetime
from database import db_connect, MangaAnimeNews
from datetime import datetime
from dateutil.parser import parse
import os
from crawler import get_soup_url, check_latest_news, insert_db, download_img, get_basic_info, update_idx

today = datetime.today().date()
print(f'***************** {today}')
year = today.year
month = today.month
day = today.day



def get_news_links(page_url):
    soup = get_soup_url(page_url)
    
    news_links = []
    
    # Extract primary news links
    list_primary_news = soup.find_all('div', {'class': 'sport-feed-item-primary'})
    for news in list_primary_news:
        href = news.find('a')['href']
        news_url = f'https://www.sportskeeda.com{href}'
        news_soup = get_soup_url(page_url=news_url)
        update_time = news_soup.find('meta',{'property':'article:modified_time'})['content']
        # update_time_obj = datetime.strptime(update_time, '%Y-%m-%dT%H:%M:%S+%z').date()
        update_time_obj = parse(update_time).date()
        if check_latest_news(update_time_obj):
            news_links.append(news_url)
    
    # Extract secondary news links
    list_secondary_news = soup.find_all('div', {'class': 'feed-item-secondary'})
    for news in list_secondary_news:
        href = news.find('a')['href']
        news_url = f'https://www.sportskeeda.com{href}'
        news_soup = get_soup_url(page_url=news_url)
        update_time = news_soup.find('meta',{'property':'article:modified_time'})['content']
        # update_time_obj = datetime.strptime(update_time, '%Y-%m-%dT%H:%M:%S+%z').date()
        update_time_obj = parse(update_time).date()
        if check_latest_news(update_time_obj):
            news_links.append(news_url)
    
    return news_links                                                                                                                            

def scrape_news_links(base_url):
    page_number = 1
    all_news_links = []
    
    while True:
        page_url = f"{base_url}?page={page_number}"
        news_links = get_news_links(page_url)
        
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
    news_slug = news_url.split('/')[-1]
    img_name = f'{news_slug}_{img_count}.jpg'
    formatted_thumb = os.path.join('images/news', str(year), str(month), str(day), img_name)
    list_download_imgs.append({'url':news_thumb_url,'path':formatted_thumb})
    news_author = news_soup.find('meta',{'name':'author'})['content']
    content_div = news_soup.find('div',{'id':'article-content'})

    
    # Check if content has twitter embeded 
    embeded = content_div.find('div',{'class':'sportskeeda-embed'})
    if embeded is None:
        # Remove video ads
        video_ads = content_div.find_all('div',{'id':'video-player-container--'})
        for vid_ads in video_ads:
            vid_ads.decompose()
        # Remove ads
        ads_containter = content_div.find_all('div',{'class':'ad-container'})
        for ad_con in ads_containter:
            ad_con.decompose()
        
        # Remove comment box
        comments_container = content_div.find('div',{'id':'keeda-comments-container'})
        comments_container.decompose()
        
        # Remove unneccessary parts
        bottom_tagline = content_div.find('div',{'class':'bottom-tagline'})
        bottom_tagline.decompose()
        
        tag_cloud = content_div.find('div',{'id':'tag-cloud'})
        tag_cloud.decompose()
        
        bottom_info_container = content_div.find('div',{'class':'bottom-info-container'})
        bottom_info_container.decompose()
        
        # Remove source href
        a_link_source = content_div.find_all('a',{'data-is-sponsored':'false'})
        for link in a_link_source:
            link.unwrap()
            
        # Remove hr
        hr_div = content_div.find_all('hr')
        for hr in hr_div:
            hr.decompose()
        
        # Get list images
        figure_images = content_div.find_all('figure',{'class':'image'})
        # src_key = 'src'
        for figure in figure_images:
            print(figure)
            img_count += 1
            img = figure.find('img',{'class':'lazy-img'})
            img_src = img['data-img']
            print(f'======================== {img_src}')
            new_img_name = f'{news_slug}_{img_count}.jpg'
            formatted_img_name = os.path.join('images/news', str(year), str(month), str(day), new_img_name)
            # Change name
            img['src'] = f'https://static.animeranku.com/i/{formatted_img_name}'
            # Add to download list
            list_download_imgs.append({'url':img_src,'path':formatted_img_name})
        
        # Save image
        download_img(list_download_imgs)
        
        # Insert to DB
        news = {
            'slug': news_slug,
            'name': news_title,
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
    else:
        print(f'{news_url} has embeded')
    db.close()
    

if __name__ == "__main__":  
    url = 'https://www.sportskeeda.com/anime/news'
    all_links = scrape_news_links(url)
    
    for link in all_links:
        get_news(link)
        
    
