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

    _pbautojoin = "on"
    _pbautojoinlevel = 100
    _autojoinminlevel = 40
    _nowarnminlevel = 20

    def onStartup(self):
        
        self._adminPlugin = self.console.getPlugin('admin')
        
        if not self._adminPlugin:

            self.error('Could not find admin plugin')
            return False
    
        self._adminPlugin.registerCommand(self, 'pbautojoin',self._pbautojoinlevel, self.cmd_pbautojoin, 'autojoin')
        
        self.registerEvent(b3.events.EVT_CLIENT_TEAM_CHANGE)
        self.registerEvent(b3.events.EVT_GAME_MAP_CHANGE)
        self.registerEvent(b3.events.EVT_GAME_ROUND_START)
   
    def onLoadConfig(self):

        try:
            self._pbautojoin = self.config.get('settings', 'pbautojoin')
        except Exception, err:
            self.warning("Using default value %s for pbautojoin. %s" % (self._pbautojoin, err))
        self.debug('PBAutojoin : %s' % self._pbautojoin)

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

        if self._pbautojoin == 'on':
        
            swaproles = self.console.getCvar('g_swaproles').getInt()
            gametype = self.console.getCvar('g_gametype').getInt()

            if gametype == 0 or gametype == 1:
                return False

            if event.type == b3.events.EVT_GAME_MAP_CHANGE:

                self._test = None

                thread.start_new_thread(self.wait, (30,))

            if event.type == b3.events.EVT_GAME_ROUND_START and swaproles == 1:

                self._test = None

                thread.start_new_thread(self.wait, (10,))     

            if event.type == b3.events.EVT_CLIENT_TEAM_CHANGE:
            
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

        else:
            return False

    def cmd_pbautojoin(self, data, client, cmd=None):
        
        """\
        pbautojoin on/off
        """
        
        if not data:
            
            if self._pbautojoin == 'off':

                message = "^1Off"
            
            if self._pbautojoin == 'on':

                message = "^2On"
            
            client.message('^3PBAutojoin : %s'%(message))
            client.message('!pbautojoin <on / off>')
            return
        
        if data != "on" and data != "off":
            
            client.message('!pbautojoin <on / off>')
            return

        if data == 'off':

            client.message('^3PBAutojoin : ^1Off')
            self._pbautojoin = 'off'

        if data == 'on':

            self._pbautojoin = 'on'
            client.message('^3PBAutojoin : ^2On')

    def wait(self, temps):

        time.sleep(temps)
        self._test = 'ok'
        self.debug('PBAutojoin wait : %s '%(temps))
