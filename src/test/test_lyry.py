'''
Created on Jan 21, 2018

@author: aleks
'''

import unittest

import lyry

class TestLyry(unittest.TestCase) :
        
    def test_pull_chart_names(self) :
        
        bingo = lyry.pull_chart_names()
        print(bingo[0])
        
        self.assertEqual(len(bingo), 2, "Something's wrong!")
        
    def test_get_song_and_artist_names_from_charts(self) :
        url_list = ["https://www.billboard.com//charts/country-airplay/1995-05-06"]
        all_songs_and_artists_dict = lyry.get_song_and_artist_names_from_charts(url_list)
        lyry.write_lyrics(url_list, all_songs_and_artists_dict)    
        
#     def test_create_azlyrics_url(self) :
#         
#         url1 = "http://www.metrolyrics.com/thunder-lyrics-imagine-dragons.html"
#         url2 = "http://www.metrolyrics.com/don't-stop-believin'-lyrics-journey.html"
#         url3 = "http://www.metrolyrics.com/pumped-up-kicks-lyrics-foster-the-people.html"
#         
#         az_url1 = lyry.create_azlyrics_url(url1)
#         az_url2 = lyry.create_azlyrics_url(url2)
#         az_url3 = lyry.create_azlyrics_url(url3)
#         
#         print(az_url1)
#         print(az_url2)
#         print(az_url3)
    
#     def test_extract_azlyrics(self) :
#         
#         url1 = 'https://www.azlyrics.com/lyrics/imaginedragons/thunder.html'
#         url2 = 'https://www.azlyrics.com/lyrics/journey/dontstopbelievin.html'
#         url3 = 'https://www.azlyrics.com/lyrics/fosterthepeople/pumpedupkicks.html'
#         
#         lyry.extract_azlyrics(url1)
#         lyry.extract_azlyrics(url2)
#         lyry.extract_azlyrics(url3)
        