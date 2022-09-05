##
# mame
##

import os, sys
import shlex, subprocess
import xml.etree.ElementTree as ET
import _pickle as cPickle
import json

from lib import utils
from lib import db

# categories
with open("../resources/mame/data.pkl", "rb") as input_file:
    data = cPickle.load(input_file)
input_file.close()

class Mame():
    # mame executable
    def mameExec(self, binnary, parameter):
        which_bin = subprocess.Popen(['/usr/bin/which', binnary], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (which_stdout, which_stderr) = which_bin.communicate()
        if len(which_stdout) > 0:
            utils.logging.info('MAME: binary path: %s' % which_stdout.decode('utf-8').strip())
            mamebin = which_stdout.decode('utf-8').strip()
        elif len(which_stderr) > 0:
            utils.logging.error('MAME: %s' % which_stderr.decode('utf-8').strip())
        else:
            utils.logging.error('MAME: there is no mame binary file')
            sys.stderr.write('ERROR - MAME: there is no mame binary file')
            sys.exit(1)
        utils.logging.info('MAME: executing mame command: %s %s' % (mamebin, parameter))
        command = subprocess.Popen(shlex.split('%s %s' % (mamebin, parameter)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (standardout, standarderr) = command.communicate()
        '''if len(standardout) > 0 and len(standardout) < 255:
            utils.logging.info('MAME: %s' % standardout.decode('utf-8').strip())
        elif len(standarderr) > 0:
            utils.logging.error('MAME: %s' % standarderr.decode('utf-8').strip())'''
        return standardout.decode('utf-8').strip()

    def restart(self, *extra_args):
        python = sys.executable
        args = [sys.argv[0]]
        for arg in extra_args:
            args.append(str(arg))
        os.execl(python, python, *args)

    def getNodetext(self, elem, node_name, default_value=None):
        node = elem.find(node_name)
        if node == None:
            return default_value
        return node.text

    def xmlParse(self, game):
        utils.logging.info('MAME: generating xml information: %s' % game)
        listxml = self.mameExec('mame', '%s -listxml' % game)
        tree = ET.fromstring(listxml)
        utils.logging.info('MAME: parsing xml information: %s' % game)
        for game_node in tree.findall('.//machine[@name="%s"]' % game):
            name = game_node.attrib.get("name", None)
            description = self.getNodetext(game_node,"description", "")
            year = self.getNodetext(game_node,"year", "")
            manufacturer = self.getNodetext(game_node,"manufacturer", "")
        utils.logging.info('MAME: checking if the rom file is good')
        romgood = self.mameExec('mame', '%s -verifyroms' % game)
        if '1 were OK' in romgood:
            game_info = [name, description, year, manufacturer, 1]
        else:
            game_info = [name, description, year, manufacturer, 0]
        return game_info

    def getCategory(self, game):
        js_data = json.loads(data)
        for key, value in js_data['Category'].items():
            if key == game:
                libname = value
                return(libname)