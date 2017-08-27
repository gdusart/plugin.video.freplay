#-*- coding: utf-8 -*-
from bs4 import BeautifulSoup as bs
import re


title       = ['Les docus']
img         = ['lesdocus']
readyForUse = True
bypass_cache = False
debug = False

forced_headers = {'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
root_url = 'http://www.les-docus.com'

def load_soup(url, cache_key):
    if debug:
        from urllib.request import Request, urlopen
        q = Request(root_url, headers=forced_headers)
        html = urlopen(q).read()
    else:
        from resources.lib import utils
        file_path = utils.download_catalog(url, cache_key, bypass_cache, 'get', {}, True, {})
        html = open(file_path).read()

    return bs(html, 'html.parser')


#**list_shows(channel,folder)**: Utilise pour recuperer la liste des menus.
# Channel est toujours renseigne.Folder est un parametre remseigbne a none la 1ere fois et contient votre parametre les fois suivantes.
# Retourne un tableau **Ligne=[ channel, parameter pour prochain passage dans fonction, Titre pour menu, image pour menu, action effectuee quand clic sur menu]**
#_Dernier parametre : 'folder' : retour dans meme fonctions, 'shows' prochain passage est dans "list_videos"
def list_shows(channel, folder):
    categories = []

    print('listing categories for folder ' + folder)
    if folder != 'none':
        #level 2
        selector = '#%s li'%(folder)
    else:
        #level 1
        selector = 'ul.blog-menu > li'

    print('selector ' + selector)

    soup = load_soup(root_url, root_url)
    menu_items = soup.select(selector)

    #print('soup :%s'%(soup.prettify(encoding='utf-8')))

    for item in menu_items:
        #has_sub_menus = len(item.select('li')) != 0
        has_sub_menus = item.select_one('li') is not None

        if has_sub_menus:
            categories.append([channel, item.attrs['id'], item.select_one('a').getText().encode('utf-8'), '', 'folder'])
        else:
            categories.append([channel, item.select_one('a').attrs['href'], item.select_one('a').getText().encode('utf-8'), '', 'shows'])

    print('Categories: %s'%(categories))

    return categories


#**list_videos(channel,show_URL)**: Fonctionne de maniere similaire.
# Retourne un tableau **Ligne=[ channel, param pour passage dans fonction getvideoURL, Titre pour menu, image pour menu, infoLabels, 'play']**
def list_videos(channel, show_name):
    videos = []
    max_loops = 10
    loop_idx = 0

    next_page_link = show_name
    while (next_page_link is not None and loop_idx < 10):
        print('loading page %d: %s'%(loop_idx+1, next_page_link))
        next_page_link = get_posts(channel, next_page_link, videos)
        loop_idx+=1

    print('Videos : %s'%(videos))
    print('Next page link : %s'%(next_page_link))

    #add link to next page >> does not work
    #videos.append([channel, next_page_link, 'Next >>', '', 'shows'])

    return videos

def get_posts(channel, list_page, videos):
    print("Listing videos: " + list_page)
    soup = load_soup(list_page, list_page)

    posts = soup.select('.post')
    print('Found %d posts ' % (len(posts)))

    #print(posts[0].prettify(encoding='utf-8'))
    for post in posts:
        title = post.select_one('h2 a').getText().encode('utf-8')
        link = post.select_one('h2 a').attrs['href'].encode('utf-8')
        img = post.select_one('.post-header img')
        img_url = img.attrs['data-lazy-src'].encode('utf-8') if img is not None else ''
        desc = post.select_one('.post-header p')
        desc_txt = desc.getText().encode('utf-8') if desc is not None else ''
        videos.append([channel, link, title, img_url, desc_txt, 'play'])

    next_page_item = soup.select_one('.post-nav a.next')

    next_page_link =  next_page_item.attrs['href'] if next_page_item is not None else None

    print('next page link : %s' % (next_page_link))
    return next_page_link

#getVideoURL(channel,video_URL)**: Retourne l'URL qui devra etre lu par KODI
def getVideoURL(channel,video_url):
    return []


def main():
    root_menu = (list_shows('lesdocus', 'none'))
    print('Root menu %s'%(root_menu))

    first_sub_menu = list_shows('lesdocus', root_menu[0][1])
    print('Sub menu %s'%(first_sub_menu))

    videos = list_videos('lesdocus', first_sub_menu[0][1])
    print('Videos: %s'%(videos))

if __name__ == "__main__":
    main()