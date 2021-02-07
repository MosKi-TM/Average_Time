from pyplanet.apps.contrib.admin.server import ServerAdmin
from pyplanet.apps.core.maniaplanet.callbacks.player import player_chat
from pyplanet.contrib.command import Command
import mysql.connector
from pyplanet.conf import settings


class Tac( ServerAdmin ):

	def __init__( self, app ):
		super().__init__( app ) 
		self.context = app.context
		self.instance = app.instance
		self.db_process = self.instance.process_name
		self.prev_map = ""
		self.waitingmap = ""
		self.waitingmap_id = -1
		self.cnx = mysql.connector.connect(	user	=	settings.DATABASES[self.db_process]['OPTIONS']['user'],
											password=	settings.DATABASES[self.db_process]['OPTIONS']['password'],
                              				host	=	settings.DATABASES[self.db_process]['OPTIONS']['host'],
                              				database=	settings.DATABASES[self.db_process]['NAME'])

	
	def get_map(self):
		return self.app.tac.waitingmap_id 
	
	def get_current_map(self):
		return self.instance.map_manager.current_map.name
	
	async def on_start(self):
			
		player_chat.register(self.on_chat)
		
	
	async def ms_time(self, time):
		if len(str(time)) == 0:
			return "000"
		elif len(str(time)) == 1:
			return "00%i" %(time)
		elif len(str(time)) == 2:
			return "0%i" %(time)
		else:
			return time
    


	async def tm_time(self, time):
		if len(str(time)) == 0:
			return "00"
		elif len(str(time)) == 1:
			return "0%i" %(time)
		else:
			return time

	async def delete_locals(self,player,data,**kwargs):
		cursor_to_delete = self.cnx.cursor()
		cursor_to_delete.execute("TRUNCATE `localrecord`;")
		message = '$fffLocal Record has been deleted'
		await self.instance.chat(message)
	
	async def convert_time(self, ms):
		h = ms//3600000
		m = (ms-h*3600000)//60000
		s = (ms-h*3600000-m*60000)//1000
		ms = (ms-h*3600000-m*60000-s*1000)
		if h == 0:    
			t = "%s:%s.%s" %(m,await self.tm_time(s),await self.ms_time(ms))
		else:
			t = "%i:%s:%s.%s" %(h,m,await self.tm_time(s),await self.ms_time(ms))
		return t
		
	async def exec_func(self, player, data, **kwargs):
		await AverageRankWidget.show_top(self, player, data)
