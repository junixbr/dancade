##
# database
##

import os, sys
import logging
import sqlite3 as lite

# logging
logging.basicConfig(filename='log/daniel.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%m-%y %H:%M:%S')

# database
class dataBase():
    def open(self):
        try:
            self.conn = lite.connect('db/daniel.db3')
        except lite.Error, e:
            logging.error('%s:' % e.args[0])
            sys.exit(1)
        return self.conn

    def startTransaction(self):
        self.cur = self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def insert(self, sql, values):
        self.cur.execute(sql, values)

    def close(self):
        self.conn.close()

    def createDb(self):
        conn = self.open()
        with conn:
            # create a library of games table
            logging.info('DB: creating a library of games table')
            cur_libname = conn.cursor()
            cur_libname.execute('''CREATE TABLE libraryname (
                                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                                    name TEXT
                                )''')
            cur_libname.execute('INSERT INTO libraryname (name) VALUES ("Recently Played")')
            cur_libname.execute('INSERT INTO libraryname (name) VALUES ("Top Rated")')
            cur_libname.execute('INSERT INTO libraryname (name) VALUES("Action")')
            cur_libname.execute('INSERT INTO libraryname (name) VALUES("Shooter")')
            cur_libname.execute('INSERT INTO libraryname (name) VALUES("Fighting")')
            cur_libname.execute('INSERT INTO libraryname (name) VALUES("Beat-em up")')
            cur_libname.execute('INSERT INTO libraryname (name) VALUES("Platformer")')
            cur_libname.execute('INSERT INTO libraryname (name) VALUES("Shmup")')
            cur_libname.execute('INSERT INTO libraryname (name) VALUES("Adventure")')
            cur_libname.execute('INSERT INTO libraryname (name) VALUES("Role-Playing")')
            cur_libname.execute('INSERT INTO libraryname (name) VALUES("Hack and slash")')
            cur_libname.execute('INSERT INTO libraryname (name) VALUES("Run and gun")')
            cur_libname.execute('INSERT INTO libraryname (name) VALUES("Simulation")')
            cur_libname.execute('INSERT INTO libraryname (name) VALUES("Strategy")')
            cur_libname.execute('INSERT INTO libraryname (name) VALUES("Sports")')
            cur_libname.execute('INSERT INTO libraryname (name) VALUES("Racing")')
            cur_libname.execute('INSERT INTO libraryname (name) VALUES("Puzzle")')
            cur_libname.execute('INSERT INTO libraryname (name) VALUES("Educational")')
            cur_libname.execute('INSERT INTO libraryname (name) VALUES("Not Related")')

            cur_libgame = conn.cursor()
            cur_libgame.execute('''CREATE TABLE library (
                                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                                    idgame INTEGER,
                                    idlibname INTEGER,
                                    FOREIGN KEY(idgame) REFERENCES game(id),
                                    FOREIGN KEY(idlibname) REFERENCES libraryname(id)
                                )''')
            # Create a games list table
            logging.info('DB: creating a games list table')
            cur_game = conn.cursor()
            cur_game.execute('''CREATE TABLE game ( \
                                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                                game TEXT,
                                description TEXT,
                                year TEXT,
                                manufacturer TEXT,
                                picture TEXT,
                                video TEXT,
                                lastplayed TEXT,
                                playcount INTEGER,
                                rating INTEGER,
                                status INTEGER
                            )''')
            conn.commit()
        self.close()

    def queryLibrary(self):
        # Generate a library
        #logging.info('DB: generating a library of games')
        conn = self.open()
        cur_lib = conn.cursor()
        cur_lib.execute("SELECT * FROM libraryname")
        data_lib = cur_lib.fetchall()
        conn.close()
        return data_lib

    def queryGame(self):
        # Generate a games list
        logging.info('DB: generating a simple list of games')
        conn = self.open()
        cur_game = conn.cursor()
        cur_game.execute("SELECT * FROM game ORDER BY 'description'")
        data_game = cur_game.fetchall()
        cur_game.execute("SELECT COUNT(*) FROM game")
        data_game_count = cur_game.fetchone()
        conn.close()
        return data_game, data_game_count

    def queryOrganicGames(self, library, order_by='libraryname.name'):
        # Generate a games list
        #logging.info('DB: generating an organic list of games')
        conn = self.open()
        cur_game = conn.cursor()
        cur_game.execute('''SELECT game.id, game.game, game.description, game.year, game.manufacturer, 
                                game.picture, game.video, game.lastplayed, game.playcount, 
                                game.rating, game.status, libraryname.name 
                            FROM game 
                                INNER JOIN library
                                    ON game.id = library.idgame 
                                INNER JOIN libraryname 
                                    ON library.idlibname = libraryname.id
                            WHERE library.idlibname = %s 
                            ORDER BY %s''' % (library, order_by))

        data_game = cur_game.fetchall()
        conn.close()
        return data_game, 


# checks
def check_db_exist():
    if not os.path.isfile('db/daniel.db3'):
        logging.info('DB: Daniel needs to update the game database from mame')
        return False
    else:
        db = dataBase()
        data_game, game_count = db.queryGame()
        logging.info('DB: game counted: %d' % game_count)
        if game_count > 0:
            logging.info('DB: database Daniel exists.')
            return True
        else:
            logging.info('DB: Daniel needs to update the game database from mame')
            return False

