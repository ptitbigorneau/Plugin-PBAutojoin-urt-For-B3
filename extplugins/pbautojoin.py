# PBAutojoin Plugin b3 for UrT

__author__  = 'PtitBigorneau www.ptitbigorneau.fr'
__version__ = '1.2'

import b3, time, threading, thread
import b3.plugin
import b3.events
from b3 import clients
    
class PbautojoinPlugin(b3.plugin.Plugin):
    
    _adminPlugin = None
    _test = 'ok'
    _cronTab = None

    _pbautojoinlevel = 100
    _autojoinminlevel = 40
    _nowarnminlevel = 20

    def onStartup(self):
        
        self._adminPlugin = self.console.getPlugin('admin')
        
        if not self._adminPlugin:

            self.error('Could not find admin plugin')
            return False
    
        self.registerEvent(b3.events.EVT_CLIENT_TEAM_CHANGE)
        self.registerEvent(b3.events.EVT_GAME_MAP_CHANGE)
        self.registerEvent(b3.events.EVT_GAME_ROUND_START)
   
    def onLoadConfig(self):

        try:
            self._pbautojoinlevel = self.config.getint('settings', 'pbautojoinlevel')
        except Exception, err:
            self.warning("Using default value %s for pbautojoinlevel. %s" % (self._pbautojoinlevel, err))
        self.debug('pbautojoinlevel : %s' % self._pbautojoinlevel)

        try:
            self._autojoinminlevel = self.config.getint('settings', 'autojoinminlevel')
        except Exception, err:
            self.warning("Using default value %s for autojoinminlevel. %s" % (self._autojoinminlevel, err))
        self.debug('autojoinminlevel : %s' % self._autojoinminlevel)
    
        try:
            self._nowarnminlevel = self.config.getint('settings', 'nowarnminlevel')
        except Exception, err:
            self.warning("Using default value %s for nowarnminlevel. %s" % (self._nowarnminlevel, err))
        self.debug('nowarnminlevel : %s' % self._nowarnminlevel)

    def onEvent(self, event):

        if event.type == b3.events.EVT_GAME_MAP_CHANGE:

            swaproles = self.console.getCvar('g_swaproles').getInt()
            gametype = self.console.getCvar('g_gametype').getInt()

            if gametype == 0 or gametype == 1 or gametype == 9:
                return False            

            self._test = None

            thread.start_new_thread(self.wait, (30,))

        if event.type == b3.events.EVT_GAME_ROUND_START:

            swaproles = self.console.getCvar('g_swaproles').getInt()
            gametype = self.console.getCvar('g_gametype').getInt()
			
            if gametype == 0 or gametype == 1 or gametype == 9:
                return False        

            if swaproles == 1:

                self._test = None

                thread.start_new_thread(self.wait, (10,))     

        if event.type == b3.events.EVT_CLIENT_TEAM_CHANGE:
        
            swaproles = self.console.getCvar('g_swaproles').getInt()
            gametype = self.console.getCvar('g_gametype').getInt()

            if gametype == 0 or gametype == 1 or gametype == 9:
                return False
        
            sclient = event.client
            sclientteam = sclient.team
            
            if sclient.guid[:3] == 'BOT':
                return False

            if self._test == None:
                return False

            if sclient.maxLevel >= self._autojoinminlevel:
                return False

            if self._pbautojoin == 'on':

                scores = self.console.getTeamScores()
                redscore = scores[0]
                bluescore = scores[1]
                teamred = 0
                teamblue = 0
                oldteamred = 0
                oldteamblue = 0

                if sclientteam not in (2, 3):
                    return
                
                for x in self.console.clients.getList():
                    if x.team == 2:
                        teamred +=1
                    if x.team == 3:
                        teamblue +=1
                    
                if sclientteam == 2:

                    oldteamred = teamred - 1
                    oldteamblue = teamblue

                if sclientteam == 3:

                    oldteamred = teamred
                    oldteamblue = teamblue - 1

                if gametype != 0:

                    if oldteamred == oldteamblue:
                        
                        if int(redscore) == int(bluescore):
                            
                            if gametype != 8:
                                team = 0

                            if gametype == 8:
                                team = 3

                        if int(redscore) > int(bluescore):
                            team = 3
                        if int(redscore) < int(bluescore):
                            team = 2

                    if oldteamred > oldteamblue:
                        team = 3
            
                    if oldteamred < oldteamblue:
                        team = 2

                    if team != 0 and sclientteam != team:

                        if team == 2:
                            dteam = 'red'
                        if team == 3:
                            dteam = 'blue'

                        self.console.write('forceteam %s %s' %(sclient.cid, dteam))
                        self.console.say('%s ^3Change Team No Respect Autojoin'%(sclient.exactName))
                        self.debug('PBAutojoin change team : %s %s - red %s %s - blue %s %s'%(sclient.name, sclientteam, oldteamred, redscore, oldteamblue, bluescore))
                       
                        if oldteamred != 0 or oldteamblue != 0:
                                          
                            if sclient.maxLevel < self._nowarnminlevel: 
                                self._adminPlugin.warnClient(sclient, '^3No Respect Autojoin', None, False, '', 60)
                                self.debug('PBAutojoin warn : %s %s - red %s %s - blue %s %s'%(sclient.name, sclientteam, oldteamred, redscore, oldteamblue, bluescore))

    def wait(self, temps):

        time.sleep(temps)
        self._test = 'ok'
        self.debug('PBAutojoin wait : %s '%(temps))
