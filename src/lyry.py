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
sep = "="*105

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
    chart_url = get_date_selection(chart_link)
    song_urls = create_song_and_artists_urls(chart_url)
       

def get_chart_selection() :
    chart = input("Please enter a billboard chart name or number: ").strip()   

    if chart == "ls" :
        ls(chart_names)
        return get_chart_selection()
    elif chart == "q" :
        print(sep, "\nThanks for using the program!")
        sys.exit()
    else: 
        if chart.isdigit() :
            chart_name = chart_names[int(chart)]
            print(sep + "\nYou have selected: " + chart_name + ".")
            return charts_dict[chart_name]
        elif all((x.isalpha() or x.isspace()) and x.isdigit() for x in chart) :
            print("You have selected: " + chart + ".")
            return charts_dict[chart]
        else :
            print(sep + "\nYou have made an invalid selection " + 
                        "(name with number is not allowed) Try again.\n")
            return get_chart_selection()
            

def pull_chart_names() :
    url = "https://www.billboard.com/charts"
    html = requestURL(url)
    
    soup = BeautifulSoup(html, 'lxml')
    soup.prettify()
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
    date = input("Please enter a date or range of dates: ")
    print("chart_link: " + chart_link)

    
    if date == '' :  
        return ["https://www.billboard.com/" + chart_link]
    else :
        print("Uh-oh. Can't handle that yet.")
        sys.exit()


def create_song_and_artists_urls(url_list) :
    for url in url_list : 
        html = requestURL(url)
        
        soup = BeautifulSoup(html, 'lxml')
        song_tags = soup.select(".chart-row__song")
        artist_tags = soup.select(".chart-row__artist")
                
        song_list = []
        [song_list.append(tag.string) for tag in song_tags]
        
        # [1:-1] slice removes newline characters from the beginning and end of the artist tag
        artist_list = []
        [artist_list.append(tag.string[1:-1]) for tag in artist_tags]
        
        print(song_list)
        print(artist_list)
                
        assert len(song_list) == len(artist_list)

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
        

def display_options() :
    print("\tls -" + " "*10 + "display all chart names")
    print("\tq  -" + " "*10 + "exit program")    


def requestURL(url) :
    req = requests.get(url)
    if req.status_code == 200 :
        return req.text
    else :
        print("Page Not Found.")
        return ''
    


if __name__=="__main__" :
    script_start()
    
