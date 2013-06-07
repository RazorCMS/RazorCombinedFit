#! /usr/bin/env python
import os.path
import sys
import datetime, time

def getXsecRange(box,neutralinopoint,gluinopoint):

    if gluinopoint <= 150 :
        return [0.01, 0.05, 0.07, 1.0, 2.0]
    elif gluinopoint ==175 :
        return [0.01, 0.05, 0.07, 1.0, 1.5]
    elif gluinopoint == 200 :
        return [0.01, 0.05, 0.07, 0.5, 0.7, 1.0, 1.5]
    elif gluinopoint == 225 :
        return [ 0.05, 0.1, 0.2, 0.5, 0.7, 1.0, 1.5]
    elif gluinopoint == 250 :
        return [ 0.05, 0.1, 0.5, 0.7, 1.0]
    elif gluinopoint == 275 :
        return [ 0.05, 0.1, 0.5, 0.7, 1.0]
    elif gluinopoint == 300 :
        return [ 0.05, 0.1, 0.5, 0.7, 1.0]
    elif gluinopoint == 325 :
        return [  0.1, 0.5, 0.7, 1.0]
    elif gluinopoint == 350 :
        return [  0.05, 0.1, 0.5, 0.7, 1.0]
    elif gluinopoint == 375 :
        return [ 0.05, 0.1, 0.5, 0.7, 1.0]
    elif gluinopoint == 400 :
        return [ 0.05, 0.1, 0.5, 0.7, 1.0]
    elif gluinopoint == 425 :
        return [ 0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0]
    elif gluinopoint == 450 :
        return [ 0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0]
    elif gluinopoint == 475 :
        return [ 0.01, 0.1, 0.2, 0.3, 0.5]
    elif gluinopoint == 500 :
        return [ 0.01, 0.05, 0.1, 0.2, 0.3]
    elif gluinopoint == 525 :
        return [0.01, 0.05, 0.1, 0.2]
    elif gluinopoint == 550 :
        return [ 0.01, 0.05, 0.1, 0.2, 0.3]
    elif gluinopoint == 575 :
        return [ 0.01, 0.05, 0.1, 0.2, 0.3]
    elif gluinopoint == 600 :
        return [ 0.005, 0.01, 0.05, 0.1, 0.2]
    elif gluinopoint == 625 :
        return [ 0.005, 0.01, 0.05, 0.1, 0.2]
    elif gluinopoint == 650 :
        return [ 0.005, 0.01, 0.05, 0.1]
    elif gluinopoint == 675 :
        return [ 0.005, 0.01, 0.05, 0.1]
    elif gluinopoint == 700 :
        return [ 0.005, 0.01, 0.03, 0.05, 0.1] 
    elif gluinopoint == 725 :
        return [ 0.005, 0.01, 0.03, 0.05, 0.1]
    elif gluinopoint == 750 :
        return [ 0.005, 0.01, 0.03, 0.05, 0.1]
    elif gluinopoint == 775 :
        return [ 0.005, 0.01, 0.03, 0.05, 0.1]
    elif gluinopoint == 800 :
        return [ 0.005, 0.01, 0.03, 0.05, 0.1]

def getStopMassPoints(box, neutralinopoint):

    if box == 'Mu':
        stopMassDict = {
            25: (150.0, 175.0, 200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            50: (150.0, 175.0, 200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            75: (175.0, 225.0, 250.0, 300.0, 325.0, 425.0, 475.0, 500.0, 550.0, 575.0, 650.0, 700.0, 750.0, 800.0),
            100: (200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            125: (225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            150: (250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            175: (275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 800.0),
            200: (300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            225: (325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            250: (350.0, 375.0, 400.0, 425.0, 475.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            275: (375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            300: (450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 750.0, 775.0, 800.0),
            325: (425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            350: (450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            375: (475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            400: (500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            425: (525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            450: (550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            475: (575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            500: (600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            525: (625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            550: (650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            575: (675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            600: (700.0, 725.0, 750.0, 775.0, 800.0),
            625: (725.0, 750.0, 775.0, 800.0),
            650: (750.0, 775.0, 800.0),
            675: (775.0, 800.0),
            700: (800.0,)
        }
    elif box == 'Ele':
        stopMassDict = {
            25: (150.0, 175.0, 200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            50: (150.0, 175.0, 200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            75: (175.0, 225.0, 250.0, 300.0, 325.0, 425.0, 475.0, 500.0, 550.0, 575.0, 650.0, 700.0, 750.0, 800.0),
            100: (200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            125: (225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            150: (250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            175: (275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 800.0),
            200: (300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            225: (325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            250: (350.0, 375.0, 400.0, 425.0, 475.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            275: (375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            300: (450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 750.0, 775.0, 800.0),
            325: (425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            350: (450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            375: (475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            400: (500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            425: (525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            450: (550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            475: (575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            500: (600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            525: (625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            550: (650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            575: (675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            600: (700.0, 725.0, 750.0, 775.0, 800.0),
            625: (725.0, 750.0, 775.0, 800.0),
            650: (750.0, 775.0, 800.0),
            675: (775.0, 800.0),
            700: (800.0,)
        }
    elif box == 'BJetHS':
        stopMassDict = {
            50: (150.0, 175.0, 200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            75: (175.0, 225.0, 250.0, 300.0, 325.0, 425.0, 475.0, 500.0, 550.0, 575.0, 650.0, 700.0, 750.0, 800.0),
            100: (200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            25: (150.0, 175.0, 200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            125: (225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            150: (250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            175: (275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 800.0),
            200: (300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            225: (325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            250: (350.0, 375.0, 400.0, 425.0, 475.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            275: (375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            300: (400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            325: (425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            350: (450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            375: (475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            400: (500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            425: (525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            450: (550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            475: (575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            500: (600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            525: (625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            550: (650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            575: (675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            600: (700.0, 725.0, 750.0, 775.0, 800.0),
            625: (725.0, 750.0, 775.0, 800.0),
            650: (750.0, 775.0, 800.0),
            675: (775.0, 800.0),
            700: (800.0,)
        }
    elif box == 'BJetLS':
        stopMassDict = {
            25: (150.0, 175.0, 200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            50: (150.0, 175.0, 200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            75: (175.0, 225.0, 250.0, 300.0, 325.0, 425.0, 475.0, 500.0, 550.0, 575.0, 650.0, 700.0, 750.0, 800.0),
            100: (200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            125: (225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            150: (250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            175: (275.0, 300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 800.0),
            200: (300.0, 325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            225: (325.0, 350.0, 375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            250: (350.0, 375.0, 400.0, 425.0, 475.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            275: (375.0, 400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            300: (400.0, 425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            325: (425.0, 450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            350: (450.0, 475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            375: (475.0, 500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            400: (500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            425: (525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            450: (550.0, 575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            475: (575.0, 600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            500: (600.0, 625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            525: (625.0, 650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            550: (650.0, 675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            575: (675.0, 700.0, 725.0, 750.0, 775.0, 800.0),
            600: (700.0, 725.0, 750.0, 775.0, 800.0),
            625: (725.0, 750.0, 775.0, 800.0),
            650: (750.0, 775.0, 800.0),
            675: (775.0, 800.0),
            700: (800.0,)
        }
    return stopMassDict[neutralinopoint]

def writeBashScript(box,neutralinopoint,gluinopoint,xsecpoint,hypo,t, outputDir):
    nToys = 30 ## instead of 500 for the 2011 hybrid

    if box == 'Mu' or box == 'Ele':
        name = "SMS-T2tt_mStop-Combo_mLSP_0.0_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY_MR350.0_R0.22360679775"
    else : #assume bjetHS or bjetLS
        if neutralinopoint in [50, 100, 150, 200, 300]:
            name = "SMS-T2tt_mStop-Combo_mLSP_" + str(neutralinopoint) + ".0_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY_MR500.0_R0.22360679775"
        else:
            name = "SMS-T2tt_mStop-Combo_mLSP_" + str(neutralinopoint) + ".0_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY_MR500_R0.22360679775"
    massPoint = "%.1f_%.1f"%(gluinopoint, neutralinopoint)

    # prepare the script to run
    xsecstring = str(xsecpoint).replace(".","p")
    outputname = submitDir+"/submit_"+massPoint+"_"+box+"_xsec"+xsecstring+"_"+hypo+"_"+str(t)+".src"
    outputfile = open(outputname,'w')
    
    tagHypo = ""
    if hypo == "B":
        tagHypo = "-e"
        
    ffDir = outputDir+"/logs_"+massPoint+"_"+xsecstring+"_"+hypo
    outputfile.write('#!/usr/bin/env bash -x\n')
    outputfile.write("export WD=/tmp/${USER}/Razor2012_%s_%s_%s_%i\n"%(massPoint,box,xsecstring,t))
    outputfile.write("mkdir -p $WD\n")
    outputfile.write("cd $WD\n")
    outputfile.write("scramv1 project CMSSW CMSSW_6_1_1\n")
    outputfile.write("cd CMSSW_6_1_1/src\n")
    outputfile.write("eval `scramv1 run -sh`\n")

    outputfile.write("export CVSROOT=:gserver:cmssw.cvs.cern.ch:/local/reps/CMSSW\n")
    outputfile.write("cvs co -r wreece_101212_2011_style_fits -d RazorCombinedFit UserCode/wreece/RazorCombinedFit\n")
    outputfile.write("cd RazorCombinedFit\n")
    outputfile.write("mkdir lib\n")
    outputfile.write("source setup.sh\n")
    outputfile.write("source /afs/cern.ch/sw/lcg/external/gcc/4.3.2/x86_64-slc5/setup.sh\n")
    outputfile.write("source /afs/cern.ch/sw/lcg/app/releases/ROOT/5.34.05/x86_64-slc5-gcc43-opt/root/bin/thisroot.sh\n")
    outputfile.write("make\n")
    
    outputfile.write("export NAME=\"T2tt\"\n")
    outputfile.write("export LABEL=\"MR500.0_R0.22360679775\"\n")

    if box == 'had' or box == 'BJetHS' or box == 'BJetLS':
        outputfile.write("cp /afs/cern.ch/user/w/wreece/public/Razor2012/500_0_05/FullRegion/Run2012ABCD_Full_Search-280113.root $PWD\n")
    elif box == 'Ele':
        outputfile.write("cp /afs/cern.ch/user/l/lucieg/public/Razor2012/350_0_05/FitRegion/Run2012ABCD_Fit_Ele-120313.root $PWD\n")
    elif box == 'Mu':
        outputfile.write("cp /afs/cern.ch/user/l/lucieg/public/Razor2012/350_0_05/FitRegion/Run2012ABCD_Fit_Mu-120313.root $PWD\n")
      

    outputfile.write("cp /afs/cern.ch/work/l/lucieg/public/forRazorStop/SMS-T2tt_mStop-Combo_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY/Datasets/mLSP%s.0/%s_%s_%s.root $PWD\n"%(neutralinopoint,name,massPoint,box))
                
    if box == 'had':
        nToyOffset = nToys*(2*t)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Full_Search-280113.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_BJetHS.root %s_%s_BJetLS.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
        nToyOffset = nToys*(2*t+1)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Full_Search-280113.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_BJetHS.root %s_%s_BJetLS.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))

    elif box == 'BJetHS':
        nToyOffset = nToys*(2*t)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Full_Search-280113.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_BJetHS.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
        nToyOffset = nToys*(2*t+1)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Full_Search-280113.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_BJetHS.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))

    elif box == 'BJetLS':
        nToyOffset = nToys*(2*t)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Full_Search-280113.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_BJetLS.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
        nToyOffset = nToys*(2*t+1)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Full_Search-280113.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_BJetLS.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))

    elif box == 'lep':
        nToyOffset = nToys*(2*t)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Had-280113.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_Ele.root %s_%s_Mu.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
        nToyOffset = nToys*(2*t+1)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Had-280113.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_Ele.root %s_%s_Mu.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))

    elif box == 'Ele':
        nToyOffset = nToys*(2*t)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Ele-120313.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_Ele.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
        nToyOffset = nToys*(2*t+1)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Ele-120313.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_Ele.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))

    elif box == 'Mu':
        nToyOffset = nToys*(2*t)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Mu-120313.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_Mu.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
        nToyOffset = nToys*(2*t+1)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Mu-120313.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_Mu.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
        

    # the output directory must be changed
    outputfile.write("cp $WD/CMSSW_6_1_1/src/RazorCombinedFit/*.root %s/\n" %outputDir)
    outputfile.write("rm -rf $WD\n")
    
    outputfile.close

    return outputname,ffDir

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "\nRun the script as follows:\n"
        print "python scripts/runHybridLimits.py Box mLSP OutputTextFile"
        print "with:"
        print "- Box = name of the Box (BJetHS, Mu, etc.)"
        print "- mLSP = LSP mass integer (25, 50, etc.)"
        print "- CompletedOutputTextFile = text file containing all completed output files"
        print ""
        sys.exit()
    box = sys.argv[1]
    neutralinopoint = int(sys.argv[2])
    done = sys.argv[3]

    nJobs = 50
    nToys = 30 # do 60=30+30 toys each job => 3000 toys
    timestamp = str(datetime.date.today())
    print box
    
    gluinopoints = getStopMassPoints(box, neutralinopoint)
    queue = "2nd"
    
    pwd = os.environ['PWD']

    submitDir = "submit"
    outputDir = "/afs/cern.ch/work/s/salvati/private/workspace/RazorStops/ScanHybrid_" + box + "_" + str(neutralinopoint)
    print outputDir
   
    os.system("mkdir -p %s"%(submitDir))
    os.system("mkdir -p %s" %outputDir)
    os.system("ln -s %s" %outputDir)

    hypotheses = ["B","SpB"]

    os.system("touch %s" %done)
    doneFile = open(done)
    outFileList = [outFile.replace(".root\n","") for outFile in doneFile.readlines()]

    # dictionary of src file to output file names
    srcDict = {}
    for i in xrange(0,50):
        srcDict[i] = ["%i-%i"%(2*i*nToys,(2*i+1)*nToys-1), "%i-%i"%((2*i+1)*nToys, (2*i+2)*nToys-1)]

    totalJobs = 0
    missingFiles = 0

    # for neutralinopoint in neutralinopoints:
    for gluinopoint in gluinopoints:
        xsecRange = getXsecRange(box,neutralinopoint,gluinopoint)
        for xsecpoint in xsecRange:
            for hypo in hypotheses:
                for t in xrange(0,nJobs):
                    massPoint = "%.1f_%.1f"%(gluinopoint, neutralinopoint)

                    fileNameToCheck = outputDir + "/Razor2012HybridLimit_T2tt_" + massPoint + "_" + box + "_" + str(xsecpoint).replace(".","p")  + "_" + hypo + "_" + str(t)
                    output0 = fileNameToCheck.replace("B_%i"%t, "B_%s"%srcDict[t][0])
                    output1 = fileNameToCheck.replace("B_%i"%t, "B_%s"%srcDict[t][1])
    
                    runJob = False
                    if output0 not in outFileList:
                        missingFiles += 1
                        print output0
                        runJob = True
                    if output1 not in outFileList:
                        missingFiles += 1
                        runJob = True
                        print output1

                    if not runJob: continue
                    
                    print "Now scanning xsec = %f"%xsecpoint
                    outputname,ffDir = writeBashScript(box,neutralinopoint,gluinopoint,xsecpoint,hypo,t,outputDir)
                    os.system("mkdir -p %s" %ffDir)
                    totalJobs += 1
                    time.sleep(3)
                    os.system("echo bsub -q "+queue+" -o " + ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                    os.system("bsub -q "+queue+" -o " + ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                        
    print "Missing files = ", missingFiles
    print "Total jobs = ", totalJobs
