'''
    NRK plugin for XBMC
    Copyright (C) 2010 Thomas Amland

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import urllib, re, time
import xbmcaddon
from BeautifulSoup import BeautifulSoup
from DataItem import DataItem
from dataStatic import *

id = xbmcaddon.Addon(id="plugin.video.nrk").getSetting("quality")
QUALITY = {'0' : '400', '1' : '800', '2' : '1200' }[id]
QUALITY_STR = {'0' : 'l', '1' : 'm', '2' : 'h' }[id]

def getLive():
    items = [
    DataItem(title="NRK 1", url="mms://straumv.nrk.no/nrk_tv_direkte_nrk1_"+QUALITY_STR+"?UseSilverlight=1",
             thumb=os.path.join(R_PATH, "nrk1.jpg"), isPlayable=True),
    DataItem(title="NRK 2", url="mms://straumv.nrk.no/nrk_tv_direkte_nrk2_"+QUALITY_STR+"?UseSilverlight=1",
             thumb=os.path.join(R_PATH, "nrk2.jpg"), isPlayable=True),
    DataItem(title="NRK 3", url="mms://straumv.nrk.no/nrk_tv_direkte_nrk3_"+QUALITY_STR+"?UseSilverlight=1",
             thumb=os.path.join(R_PATH, "nrk3.jpg"), isPlayable=True) ]
    return items


def getLatest():
    soup = BeautifulSoup(urllib.urlopen("http://www.nrk.no/nett-tv/"))
    li = soup.find('div', attrs={'class' : 'nettv-latest'}).findAll('li')
    items = []
    for e in li:
        anc = e.find('a', attrs={'href' : re.compile('^/nett-tv/klipp/[0-9]+')})
        items.append( _getVideoById(anc['href'].split('/').pop()) )
    return items


def getByUrl(url):
    if (url.startswith("/nett-tv/tema") or url.startswith("/nett-tv/bokstav")):
        url = "http://www.nrk.no" + url 
        soup = BeautifulSoup(urllib.urlopen(url))
        return _getAllProsjekt(soup)
    
    elif (url.startswith("/nett-tv/prosjekt")):
        url = "http://www.nrk.no" + url
        
    elif (url.startswith("/nett-tv/kategori")):
        url = "http://www.nrk.no/nett-tv/menyfragment.aspx?type=category&id=" + url.split('/').pop()
    
    soup = BeautifulSoup(urllib.urlopen(url))
    items = []
    items.extend(_getAllKlipp(soup))
    items.extend(_getAllKategori(soup))
    return items


def _getAllKlipp(soup):
    items = soup.findAll('a', attrs={'class':re.compile('icon-video-black.*'), 'href':re.compile('.*nett-tv/klipp/[0-9]+$')})
    return [ _getVideoById(e['href'].split('/').pop()) for e in items ]


def _getAllKategori(soup):
    items = soup.findAll('a', attrs={'class':re.compile('icon-closed-black.*'), 'href':re.compile('^/nett-tv/kategori/[0-9]+')})
    return [ DataItem(title=e['title'], url=e['href']) for e in items ]


def _getAllProsjekt(soup):
    items = []
    li = soup.find('div', attrs={'class' : 'nettv-category clearfix'}).findAll('li') 
    for e in li:
        anc = e.find('a', attrs={'href' : re.compile('^/nett-tv/prosjekt/[0-9]+')})
        title = anc['title']
        url   = anc['href']
        img   = e.find('img')['src']
        descr = str(e.find('div', attrs={'class':'summary'}).find('p').string)
        
        items.append( DataItem(title=title, description=descr, thumb=img, url=url) )
    return items


def _getVideoById(id):
    url = "http://www.nrk.no/nett-tv/silverlight/getmediaxml.ashx?id=" + id + "&hastighet=" + QUALITY
    soup = BeautifulSoup(urllib.urlopen(url))
    title = soup.find('title').string
    descr = str(soup.find('description').string)
    
    img = soup.find('imageurl').string
    url = soup.find('mediaurl').string
    #some uri's contais illegal chars so need to fix this
    url = url.split("mms://", 1)[1]
    url = url.encode('latin-1') #urllib cant unicode
    url = urllib.quote(url)
    url = "mms://" + url + "?UseSilverlight=1"
    
    return DataItem(title=title, description=descr, thumb=img, url=url, isPlayable=True)

def _getSizeBig(url):
    _150 = re.sub("^(.*cropid.*)w[0-9]+$", "\\1w150", url)
    _480 = re.sub("^(.*cropid.*)w[0-9]+$", "\\1w480", url)
    
    p = urllib.urlopen(_480)
    size = p.info().getheaders("Content-Length")
    if (size and size[0] > 0):
        return _480
    return url

