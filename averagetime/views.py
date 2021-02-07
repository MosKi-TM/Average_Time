import math

from pyplanet.utils.style import style_strip
from pyplanet.utils.times import format_time
from pyplanet.views.generics.widget import TimesWidgetView
from pyplanet.views.generics.list import ManualListView
from pyplanet.utils import times
from .Tac import Tac
import mysql.connector
from pyplanet.conf import settings
global player_index
player_index = ''
global datas
datas = []

class AverageRankWidget(TimesWidgetView):
    widget_x = -160
    widget_y = 70.5
    size_x = 38
    size_y = 55.5
    top_entries = 5
    title = 'Average Rank'

    def __init__(self, app):
        super().__init__(app.context.ui)
        self.app = app
        self.id = 'pyplanet__widgets_tacount'
        self.instance = app.instance
        self.action = self.action_recordlist
        self.datas = []
        self.map_count = 1
        self.db_process = self.instance.process_name
        self.cnx = mysql.connector.connect(	user	=	settings.DATABASES[self.db_process]['OPTIONS']['user'],
                                            password=	settings.DATABASES[self.db_process]['OPTIONS']['password'],
                                            host	=	settings.DATABASES[self.db_process]['OPTIONS']['host'],
                                            database=	settings.DATABASES[self.db_process]['NAME'])
        
    def get_player(player_args):
        global player_index
        player_index = player_args
        return
    
    async def Refresh_scores(self):
        
        maps = []
        for i in self.instance.map_manager.maps:
            maps.append(i.id)

        cursor = self.cnx.cursor()
        query = "select id from player"
        cursor.execute(query)

        players = cursor.fetchall()
        player_list = []
        plr_counter = {}

        for i, in players:
            player_list.append(i)
            plr_counter[str(i)]=0
            

        rec = []
        endpoint_tupples = []

        for id in maps:
            cursor = self.cnx.cursor()
            query = "SELECT player_id FROM `localrecord` WHERE map_id = {} order by score ASC".format(id)
            
            cursor.execute(query)
            tmp_rec = []
            for i, in cursor.fetchall():
                tmp_rec.append(i)
            rec.append(tmp_rec)

        counted_map = len(rec)

        for record in rec:
            tmp_plr = player_list.copy()
            
            counter = 1
            for plr in record:
                plr_counter[str(plr)] += counter
                counter += 1
                tmp_plr.remove(plr)
                
            if counter != 1:
                for left_player in tmp_plr:
                    plr_counter[str(left_player)] += counter
            else: counted_map -= 1

        for player in plr_counter:
            cursor = self.cnx.cursor()
            query = "SELECT login, nickname FROM `player` WHERE id = {}".format(
                player)
            cursor.execute(query)
            datas = cursor.fetchall()

            cursor = self.cnx.cursor()
            map_count_query = 'SELECT COUNT(*) FROM `localrecord` WHERE player_id= {}'.format(player)
            cursor.execute(map_count_query)

            if cursor.fetchall()[0][0] > 1:
                for login, nickname in datas:
                    endpoint_tupples.append((round(plr_counter[player]/counted_map, 2),login, nickname))

        endpoint_tupples.sort()
        self.datas = endpoint_tupples
        return

    async def get_context_data(self):
        self.widget_y = 12.5 if self.app.dedimania_enabled else 70.5
        context = await super().get_context_data()
        
        global player_index		
        pindex_length = len(self.datas)
        try:
            pindex = [x[0] for x in self.datas].index(player_index)
        except:
            pindex = 0
        index = 1
        list_records = []
        min_index = 0
        max_index = 0
        if self.datas != 0:
            for total, login, nickname in self.datas[:5]:
                list_record = dict()
                list_record['index'] = index	
                list_record['color'] = '$ff0'				
                if login == player_index:
                    list_record['color'] = '$0f3'
                list_record['nickname'] = nickname
                list_record['score'] = total
                list_records.append(list_record)
                index += 1
            if pindex_length > 5:
                if pindex > 15 :
                    min_index = pindex - 5
                    max_index = pindex + 5
                    index = pindex - 4
                else:
                    min_index = 5
                    max_index = 15
                    
            for total, login, nickname in self.datas[min_index:max_index]:
                list_record = dict()
                list_record['index'] = index
                list_record['color'] = '$fff'
                if login == player_index:
                    list_record['color'] = '$0f3'
                list_record['nickname'] = nickname
                list_record['score'] = total
                list_records.append(list_record)
                index += 1

        context.update({
                'times': list_records
        })	
        
        return context
        
    async def action_recordlist(self, player, **kwargs):
        await self.app.show_records_list(player)
        
class AverageRankList(ManualListView):
    title = 'Average Rank'
    icon_style = 'Icons128x128_1'
    icon_substyle = 'Average Rank'
    
    fields = [
        {
            'name': '#',
            'index': 'index',
            'sorting': True,
            'searching': False,
            'width': 10,
            'type': 'label'
        },
        {
            'name': 'Player',
            'index': 'player_nickname',
            'sorting': False,
            'searching': True,
            'width': 70
        },
        {
            'name': 'Times',
            'index': 'score',
            'sorting': True,
            'searching': False,
            'width': 30,
            'type': 'label'
        },
        {
            'name': 'Number of maps',
            'index': 'map_nb',
            'sorting': True,
            'searching': False,
            'width': 20,
            'type': 'label'
        },
    ]
    
    def __init__(self, app, *args, **kwargs):
        super().__init__(self,*args, **kwargs)
        self.app = app
        self.manager = app.context.ui
        self.instance = app.instance
        self.db_process = self.instance.process_name
        self.datas = []
        self.cooldown = 0
        self.cnx = mysql.connector.connect(	user	=	settings.DATABASES[self.db_process]['OPTIONS']['user'],
                                            password=	settings.DATABASES[self.db_process]['OPTIONS']['password'],
                                            host	=	settings.DATABASES[self.db_process]['OPTIONS']['host'],
                                            database=	settings.DATABASES[self.db_process]['NAME'])
        
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
        
    async def Refresh_scores(self):
        global datas

        maps = []
        for i in self.instance.map_manager.maps:
            maps.append(i.id)

        cursor = self.cnx.cursor()
        query = "select id from player"
        cursor.execute(query)

        players = cursor.fetchall()
        player_list = []
        plr_counter = {}

        for i, in players:
            player_list.append(i)
            plr_counter[str(i)]=0
            

        rec = []
        endpoint_tupples = []

        for id in maps:
            cursor = self.cnx.cursor()
            query = "SELECT player_id FROM `localrecord` WHERE map_id = {} order by score ASC".format(id)
            
            cursor.execute(query)
            tmp_rec = []
            for i, in cursor.fetchall():
                tmp_rec.append(i)
            rec.append(tmp_rec)

        counted_map = len(rec)

        for record in rec:
            tmp_plr = player_list.copy()
            
            counter = 1
            for plr in record:
                plr_counter[str(plr)] += counter
                counter += 1
                tmp_plr.remove(plr)
                
            if counter != 1:
                for left_player in tmp_plr:
                    plr_counter[str(left_player)] += counter
            else: counted_map -= 1

        for player in plr_counter:
            cursor = self.cnx.cursor()
            query = "SELECT login, nickname FROM `player` WHERE id = {}".format(
                player)
            cursor.execute(query)
            datas = cursor.fetchall()

            cursor = self.cnx.cursor()
            map_count_query = 'SELECT COUNT(*) FROM `localrecord` WHERE player_id= {}'.format(player)
            cursor.execute(map_count_query)

            if cursor.fetchall()[0][0] > 1:
                for login, nickname in datas:
                    endpoint_tupples.append((round(plr_counter[player]/counted_map, 2),login, nickname))

        endpoint_tupples.sort()
        datas = endpoint_tupples
        return

    async def get_data(self):
        global datas
        map_attente = Tac.get_map(self)

        index = 1
        items = []
        difference = ''

        for total, login, nickname in datas:
            cursor = self.cnx.cursor()
            player_index_query = 'SELECT id FROM `player` WHERE login=\'' + str(login) + '\''
            cursor.execute(player_index_query)
            player_id = cursor.fetchall()

            cursor = self.cnx.cursor()
            map_count_query = 'SELECT COUNT(*) FROM localrecord WHERE player_id=' + str(player_id[0][0])
            cursor.execute(map_count_query)
            map_number = cursor.fetchall()

            items.append({
                'index': index, 
                'player_nickname': nickname,
                'score': total,
                'map_nb': map_number[0][0],
                'login': login,
            })
            index += 1
        return items

        