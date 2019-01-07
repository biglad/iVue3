#
#      Copyright (C) 2012 Tommy Winther
#      http://tommy.winther.nu

#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this Program; see the file LICENSE.txt.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#

import xbmc,xbmcgui,xbmcaddon,os,time
import urllib
import urllib2
import datetime
import config
import shutil
import gui, settings
import utils, base64
import sys
import threading
import re
from shutil import copytree
settings.setUrl()


ADDONID = 'script.ivueguide'
ADDON = xbmcaddon.Addon(ADDONID) 
PACKAGES       = xbmc.translatePath(os.path.join('special://home', 'addons', 'packages'))
FORCE       = xbmc.translatePath(os.path.join('special://home', 'addons', 'script.ivueguide', 'force.py'))
ivue = utils.folder()
skin = ADDON.getSetting('skin')
default = xbmc.translatePath(os.path.join('special://profile', 'addon_data', 'script.ivueguide', 'resources', 'skins', 'Default'))
setSkin = xbmc.translatePath(os.path.join('special://profile', 'addon_data', 'script.ivueguide', 'resources', 'skins', skin))
xmasSkin = xbmc.translatePath(os.path.join('special://profile', 'addon_data', 'script.ivueguide', 'resources', 'skins', 'Christmas'))

SkinFolder = xbmc.translatePath(os.path.join('special://profile', 'addon_data', 'script.ivueguide', 'resources', 'skins'))
iniPath = xbmc.translatePath(os.path.join('special://profile', 'addon_data', 'script.ivueguide', 'addons2.ini')) 
iniFile = xbmc.translatePath(os.path.join('special://profile', 'addon_data', 'script.ivueguide', 'addons.ini'))
catchupFile = xbmc.translatePath(os.path.join('special://profile', 'addon_data', 'script.ivueguide', 'resources', 'catchup.xml'))
catPath = xbmc.translatePath(os.path.join('special://profile', 'addon_data', 'script.ivueguide', 'resources', 'categories'))
ivuecatsFile = xbmc.translatePath(os.path.join(catPath,'iVue.ini'))
customcatsFile = xbmc.translatePath(os.path.join(catPath,'custom.ini'))
addons_index_path = xbmc.translatePath('special://profile/addon_data/plugin.video.IVUEcreator/addons_index.ini')
ivueFile = ivue+'/categories.ini'
ivueINI = ivue+'/addons.ini'
ivueCatchup = ivue+'/catchup.xml'
skinsurl = ivue+'/skins/'
skinfiles = [] 
d = xbmcgui.Dialog()
dp = xbmcgui.DialogProgress()
month = datetime.datetime.now().strftime('%B')
day = datetime.datetime.now().strftime('%m')
interval = int(ADDON.getSetting('creator.interval'))
iVueRepo = xbmc.translatePath('special://home/addons/xbmc.repo.ivueguide')


INTERVAL_ALWAYS = 0
INTERVAL_12 = 1
INTERVAL_24 = 2
INTERVAL_48 = 3
INTERVAL_72 = 4
INTERVAL_96 = 5
INTERVAL_120 = 6
INTERVAL_OFF = 7

if not os.path.exists(PACKAGES):
    os.makedirs(PACKAGES)

if not os.path.exists(catPath):
    os.makedirs(catPath)
#Karls changes
def creator():
    if os.path.exists(iniPath) and os.path.exists(addons_index_path) and not interval == INTERVAL_OFF:
        if interval <> INTERVAL_ALWAYS:
            modTime = datetime.datetime.fromtimestamp(os.path.getmtime(iniPath))
            td = datetime.datetime.now() - modTime
            diff = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10 ** 6) / 10 ** 6
            if ((interval == INTERVAL_12 and diff >= 43200) or
                    (interval == INTERVAL_24 and diff >= 86400) or
                    (interval == INTERVAL_48 and diff >= 172800) or
                    (interval == INTERVAL_72 and diff >= 259200) or
                    (interval == INTERVAL_96 and diff >= 345600) or
                    (interval == INTERVAL_120 and diff >= 432000)):
                xbmc.executebuiltin('RunPlugin(plugin://plugin.video.IVUEcreator/update)')
            else:
                w = gui.TVGuide()
                w.doModal()
                del w
        else:
            xbmc.executebuiltin('RunPlugin(plugin://plugin.video.IVUEcreator/update)')
    else:
        w = gui.TVGuide()
        w.doModal()
        del w

if month != 'December' and ADDON.getSetting('xmas.ignore') != 'false':
    if skin == 'Christmas':
        popup = d.yesno('[COLOR ffff7e14][B]IVUE[/B][/COLOR]', 'TeamiVue would like to wish you a Happy New Year!', 'Would you like to disable the christmas theme?',nolabel='Ignore',yeslabel='Disable')
        if popup:
        	d.ok('Team iVue', ADDON.getSetting('last.skin')+' theme has been successfully set', '', 'Please run iVue again for changes to take affect')
        	ADDON.setSetting('skin', ADDON.getSetting('last.skin'))
        	sys.exit()
    else:
        ADDON.setSetting('xmas.ignore', 'false')

try:
    req = urllib2.Request('http://google.com')
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    urllib2.urlopen(req)
except:
    d.ok('iVue Notice', 'No internet connection', '', 'Please check your network settings and try again')
    sys.exit()

if not os.path.exists(iVueRepo):
    url = 'http://ivuetvguide.com/install/repo.ivueguide-0.0.1.zip'
    zipfile = os.path.join(PACKAGES,"repo.ivueguide-0.0.1.zip") 
    d.ok('iVue Notice', 'iVue repo is not installed', 'You should only install addons from the original source', '')
    dp.create("iVue","Downloading Repo",'')
    urllib.urlretrieve(url,zipfile,lambda nb, bs, fs, url=url: config._pbhook(nb,bs,fs,url,dp))
    config.extract(zipfile, xbmc.translatePath('special://home/addons'))
    xbmc.executebuiltin("XBMC.UpdateLocalAddons()")
    time.sleep(1)
    config.enableRepo()
    time.sleep(1)
    dp.close() 
    d.ok('iVue', 'iVue repo was successfully installed', '', 'Please Run iVue again')
    sys.exit()

try:
    if os.path.exists(FORCE) and os.path.exists(SkinFolder):
        viewskins = config.openURL(skinsurl)
        matchskin =re.compile('<a href="(.*?)">').findall(viewskins)
        for name in matchskin:
            name = re.sub(r'%20', ' ', name)
            name = re.sub(r'.zip', '', name)
            if name in os.listdir(SkinFolder):
                shutil.rmtree(os.path.join(SkinFolder, name))
        url = ivue+'/skins/skins.zip'
        zipfile = os.path.join(PACKAGES,"skins.zip") 
        dp.create("iVue","Downloading latest Skin Pack",'')
        urllib.urlretrieve(url,zipfile,lambda nb, bs, fs, url=url: config._pbhook(nb,bs,fs,url,dp))
        config.extract(zipfile, SkinFolder)
        time.sleep(1)
        os.remove(FORCE)
        ADDON.setSetting('scroll.chan', 'Enabled')
        ADDON.setSetting('font', 'Disabled')
        import reset
        reset.SoftReset()
        dp.close() 
    elif os.path.exists(FORCE) and not os.path.exists(SkinFolder):
        os.remove(FORCE)
except Exception as e:
    xbmc.log('iVue TV Guide --> ' + repr(e),4)
    d.ok('iVue Notice', 'Error Installing Skin Packs', '', repr(e))

try:
    if not os.path.exists(default):
        url = ivue+'/skins/Default.zip'
        zipfile = os.path.join(PACKAGES,"default.zip") 
        dp.create("iVue","Downloading Default Skin",'')
        urllib.urlretrieve(url,zipfile,lambda nb, bs, fs, url=url: config._pbhook(nb,bs,fs,url,dp))
        config.extract(zipfile, SkinFolder)
        ADDON.setSetting('scroll.chan', 'Enabled')
        ADDON.setSetting('font', 'Disabled')
        time.sleep(1)
        dp.close() 
except Exception as e:
    xbmc.log('iVue TV Guide --> ' + repr(e),4)
    d.ok('iVue Notice', 'Error Installing Default Skin', '', repr(e))

try: 
    if not os.path.exists(setSkin):
        try:
            url = ivue+'/skins/%s.zip' %(skin).replace (" ","%20") 
            urllib2.urlopen(url)
            zipfile = os.path.join(PACKAGES,"%s.zip" % skin) 
            dp.create("iVue","Downloading %s" % skin,'')
            urllib.urlretrieve(url,zipfile,lambda nb, bs, fs, url=url: config._pbhook(nb,bs,fs,url,dp))
            config.extract(zipfile, SkinFolder)
            ADDON.setSetting('scroll.chan', 'Enabled')
            ADDON.setSetting('font', 'Disabled')
            time.sleep(1)
            dp.close() 
        except urllib2.HTTPError, e:
            ADDON.setSetting('skin', 'Default')
            ADDON.setSetting('font', 'Disabled')
            ADDON.setSetting('scroll.chan', 'Enabled')
            pass
except Exception as e:
    xbmc.log('iVue TV Guide --> ' + repr(e),4)
    d.ok('iVue Notice', 'Error Installing ' + setSkin, '', repr(e))

try:
    if month == 'December' and int(day) >=05 and ADDON.getSetting('xmas.ignore') != 'true':
	    ADDON.setSetting('last.skin', skin)
	    if not skin == 'Christmas':
		    popup = d.yesno('[COLOR ffff7e14][B]IVUE[/B][/COLOR]', 'TeamiVue would like to wish you a very Merry Christmas.', 'Would you like to enable the christmas theme?',nolabel='Ignore',yeslabel='Enable')
		    if popup:
			    if not os.path.exists(xmasSkin):
			        try:
			            url = ivue+'/skins/Christmas.zip'
			            urllib2.urlopen(url)
			            zipfile = os.path.join(PACKAGES,"Christmas.zip") 
			            dp.create("iVue","Downloading Christmas Skin",'')
			            urllib.urlretrieve(url,zipfile,lambda nb, bs, fs, url=url: config._pbhook(nb,bs,fs,url,dp))
			            config.extract(zipfile, SkinFolder)
			            ADDON.setSetting('scroll.chan', 'Enabled')
			            ADDON.setSetting('font', 'Disabled')
			            ADDON.setSetting('skin', 'Christmas')
			            ADDON.setSetting('xmas.ignore', 'true')
			            time.sleep(1)
			            dp.close()
			            d.ok('Merry Christmas', 'Christmas theme has been successfully set', '', 'Please run iVue again for changes to take affect')
			            sys.exit()
			        except urllib2.HTTPError, e:
			            d.ok('iVue Notice', 'Error Installing Christmas Skin', '', repr(e))
			            pass
			    else:
				    ADDON.setSetting('skin', 'Christmas')
				    ADDON.setSetting('xmas.ignore', 'true')
				    d.ok('Merry Christmas', 'Christmas theme has been successfully set', '', 'Please run iVue again for changes to take affect')
				    sys.exit()
		    else:
				ADDON.setSetting('xmas.ignore', 'true')
except Exception as e:
    xbmc.log('iVue TV Guide --> ' + repr(e),4)
    d.ok('iVue Notice', 'Error Installing Christmas Skin', '', repr(e))


try:
    if not os.path.exists(iniFile) or ADDON.getSetting('ivue.addons.ini') == 'true':
        dp.create("iVue","Downloading addons.ini",'')
        urllib.urlretrieve(ivueINI,iniFile,lambda nb, bs, fs, url=ivueINI: config._pbhook(nb,bs,fs,url,dp))
        dp.close()
except Exception as e:
    xbmc.log('iVue TV Guide --> ' + repr(e),4)
    d.ok('iVue Notice', 'Error Installing addon.ini file', '', repr(e))

try:
    if not os.path.exists(catchupFile) or ADDON.getSetting('ivue.addons.ini') == 'true':
        dp.create("iVue","Downloading catchup.xml",'')
        urllib.urlretrieve(ivueCatchup,catchupFile,lambda nb, bs, fs, url=ivueCatchup: config._pbhook(nb,bs,fs,url,dp))
        dp.close()
except Exception as e:
    xbmc.log('iVue TV Guide --> ' + repr(e),4)
    d.ok('iVue Notice', 'Error Installing catchup file', '', repr(e))

try:
    if not os.path.exists(ivuecatsFile) or ADDON.getSetting('ivue.addons.ini') == 'true':
        dp.create("iVue","Downloading categories file",'')
        urllib.urlretrieve(ivueFile,ivuecatsFile,lambda nb, bs, fs, url=ivueFile: config._pbhook(nb,bs,fs,url,dp))
        dp.close()
except Exception as e:
    xbmc.log('iVue TV Guide --> ' + repr(e),4)
    d.ok('iVue Notice', 'Error Installing category file', '', repr(e))
    

try:
    if ADDON.getSetting('categories.ini.enabled') == 'true':
        if ADDON.getSetting('categories.ini.type') == '0':
            if not ADDON.getSetting('categories.ini.file') == '':
                customFile = str(ADDON.getSetting('categories.ini.file'))
                shutil.copy(customFile, customcatsFile)
                ADDON.setSetting('categories.ini.enabled', 'false')
        else:
            customURL = str(ADDON.getSetting('categories.ini.url')) 
            urllib.urlretrieve(customURL, customcatsFile)
            ADDON.setSetting('categories.ini.enabled', 'false')
except:
    pass

    
#End of Karls changes

#addons ini fix start

# set filepath
addons_data_ini_path = xbmc.translatePath('special://profile/addon_data/plugin.video.IVUEcreator/addons_index.ini')
old_ini_path = xbmc.translatePath('special://home/addons/plugin.video.IVUEcreator/addons_index.ini')

if os.path.exists(old_ini_path):
    shutil.move(old_ini_path, addons_data_ini_path)
#addons ini end

if ADDON.getSetting('ivue.addons.ini') == 'true':
    ADDON.setSetting('ivue.addons.ini', 'false')
try:
	runType = len(sys.argv)    
	if interval == INTERVAL_OFF:	        
	    w = gui.TVGuide()
	    w.doModal()
	    del w
	elif not interval == INTERVAL_OFF and runType == 1:
	    creator()
	elif not interval == INTERVAL_OFF and runType > 1:
	    w = gui.TVGuide()
	    w.doModal()
	    del w


except urllib2.HTTPError, e:
		utils.notify(addon_id, e)
