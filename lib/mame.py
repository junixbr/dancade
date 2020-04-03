##
# mame
##

import os, sys
import shlex, subprocess
import logging
from xml.dom import minidom

# logging
logging.basicConfig(filename='log/daniel.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%m-%y %H:%M:%S')

class Mame():
    def mameExec(self, parameter):
        mamebin = os.popen("/usr/bin/which mame").read()
        if not mamebin:
            logging.error('MAME: there is no mame binary file')
            sys.exit(1)
        logging.info('MAME: executing mame command: %s %s' % (mamebin.strip(), parameter))
        command = subprocess.Popen(shlex.split('%s %s' % (mamebin.strip(), parameter)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (standardout, standarderr) = command.communicate()
        if len(standardout) > 0 and len(standardout) < 255:
            logging.info('MAME: %s' % standardout.strip())
        elif len(standarderr) > 0:
            logging.error('MAME: %s' % standarderr.strip())
        return standardout


    def restart(self, *extra_args):
        python = sys.executable
        args = [sys.argv[0]]
        for arg in extra_args:
            args.append(str(arg))
        os.execl(python, python, *args)

    '''def populateLibrary(self, trLibraries):
        # populate category
        trLibraries.clear()
        querylib = dataBase().queryLibrary()
        for l in querylib:
            item = QtGui.QTreeWidgetItem(trLibraries)
            item.setText(0, l[1])
    '''

    def getChildrenByTitle(self, node, title):
        for child in node.childNodes:
            if child.localName==title:
                yield child

    def xmlParse(self, game_xml):
        try:
            xmldoc = minidom.parseString(game_xml)
        except Exception, e:
            logging.error('MAME: xml parser error: %s' % e)
            return False
        machine = xmldoc.getElementsByTagName('machine')
        name = machine[0].attributes['name'].value
        for node in machine:
            desc = self.getChildrenByTitle(node, 'description')
            yrgm = self.getChildrenByTitle(node, 'year')
            mnfc = self.getChildrenByTitle(node, 'manufacturer')
            for a in desc:
                description = a.childNodes[0].nodeValue
            for a in yrgm:
                year = a.childNodes[0].nodeValue
            for a in mnfc:
                manufacturer = a.childNodes[0].nodeValue
            break
        game_info = [name, description, year, manufacturer]
        return game_info