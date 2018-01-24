'''
Created on Jan 13, 2018

@author: aleks
'''

import sys
import re
from time import sleep

from bs4 import BeautifulSoup
import requests
import datetime
from nose.tools import assert_equals
import random

# global variables
chart_names = []
charts_dict = {}

# string constants
msg = "Welcome to Lyry, a program which allows you to obtain the lyrics from any billboard chart."
sep = "\n" + "="*105 + "\n"

# import socks
# import socket
# 
# import stem.process
# 
# SOCKS_PORT=7000# You can change the port number
# 
# tor_process = stem.process.launch_tor_with_config(
#     config = {
#         'SocksPort': str(SOCKS_PORT),
#     },
# )
# 
# 
# socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5,
#                       addr="127.0.0.1",
#                       port=SOCKS_PORT)
# socket.socket = socks.socksocket


"""  """
def script_start() :
    # obtain all billboard chart names and links 
    charts_tuples = pull_chart_names()
    
    global chart_names
    chart_names = charts_tuples[0]
    global charts_dict
    charts_dict = charts_tuples[1]
    
    # begin user interaction
    print(msg)
    display_options()
    chart_link = get_chart_selection()
    chart_url_list = get_date_selection(chart_link)
    all_songs_and_artists_dict = get_song_and_artist_names(chart_url_list)
    write_billboard_lyrics(chart_url_list, all_songs_and_artists_dict)
    
#     all_metrolyrics_urls_dict = create_song_and_artists_urls(chart_url_list)
    
#     extract_and_write_lyrics(chart_url_list, all_metrolyrics_urls_dict)   


""" Accesses billboard.com to get a list of all currently offered charts and their 
    respective bilbloard.com links.
    
    The function returns both a list of chart names (for pretty printing) and a 
    dictionary that returns a billboard.com link when queried with the name of a
    particular chart.

    @return name_list: a list of all billboard chart names, as appearing on 
                       https://www.billboard.com/charts 
    
    @return chart_dict: a dictionary where the key-value pairs are chart names and
                        their respective billboard.com links """
def pull_chart_names() :
    url = "https://www.billboard.com/charts"
    html = requestURL(url)
    
    soup = BeautifulSoup(html, 'lxml')
    chart_links = soup.select('.chart-row__chart-link')
    
    name_list, href_list= [], []
    for i in chart_links :
        name_list.append(i.string)
        href_list.append(i['href'])
    chart_dict = dict(zip(name_list, href_list))

    return (name_list, chart_dict)


""" Prompts the user to select a billboard chart for lyrics extraction.

    The user can make a few different choices. They can enter a number corresponding to
    a particular billboard chart (i.e. "40" representing "Hot Country Songs") or they can
    enter the chart name in full.  """
def get_chart_selection() :
    chart = input("Please enter a billboard chart name or number: ").strip()   

    if chart == "ls" :
        ls(chart_names)
        return get_chart_selection()
    elif chart == "q" :
        print(sep, "\nThanks for using the program!")
        sys.exit()
    else: 
        # if user enters chart number
        if chart.isdigit() :
            pos = int(chart) - 1
            
            if pos < 1 or pos > len(chart_names) :
                print(sep + "\nInvalid number selection. Please try again.\n")
                return get_chart_selection() 
            
            chart_name = chart_names[pos]
            earliest_date = getEarliestDate(charts_dict[chart_name])
            
            print(sep + "\nYou have selected: " + chart_name + ".")
            print("\nNow enter a date or range of dates from which " +
              "you would like to obtain lyrics.\n\n(Note: dates need to be entered in " +
              "a valid YYYY-MM-DD format. To enter a range of dates, simply enter two " +
              "dates\nseparated by a single space (e.g. '2011-01-03 2011-07-21'). Hit " +
              "'Enter' without typing anything to obtain the\ncurrent chart by default.)" + 
              "\n\nThe earliest available date for " + chart_name + " is: " + earliest_date)
                        
            return charts_dict[chart_name]
        
        # if user enters chart name
        elif all((x.isalpha() or x.isspace()) and not(x.isdigit()) for x in chart) :
            print("You have selected: " + chart + ".")
            return charts_dict[chart]
        
        # if user enters an invalid option
        else :
            print(sep + "\nYou have made an invalid selection " + 
                        "(name with number is not allowed) Try again.\n")
            return get_chart_selection()


""" Prompt user for valid date or range of dates corresponding to available 
    Billboard chart(s). """
def get_date_selection(chart_link) :
 
    date = input("Please enter your date selection: ").strip()
    
    if date == 'q' :
        print(sep, "\nThanks for using the program!")
        sys.exit()
    
    elif date == '' :  
        today = datetime.date.today()
        # move date up to Saturday, if not on Saturday
        date = resetDate(today)
        
        return ["https://www.billboard.com/" + chart_link + "/" + str(date)]
    
    elif len(date) == 10 :
        date = validate(date)
        if date == '#' :
            return get_date_selection(chart_link) 
        
        return ["https://www.billboard.com/" + chart_link + "/" + str(date)]
    
    elif len(date) == 21 :
        split = date.find(" ")
        date1 = date[:split]
        date2 = date[split+1:]

        all_dates = validate(date1, date2)
        
        func = lambda each_date : "https://www.billboard.com/" + chart_link + "/" + str(each_date)
        all_chart_urls = list( map(func, all_dates) )

        return all_chart_urls
    else :
        print("Invalid date selection: " + date + ". Please try again or enter 'q' to stop." )
        return get_date_selection(chart_link)


""" """
def get_song_and_artist_names(chart_url_list) :
    all_songs_and_artists_dict = {}
    
    for url in chart_url_list :
        
        html = requestURL(url)
        soup = BeautifulSoup(html, 'lxml')
        song_tags = soup.select(".chart-row__song")
        artist_tags = soup.select(".chart-row__artist") 
        assert len(song_tags) == len(artist_tags)

        song_list = []
        [song_list.append(tag.string) for tag in song_tags]
        
        # [1:-1] slice removes bookend newline characters from the artist tag
        artist_list = []
        [artist_list.append(tag.string[1:-1]) for tag in artist_tags]
        
        song_and_artist_names = list(zip(song_list, artist_list))
        all_songs_and_artists_dict[url] = song_and_artist_names
    
    return all_songs_and_artists_dict


""" """
def extract_billboard_lyrics(song_name, artist_name) :
    
    metrolyrics_url = create_metrolyrics_url(song_name, artist_name)
    title_and_lyrics = extract_metrolyrics(metrolyrics_url)
    
    if title_and_lyrics == '' :    
        genius_url = create_genius_url(song_name, artist_name)
        title_and_lyrics = extract_genius(genius_url)
        
#     if title_and_lyrics == '' :
#         az_url = create_azlyrics_url(song_name, artist_name)
#         title_and_lyrics = extract_azlyrics(az_url)

    return title_and_lyrics


""" """
def write_billboard_lyrics(chart_url_list, all_songs_and_artists_dict) :
    for chart_url in chart_url_list :
        filename = createFilename(chart_url)
        
        print("Extracting and writing lyrics to file...")
        
        with open(filename, 'w', encoding="utf-8") as file: 
            
            song_and_artist_name_list = all_songs_and_artists_dict[chart_url]
            
            tot_num_songs = len(song_and_artist_name_list)
            tot_num_missd = 0
            def tot_num_found() : return tot_num_songs - tot_num_missd
            def percent_yield() : return ((tot_num_songs - tot_num_missd)/tot_num_songs)*100
            
            for song_and_artist_pair in song_and_artist_name_list :
                song_name   = song_and_artist_pair[0]
                artist_name = song_and_artist_pair[1]
                
                title_and_lyrics = extract_billboard_lyrics(song_name, artist_name)
                
                if title_and_lyrics == '' : 
                    tot_num_missd += 1
                    continue
                
                title =  title_and_lyrics[0]
                lyrics = title_and_lyrics[1]
                
                file.write(title)
                file.write(lyrics)
                file.write(sep)   
                
            file.write("Number of total songs: " + str(tot_num_songs) + "\n")
            file.write("Number of found lyrics: " + str(tot_num_found()) + "\n")
            file.write("Success rate: " + str(percent_yield()) + "%")           


# """  """
# def create_song_and_artists_urls(chart_url_list) :
#     all_metrolyrics_urls_dict = {}
#     
#     for url in chart_url_list :
#         print(url)
# 
#         html = requestURL(url)
#         soup = BeautifulSoup(html, 'lxml')
#         song_tags = soup.select(".chart-row__song")
#         artist_tags = soup.select(".chart-row__artist") 
#         assert len(song_tags) == len(artist_tags)
#                 
#         song_list = []
#         [song_list.append(tag.string) for tag in song_tags]
#         
#         # [1:-1] slice removes bookend newline characters from the artist tag
#         artist_list = []
#         [artist_list.append(tag.string[1:-1]) for tag in artist_tags]
#         
#         metrolyrics_urls = []
#         for i in range(len(song_list)) :
#             metrolyrics_url = create_metrolyrics_url(song_list[i], artist_list[i]) 
#             metrolyrics_urls.append(metrolyrics_url)    
#         
#         all_metrolyrics_urls_dict[url] = metrolyrics_urls
#         
#     return all_metrolyrics_urls_dict


# """  """
# def extract_and_write_lyrics(chart_url_list, all_metrolyrics_urls_dict) :
#     
#     # create list of all filenames
#     for chart_url in chart_url_list:      
#         filename = createFilename(chart_url)
#         
#         # create variables to keep track of successful scrapes
#         num_songs = len(all_metrolyrics_urls_dict[chart_url])
#         num_missed = 0
#         
#         # extract and write song lyrics            
#         print("\nExtracting and writing song lyrics...")
#         with open(filename, 'w', encoding="utf-8") as file: 
#             for song_url in all_metrolyrics_urls_dict[chart_url] :
#                 html = requestURL(song_url)
#                 
#                 # try azlyrics.com if metrolyrics 404-Missing Page is recieved
#                 if html == '' :
#                     az_url = create_azlyrics_url(song_url)
#                     az_info = extract_azlyrics(az_url)
#                     if az_info == "#" : 
#                         file.write("Could not find lyrics. Tried:\n\n\t\t" 
#                                    + song_url + "\n\t\t" + az_url + sep)
#                         num_missed += 1
#                         continue
#                     
#                     file.write(az_info[0]+"\n")
#                     file.write(az_info[1])
#                     file.write(sep)
#                     continue
#                     
#                 soup = BeautifulSoup(html, 'lxml')
#                 title = soup.find("title").text
#                 # remove "Metrolyrics" from title 
#                 split = title.find("|")
#                 title = title[:split-1] + "\n\n"
#                 
#                 verse_tags = soup.select('.verse')
#                 
#                 # if lyrics were not available on metrolyrics, try azlyrics
#                 if len(verse_tags) == 0 :
#                     az_url = create_azlyrics_url(song_url)
#                     az_info = extract_azlyrics(az_url)
#                     if az_info == "#" :
#                         file.write("Could not find lyrics. Tried:\n\n\t\t" 
#                                    + song_url + "\n\t\t" + az_url + sep)
#                         num_missed += 1
#                         continue
#                     
#                     file.write(az_info[0]+"\n")
#                     file.write(az_info[1])
#                     file.write(sep)   
#                     continue         
#                 
#                 file.write(song_url + "\n")
#                 file.write(title)
#                 [file.write(tag.text + "\n\n") for tag in verse_tags]
#                 file.write(sep)        
#             
#             file.write("Number of total songs: " + str(num_songs) + '\n')
#             file.write("Number of found lyrics: " + str(num_songs - num_missed) + '\n')
#             file.write("Success rate: " + str(((num_songs-num_missed)/num_songs)*100) + "%")    

                       
""" """        
def create_metrolyrics_url(song_name, artist_name):
    song = cleanup_song(song_name, ["(", ")", "'", "&"])
    song = (song.replace(" ", "-"))
         
    artist = cleanup_artist(artist_name, [".", "!", "?"])
    artist = (artist.replace(" ", "-"))

    url = "http://www.metrolyrics.com/" + song + "-lyrics-" + artist + ".html"
    if "lyrics-the-" in url : url = url.replace('lyrics-the-', 'lyrics-')
    if "-+-" in url : url = url.replace("-+-", "-")

    return url


""" """
def extract_metrolyrics(url) :
    
    html = requestURL(url)
    if html == '' : return ''
        
    soup = BeautifulSoup(html, 'lxml')
    
    title = soup.find("title").text
    # remove "Metrolyrics" from title 
    split = title.find("|")
    title = title[:split-1] + "\n\n"
    
    lyrics = ''             
    verse_tags = soup.select('.verse')
    if len(verse_tags) == 0 :
        print("Could not find: " + url)
        return ''
    
    for tag in verse_tags :
        lyrics = lyrics + tag.text +"\n"
    
    return (title, lyrics)


"""  """
def create_azlyrics_url(song_name, artist_name):

    illegal_char_list = [" ", "'", "&", "(", ")", "!", "?"]
    song = cleanup_song(song_name, illegal_char_list)
    artist = cleanup_artist(artist_name, illegal_char_list)    

    azlyrics_url = "https://www.azlyrics.com/lyrics/" + artist + "/" + song + ".html"
        
    return azlyrics_url


"""  """
def extract_azlyrics(url) :
    
    html = requestURL(url)
    if html == '' : return ''
        
    soup = BeautifulSoup(html, 'lxml')
    
    #get song name and artist
    title = soup.find("title").text
    
    # get lyrics
    div_tags = soup.findAll("div", {"class":None})
    lyrics = div_tags[1].text
    
    return (title, lyrics)


""" """
def create_genius_url(song_name, artist_name):
    "https://genius.com/Nina-simone-dont-let-me-be-misunderstood-lyrics"
    
    
    song = cleanup_song(song_name, ["'", "&", "(", ")", "!", "?"])
    song = song.replace(" ", "-")

    
    artist = cleanup_artist(artist_name,  [".", "!", "?"])
    artist = artist.replace(" ", "-")

    
    url = "https://genius.com/" + artist + "-" + song + "-lyrics"
    if "-+-" in url : url = url.replace("-+-", "-")

    return url


""""""
def extract_genius(url) :
    html = requestURL(url)
    if html == '' : return ''
        
    soup = BeautifulSoup(html, 'lxml')
    
    #get song name and artist
    title = soup.find("title").text
    
    # get lyrics
    lyrics = soup.select(".lyrics")[0].text
    
    return (title, lyrics)


""" """
def createFilename(chart_url) :
    name_and_date = chart_url[34:]    
    split = name_and_date.find('/')        
    
    name = name_and_date[:split]
    date = name_and_date[split+1:]
    
    return name + " (" + date + ")"
              
        
""" Shows user message containing possible keyboard inputs """
def display_options() :
    print("\tls -" + " "*10 + "display all chart names")
    print("\tq  -" + " "*10 + "exit program")    


""""""
def cleanup_song(name, illegal_char_list) :
    for char in illegal_char_list :
        if char in name :
            name = name.replace(char, "")
            
    return name.lower()


""""""
def cleanup_artist(name, illegal_char_list) :
    
    symbol_list = ["&", "Featuring", ",", "And", "Feat", "With"]
    # check for cutoff symbols (for songs with multiple artists, only the first name is kept)
    # e.g. "Queen Featuring David Bowie" -> "Queen." 
    cutoff = len(name)
    for symbol in symbol_list :
        if symbol in name :
            cutoff = name.find(symbol)

    name = (name[:cutoff]).strip()
    
    illegal_char_list = ["'", "&", "(", ")", "!", "?"]
    for char in illegal_char_list :
        if char in name :
            name = name.replace(char, "")
            
    return name.lower()


""" lname: list that contains strings representing billboard chart names
    
    displays a formatted 2-column numbered list of billboard chart names. """
def ls(lname) :
    assert(isinstance(lname, list))
    print("\n")
 
    # break list up into 2 columns using 2 iterators
    for a, b in zip(*[iter(enumerate(lname, start=1))]*2) :
        print(str(a[0]) + ": " + "{0:<55s}".format(a[1]) + 
              str(b[0]) + ": " + "{0:<50s}".format(b[1]) )
    
    print("\n")


""" """
def getEarliestDate(chart_name) :
    # Pick absurdly early date; Billboard.com will automatically round up to earliest chart
    url = "https://www.billboard.com" + chart_name + "/1900-01-01"
    html = requestURL(url)
    
    soup = BeautifulSoup(html, 'lxml')
    date = soup.find("time")['datetime']
    
    return date


""""""
def validate(date1, date2=None) :
    
    try :
        date1 = datetime.datetime.strptime(date1, '%Y-%m-%d')
    except ValueError :
        print("Invalid date entered: " + date1)
        return '#'
    
    # if only one date provided
    if date2 == None :
        date1 = resetDate(date1.date())
        
        return str(date1)
    
    # if both dates are provided
    else :
        try :
            date2 = datetime.datetime.strptime(date2, '%Y-%m-%d')
        except ValueError :
            print("Invalid date entered: " + date2)
            return '#'            
    
        date1 = resetDate(date1.date())
        date2 = resetDate(date2.date())

        if str(date1) == str(date2) : 
            return str(date1)
        
        if date2 < date1 :
            print("Error: second date earlier than the first.")
            return "#"
        
        # get dates for every chart before starting and ending date
        all_chart_dates = []
        while date1 <= date2 :
            all_chart_dates.append(str(date1))
            date1 += datetime.timedelta(days = 7)
        
        return all_chart_dates


""" date: a datetime object representing a date falling on a week when a given 
          billboard chart was published 
          
    billboard charts are """
def resetDate(date) :
    
    day_of_week = date.strftime("%A")
    
    switchover_date = datetime.date(1961, 12, 25)
    
    if date <= switchover_date :
        while day_of_week != "Monday" :
            date = date + datetime.timedelta(days = 1)
            day_of_week = date.strftime("%A")           
    else :
        while day_of_week != "Saturday" :
            date = date + datetime.timedelta(days = 1)
            day_of_week = date.strftime("%A")    
    
    return date


"""  """
def requestURL(url) :
    
    proxies = [{"http": "http://107.170.13.140:3128"}, {"http": "http://198.23.67.90:3128"}]
#     headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }        
    hdrs = {'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.112 Safari/534.30"}
    hdrs3 = {'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)'}
    
    headers = [
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
        'Opera/9.25 (Windows NT 5.1; U; en)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
        'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:8.0.1) Gecko/20100101 Firefox/8.0.1',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.151 Safari/535.19']
    
    sleep(random.randint(0, 10))
    req = requests.get(url, headers = hdrs)
    if req.status_code == 200 :
        return req.text
    else :
        print("Could not find: " + url)
        return ''
    

if __name__=="__main__" :
    script_start()
#     tor_process.kill()

    
