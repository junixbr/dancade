##
# utils
##

# logging
import logging
logging.basicConfig(filename='log/dancade.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%m-%y %H:%M:%S')
logging.info('MAIN: Starting engine...')

from cv2 import VideoCapture, CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT
import os, subprocess
import sip

from PyQt5.QtCore import Qt, QCoreApplication, QEvent, QSizeF, QRectF, QUrl
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QLabel, QProgressBar, QFrame, QGraphicsRectItem
from PyQt5.QtGui import QPainter, QPainterPath, QPixmap, QFont, QPen, QBrush, QColor
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem

from lib import db
from lib import mame

# settings
global CONFS
CONFS=[]
#CONFS = settings.readConf()
CONFS.append('../resources/mame/roms')

database = db.dataBase()
existDb = db.check_db_exist()
emulator = mame.Mame()

# main class
class utilsMain():
    def __init__(self, window):
        self.Window = window
        self.widgetMain = self.Window.cwidget


        self.load_game_list()

        self.Scene = myScene(self.Window)
        self.View = QGraphicsView(self.Scene, self.Window)
        sizeScreen = QDesktopWidget().screenGeometry(-1)
        self.View.setGeometry(0, 0, sizeScreen.width(), sizeScreen.height())
        self.View.setStyleSheet("border: 0px")
        self.View.setViewportMargins(-2, -2, -2, -2)
        self.View.setFrameStyle(QFrame.NoFrame)

        # clean first screen
        self.Window.setStyleSheet("")
        self.Window.pbar.setParent(None)

        self.View.show()

    # load game list
    def load_game_list(self):
        logging.info('MAIN: trying to load the game library')
        if existDb:
            logging.info('MAIN: check if there is a new rom')
            total_mame_games = self.total_roms()
            data_game, data_game_count = database.queryGame()
            logging.info('MAIN: total roms in the directory: %d' % int(total_mame_games.strip()))
            logging.info('MAIN: total roms in the database: %d' % data_game_count[0])
            if int(total_mame_games) != data_game_count[0]:
                logging.info('MAIN: there is roms to change')
                self.collectRomsInfo()
            else:
                library = database.queryLibrary()
        else:
            logging.info('MAIN: updating game library database')
            self.collectRomsInfo()

    # total roms
    def total_roms(self):
        # count number of roms in the directory
        proc = subprocess.Popen('ls %s/*.zip | wc -l' % CONFS[0], shell=True, stdout=subprocess.PIPE)
        total_mame_games = proc.stdout.read()
        return total_mame_games

    # check roms
    def collectRomsInfo(self):
        # remove old database file
        logging.info('MAIN: removing old database file if exist')
        try:
            database.close()
        except Exception as e:
            logging.info('MAIN: the database is not open')

        try:
            if os.path.isfile('db/dancade.db3'):
                os.remove('db/dancade.db3')
        except Exception as e:
            logging.error('MAIN: error to remove database file: %s' % e)

        # create a new database
        database.createDb()
        database.open()
        database.startTransaction()
        total_mame_games = self.total_roms()
        logging.info('MAIN: total mame games: %s' % total_mame_games.decode('utf-8').strip())
        max_a = int(total_mame_games)
        proc = subprocess.Popen(['ls %s | grep zip' % CONFS[0]], shell=True, stdout=subprocess.PIPE)
        tmp_games = proc.stdout.readlines()
        progressBar = self.Window.pbar
        progressBar.setRange(1, max_a)
        item = 1
        for game in tmp_games:
            self.Window.drawBar(item)
            self.Window.update()
            QCoreApplication.processEvents()
            game_info = emulator.xmlParse(game.decode('utf-8').strip().split('.')[0])
            if type(game_info) != bool:
                logging.info('MAIN: adding game: %s - %s...' % (game_info[0], game_info[1][:20]))
                sql = """INSERT INTO game (game, description, year, manufacturer, picture, video, status) VALUES (?, ?, ?, ?, ?, ?, ?)"""
                idgame = database.insert(sql, [game_info[0], game_info[1], game_info[2], game_info[3], game_info[0] + ".png", game_info[0] + ".mng", game_info[4]])
            else:
                logging.info('MAIN: some game information is missing')
            item += 1

            # generate categories
            category_info = emulator.getCategory(game.decode('utf-8').strip().split('.')[0])
            if type(category_info) != bool:
                logging.info('MAIN: adding category: %s' % category_info)
                # library name
                idlibname = db.check_library(category_info)
                # library
                sql = """INSERT INTO library (idgame, idlibname) VALUES (?, ?)"""
                database.insert(sql, [idgame, idlibname[0]])
                database.commit()
            else:
                logging.info('MAIN: category is on the database already or information is missing')

class myScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(myScene, self).__init__(parent)
        self.parent = parent

        sizeScreen = QDesktopWidget().screenGeometry(-1)
        self.setSceneRect(QRectF(0, 0, sizeScreen.width(), sizeScreen.height()))
        self.installEventFilter(self)
        
        self.main_menu_cur = 0
        self.scnd_menu_cur = 0
        self.hglt_menu_cur = 0
        self.game_menu_cur = 0
        self.lastKey = None
        self.is_going_up = False
        self.is_going_right = False
        self.game_info_label = []
        self.video_frame = []

        self.topMenu = ['Highlights', 'All', 'Categories', 'Search', 'Settings']
        self.game_line = []
        self.all_category = []

        self.video_item = QGraphicsVideoItem()
        self.addItem(self.video_item)
        self.video_item.setSize(QSizeF(709.33, 532))
        self.video_item.setPos(1192, 0)
        self.video_item.setZValue(2)

        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_item)
        self.media_player.mediaStatusChanged.connect(self.videoStatusChanged)

        # change background
        background_image = QGraphicsPixmapItem()
        background_image.setPixmap(QPixmap('../resources/img/background2.png'))
        self.addItem(background_image)
        background_image.setZValue(-10)

        # mount hud
        self.mountHud()

    # keyboard events
    def eventFilter(self, source, event):
        if source is self and event.type() == QEvent.KeyPress:
            key = event.key()
            # main menu
            if key == Qt.Key_Right and self.scnd_menu_cur == 0:
                self.main_menu_cur += 1
                if self.main_menu_cur > 4:
                    self.main_menu_cur = 4
                self.updateHud()
            elif key == Qt.Key_Left and self.scnd_menu_cur == 0:
                self.main_menu_cur -= 1
                if self.main_menu_cur < 0:
                    self.main_menu_cur = 0
                self.updateHud()

            # highlight slide
            elif key == Qt.Key_Right and self.scnd_menu_cur == 1:
                self.hglt_menu_cur += 1
                self.highlight_counter = None
                if self.hglt_menu_cur > 4:
                    self.hglt_menu_cur = 4
                self.updateHud()
            elif key == Qt.Key_Left and self.scnd_menu_cur == 1:
                self.hglt_menu_cur -= 1
                self.highlight_counter = None
                if self.hglt_menu_cur < 0:
                    self.hglt_menu_cur = 0
                self.updateHud()

            # game slide
            elif key == Qt.Key_Right and self.scnd_menu_cur > 1 and self.game_menu_cur <= self.games_per_lin[self.scnd_menu_cur - 2] - 2:
                self.game_menu_cur += 1
                self.is_going_right = True
                self.lastKey = Qt.Key_Right
                self.updateHud()
            elif key == Qt.Key_Left and self.scnd_menu_cur > 1 and self.game_menu_cur > 0:
                self.game_menu_cur -= 1
                self.is_going_right = False
                self.lastKey = Qt.Key_Left
                self.updateHud()

            # slide up and down
            elif key == Qt.Key_Up and self.scnd_menu_cur == 2:
                self.scnd_menu_cur = 1
                self.is_going_up = True
                self.lastKey = Qt.Key_Up
                self.updateHud()
            elif key == Qt.Key_Up:
                self.scnd_menu_cur -= 1
                self.is_going_up = True
                if self.scnd_menu_cur < 0:
                    self.scnd_menu_cur = 0
                self.lastKey = Qt.Key_Up
                self.updateHud()
            elif key == Qt.Key_Down and self.scnd_menu_cur == 0:
                self.scnd_menu_cur = 1
                self.is_going_up = False
                self.lastKey = Qt.Key_Down
                self.updateHud()
            elif key == Qt.Key_Down and self.scnd_menu_cur < self.total_library + 1:
                self.scnd_menu_cur += 1
                self.is_going_up = False
                self.lastKey = Qt.Key_Down
                self.updateHud()

            # quit frontend
            elif key == Qt.Key_Escape:
                self.parent.close()
                QCoreApplication.quit()
        return super(myScene, self).eventFilter(source, event)

    # create label
    def printLabel(self, text, x, y, size, color):
        label_name = self.addText(text, QFont(self.parent.families[0], size))
        label_name.setPos(x, y)
        label_name.setDefaultTextColor(color)
        return(label_name)

    # update label
    def updateLabel(self, label_object, text, x, y, size, color):
        label_name = label_object
        label_name.setPlainText(text)
        label_name.setDefaultTextColor(color)
        label_name.setPos(x, y)

    # load dots
    def loadSlideDot(self, x, y, cur=False):
        # load slide dots
        picture = QGraphicsPixmapItem()
        if cur:
            picture.setPixmap(QPixmap('../resources/sprite/white_dot.png'))
        else:
            picture.setPixmap(QPixmap('../resources/sprite/grey_dot.png'))
        picture.setPos(x, y)
        self.addItem(picture)
        return picture

    def updateSlideDot(self, dot_object, place, cur=False):
        if cur:
            dot_object.setPixmap(QPixmap('../resources/sprite/white_dot.png'))
        else:
            dot_object.setPixmap(QPixmap('../resources/sprite/grey_dot.png'))

        if place == 0:
            dot_object.setPos(60, 450)
        elif place == 1:
            dot_object.setPos(90, 450)
        elif place == 2:
            dot_object.setPos(120, 450)
        elif place == 3:
            dot_object.setPos(150, 450)
        elif place == 4:
            dot_object.setPos(180, 450)

    # load highlight imgage
    def loadHighlightImage(self, image, x, y):
        logging.info('MAIN: loading highlight image: %s' % image)
        try:
            if os.path.isfile(image):
                picture = QGraphicsPixmapItem()
                picture.setPixmap(QPixmap(image).scaled(1920, 532, Qt.KeepAspectRatio))
                self.addItem(picture)
                picture.setPos(x, y)
                picture.setZValue(-5)
                return picture
            else:
                picture = QGraphicsPixmapItem()
                picture.setPixmap(QPixmap('../resources/img/highlight/highlight_no_image.png').scaled(1920, 532, Qt.KeepAspectRatio))
                self.addItem(picture)
                picture.setPos(x, y)
                picture.setZValue(-5)
                return picture
            picture.setZValue(-5)
        except Exception as e:
            logging.error('MAIN: %s' % e)

    # update highliht image
    def updateHighlightImage(self, highlight_object, image, x, y):
        try:
            if os.path.isfile(image):
                logging.info('MAIN: updating highlight image: %s' % image)
                highlight_object.setPixmap(QPixmap(image))
                return highlight_object
            else:
                highlight_object.setPixmap(QPixmap('../resources/img/highlight/highlight_no_image.png'))
                return highlight_object
        except Exception as e:
            logging.error('MAIN: %s' % e)
            
    # load game images from a line
    def loadGameFrame(self, x, y):
        rect_item = QGraphicsRectItem(QRectF(x - 2, y - 2, 303, 203))
        rect_item.setBrush(QColor(191,191,191))
        self.addItem(rect_item)
        return(rect_item)

    # load any image
    def loadImage(self, image, x, y, z):
        try:
            if os.path.isfile(image):
                picture = QGraphicsPixmapItem()
                picture.setPixmap(QPixmap(image))
                self.addItem(picture)
                picture.setPos(x, y)
                picture.setZValue(z)
                return picture
        except Exception as e:
            logging.error('MAIN: %s' % e)

    # update any image file
    def updateImage(self, image_object, image, x, y, z):
        image_object.setPixmap(QPixmap(image))
        image_object.setPos(x, y)

    # load the game image file
    def loadGamePicture(self, image, x, y):
        logging.info('MAIN: loading the game picture: %s' % image)
        try:
            if os.path.isfile(image):
                picture = QGraphicsPixmapItem()
                picture.setPixmap(QPixmap(image).scaledToHeight(200))
                if picture.boundingRect().width() > 300:
                    picture.setPixmap(QPixmap(image).scaledToWidth(300))
                self.addItem(picture)
                x = x + 150 - (picture.boundingRect().width() / 2)
                picture.setPos(x, y)
                picture.setZValue(1)
                return picture
            else:
                logging.info('MAIN: no game image found: %s' % image)
                picture = QGraphicsPixmapItem()
                picture.setPixmap(QPixmap('../resources/sprite/game_no_image.png').scaledToHeight(200))
                self.addItem(picture)
                x = x + 150 - (picture.boundingRect().width() / 2)
                picture.setPos(x, y)
                picture.setZValue(1)
                return picture
        except Exception as e:
            logging.error('MAIN: %s' % e)

    # update the game image file
    def updateGamePicture(self, game_object, x, y):
        x = x + 150 - (game_object.boundingRect().width() / 2)
        game_object.setPos(x, y)

    # fill game list
    def generateGameList(self):
        size = 22
        white = (255,255,255)
        yellow = (252, 202, 3)
        col = 64
        lin = 530

        # generate a game list of library
        self.library = database.queryLibrary()
        self.library_label = []
        self.total_library = len(self.library)
        self.games = []
        game = {}
        self.games_per_lin = []
        self.games_per_lin = [0 for x in range(len(self.library))]
        glin = 0
        for lib in self.library:
            data_game = database.queryOrganicGames(lib[0])
            if len(data_game) > 0:
                self.games_per_lin[glin] = len(data_game)
                libText = self.printLabel(lib[1], col, lin, size, Qt.lightGray)
                self.library_label.append({'id': lib[0], 'label': libText, 'col': col, 'lin': lin})
                for item in data_game:
                    #QCoreApplication.processEvents()
                    if len(item[2]) > 20:
                        game_label_text = '%s..' % item[2][:20]
                    else:
                        game_label_text = item[2]
                    lbl = self.printLabel(game_label_text, col, lin, 16, Qt.white)
                    col_game_label = col + 150 - lbl.boundingRect().width() / 2
                    lin_game_label = lin + 240
                    self.updateLabel(lbl, game_label_text, col_game_label, lin_game_label, 14, Qt.white)
                    game_item = self.loadGamePicture('../resources/mame/artwork/%s' % item[5], col, lin + 40)
                    game = {'id': item[0], 'game': item[1], 'description': item[2], 'year': item[3],
                                'manufacturer': item[4], 'picture': item[5], 'video': item[6],
                                'lastplayed': item[7], 'playcount': item[8], 'rating': item[9],
                                'status': item[10], 'libraryname': item[11], 'game_object': game_item,
                                'game_pos': [col, lin + 40], 'game_label': lbl, 'game_label_desc': game_label_text, 'col_game_label': col_game_label, 
                                'lin_game_label': lin_game_label}

                    col += 310
                    self.games.append(game)
                self.game_line.append(self.games)
                self.games = []
                lin += 290
                col = 64
                glin += 1

    # show game information
    def gameInfo(self, show, game_info=None):
        size = 22
        if show:
            logging.info('MAIN: show game information: %s' % game_info['game'])
            if not self.game_info_label:
                self.game_info_label.append(self.printLabel(game_info['description'], 80, 100, size, Qt.white))
                self.game_info_label.append(self.printLabel('Year: %s ' % game_info['year'], 80, 150, size, Qt.lightGray))
                self.game_info_label.append(self.printLabel('Publisher: %s ' % game_info['manufacturer'], 80, 180, size, Qt.lightGray))
                self.game_info_label.append(self.printLabel('Last played: %s ' % game_info['lastplayed'], 80, 210, size, Qt.lightGray))
                self.game_info_label.append(self.printLabel('Play count: %s ' % game_info['playcount'], 500, 210, size, Qt.lightGray))
                self.game_info_label.append(self.printLabel('Rating: %s ' % game_info['rating'], 310, 210, size, Qt.lightGray))
            else:
                self.updateLabel(self.game_info_label[0], game_info['description'], 80, 100, size, Qt.white)
                self.updateLabel(self.game_info_label[1], 'Year: %s ' % game_info['year'], 80, 150, size, Qt.lightGray)
                self.updateLabel(self.game_info_label[2], 'Publisher: %s ' % game_info['manufacturer'], 80, 180, size, Qt.lightGray)
                self.updateLabel(self.game_info_label[3], 'Last played: %s ' % game_info['lastplayed'], 80, 210, size, Qt.lightGray)
                self.updateLabel(self.game_info_label[4], 'Play count: %s ' % game_info['playcount'], 500, 210, size, Qt.lightGray)
                self.updateLabel(self.game_info_label[5], 'Rating: %s ' % game_info['rating'], 310, 210, size, Qt.lightGray)
                for i in range(len(self.game_info_label)):
                        self.game_info_label[i].show()
        else:
            for i in range(len(self.game_info_label)):
                self.game_info_label[i].hide()

    # check if video is horizontal or vertical
    def checkVideoOrientation(self, current_game):
        file = os.path.join(os.path.dirname(__file__), "../../resources/mame/snap/%s.mp4" % current_game)
        video = VideoCapture(file)
        width = video.get(CAP_PROP_FRAME_WIDTH)
        height = video.get(CAP_PROP_FRAME_HEIGHT)
        try:
            if not self.video_frame:
                if width >= height:
                    self.video_frame = self.loadImage('../resources/img/highlight/frame_horizontal.png', 1180, 0, 5)
                else:
                    self.video_frame = self.loadImage('../resources/img/highlight/frame_tate.png', 1330, 0, 5)
            else:
                if width >= height:
                    self.updateImage(self.video_frame, '../resources/img/highlight/frame_horizontal.png', 1180, 0, 5)
                else:
                    self.updateImage(self.video_frame,'../resources/img/highlight/frame_tate.png', 1330, 0, 5)
            self.video_frame.show()
        except Exception as e:
            logging.error('MAIN: %s' % e)

    # check end of video playback
    def videoStatusChanged(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.video_frame.hide()

    # play video
    def playVideo(self, current_game):
        logging.info('MAIN: playing %s video' % current_game)
        file = os.path.join(os.path.dirname(__file__), "../../resources/mame/snap/%s.mp4" % current_game)
        try:
            if self.media_player.state() == QMediaPlayer.PlayingState:
                self.media_player.stop()

                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file)))
                self.media_player.play()
            else:
                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file)))
                self.media_player.play()
        except Exception as e:
            logging.error('MAIN: was not possible to play a video: %s' % e)

    # move library and game names
    def moveFirst(self):
        col = 64
        size = 14
        game_count = self.scnd_menu_cur - 2
        for gcol in range(self.games_per_lin[game_count]):
            current_game_image = self.game_line[game_count][gcol]['game_object']
            current_game_pos_x = col
            current_game_pos_y = self.game_line[game_count][gcol]['game_pos'][1]
            current_game_descr = self.game_line[game_count][gcol]['description']

            current_game_label = self.game_line[game_count][gcol]['game_label']
            current_game_label_desc = self.game_line[game_count][gcol]['game_label_desc']
            current_game_label_x = col + 150 - current_game_label.boundingRect().width() / 2
            current_game_label_y = self.game_line[game_count][gcol]['lin_game_label']

            self.updateGamePicture(current_game_image, current_game_pos_x, current_game_pos_y)
            self.game_line[game_count][gcol]['game_pos'][0] = current_game_pos_x

            self.updateLabel(current_game_label, current_game_label_desc, current_game_pos_x, current_game_pos_y, size, Qt.white)
            self.game_line[game_count][gcol]['col_game_label'] = current_game_label_x

            
            col += 310

    def moveVertical(self):
        size = 20

        # image frame
        if self.scnd_menu_cur > 1:
            try:
                self.game_frame.show()
            except Exception as e:
                self.game_frame = self.loadGameFrame(64, 280)
                logging.error("MAIN: %s" % e)
        else:
                self.game_frame.hide()

        # move lib names
        lib_count = 0
        for lib in self.library:
            for lbl in self.library_label:
                if lbl['id'] == lib[0]:
                    if self.is_going_up:
                        # move libs labels
                        if lbl['lin'] + 290 == 240:
                            color = Qt.white
                        else:
                            color = Qt.lightGray

                        current_lib_pos_x = lbl['col']
                        current_lib_pos_y = lbl['lin'] + 290
                        self.updateLabel(lbl['label'], lib[1], current_lib_pos_x, current_lib_pos_y, size, color)
                        self.library_label[lib_count]['lin'] = current_lib_pos_y

                        # move games
                        for gcol in range(self.games_per_lin[lib_count]):
                            current_game_image = self.game_line[lib_count][gcol]['game_object']
                            current_game_pos_x = self.game_line[lib_count][gcol]['game_pos'][0]
                            current_game_pos_y = self.game_line[lib_count][gcol]['game_pos'][1] + 290
                            current_game_label = self.game_line[lib_count][gcol]['game_label']
                            current_game_label_desc = self.game_line[lib_count][gcol]['game_label_desc']
                            current_game_label_x = self.game_line[lib_count][gcol]['col_game_label']
                            current_game_label_y = self.game_line[lib_count][gcol]['lin_game_label'] + 290
                            self.updateGamePicture(current_game_image, current_game_pos_x, current_game_pos_y)
                            self.game_line[lib_count][gcol]['game_pos'][1] = current_game_pos_y
                            self.updateLabel(current_game_label, current_game_label_desc, current_game_label_x, current_game_label_y, 14, color)
                            self.game_line[lib_count][gcol]['lin_game_label'] = current_game_label_y
                    else:
                        # move libs labels
                        if lbl['lin'] - 290 == 240:
                            color = Qt.white
                        else:
                            color = Qt.lightGray
                        current_lib_pos_x = lbl['col']
                        current_lib_pos_y = lbl['lin'] - 290
                        self.updateLabel(lbl['label'], lib[1], current_lib_pos_x, current_lib_pos_y, size, color)
                        self.library_label[lib_count]['lin'] = current_lib_pos_y

                        # move games
                        for gcol in range(self.games_per_lin[lib_count]):
                            current_game_image = self.game_line[lib_count][gcol]['game_object']
                            current_game_pos_x = self.game_line[lib_count][gcol]['game_pos'][0]
                            current_game_pos_y = self.game_line[lib_count][gcol]['game_pos'][1] - 290
                            current_game_label = self.game_line[lib_count][gcol]['game_label']
                            current_game_label_desc = self.game_line[lib_count][gcol]['game_label_desc']
                            current_game_label_x = self.game_line[lib_count][gcol]['col_game_label']
                            current_game_label_y = self.game_line[lib_count][gcol]['lin_game_label'] - 290
                            self.updateGamePicture(current_game_image, current_game_pos_x, current_game_pos_y)
                            self.game_line[lib_count][gcol]['game_pos'][1] = current_game_pos_y
                            self.updateLabel(current_game_label, current_game_label_desc, current_game_label_x, current_game_label_y, 14, color)
                            self.game_line[lib_count][gcol]['lin_game_label'] = current_game_label_y

                    # hide - out of screen
                    if lbl['label'].isVisible() and lbl['lin'] < 300:
                        lbl['label'].hide()
                    elif not lbl['label'].isVisible() and lbl['lin'] >= 300:
                        lbl['label'].show()
                    for gcol in range(self.games_per_lin[lib_count]):
                        current_game_image = self.game_line[lib_count][gcol]['game_object']
                        current_game_label = self.game_line[lib_count][gcol]['game_label']
                        if current_game_image.isVisible() and current_game_pos_y < 270:
                            current_game_image.hide()
                        elif not current_game_image.isVisible() and current_game_pos_y >= 270:
                            current_game_image.show()
                        if current_game_label.isVisible() and current_game_label_y < 470:
                            current_game_label.hide()
                        elif not current_game_label.isVisible() and current_game_label_y >= 470:
                            current_game_label.show()
                    lib_count += 1

    def moveHorizontal(self):
        game_count = self.scnd_menu_cur - 2
        if self.is_going_right:
            for gcol in range(self.games_per_lin[game_count]):
                current_game_image = self.game_line[game_count][gcol]['game_object']
                current_game_pos_x = self.game_line[game_count][gcol]['game_pos'][0] - 310
                current_game_pos_y = self.game_line[game_count][gcol]['game_pos'][1]
                current_game_label = self.game_line[game_count][gcol]['game_label']
                current_game_label_desc = self.game_line[game_count][gcol]['game_label_desc']
                current_game_label_x = self.game_line[game_count][gcol]['col_game_label'] - 310
                current_game_label_y = self.game_line[game_count][gcol]['lin_game_label']
                self.updateGamePicture(current_game_image, current_game_pos_x, current_game_pos_y)
                self.game_line[game_count][gcol]['game_pos'][0] = current_game_pos_x
                self.updateLabel(current_game_label, current_game_label_desc, current_game_label_x, current_game_label_y, 14, Qt.white)
                self.game_line[game_count][gcol]['col_game_label'] = current_game_label_x
        else:
            for gcol in range(self.games_per_lin[game_count]):
                current_game_image = self.game_line[game_count][gcol]['game_object']
                current_game_pos_x = self.game_line[game_count][gcol]['game_pos'][0] + 310
                current_game_pos_y = self.game_line[game_count][gcol]['game_pos'][1]
                current_game_label = self.game_line[game_count][gcol]['game_label']
                current_game_label_desc = self.game_line[game_count][gcol]['game_label_desc']
                current_game_label_x = self.game_line[game_count][gcol]['col_game_label'] + 310
                current_game_label_y = self.game_line[game_count][gcol]['lin_game_label']
                self.updateGamePicture(current_game_image, current_game_pos_x, current_game_pos_y)
                self.game_line[game_count][gcol]['game_pos'][0] = current_game_pos_x
                self.updateLabel(current_game_label, current_game_label_desc, current_game_label_x, current_game_label_y, 14, Qt.white)
                self.game_line[game_count][gcol]['col_game_label'] = current_game_label_x

    # hud
    def mountHud(self):
        size = 28
        y = 10

        # highlights
        self.highlight_object = self.loadHighlightImage('../resources/img/highlight/highlight-%s.png' % self.hglt_menu_cur, 0, 0)

        # game list
        self.generateGameList()

        # main menu
        self.menu_label_0 = self.printLabel(self.topMenu[0], 80, y, size, Qt.yellow)
        self.menu_label_1 = self.printLabel(self.topMenu[1], 350, y, size, Qt.white)
        self.menu_label_2 = self.printLabel(self.topMenu[2], 455, y, size, Qt.white)
        self.menu_label_3 = self.printLabel(self.topMenu[3], 720, y, size, Qt.white)
        self.menu_label_4 = self.printLabel(self.topMenu[4], 940, y, size, Qt.white)

        #slide dots
        self.slideDot0 = self.loadSlideDot(60, 450, True)
        self.slideDot1 = self.loadSlideDot(90, 450)
        self.slideDot2 = self.loadSlideDot(120, 450)
        self.slideDot3 = self.loadSlideDot(150, 450)
        self.slideDot4 = self.loadSlideDot(180, 450)

    # update hud
    def updateHud(self):
        size = 28
        y = 10

        current_line = self.scnd_menu_cur - 2
        current_game = self.game_menu_cur

        if self.main_menu_cur == 0 and self.scnd_menu_cur == 0:
            # main menu
            self.updateLabel(self.menu_label_0, self.topMenu[0], 80, y, size, Qt.yellow)
            self.updateLabel(self.menu_label_1, self.topMenu[1], 350, y, size, Qt.white)
            self.updateLabel(self.menu_label_2, self.topMenu[2], 455, y, size, Qt.white)
            self.updateLabel(self.menu_label_3, self.topMenu[3], 720, y, size, Qt.white)
            self.updateLabel(self.menu_label_4, self.topMenu[4], 940, y, size, Qt.white)

            # hide game info
            self.gameInfo(False)

            # highlights
            highlight_object = self.updateHighlightImage(self.highlight_object, '../resources/img/highlight/highlight-%s.png' % self.hglt_menu_cur, 0, 0)

        if self.main_menu_cur == 0 and self.scnd_menu_cur == 1:
            # hide game info
            self.gameInfo(False)

            # highlights
            highlight_object = self.updateHighlightImage(self.highlight_object, '../resources/img/highlight/highlight-%s.png' % self.hglt_menu_cur, 0, 0)

            # show slide dots
            if self.hglt_menu_cur == 0:
                self.updateSlideDot(self.slideDot0, 0, cur=True)
                self.updateSlideDot(self.slideDot1, 1)
                self.updateSlideDot(self.slideDot2, 2)
                self.updateSlideDot(self.slideDot3, 3)
                self.updateSlideDot(self.slideDot4, 4)
            elif self.hglt_menu_cur == 1:
                self.updateSlideDot(self.slideDot0, 0)
                self.updateSlideDot(self.slideDot1, 1, cur=True)
                self.updateSlideDot(self.slideDot2, 2)
                self.updateSlideDot(self.slideDot3, 3)
                self.updateSlideDot(self.slideDot4, 4)
            elif self.hglt_menu_cur == 2:
                self.updateSlideDot(self.slideDot0, 0)
                self.updateSlideDot(self.slideDot1, 1)
                self.updateSlideDot(self.slideDot2, 2, cur=True)
                self.updateSlideDot(self.slideDot3, 3)
                self.updateSlideDot(self.slideDot4, 4)
            elif self.hglt_menu_cur == 3:
                self.updateSlideDot(self.slideDot0, 0)
                self.updateSlideDot(self.slideDot1, 1)
                self.updateSlideDot(self.slideDot2, 2)
                self.updateSlideDot(self.slideDot3, 3, cur=True)
                self.updateSlideDot(self.slideDot4, 4)
            elif self.hglt_menu_cur == 4:
                self.updateSlideDot(self.slideDot0, 0)
                self.updateSlideDot(self.slideDot1, 1)
                self.updateSlideDot(self.slideDot2, 2)
                self.updateSlideDot(self.slideDot3, 3)
                self.updateSlideDot(self.slideDot4, 4, cur=True)

            # main menu
            self.updateLabel(self.menu_label_0, self.topMenu[0], 80, y, size, Qt.yellow)

            # clean game slide
            if self.is_going_up:
                self.moveVertical()

        elif self.main_menu_cur == 0 and self.scnd_menu_cur > 1:
            if self.lastKey == Qt.Key_Up or self.lastKey == Qt.Key_Down:
                self.game_menu_cur = 0
                self.moveFirst()
                self.moveVertical()
            elif self.lastKey == Qt.Key_Right or self.lastKey == Qt.Key_Left:
                self.moveHorizontal()

            # change highlight
            self.updateHighlightImage(self.highlight_object, '../resources/img/highlight/highlight-info.png', 0, 0)

            # show game info
            self.gameInfo(True, self.game_line[current_line][current_game])
            
            # play video
            self.checkVideoOrientation(self.game_line[current_line][current_game]['game'])
            self.playVideo(self.game_line[current_line][current_game]['game'])
            


        elif self.main_menu_cur == 1:
            self.updateLabel(self.menu_label_0, self.topMenu[0], 80, y, size, Qt.white)
            self.updateLabel(self.menu_label_1, self.topMenu[1], 350, y, size, Qt.yellow)
            self.updateLabel(self.menu_label_2, self.topMenu[2], 455, y, size, Qt.white)
            self.updateLabel(self.menu_label_3, self.topMenu[3], 720, y, size, Qt.white)
            self.updateLabel(self.menu_label_4, self.topMenu[4], 940, y, size, Qt.white)
        elif self.main_menu_cur == 2:
            self.updateLabel(self.menu_label_0, self.topMenu[0], 80, y, size, Qt.white)
            self.updateLabel(self.menu_label_1, self.topMenu[1], 350, y, size, Qt.white)
            self.updateLabel(self.menu_label_2, self.topMenu[2], 455, y, size, Qt.yellow)
            self.updateLabel(self.menu_label_3, self.topMenu[3], 720, y, size, Qt.white)
            self.updateLabel(self.menu_label_4, self.topMenu[4], 940, y, size, Qt.white)
        elif self.main_menu_cur == 3:
            self.updateLabel(self.menu_label_0, self.topMenu[0], 80, y, size, Qt.white)
            self.updateLabel(self.menu_label_1, self.topMenu[1], 350, y, size, Qt.white)
            self.updateLabel(self.menu_label_2, self.topMenu[2], 455, y, size, Qt.white)
            self.updateLabel(self.menu_label_3, self.topMenu[3], 720, y, size, Qt.yellow)
            self.updateLabel(self.menu_label_4, self.topMenu[4], 940, y, size, Qt.white)
        elif self.main_menu_cur == 4:
            self.updateLabel(self.menu_label_0, self.topMenu[0], 80, y, size, Qt.white)
            self.updateLabel(self.menu_label_1, self.topMenu[1], 350, y, size, Qt.white)
            self.updateLabel(self.menu_label_2, self.topMenu[2], 455, y, size, Qt.white)
            self.updateLabel(self.menu_label_3, self.topMenu[3], 720, y, size, Qt.white)
            self.updateLabel(self.menu_label_4, self.topMenu[4], 940, y, size, Qt.yellow)