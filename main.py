from requests import request
from bs4 import BeautifulSoup
import re

URL = 'https://rezka.ag/'
URL_SEARCH = 'https://rezka.ag/search/?do=search&subaction=search&q='
URL_POST = 'https://rezka.ag/ajax/get_cdn_series/'


def soap(html):
    return BeautifulSoup(html, 'html.parser')

def get_page(url):
    return request('GET', url).text

class Something:
    '''Нечто из мира фильмов, сериалов, мультфильмов и аниме'''

    def __init__(self, item):
        """Constructor"""
        self.id = item['data-id']
        self.url = item['data-url']
        self.name = item.find(class_='b-content__inline_item-link').a.string
        self.description = item.find(class_='b-content__inline_item-link').div.string
        self.type = item.find(class_='entity').string
        self.page = soap(get_page(self.url))
        try:
            '''Если нечто имеет озвучку по умолчанию или нет'''
            self.t_id = re.findall(r'Events\(\d+, \d+',str(self.page))[0].split(' ')[-1]
        except:
            self.t_id = -1;

        try:
            '''Если нечто - односерийное и его нет в html'''
            self.state = item.find(class_='info').string
        except AttributeError:
            self.state = "Существует"

        if (self.state != 'Существует'):
            #[ [1,20], [21,39] ] - 2 сезона
            self.seasons = []
            episodes = self.page.findAll(class_='b-simple_episodes__list')
            for i in range(len(self.page.findAll(class_='b-simple_episodes__list'))):
                self.seasons.append([ int(episodes[i]('li')[0]['data-episode_id']) , int(episodes[i]('li')[-1]['data-episode_id']) ])


    def _post(self, data_):
        '''post запрос для получения json фильма'''
        return request('POST', URL_POST, data=data_).text


    def show(self,i):
        print('%i) Название - "%s", Тип - "%s", Описание - "%s", Статус - "%s"'%(i ,self.name ,self.type ,self.description ,self.state))


    def get_urls_mp4(self,season=0, episode=0):
        '''Создание запроса и возращение json'''
        if (self.t_id!=-1):
            res = 0
            if (self.state=='Существует'):
                res = self._post({
                    'id': self.id,
                    'translator_id': self.t_id,
                    'is_camrip': 0,
                    'is_ads': 0,
                    'is_director': 0,
                    'action': 'get_movie'
                })
            elif (self.state!='Существует'):
                res = self._post({
                    'id': self.id,
                    'translator_id': self.t_id,
                    'season': season,
                    'episode': episode,
                     'action': 'get_stream'
                })


            return res
        return "Нет доступа"


name = input("Введите название того, что вы хотите посмотреть:\n")

page = soap(get_page(URL_SEARCH+name))

items_str = page.find(class_='b-content__inline_items')
items = items_str.findAll(class_="b-content__inline_item")


somethings = []

for i in range(len(items)):
    somethings.append(Something(items[i]))
    print(somethings[i].show(i+1))


num = int(input("Выберите то, что нужно посмотреть и напишите его номер:\n"))
elem = somethings[num-1]
if (elem.state == 'Существует'):
    res = (elem.get_urls_mp4())

elif(elem.state != 'Существует'):
    seas = int(input("Выберите сезон (%d сезон(ов)):\n"%len(elem.seasons)))
    ep = int(input("Выберите серию (%d - %d):\n"%(elem.seasons[seas-1][0],elem.seasons[seas-1][1])))
    res = (elem.get_urls_mp4(seas, ep))

if (res.split(',')[0].split(':')[-1]=='true') :
    url_res = res.replace('\\', '').split(']')[-1][:-1].split(' ')
    print(url_res[0] if url_res[0][-3:] == 'mp4' else url_res[2].split('"')[0])
