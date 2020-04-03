#!/usr/bin/python
# -*- coding: utf-8 -*-

####
# Project Daniel
# A Raspberry Pi Arcade Frontend.
#
# Copyright © 2020 Junix (@junixbr)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation; version 2 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
####

import os, sys, time
import subprocess
import logging
from random import randrange
#from moviepy.editor import *

import pygame
from lib import settings
from lib import db
from lib import mame


##
# initialize
##
FPS = 60
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_center = screen.get_rect().center
#screen = pygame.display.set_mode((1020,1080))

# logging
logging.basicConfig(filename='log/daniel.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%m-%y %H:%M:%S')
logging.info('MAIN: Starting engine...')


def drawBar(progress):
    barPosX = 860
    barPosY = 662
    barSizeW = 200
    barSizeH = 20
    borderColor = (255, 255, 255)
    barColor = (0, 128, 0)
    pygame.draw.rect(screen, borderColor, (barPosX, barPosY, barSizeW, barSizeH), 1)
    pygame.draw.rect(screen, barColor, (barPosX + 2, barPosY + 2, (barSizeW - 4) * progress, barSizeH - 4))
    pygame.display.flip()

def total_roms():
    # count number of roms in the directory
    proc = subprocess.Popen('ls %s/*.zip | wc -l' % CONFS[0], shell=True, stdout=subprocess.PIPE)
    total_mame_games = proc.stdout.read()
    return total_mame_games

def collectRomsInfo():
    # intro
    bg_intro = pygame.image.load("resources/background/intro.png")

    # remove old database file
    logging.info('MAIN: removing old database file if exist')
    try:
        database.close()
    except Exception, e:
        logging.info('MAIN: the database is not open')

    try:
        if os.path.isfile('db/daniel.db3'):
            os.remove('db/daniel.db3')
    except Exception, e:
        logging.error('MAIN: error to remove database file: %s' % e.message())

    # create a new database
    database.createDb()
    database.open()
    database.startTransaction()
    total_mame_games = total_roms()

    emulator = mame.Mame()
    logging.info('MAIN: total mame games: %s' % total_mame_games)
    max_a = int(total_mame_games)
    proc = subprocess.Popen(['ls', CONFS[0]], stdout=subprocess.PIPE)
    tmp = proc.stdout.readlines()

    item = 1
    for game in tmp:
        screen.blit(bg_intro, (0, 0))
        drawBar(float(item)/max_a)
        game_xml = emulator.mameExec('-lx -norc %s' % game.split('.')[0])
        game_info = emulator.xmlParse(game_xml)
        if type(game_info) != bool:
            logging.info('MAIN: adding game: %s' % game_info[1])
            sql = """INSERT INTO game (game, description, year, manufacturer, picture, video, status) VALUES (?, ?, ?, ?, ?, ?, ?)"""
            database.insert(sql, [game_info[0], game_info[1], game_info[2], game_info[3], game_info[0] + ".png", game_info[0] + ".mng", 0])
        else:
            logging.info('MAIN: some game information is missing')
        item += 1
    database.commit()

    # play start
    finish_sound = pygame.mixer.Sound("resources/sfx/start.wav")
    finish_sound.play()
    pygame.time.wait(1500)


# settings
global CONFS
CONFS=[]
#CONFS = settings.readConf()
CONFS.append('/mnt/hgfs/Share/Sources/Daniel/mame/roms')

# load game list
database = db.dataBase()
existDb = db.check_db_exist()

if existDb:
    logging.info('MAIN: check if there is a new rom')
    total_mame_games = total_roms()
    data_game, data_game_count = database.queryGame()
    logging.info('MAIN: total roms in the directory: %d' % int(total_mame_games.strip()))
    logging.info('MAIN: total roms in the database: %d' % data_game_count[0])
    if int(total_mame_games) > data_game_count[0]:
        logging.info('MAIN: there is new roms to add')
        collectRomsInfo()
    else:
        library = database.queryLibrary()
else:
    collectRomsInfo()


class ui():
    def __init__(self):        
        # background
        bg = pygame.image.load("resources/background/bg.png")

        # menu
        self.main_menu_cur = 0
        self.scnd_menu_cur = 0
        self.hglt_menu_cur = 0
        self.game_menu_cur = 0

        self.highlight_flag = False
        highlight_timer = 0
        highlight_counter = 0
        self.highlightX = 50
        self.highlightY = 50
        self.game_line = []

        # main loop
        run = True
        while run:
            # background
            screen.blit(bg, (0, 0))

            # HUD
            if self.main_menu_cur != 0:
                highlight_timer += 1
            self.mountHud(highlight_counter)

            # keyboard
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        logging.info('MAIN: quitting...')
                        run = False
                    # main menu
                    elif event.key == pygame.K_RIGHT and self.scnd_menu_cur == 0:
                        self.main_menu_cur += 1
                    elif event.key == pygame.K_LEFT and self.scnd_menu_cur == 0:
                        self.main_menu_cur -= 1

                    # highlight slide
                    elif event.key == pygame.K_RIGHT and self.scnd_menu_cur == 1:
                        self.hglt_menu_cur += 1
                        highlight_counter = None
                    elif event.key == pygame.K_LEFT and self.scnd_menu_cur == 1:
                        self.hglt_menu_cur -= 1
                        highlight_counter = None

                    # game slide
                    elif event.key == pygame.K_RIGHT and self.scnd_menu_cur >= 2:
                        self.game_menu_cur += 1
                    elif event.key == pygame.K_LEFT and self.scnd_menu_cur >= 2:
                        self.game_menu_cur -= 1

                    # slide up and down
                    elif event.key == pygame.K_UP and self.scnd_menu_cur == 2:
                        self.scnd_menu_cur = 1
                        self.highlight_flag = True
                    elif event.key == pygame.K_UP:
                        self.scnd_menu_cur -= 1
                    elif event.key == pygame.K_DOWN and self.scnd_menu_cur == 0:
                        self.scnd_menu_cur = 1
                        self.highlight_flag = True
                    elif event.key == pygame.K_DOWN:
                        self.scnd_menu_cur += 1

                    # run game
                    elif event.key == pygame.K_RETURN:
                        self.runGame(self.currentGameName)

            if self.main_menu_cur > 4:
                self.main_menu_cur = 4
            if self.main_menu_cur < 0:
                self.main_menu_cur = 0
            if self.scnd_menu_cur < 0:
                self.scnd_menu_cur = 0
            if self.hglt_menu_cur > 4:
                self.hglt_menu_cur = 4
            if self.hglt_menu_cur < 0:
                self.hglt_menu_cur = 0
            if self.game_menu_cur > (self.games_per_lin[self.scnd_menu_cur - 2] - 1):
                self.game_menu_cur = (self.games_per_lin[self.scnd_menu_cur - 2] - 1)
            if self.game_menu_cur < 0:
                self.game_menu_cur = 0

            # change highlight
            #print '----------------'
            #print 'main_menu_cur %d' % self.main_menu_cur
            #print 'scnd_menu_cur %d' % self.scnd_menu_cur
            #print 'hglt_menu_cur %d' % self.hglt_menu_cur
            #print 'game_menu_cur %d' % self.game_menu_cur
            
            if highlight_timer >= 100:
                #print highlight_timer, highlight_counter
                highlight_counter = randrange(2)
                highlight_timer = 0

            # update screens
            pygame.display.flip()

        pygame.quit()
        sys.exit(1)

    def printText(self, text, size, x, y, colour=(255,255,255), font=None):
        text_font = pygame.font.Font(font, size)
        text_bitmap = text_font.render(text, True, colour)
        screen.blit(text_bitmap, (x, y) )

    def mountHud(self, highlight_pict=None):
        # main menu
        top_menu = ['Highlights', 'All', 'Favorites', 'Search', 'Settings']
        size = 50
        x = 80
        y = 60
        white = (255,255,255)
        yellow = (252, 202, 3)
        ttfont = 'resources/font/Typo Grotesk Rounded Demo.otf'
        if self.main_menu_cur == 0 and self.scnd_menu_cur == 0:
            # highlights
            if highlight_pict == None:
                highlight_object = self.loadHighlightImage('resources/background/highlight/highlight-%s.png' % self.hglt_menu_cur, 50, 50)
            else:
                highlight_object = self.loadHighlightImage('resources/background/highlight/highlight-%s.png' % highlight_pict, 50, 50)

            # generate game list
            self.generateGameList(True)

            # main menu
            self.printText(top_menu[0], size, 80, y, colour=yellow, font=ttfont)        
            self.printText(top_menu[1], size, 350, y, colour=white, font=ttfont)
            self.printText(top_menu[2], size, 455, y, colour=white, font=ttfont)
            self.printText(top_menu[3], size, 720, y, colour=white, font=ttfont)
            self.printText(top_menu[4], size, 940, y, colour=white, font=ttfont)

        if self.main_menu_cur == 0 and self.scnd_menu_cur == 1:
            # highlights
            highlight_object = self.loadHighlightImage('resources/background/highlight/highlight-%s.png' % self.hglt_menu_cur, self.highlightX, self.highlightY)

            # generate game list
            self.generateGameList(False)

            if self.highlight_flag == True:
                # move highlight image effect
                self.changeHighlightPosition(highlight_object)
                self.highlight_flag = False
            # show slide dots
            if self.hglt_menu_cur == 0:
                self.loadSlideDot(0, cur=True)
                self.loadSlideDot(1)
                self.loadSlideDot(2)
                self.loadSlideDot(3)
                self.loadSlideDot(4)
            elif self.hglt_menu_cur == 1:
                self.loadSlideDot(0)
                self.loadSlideDot(1, cur=True)
                self.loadSlideDot(2)
                self.loadSlideDot(3)
                self.loadSlideDot(4)
            elif self.hglt_menu_cur == 2:
                self.loadSlideDot(0)
                self.loadSlideDot(1)
                self.loadSlideDot(2, cur=True)
                self.loadSlideDot(3)
                self.loadSlideDot(4)
            elif self.hglt_menu_cur == 3:
                self.loadSlideDot(0)
                self.loadSlideDot(1)
                self.loadSlideDot(2)
                self.loadSlideDot(3, cur=True)
                self.loadSlideDot(4)
            elif self.hglt_menu_cur == 4:
                self.loadSlideDot(0)
                self.loadSlideDot(1)
                self.loadSlideDot(2)
                self.loadSlideDot(3)
                self.loadSlideDot(4, cur=True)

            # main menu
            self.printText(top_menu[0], size, 80, y, colour=yellow, font=ttfont)

        elif self.main_menu_cur == 0 and self.scnd_menu_cur > 1:
            # generate game list (with focus)
            self.generateGameList(True, True)

            # zoom game image
            current_line = self.scnd_menu_cur - 2
            current_game = self.game_menu_cur
            current_game_image = self.game_line[current_line][current_game]['game_object']
            current_game_pos_x = self.game_line[current_line][current_game]['game_pos'][0]
            current_game_pos_y = self.game_line[current_line][current_game]['game_pos'][1]
            self.currentGameName = self.game_line[current_line][current_game]['game']

            #print '-------------'
            #print 'self.games_per_lin: %d' % self.games_per_lin[self.scnd_menu_cur - 2]
            #print 'current_line: %d' % current_line
            #print 'current_game: %d' % current_game
            #print 'current_game_Name: %s' % self.game_line[0][current_line]['description']
            #print 'current_game_pos_x: %s' % current_game_pos_x
            #print 'current_game_pos_y: %s' % current_game_pos_y

            self.gameZoom(current_game_image, current_game_pos_x, current_game_pos_y)
            self.gameInfo(self.game_line[current_line][current_game])

        elif self.main_menu_cur == 1:
            self.printText(top_menu[0], size, 80, y, colour=white, font=ttfont)        
            self.printText(top_menu[1], size, 350, y, colour=yellow, font=ttfont)
            self.printText(top_menu[2], size, 455, y, colour=white, font=ttfont)
            self.printText(top_menu[3], size, 720, y, colour=white, font=ttfont)
            self.printText(top_menu[4], size, 940, y, colour=white, font=ttfont)
        elif self.main_menu_cur == 2:
            self.printText(top_menu[0], size, 80, y, colour=white, font=ttfont)        
            self.printText(top_menu[1], size, 350, y, colour=white, font=ttfont)
            self.printText(top_menu[2], size, 455, y, colour=yellow, font=ttfont)
            self.printText(top_menu[3], size, 720, y, colour=white, font=ttfont)
            self.printText(top_menu[4], size, 940, y, colour=white, font=ttfont)
        elif self.main_menu_cur == 3:
            self.printText(top_menu[0], size, 80, y, colour=white, font=ttfont)        
            self.printText(top_menu[1], size, 350, y, colour=white, font=ttfont)
            self.printText(top_menu[2], size, 455, y, colour=white, font=ttfont)
            self.printText(top_menu[3], size, 720, y, colour=yellow, font=ttfont)
            self.printText(top_menu[4], size, 940, y, colour=white, font=ttfont)
        elif self.main_menu_cur == 4:
            self.printText(top_menu[0], size, 80, y, colour=white, font=ttfont)        
            self.printText(top_menu[1], size, 350, y, colour=white, font=ttfont)
            self.printText(top_menu[2], size, 455, y, colour=white, font=ttfont)
            self.printText(top_menu[3], size, 720, y, colour=white, font=ttfont)
            self.printText(top_menu[4], size, 940, y, colour=yellow, font=ttfont)

    def loadSlideDot(self, place, cur=False):
        # load slide dots
        if cur:
            picture = pygame.image.load('resources/sprite/grey_dot.png')
        else:
            picture = pygame.image.load('resources/sprite/white_dot.png')
        if place == 0:
            screen.blit(picture, (60, 600))
        elif place == 1:
            screen.blit(picture, (90, 600))
        elif place == 2:
            screen.blit(picture, (120, 600))
        elif place == 3:
            screen.blit(picture, (150, 600))
        elif place == 4:
            screen.blit(picture, (180, 600))

    def loadHighlightImage(self, image, x, y):
        # load highlight imgage
        try:
            picture = pygame.image.load(image)
            screen.blit(picture, (x, y))
            return picture
        except Exception, e:
            logging.error('MAIN: %s' % e)
            picture = pygame.image.load('resources/background/highlight/highlight_no_image.png')
            screen.blit(picture, (x, y))
            return picture

    def changeHighlightPosition(self, highlight_object):
        for y_pos in range(1,4):
            screen.blit(highlight_object,(50,50 - y_pos))
        self.highlightX = 50
        self.highlightY = y_pos

    def loadHighlightVideo(self, video):
        # load highlight video
        pass

    def generateLibaryList(self):
        # get the list of library
        library_db = database.queryLibrary()
        return library_db

    def generateGameList(self, is_first, is_focus=False):
        size = 20
        white = (255,255,255)
        yellow = (252, 202, 3)
        ttfont = 'resources/font/Typo Grotesk Rounded Demo.otf'
        col = 64
        if is_focus:
            lin = 400
            title_lin = 70
        elif is_first:
            lin = 600
            title_lin = 40
        else:
            lin = 700
            title_lin = 40

        # game list is exist
        if self.game_line:
            for lib in self.filtered_library: 
                self.printText(lib[1], size, col, lin - title_lin, colour=white, font=ttfont)
                for item in self.game_line[lib[0]-1]:
                    if item['libraryname'] == lib[1]:
                        game_item, game_rect = self.loadGameImage('mame/snap/%s' % item['picture'], col, lin)
                        col += 310
                lin += 250
                col = 64
        else:
            # generate a game list of library
            self.library = self.generateLibaryList()
            self.filtered_library = []
            self.games = []
            game = {}
            self.games_per_lin = []
            self.games_per_lin = range(len(self.library))
            for lib in self.library:
                data_game = database.queryOrganicGames(lib[0])
                if len(data_game[0]) > 0:
                    self.games_per_lin[lib[0]-1] = len(data_game[0])
                    self.printText(lib[1], size, col, lin - title_lin, colour=white, font=ttfont)
                    for item in data_game[0]:
                        game_item, game_rect = self.loadGameImage('mame/snap/%s' % item[5], col, lin)
                        game = {'id': item[0], 'game': item[1], 'description': item[2], 'year': item[3], 
                                    'manufacturer': item[4], 'picture': item[5], 'video': item[6], 
                                    'lastplayed': item[7], 'playcount': item[8], 'rating': item[9], 
                                    'status': item[10], 'libraryname': item[11], 'game_object': game_item, 
                                    'game_pos': game_rect}
                        col += 310
                        self.games.append(game)
                    self.filtered_library.append(lib)
                    self.game_line.append(self.games)
                    self.games = []
                    lin += 250
                    col = 64

    def loadGameImage(self, image, x, y):
        # load game image
        try:
            pygame.draw.rect(screen, (191,191,191), (x-2, y-2, 303, 203), 2)
            picture = pygame.image.load(image)
            big_pic = pygame.transform.scale(picture, (300, 200))
            rect_pic = big_pic.get_rect(topleft=(x, y))
            screen.blit(big_pic, rect_pic)
            return big_pic, rect_pic
        except Exception, e:
            logging.error('MAIN: %s' % e)
            picture = pygame.image.load('resources/sprite/game_no_image.png')
            screen.blit(picture, (x, y))
            return picture

    def gameZoom(self, image, x, y):
        # zooing the game picture
        logging.info('MAIN: zooing the game picture')
        big_pic = pygame.transform.scale(image, (350, 250))
        screen.blit(big_pic,(x - 25, (y - 25) - 200))

    def gameInfo(self, game_info):
        # show game information
        logging.info('MAIN: show game information: %s' % game_info['game'])
        white = (255,255,255)
        ttfont = 'resources/font/Typo Grotesk Rounded Demo.otf'
        self.printText(game_info['description'], 30, 80, 100, colour=white, font=ttfont)
        self.printText('Year: %s ' % game_info['year'], 20, 80, 150, colour=white, font=ttfont)
        self.printText('Publisher: %s ' % game_info['manufacturer'], 20, 80, 180, colour=white, font=ttfont)
        self.printText('Last played: %s ' % game_info['lastplayed'], 20, 80, 210, colour=white, font=ttfont)
        self.printText('Play count: %s ' % game_info['playcount'], 20, 80, 240, colour=white, font=ttfont)
        self.printText('Rating: %s ' % game_info['rating'], 20, 80, 270, colour=white, font=ttfont)

    def loadGameVideo(self, video):
        # load game video
        pass

    def runGame(self, game):
        # load a game
        logging.info('MAIN: running the game: %s' % game)
        pygame.quit()
        emulator = mame.Mame()
        run_game = emulator.mameExec('-rompath %s -skip_gameinfo %s' % (CONFS[0], game))
        emulator.restart()

def main():
    app = ui()

if __name__ == '__main__':
    main()