# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as bs
import YDStreamExtractor


title = ['Les docus']
img = ['lesdocus']
readyForUse = True
bypass_cache = False
test_mode = False
max_pages_per_category = 50
root_url = 'http://www.les-docus.com'


def load_soup(url, cache_key):
    if test_mode:
        import urllib2
        force_headers = {
            'user-agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
        req = urllib2.Request(url, headers=force_headers)
        html = urllib2.urlopen(req).read()
    else:
        from resources.lib import utils
        file_path = utils.download_catalog(url, cache_key, bypass_cache, 'get', {}, True, {})
        html = open(file_path).read()

    return bs(html, 'html.parser')


# **list_shows(channel,folder)**: Utilise pour recuperer la liste des menus.
# Channel est toujours renseigne.Folder est un parametre remseigbne a none la 1ere fois et contient votre parametre
# les fois suivantes.
# Retourne un tableau **Ligne=[ channel, parameter pour prochain passage dans fonction,
# Titre pour menu, image pour menu, action effectuee quand clic sur menu]**
# _Dernier parametre : 'folder' : retour dans meme fonctions, 'shows' prochain passage est dans "list_videos"
# noinspection PyPep8Naming
def list_shows(channel, folder):
    categories = []

    print('listing categories for folder ' + folder)
    if folder != 'none':
        # level 2
        selector = '#%s li' % folder
    else:
        # level 1
        selector = 'ul.blog-menu > li'

    print('selector ' + selector)

    soup = load_soup(root_url, root_url)
    menu_items = soup.select(selector)

    # print('soup :%s'%(soup.prettify(encoding='utf-8')))

    for item in menu_items:
        # has_sub_menus = len(item.select('li')) != 0
        has_sub_menus = item.select_one('li') is not None

        if has_sub_menus:
            categories.append([channel, item.attrs['id'], item.select_one('a').getText().encode('utf-8'), '', 'folder'])
        else:
            categories.append(
                [channel, item.select_one('a').attrs['href'], item.select_one('a').getText().encode('utf-8'), '',
                 'shows'])

    print('Categories: %s' % categories)

    return categories


# **list_videos(channel,show_URL)**: Fonctionne de maniere similaire.
# Retourne un tableau **Ligne=[ channel, param pour passage dans fonction
# getvideoURL, Titre pour menu, image pour menu, infoLabels, 'play']**
# noinspection PyPep8Naming
def list_videos(channel, show_name):
    videos = []
    loop_idx = 0

    next_page_link = show_name
    while next_page_link is not None and loop_idx < max_pages_per_category:
        next_page_link = get_posts(channel, next_page_link, videos)
        loop_idx += 1

    print('Videos : %s' % videos)

    return videos


def get_posts(channel, list_page, videos):
    print("Listing videos: " + list_page)
    soup = load_soup(list_page, list_page)

    posts = soup.select('.post')
    print('Found %d posts ' % (len(posts)))

    # print(posts[0].prettify(encoding='utf-8'))
    for post in posts:
        post_title = post.select_one('h2 a').getText().encode('utf-8')
        link = post.select_one('h2 a').attrs['href'].encode('utf-8')
        post_img = post.select_one('.post-header img')
        img_url = post_img.attrs['data-lazy-src'].encode('utf-8') if post_img is not None else ''
        desc = post.select_one('.post-header p')
        info_labels = {
            "Title": post_title,
            "Plot": desc.getText().encode('utf-8') if desc is not None else '',
            # "Aired": date,
            # "Duration": duration,
            # "Year": date[:4]
        }
        videos.append([channel, link, post_title, img_url, info_labels, 'play'])

    next_page_item = soup.select_one('.post-nav a.next')
    next_page_link = next_page_item.attrs['href'] if next_page_item is not None else None

    return next_page_link


# getVideoURL(channel,video_URL)**: Retourne l'URL qui devra etre lu par KODI
# noinspection PyPep8Naming,PyUnusedLocal
def getVideoURL(channel, video_url):
    print('fetching URL for %s' % video_url)

    info = YDStreamExtractor.getVideoInfo(video_url, quality=3)

    if info is None:
        print('YDStream did no return anything for URL %s' % video_url)
        return None
    else:
        return info.streamURL()
