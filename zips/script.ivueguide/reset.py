import time
import os, shutil
import xbmc
import xbmcgui
import xbmcaddon
import sqlite3

databasePath = xbmc.translatePath('special://profile/addon_data/script.ivueguide')
subPath = xbmc.translatePath('special://profile/addon_data/script.ivueguide/resources/ini')
pyPath = xbmc.translatePath('special://profile/addon_data/script.ivueguide/resources/subs')
setupPath = xbmc.translatePath('special://profile/addon_data/script.ivueguide/resources/guide_setups')
fullPath = xbmc.translatePath('special://profile/addon_data/script.ivueguide')
dialog = xbmcgui.Dialog()

def SoftReset():	
    clearFiles = ["guides.ini", "addons.ini", "program.db","program_category.ini", "categories.ini"]
    keepFiles = ["settings.xml"]
    for root, dirs, files in os.walk(databasePath,topdown=True):
	    dirs[:] = [d for d in dirs if d not in ['skins']]
	    for name in files:
		    if name.endswith(".xml") and name not in keepFiles:
			    try:
				    os.remove(os.path.join(root,name))
			    except:
				    dialog.ok('Soft Reset', 'Error Removing ' + str(name),'','[COLOR yellow]Thank you for using Soft Reset[/COLOR]')
				    pass
		    elif name in clearFiles:
			    try:
				    os.remove(os.path.join(root,name))
			    except:
				    dialog.ok('Soft Reset', 'Error Removing ' + str(name),'','[COLOR yellow]Thank you for using Soft Reset[/COLOR]')
				    pass
		    else:
			    continue
    dialog.ok('Ivue guide Soft reset', 'Please restart for ','the changes to take effect','[COLOR yellow]Thank you for using Soft Reset[/COLOR]')


def HardReset():
    try:
	    shutil.rmtree(fullPath,ignore_errors=True, onerror=None)
	    if not os.path.exists(fullPath):
		    dialog.ok('Ivue guide Hard reset', 'Please restart for ','the changes to take effect','[COLOR yellow]Thank you for using Hard Reset[/COLOR]')
	    else:
		    dialog.ok('Ivue guide Hard reset', 'Failed to remove some files','[COLOR yellow]Please try again[/COLOR]')
    except:				   
	    dialog.ok('Ivue guide Hard reset', 'Failed to remove some files','[COLOR yellow]Please try again[/COLOR]')



def addons2():			
    for root, dirs, files in os.walk(databasePath,topdown=True):
	    dirs[:] = [d for d in dirs]
	    for name in files:
		    if "addons2.ini" in name:
			    try:
				    os.remove(os.path.join(root,name))
				    if not os.path.exists(os.path.join(root,name)):
				        dialog.ok('iVue %s Reset' % name, 'Please restart for ','the changes to take effect','[COLOR yellow]Thank you for using iVue Reset[/COLOR]')     
			    except:				   
				    dialog.ok('iVue %s Reset' % name, 'Error Removing ' + str(name),'','[COLOR yellow]Thank you for using iVue Reset[/COLOR]')



def purgeDB():			
    for root, dirs, files in os.walk(databasePath,topdown=True):
	    dirs[:] = [d for d in dirs]
	    for name in files:
		    if "master.db" in name:
			    try:
				    os.remove(os.path.join(root,name))
				    if not os.path.exists(os.path.join(root,name)):
				        dialog.ok('iVue %s Reset' % name, 'Please restart for ','the changes to take effect','[COLOR yellow]Thank you for using iVue Reset[/COLOR]')             
			    except:				   
				    dialog.ok('iVue %s Reset' % name, 'Error Removing ' + str(name),'','[COLOR yellow]Thank you for using iVue Reset[/COLOR]')

def WipeSetups():
    try:
	    shutil.rmtree(setupPath,ignore_errors=True, onerror=None)
	    if not os.path.exists(setupPath):
		    dialog.ok('iVue Guide Setup Reset', 'Please restart for ','the changes to take effect','[COLOR yellow]Thank you for using iVue Reset[/COLOR]')     
    except:				   
	    dialog.ok('iVue Guide Reset', 'Error Removing XML Setups','','[COLOR yellow]Thank you for using iVue Reset[/COLOR]')

def refreshthumbs():
	conn = sqlite3.connect(xbmc.translatePath("special://database/Textures13.db"))
	try:
		with conn:
			list = conn.execute("SELECT id, cachedurl FROM texture WHERE url LIKE '%%%s%%';" % ".githubusercontent.com/totaltec2014")
			for row in list:
				conn.execute("DELETE FROM sizes WHERE idtexture LIKE '%s';" % row[0])
				try: os.remove(xbmc.translatePath("special://thumbnails/" + row[1]))
				except: pass
			conn.execute("DELETE FROM texture WHERE url LIKE '%%%s%%';" % ".githubusercontent.com/totaltec2014")
			xbmc.sleep(2000)
			dialog.ok('Logo refresh complete!', 'iVue Channel logos cleared...', 'Run iVue TV Guide to receive latest channel logos.')
	except:
		pass

def refreshchannames(silent=False):
	conn = sqlite3.connect(xbmc.translatePath("special://home/userdata/addon_data/script.ivueguide/master.db"))
	try:
		with conn:
			conn.execute('DELETE FROM channels WHERE source=?', ['xmltv'])
			conn.execute('DELETE FROM programs WHERE source=?', ['xmltv'])
			conn.execute('UPDATE sources SET channels_updated=? WHERE id=?', [0, 'xmltv'])
			conn.execute("DELETE FROM updates WHERE source=?", ['xmltv'])
			xbmc.sleep(1000)
			if not silent: dialog.ok('Name refresh complete!', 'iVue channel names cleared...', 'Run iVue TV Guide to receive latest channel names.')
	except:
		pass
		
prnum=""
try:
    prnum= sys.argv[ 1 ]
except:
    pass

if prnum == 'soft':
    SoftReset()
 
elif prnum == 'hard':
    HardReset()

elif prnum == 'addons2':
    addons2()

elif prnum == 'purge':
    purgeDB()

elif prnum == 'setups':
    WipeSetups()

elif prnum == 'refreshthumbs':
	refreshthumbs()	
	
elif prnum == 'refreshchannames':
	refreshchannames()	