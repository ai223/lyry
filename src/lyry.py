'''
Created on Jan 13, 2018

@author: aleks
'''

import sys
import re

from bs4 import BeautifulSoup
import requests
import datetime
from nose.tools import assert_equals

# global variables
chart_names = []
charts_dict = {}

# string constants
msg = "Welcome to Lyry, a program which allows you to obtain the lyrics from any billboard chart."
sep = "="*105 + "\n"


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
    all_metrolyrics_urls_dict = create_song_and_artists_urls(chart_url_list)
    extract_and_write_lyrics(chart_url_list, all_metrolyrics_urls_dict)   


"""  """
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
            print("The earliest available date for " + chart_name + " is: " + earliest_date)
            
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
            

"""  """
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


""" Prompt user for valid date or range of dates corresponding to available 
    Billboard chart(s). """
def get_date_selection(chart_link) :
    print("Note: dates need to be entered in a valid YYYY-MM-DD format.\n" + 
          "Hit 'Enter' to obtain default current chart information.")
    date = input("Please enter a date or range of dates: ").strip()
    
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
        print("Uh-oh. Can't handle that yet.")
        sys.exit()


"""  """
def create_song_and_artists_urls(chart_url_list) :
    all_metrolyrics_urls_dict = {}
    
    for url in chart_url_list :
        print(url)

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
        
        metrolyrics_urls = []
        for i in range(len(song_list)) :
            metrolyrics_url = create_metrolyrics_url(song_list[i], artist_list[i]) 
            metrolyrics_urls.append(metrolyrics_url)    
        
        all_metrolyrics_urls_dict[url] = metrolyrics_urls
        
    return all_metrolyrics_urls_dict


"""  """
def extract_and_write_lyrics(chart_url_list, all_metrolyrics_urls_dict) :
    
    # create list of all filenames
    for chart_url in chart_url_list:      
        filename = createFilename(chart_url)
        
        # create variables to keep track of successful scrapes
        num_songs = len(all_metrolyrics_urls_dict[chart_url])
        num_missed = 0
        
        # extract and write song lyrics            
        print("\nExtracting and writing song lyrics...")
        with open(filename, 'w', encoding="utf-8") as file: 
            for song_url in all_metrolyrics_urls_dict[chart_url] :
                html = requestURL(song_url)
                
                # try azlyrics.com if metrolyrics 404-Missing Page is recieved
                if html == '' :
                    az_url = create_azlyrics_url(song_url)
                    az_info = extract_azlyrics(az_url)
                    if az_info == "#" : 
                        file.write("Could not find: " + az_url + "\n" + sep)
                        num_missed += 1
                        continue
                    
                    file.write(az_info[0]+"\n")
                    file.write(az_info[1])
                    file.write("\n" + sep + "\n")
                    continue
                    
                soup = BeautifulSoup(html, 'lxml')
                title = soup.find("title").text
                # remove "Metrolyrics" from title 
                split = title.find("|")
                title = title[:split-1] + "\n\n"
                
                verse_tags = soup.select('.verse')
                
                # if lyrics were not available on metrolyrics, try azlyrics
                if len(verse_tags) == 0 :
                    az_url = create_azlyrics_url(song_url)
                    az_info = extract_azlyrics(az_url)
                    if az_info == "#" :
                        file.write("Could not find" + az_url + "\n" + sep + "\n")
                        num_missed += 1
                        continue
                    
                    file.write(az_info[0]+"\n")
                    file.write(az_info[1])
                    file.write("\n" + sep + "\n")   
                    continue         
                
                file.write(song_url + "\n")
                file.write(title)
                [file.write(tag.text + "\n\n") for tag in verse_tags]
                file.write("\n" + sep + "\n")        
            
            file.write("Number of total songs: " + str(num_songs) + '\n')
            file.write("Number of found lyrics: " + str(num_songs - num_missed) + '\n')
            file.write("Success rate: " + str(((num_songs-num_missed)/num_songs)*100) + "%")    

                       
""" """        
def create_metrolyrics_url(song_name, artist_name):
    # process song name
    song = (song_name.lower()).replace(" ", "-")
        
    # check for illegal characters in song name
    song = cleanup(song, ["(", ")", "'"])
    print(song)
    
    # process artist name
    symbol_list = ["&", "Featuring", ","]
    
    # check for cutoff symbols (for songs with multiple artists, only the first name is kept)
    # e.g. "Queen Featuring David Bowie" -> "Queen." 
    cutoff = len(artist_name)
    for symbol in symbol_list :
        if symbol in artist_name :
            cutoff = artist_name.find(symbol)

    artist_name = (artist_name[:cutoff]).strip()
    
    artist = (artist_name.lower()).replace(" ", "-")
    
    # check for illegal character's in artist's name
    # E.g. 'the' is not kept in artist's name, so "the-beatles" -> "beatles" 
    artist = cleanup(artist, [".", "!", "?"])
    
    url = "http://www.metrolyrics.com/" + song + "-lyrics-" + artist + ".html"
    if "lyrics-the-" in url : url = url.replace('lyrics-the-', 'lyrics-')

    return url


"""  """
def create_azlyrics_url(metrolyrics_url):

    pos1 = metrolyrics_url.rfind("/") + 1
    pos2 = metrolyrics_url.find("-lyrics-")
    pos3 = pos2 + 8
        
    song_name = metrolyrics_url[pos1:pos2].replace("-", "")
    artist_name = metrolyrics_url[pos3:-5].replace("-", "")
    
    azlyrics_url = "https://www.azlyrics.com/lyrics/" + artist_name + "/" + song_name + ".html"
    
    if "'" in azlyrics_url :
        azlyrics_url = azlyrics_url.replace("'", "")
        
    return azlyrics_url


"""  """
def extract_azlyrics(url) :
    html = ''
    
    hdrs = {'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.112 Safari/534.30"}
    req = requests.get(url, headers=hdrs)
    
    if req.status_code == 200 :
        html = req.text
    else :
        print("AZLyrics Page Not Found.")
        return "#"

    # if scrape unsuccessful 
    if html == '' : 
        return "#"
        
    soup = BeautifulSoup(html, 'lxml')
    
    #get song name and artist
    title = soup.find("title").text
    
    # get lyrics
    div_tags = soup.findAll("div", {"class":None})
    lyrics = div_tags[1].text
    
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
    print("\n")
    print("\tls -" + " "*10 + "display all chart names")
    print("\tq  -" + " "*10 + "exit program")    


""""""
def cleanup(name, illegal_char_list) :
    for char in illegal_char_list :
        if char in name :
            name = name.replace(char, "")
            
    return name

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
    # if day of week is not Satruday, move date up to Saturday
    while day_of_week != "Saturday" :
        date = date + datetime.timedelta(days = 1)
        day_of_week = date.strftime("%A")    
    
    return date

"""  """
def requestURL(url) :
    req = requests.get(url)
    if req.status_code == 200 :
        return req.text
    else :
        print("Page Not Found.")
        return ''
    

if __name__=="__main__" :
    script_start()

    
