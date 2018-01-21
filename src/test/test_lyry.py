'''
Created on Jan 21, 2018

@author: aleks
'''

import unittest

import lyry

class TestLyry(unittest.TestCase) :
    
    def testAdd(self) :
        print("This is just a test.")
        result = True
        
        self.assertEqual(result, True, "Oh no!")
        
    def test_pull_chart_names(self) :
        
        bingo = lyry.pull_chart_names()
        print(bingo[0])
        
        self.assertEqual(len(bingo), 2, "Something's wrong!")