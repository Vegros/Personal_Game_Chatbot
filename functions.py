#imports
from lxml import etree
from bs4 import BeautifulSoup
from lxml import html
import requests
from requests_html import HTMLSession
from selenium import webdriver
import time



HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}


#functions




#*****************GET DATA RELATED TO A GAME************************
def getSummary(url):
    try:
        response = requests.get(url, headers=HEADERS)
        tree = html.fromstring(response.content)
        SummaryElement = tree.cssselect('.summary-info > div')[0]


        Summary = []
        Summary.append(SummaryElement.text_content())
        Summary = [desc.replace('\n', '').replace('\r', '').replace('\t', ' ') for desc in Summary]

        return Summary
    except:
        return ['summary not found']


def getRating(url):
    try:
        response = requests.get(url, headers=HEADERS)
        tree = html.fromstring(response.content)
        rating = tree.cssselect('.stack.jsx-604379120 > div > div')
        Ratings = []
        Ratings.append(rating[0].text_content())
        return Ratings
    except:
        return ['rating not found']






def getGenre(url):
    response = requests.get(url, headers=HEADERS)
    tree = html.fromstring(response.content)
    index = 1;
    Genres = []
    while True:

        try:
            Getgenre = tree.cssselect('.genres-info > div:nth-child(2) > a:nth-child(' + str(index) + ')')[0]
            index += 2
            Genres.append(Getgenre.text_content())

        except:
            break
    if Genres == []:
        return ['genre not found']
    return Genres

def getPlatform(url):

    response = requests.get(url, headers=HEADERS)
    tree = html.fromstring(response.content)
    index = 1
    Platform = []
    while True:
        try:
            platform = tree.cssselect('.platforms > a:nth-child('  + str(index) + ' ) > svg > title')
            Platform.append(platform[0].text_content())
            index += 1

        except:
            break

    if(  Platform == []):
        return ['platforms not found']

    return Platform




def getDeveloper(url):

    try:
        response = requests.get(url, headers=HEADERS)
        tree = html.fromstring(response.content)
        dev = tree.cssselect('.developers-info > div:nth-child(2) > a')[0]
        Developer = []
        Developer.append(dev.text_content())
        return Developer
    except:
        return ['developer not found']



def getDateReleased(url):
    try:
        response = requests.get(url, headers=HEADERS)
        tree = html.fromstring(response.content)
        date = tree.cssselect('.initial-release-info > div:nth-child(2)')[0]
        Date = []
        Date.append(date.text_content())


        return Date
    except:
        return ['date not found']


##*****************GET ITEMS BY TAGS ************************

def LongUrl(url): #only to be excecuted once
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')

    # use Selenium to scroll down the page and load all content

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    driver = webdriver.Chrome(options = options)
    driver.get(url)
    scroll_pause_time = 2
    scroll_height = driver.execute_script("return document.documentElement.scrollHeight")
    max_scroll = 4
    scroll_count = 0
    while scroll_count < max_scroll:
        # Scroll down to the end of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        scroll_count += 1
        time.sleep(1)  # Wait for page to load


    # parse the loaded content with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    return soup

def getGamesUnderGenre( soup, count):   #can be used to get franchise/genre/platform/feature/publisher

    tree = etree.HTML(str(soup))
    game = tree.cssselect('#main-content > form > div > div > div > a:nth-child(' + str(count)+') > div.details > div.interface.jsx-1545499971.jsx-957202555.title.bold')
    return game[0].text

def getAllGamesUnderGenre( url):

    soup = LongUrl(url)
    allGames = []
    count = 1
    while True:
        try:
            game = getGamesUnderGenre( soup,count)

            if game != '':
                allGames.append(game)
                count += 1
        except:
            break

    return allGames
def generateGameArray(url):

    gameArray = []

    try:
        gameArray.append(str(getSummary(url)[0].lower()))
        gameArray.append(str(getRating(url)[0].lower()))
        gameArray.append(str(getDeveloper(url)[0].lower()))
        gameArray.append(str(getDateReleased(url)[0].lower()))
        for item in getPlatform(url):
            gameArray.append(item.lower())

        for item in getRating(url):
            gameArray.append(item.lower())

        for item in getGenre(url):
            gameArray.append(item.lower())
    except:
        print('Not all information is found')

    return gameArray




