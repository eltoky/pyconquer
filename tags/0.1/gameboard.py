from sets import Set
import pygame, random, hex_system, time
from sys import exit
from operator import itemgetter
from classcollection import *
from recurser import *
from ai import *
import os

#------------------------------------------------------------------------
#
#    This file is part of Conquer.
#
#    Conquer is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Conquer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Conquer.  If not, see <http://www.gnu.org/licenses/>.
#
#    Copyright Niko Reunanen
#
#------------------------------------------------------------------------

_DEBUG = 0

# six direction matrix
edm_eveny = (
(1,0),
(0,1),
(-1,1),
(-1,0),
(-1,-1),
(0,-1)
)

edm_oddy = (
(1,0),
(1,1),
(0,1),
(-1,0),
(0,-1),
(1,-1)
)

font = pygame.font.Font(None, 12)
font2 = pygame.font.Font(None, 16)
font3 = pygame.font.Font(None, 24)
font4 = pygame.font.Font("yanone_regular.otf",20)

class TGB:
	def __init__(self,screen,ih,gp):
		# DATA: "x y" -> [playerid, unit]
		# playerid -> 0=empty, 1--n = players enumerated id
		self.data = {}
		self.ai_recursion_depth = 7
		self.show_cpu_moves_with_lines = True
		self.screen = screen
		self.fillmap(0)
		self.pics = ih
		self.gamepath = gp + os.sep
		# Instance of recursion - engine
		self.rek = TRecurser(self)
		# Cursor
		self.cursor = TCursor(self)
		self.cursor.x = 10
		self.cursor.y = 10
		self.map_edit_info = []
		self.map_edit_mode = False
		self.turn = 1
		self.cpu_names = []
		self.pisteet_s = ()
		self.gamerunning = False
		# Skin configuration
		self.sc = {}
		# Actors
		self.actors = Set([])
		self.load_skin_file("skin")
		# List of coordinates of soldiers that have moved
		self.playerlist = []
		self.load_cpu_names()
	def load_cpu_names(self):
		tiedosto = open(self.gamepath+"cpu_player_names","r")
		for kalu in tiedosto.readlines():
			if kalu.endswith("\n"):
				self.cpu_names.append(kalu[:-1])
			else:
				self.cpu_names.append(kalu)
		tiedosto.close()
	def write_edit_map(self,filunimi):
		filee = open(filunimi,"w\n")
		for i in range(self.map_edit_info[0]):
			filee.write("player\n")
		for i in range(self.map_edit_info[1]):
			filee.write("ai\n")
		if (self.map_edit_info[0]+self.map_edit_info[1]) > 0:
			for i in range(6-(self.map_edit_info[0]+self.map_edit_info[1])):
				filee.write("none\n")
		for k1,k2 in self.data.iteritems():
			filee.write("%s|%d\n"%(k1,k2))
		filee.close() 
	def read_scenarios(self):
		return os.listdir(os.path.join(self.gamepath,"scenarios"))
	def load_skin_file(self,filename1):
		filee = open(filename1,"r")
		for line in filee.xreadlines():
			if not line:
				continue
			else:
				if line[0] == "#":
					continue
				if line.isspace():
					continue
					
			rivi = line
			
			if rivi.endswith("\r\n"):
				rivi = rivi[:-1]
			if rivi.endswith("\n"):
				rivi = rivi[:-1]
			
			rivi = rivi.lower()
			rivi = rivi.split(" ")
			if rivi[0] == "interface_filename":
				self.sc["interface_filename"] = rivi[1]
			if rivi[0] == "unit_status_text_topleft_corner":
				self.sc["unit_status_text_topleft_corner"] = (int(rivi[1]),int(rivi[2]))
			if rivi[0] == "scoreboard_text_topleft_corner":
				self.sc["scoreboard_text_topleft_corner"] = (int(rivi[1]),int(rivi[2]))
			if rivi[0] == "unit_status_text_color":
				self.sc["unit_status_text_color"] = (int(rivi[1]),int(rivi[2]),int(rivi[3]))
			if rivi[0] == "scoreboard_text_color":
				self.sc["scoreboard_text_color"] = (int(rivi[1]),int(rivi[2]),int(rivi[3]))
			if rivi[0] == "button_endturn":
				self.sc["button_endturn"] = ((int(rivi[1]),int(rivi[2])),(int(rivi[3]),int(rivi[4])))
			if rivi[0] == "button_quit":
				self.sc["button_quit"] = ((int(rivi[1]),int(rivi[2])),(int(rivi[3]),int(rivi[4])))
			if rivi[0] == "making_moves_text_topleft_corner":
				self.sc["making_moves_text_topleft_corner"] = (int(rivi[1]),int(rivi[2]))
			if rivi[0] == "menu_interface_filename":
				self.sc["menu_interface_filename"] = rivi[1]
			if rivi[0] == "making_moves_text_color":
				self.sc["making_moves_text_color"] = (int(rivi[1]),int(rivi[2]),int(rivi[3]))
			
	def start_game(self):
		self.gamerunning = True
		kello = pygame.time.Clock()
		#eventti = pygame.event.wait()
		while self.gamerunning:
			kello.tick(30)
			for eventti in pygame.event.get():
				if eventti.type == pygame.MOUSEBUTTONDOWN:
					x1,y1=self.pixelToHexMap(eventti.pos)
					x1 += self.cursor.scroll_x
					self.cursor.x,self.cursor.y = x1,y1
					self.cursor.mouse_pos = eventti.pos
					if eventti.button == 1:
						self.cursor.click()
					if not self.map_edit_mode:
						if eventti.button == 3:
							self.draft_soldier(self.cursor.x,self.cursor.y)
				if eventti.type == pygame.KEYDOWN:
					if eventti.key == pygame.K_LEFT:
						self.cursor.scroll(-1)
					if eventti.key == pygame.K_RIGHT:
						self.cursor.scroll(1)
					if not self.map_edit_mode:
						if eventti.key == pygame.K_m:
							self.show_own_units_that_can_move()
						if eventti.key == pygame.K_e:
							self.end_turn()
					else:
						if eventti.key == pygame.K_UP:
							self.map_edit_info[2] += 1
							if self.map_edit_info[2] > 6:
								self.map_edit_info[2] = 6
						if eventti.key == pygame.K_DOWN:
							self.map_edit_info[2] -= 1
							if self.map_edit_info[2] < 0:
								self.map_edit_info[2] = 0
				self.draw_scoreboard(False)
				self.drawmap()
				pygame.display.flip()
	def new_game(self,skenariofilu="testikartta",randommap = False, randomplayers_cpu = 3, humanplayers = 3):
		self.turn = 1
		self.pisteet_s = ()
		self.playerlist = []
		self.map_edit_mode = False
		self.cursor.scroll_x = 0
		
		if randommap:
			for i in xrange(humanplayers):
				self.playerlist.append(TPlayer("Player %d"%(i+1),i+1,self.screen,None))
			for i in xrange(randomplayers_cpu):
				self.playerlist.append(TPlayer("%s (cpu)"%(random.choice(self.cpu_names)),i+(humanplayers+1),self.screen,TAi(self)))
				
		self.data = {}
		self.actors.clear()

		if randommap:
			self.generate_map(50,13)
		else:
			
			self.load_map(os.path.join(self.gamepath,"scenarios")+os.sep+skenariofilu)
		self.fill_capitals()
		self.salary_time_to_capitals_by_turn([1],False)
		self.salary_time_to_capitals_by_turn(self.get_player_id_list(),True)
		# Pitaa ekalle pelaajalle antaa massit		
		#
		self.drawmap()
		self.draw_scoreboard(True)
		#self.text_at("Left Mouse Button: Select",(250,500),wipe_background=False,fontti=font4)
		#self.text_at("Right Mouse Button: Draft and Update Soldiers",(250,530),wipe_background=False,fontti=font4)
		pygame.display.flip()
		
		# Jos eka pelaaja on tietokone niin sykli kayntiin
		if self.playerlist[0].ai_controller:
			self.playerlist[0].ai_controller.act(self.ai_recursion_depth)
			self.fill_capitals()
			self.end_turn()
	def get_player_id_list(self):
		return [iteraatio.id for iteraatio in self.playerlist]
	def get_right_edm(self,y):
		if (y % 2) == 1:
			return edm_oddy
		else:
			return edm_eveny
	def get_player_by_name(self,nimissi):
		for peluri in self.playerlist:
			if peluri.nimi == nimissi:
				return peluri
		return None
	def gct(self,x,y):
		return "%d %d" % (x,y)
	def count_world_specific(self,id_list):
		laskuri = 0
		for key,value in self.data.iteritems():
			if value in id_list:
				laskuri += 1
		return laskuri
	def text_input(self, caption,(x1,y1),(w1,h1),onlynumbers=False):
		#self.draw_items()
		#kello1 = pygame.time.Clock()
		
		curstr = []
		pygame.draw.rect(self.screen,(30,30,30),(x1,y1,w1,h1))
		self.text_at(caption,(x1+w1/4,y1),fontti=font2,wipe_background=False)
		pygame.display.flip()
		while 1 != 0:
			#kello1.tick(30)
			pygame.draw.rect(self.screen,(30,30,30),(x1,y1,w1,h1))
			self.text_at(caption,(x1+w1/4,y1),fontti=font2,wipe_background=False)
			e = pygame.event.poll()
			if e.type == pygame.KEYDOWN:
				e = e.key
			else:
				continue
				
			if e == pygame.K_BACKSPACE:
				if curstr:
					del curstr[len(curstr)-1]
			if e == pygame.K_RETURN:
				break
			if not onlynumbers:
				if e <= 127 and e != pygame.K_BACKSPACE:
					curstr.append(chr(e))
			else:
				if e <= 127 and e != pygame.K_BACKSPACE and chr(e) in ["1","2","3","4","5","6","7","8","9","0"]:
					curstr.append(chr(e))				
			self.text_at("".join(curstr), (((x1+(x1+w1))/2)-(len(curstr)*4),y1+15),wipe_background=False,fontti=font4)
			pygame.display.flip()
		return "".join(curstr)
	def count_world_area(self):
		laskuri = 0
		for key,value in self.data.iteritems():
			if value > 0:
				laskuri += 1
		return laskuri
	def destroy_lonely_capitals(self):
		# Lonely soldiers too will be terminated
		# Lets iterate through the set copy
		# as we may alter the original set
		for actor in self.actors.copy():
			# Only alive soldiers
			if not actor.dead:
				edm = self.get_right_edm(actor.y)
				found = False
				# If we find one (or more) friendly land next to soldier
				# or resource dump, actor will not be terminated.
				for i in xrange(6):
					if self.validxy(actor.x+edm[i][0],actor.y+edm[i][1]):
						if self.data[self.gct(actor.x+edm[i][0],actor.y+edm[i][1])] == actor.side:
							found = True
							break
				if not found:
					self.actors.discard(actor)
	def seenxy(self,x,y):
		return (x >= (0+self.cursor.scroll_x) and x <= (14+self.cursor.scroll_x))
	def validxy(self,x,y):
		return self.data.has_key(self.gct(x,y))
	def try_to_conquer(self,actori,x2,y2,simuloidaanko):
		if actori.moved:
			return
		tulos = self.is_blocked(actori,x2,y2)
		kohde = self.actorat(x2,y2)
		# Tulos[0] -> Boolean value whether the target land is blocked
		# Tulos[1] ja Tulos[2] -> if target land is blocked, these
		# hold the coordinates for the reason of block.
		if not tulos[0]:

			# Kuutosten taistelu katsotaan erikseen
			if kohde and not simuloidaanko:
				if not kohde.capital and kohde.side != actori.side:
					if actori.voima == 6 and kohde.voima == 6:
						if random.randint(1,2) == 1:
							# Turpaan tuli
							actori.x,actori.y,actori.dead=0,0,True
							self.actors.discard(actori)
							#print "SuperBattle from attacker point of view LOST!"
							return

			# Both simulation and real attack makes changes to
			# land owner policy
			self.data[self.gct(x2,y2)] = actori.side

			# If simulating for AI, we don't want to make
			# changes directly to actors.
			if not simuloidaanko:
				actori.x,actori.y = x2,y2
				actori.moved = True
				if kohde:
					#CPU INTENSIVE
					kohde.dead = True
					#kohde.capital = False
					#kohde.x = 0
					#kohde.y = 0
					#kohde.side = 0
					self.actors.discard(kohde)
				# Fix this to check one island (x2,y2) if
				# dump merging needed
				self.fill_capitals()
		else:
			# Kohde blokattu, ilmoitetaan blokkaaja graafisesti
			# mutta ei ilmoiteta graafisesti tietokonepelaajan mokia
			if self.seenxy(tulos[1],tulos[2]) and not self.get_player_by_side(actori.side).ai_controller:
				self.cursor.chosen_actor = None
				pixelX,pixelY = self.hexMapToPixel(tulos[1]-self.cursor.scroll_x,tulos[2])
				pygame.draw.circle(self.screen,(0,255,0),(pixelX+20,pixelY+20),30,2)
				self.text_at(self.block_desc(tulos[3]),(pixelX,pixelY+15),fontti=font2)
				pygame.display.flip()
				time.sleep(0.45)
				self.drawmap()
				pygame.display.flip()
	def block_desc(self,r):
		if r == "tooweak": return "Your soldier is too weak!"
		if r == "sameside": return "Target is friendly!"
		if r == "alreadymoved": return "Soldier has already moved!"
		if r == "spaceisnotlegal": return "Target is not land!"
		if r == "ownspacealreadyoccupied": return "Target is friendly!"
		if r == "outofisland": return "Out of soldiers reach!"
		return "Blocked."
	def get_player_by_side(self,side):
		for peluri in self.playerlist:
			if peluri.id == side:
				return peluri
		return None
	def merge_capitals(self,capital_coords,island_area):
		uusisumma = 0
		deletelist = []
		if len(capital_coords) > 1 and island_area:
			puoli = self.actorgctat(capital_coords[0]).side
			for coord in capital_coords:
				kalu = self.actorgctat(coord)
				#if kalu.side == puoli:
				if kalu:
					x11,y11 = self.ec(island_area[0])
					if kalu.capital and kalu.side==self.data[self.gct(x11,y11)]:
						uusisumma += kalu.massit
						deletelist.append(kalu)
			while deletelist:
				self.actors.discard(deletelist.pop())
			ok = False
			tries = 0
			while not ok and tries < 100:
				tries += 1
				uus_k = random.choice(island_area)
				kaija = self.actorgctat(uus_k)
				if not kaija:
					ok = True
			if tries < 100:
				x11,y11 = self.ec(uus_k)
				new_shared_resource_dump = TActor(x11,y11,puoli,voima=0,capital=True)
				new_shared_resource_dump.massit = uusisumma
				self.actors.add(new_shared_resource_dump)
	def fill_capitals(self):
		# Tata fill_capitalsia voi kutsua aina kun valloitellaan maita
		#   -> koska ainoastaan capilattomia maita kasitellaan
		# CPU INTENSIVE?
		# Koordinaatit joista on jo etsitty paikkaa
		# Tilaa pitaa olla vah. kaks ruutuu, muute ei tule capitalii
		searched = Set([])
		pelaajat = self.get_player_id_list()
		#for x in xrange(30):
		#	for y in xrange(14):
		# Iterated coordinate and its player id (land data)
		for xy,xy_pid in self.data.iteritems():

			# Onko koordinaatti jo etsitty
			if xy in searched:
				continue
				
			# Ei tayteta kaupunkeja tai yhdistetyita ei mukana oleville
			if xy_pid not in pelaajat:
				continue

			x,y = self.ec(xy)			
						
			# Onko tyhja
			if xy_pid > 0:
				# Kysytaan etta onko saarella capitalia
				# ja saadaan boolean-arvoinen vastaus seka
				# lista kaydyista koordinaateista
				hakutulos = self.rek.count_capitals_on_island(x,y)
				# Paivitetaan kaydyt koordinaatit
				searched.update(hakutulos[1])
				# Jos ei ole paakaupunkia viela ja area vah. 2 ja
				# alueen omistaa jokin PELAAJA eika omistamaton
				# maa
				if not hakutulos[0] and len(hakutulos[1]) > 1:
					# Etsitaan paakaupungille uusi paikka
					paikka = random.choice(list(hakutulos[1]))
					if paikka:
						# Jos paikka loytyi (saari ei ole 1-kokoinen)
						# niin heitetaan capital saatuun koordinaatti-tekstiin
						kalu = paikka.split(" ")
						self.actors.add(TActor(int(kalu[0]),int(kalu[1]),self.data[paikka],capital=True))
				# Liikaa capitalei mestoil, valloitettu hanakasti?
				elif len(hakutulos[0]) > 1:
					self.merge_capitals(hakutulos[0],list(hakutulos[1]))
	def fillmap(self, piece):
		self.data = {}
		for x in xrange(30):
			for y in xrange(14):
				self.data[self.gct(x,y)] = piece
	def actorgctat(self,gctee):
		gctee = gctee.split(" ")
		return self.actorat(int(gctee[0]),int(gctee[1]))
	def actorat(self,x,y):
		for actori in self.actors:
			if actori.x==x and actori.y==y:
				return actori
		return None
	def fill_random_units(self,d):
		pelaajat = self.get_player_id_list()
		if (d > 0):
			while (d > 0):
				retry = 0
				x = random.randint(1,28)
				y = random.randint(1,13)
				ok = False
				while not ok:
					retry += 1
					if retry == 500:
						break
					x = random.randint(1,28)
					y = random.randint(1,13)
					if ((self.data[self.gct(x,y)] in pelaajat) and (self.actorat(x,y) is None)):
						ok = True
				if retry < 500:
					self.actors.add(TActor(x,y,self.data[self.gct(x,y)],voima=random.randint(1,3)))
				d -= 1
	def fill_random_boxes(self,d,for_who,max_x):
		if (d > 0):
			while (d > 0):
				x = random.randint(1,max_x)
				y = random.randint(1,13)
				edm = self.get_right_edm(y)
				for i in xrange(6):
					if self.validxy(x+edm[i][0],y+edm[i][1]):
						playerid = random.choice(for_who)
						self.data[self.gct(x+edm[i][0],y+edm[i][1])] = playerid
				d -= 1
	def whole_map_situation_score(self,for_who):
		'''Simple scoring system based on amounts of land'''
		return self.data.values().count(for_who)
	def ec(self,gctee):
		tmp = gctee.split(" ")
		return (int(tmp[0]),int(tmp[1]))
	def draw_scoreboard(self,update=False):
		if update:
			pisteet = {}
			for peluri in self.playerlist:
				if not peluri.lost:
					pisteet[peluri] = self.whole_map_situation_score(peluri.id)
			self.pisteet_s = sorted(pisteet.iteritems(), key=itemgetter(1))
		laskuri = 0
		for peluri in self.playerlist:
			if peluri.won:
				self.cursor.chosen_actor = None
				self.cursor.chosen_capital = None
				if peluri.ai_controller:
					self.text_at("Player %s won the game!" % peluri.nimi,(200,200),fontti=font4,vari=(255,255,255)) 
				else:
					self.text_at("You (%s) won the game!" % peluri.nimi,(200,200),fontti=font4,vari=(255,255,255))
		for jau in reversed(self.pisteet_s):
			self.screen.blit(self.pics.gi("%d"%jau[0].id),(self.sc["scoreboard_text_topleft_corner"][0],self.sc["scoreboard_text_topleft_corner"][1]+35*laskuri-13))
			self.text_at("%d     %s" % (jau[1],jau[0].nimi),(self.sc["scoreboard_text_topleft_corner"][0]+15,self.sc["scoreboard_text_topleft_corner"][1]+35*laskuri),vari=(self.sc["scoreboard_text_color"][0],self.sc["scoreboard_text_color"][1],self.sc["scoreboard_text_color"][2]),fontti=font4,wipe_background = False)
			laskuri += 1
		try:
			tahko = self.get_player_by_side(self.turn)
			if not tahko.ai_controller:
				if not tahko.lost:
					self.text_at("Your (%s) turn" % (tahko.nimi),(630,300),vari=(0,0,0),fontti=font3,wipe_background = False)
				else:
					self.text_at("You (%s) lost..." % (tahko.nimi),(635,300),vari=(0,0,0),fontti=font3,wipe_background = False)
		except:
			pass
			
	def hexMapToPixel(self,mapX,mapY):
		"""
		Returns the top left pixel location of a hexagon map location.
		"""
		if mapY & 1:
			# Odd rows will be moved to the right.
			return (mapX*hex_system.TILE_WIDTH+hex_system.ODD_ROW_X_MOD,mapY*hex_system.ROW_HEIGHT)
		else:
			return (mapX*hex_system.TILE_WIDTH,mapY*hex_system.ROW_HEIGHT)
	def draw_map_edit_utilities(self):
		if self.map_edit_info[2] == 0:
			teksti = "Eraser"
		else:
			if self.map_edit_info[2] <= (self.map_edit_info[0] + self.map_edit_info[1]):
				teksti = "Player #%d land" % self.map_edit_info[2]
			else:
				teksti = "Land #%d without player" % self.map_edit_info[2]
		self.text_at("Selected:",(620,80), fontti = font4, wipe_background=False,vari=(0,0,0))
		self.text_at(teksti,(620,100), fontti = font4, wipe_background=False,vari=(0,0,0))
		
		laskuri = 0
		for i in xrange(0,self.map_edit_info[0]):
			laskuri += 1
			self.text_at("Player #%d = Human"%laskuri,(620,130+laskuri*20), fontti = font4, wipe_background=False,vari=(0,0,0))
		for i in xrange(0,self.map_edit_info[1]):
			laskuri += 1
			self.text_at("Player #%d = CPU" % laskuri,(620,130+laskuri*20), fontti = font4, wipe_background=False,vari=(0,0,0))
		if (6-laskuri) > 0:
			for i in range(0,(6-laskuri)):
				laskuri += 1
				self.text_at("Player #%d = No player" % laskuri,(620,130+laskuri*20), fontti = font4, wipe_background=False,vari=(0,0,0))
	def drawmap(self):
		#self.screen.fill((0,0,0))
		if not self.map_edit_mode:
			self.screen.blit(self.pics.gi("interface"),(0,0))
			self.draw_scoreboard(False)
		else:
			self.screen.blit(self.pics.gi("mapedit"),(0,0))
			self.draw_map_edit_utilities()
		
		for x in xrange(self.cursor.scroll_x,15+self.cursor.scroll_x):
			for y in xrange(14):
				if self.data[self.gct(x,y)] > 0:
					pixelX,pixelY = self.hexMapToPixel(x-self.cursor.scroll_x,y)
					self.screen.blit(self.pics.gi(str(self.data[self.gct(x,y)])),(pixelX,pixelY))
					actor = self.actorat(x,y)
					if actor:
						if actor.capital:
							self.screen.blit(self.pics.gi("capital"),(pixelX+3,pixelY+5))
							if self.get_player_by_side(self.turn):
								if actor.side == self.turn and not self.get_player_by_side(actor.side).ai_controller:
									self.text_at("%d"%actor.massit,(pixelX+14,pixelY+17),fontti=font2)
						else:
							teksti = "%d" % actor.voima
							if actor.moved:
								teksti = teksti + "X"
							self.screen.blit(self.pics.gi("soldier"),(pixelX+10,pixelY+10))
							self.text_at(teksti,(pixelX+20,pixelY+20),fontti=font)
		if self.cursor.chosen_actor:
			pixelX,pixelY = self.hexMapToPixel(self.cursor.x-self.cursor.scroll_x,self.cursor.y)
			pygame.draw.rect(self.screen,self.cursor.get_color(),(pixelX,pixelY,40,40),2)
		if self.cursor.chosen_capital:
			kolorissi = (self.sc["unit_status_text_color"][0],self.sc["unit_status_text_color"][1],self.sc["unit_status_text_color"][2])
			x1,y1 = self.sc["unit_status_text_topleft_corner"][0],self.sc["unit_status_text_topleft_corner"][1]
			self.text_at("Resource dump",(x1,y1+30),fontti=font4,wipe_background=False,vari=kolorissi)
			self.text_at("Income: %d" % self.cursor.chosen_capital.income,(x1,y1+50),fontti=font4,wipe_background=False,vari=kolorissi)
			self.text_at("Expends: %d" % self.cursor.chosen_capital.expends,(x1,y1+70),fontti=font4,wipe_background=False,vari=kolorissi)
			self.text_at("Supplies: %d" % self.cursor.chosen_capital.massit,(x1,y1+90),fontti=font4,wipe_background=False,vari=kolorissi)
			self.screen.blit(self.pics.gi("capital"),(x1,y1))
	def get_human_and_cpu_count(self):
		montako_h = 0
		okei = False
		while not okei:
			try:
				montako_h = int(self.text_input("How many human players (1-6)?",(800/2-110,300),(240,45),onlynumbers=True))
			except:
				continue
			okei = True
			if montako_h > 6:
				okei = False
			if montako_h < 1:
				okei = False

		montako_c = 0
		okei = False
		minssi = 0
		if montako_h != 6:
			if montako_h == 1:
				minssi = 1
			while not okei:
				try:
					montako_c = int(self.text_input("How many cpu players (%d-%d)?"%(minssi,6-montako_h),(800/2-110,300),(240,45),onlynumbers=True))
				except:
					continue
				okei = True
				if montako_c > (6-montako_h):
					okei = False
				if montako_c < minssi:
					okei = False
		return montako_h,montako_c
							
	def is_blocked(self, actori, x, y):
		# Huonompi ei valloita kovempaa
		defender = self.actorat(x,y)
		if defender:
			# Kutone hyokkaa minne haluaa
			if actori.voima < 6:
				if defender.voima >= actori.voima:
					return [True,x,y,"tooweak"]
					
			if defender.capital and actori.voima < 2:
				return [True,x,y,"tooweak"]
			if actori.side == defender.side:
				return [True,x,y,"sameside"]

		# Sotilas voi siirtya vain kerran
		if actori.moved:
			return [True,x,y,"alreadymoved"]
			
		# Mustaa avaruutta ei valloiteta
		if self.data[self.gct(x,y)] == 0:
			return [True,x,y,"spaceisnotlegal"]
			
		# Omalla alueella ei voi omia blokata
		# eli onko kohteen maan playerid sama kuin pelivuoro
		#   -> liikutaanko omalla alueella
		if self.data[self.gct(x,y)] == self.turn:
			# Ruutu pitaa olla kuitenkin tyhja, jos ruutu tyhja
			# niin palautusarvo False, muuten True.
			if defender:
				return [True,x,y,"ownspacealreadyoccupied"]
				
		# Valloituskohteen ymparilla pitaa olla omaa maata
		# (ettei seilata valloitellen iha mista sattuu).
		# Mutta oma viereinen pala pitaa olla samasta saaresta
		# mista hyokkays lahtee
		crawl_list = Set([])
		# Listataan kaikki hyokkayssaarikoordinaatit
		self.rek.crawl(actori.x,actori.y,crawl_list,[self.turn])
		
		found = False
		edm = self.get_right_edm(y)
		for i in xrange(6):
			if self.validxy(x+edm[i][0],y+edm[i][1]):
			# Naapurikoordinaatissa oleva pala pitaa olla kuitenkin samasta saaresta
			# mista hyokkays lahtee
				if self.gct(x+edm[i][0],y+edm[i][1]) in crawl_list:
					found = True
		if not found:
			return [True, x, y, "outofisland"]
			
		# Sitten tarkastellaan vastustajan blokkauksia    
		for i in xrange(6):
		# Onko 6-naapurusto - koordinaatti validi
			if self.validxy(x+edm[i][0],y+edm[i][1]):
			# Onko kohdenaapurustokoordinaatin playerid sama kuin aloitusmestan
				if self.data[self.gct(x+edm[i][0],y+edm[i][1])] == self.data[self.gct(x,y)]:
					# Onko puolustus vahvempi kuin hyokkaaja
					defenderi = self.actorat(x+edm[i][0],y+edm[i][1])
					if defenderi:
						if defenderi.side != actori.side:
							if defenderi.capital:
								# Capital puolustaa ykkosia vastaan
								if actori.voima == 1:
									return [True, x+edm[i][0], y+edm[i][1],"tooweak"]
							# Alle kutonen ei vaikeampaa vastaan parjaa
							if actori.voima < 6:
								if defenderi.voima >= actori.voima:
									return [True, x+edm[i][0], y+edm[i][1],"tooweak"]
		return [False,0,0,"legal"]
	def generate_map(self,minsize,max_x):
		self.fillmap(0)
		ok = False
		while not ok:
			self.fill_random_boxes(1,[1,2,3,4,5,6],max_x)
			if self.rek.is_the_whole_earth_connected(max_x=max_x) and self.count_world_area() >= minsize:
				ok = True
			#else:
				#print self.count_world_area(),self.rek.is_the_whole_earth_connected()
			#self.drawmap()
			#pygame.display.flip()
		self.fill_capitals()
		self.salary_time_to_capitals_by_turn(self.get_player_id_list(),True)
	def clean_deaders(self):
		for actori in self.actors.copy():
			if actori.dead:
				self.actors.discard(actori)
	def buy_units_by_turn(self):
		for city in self.actors.copy():
			# Hengissa oleva vuorossa olevan pelaajan paakaupunki jolla on rahaa>0
			if not city.dead and city.capital and city.massit > 0 and city.side == self.turn:
				
				# Onko saarella tilaa ollenkaan actorille?
				# tulos[0] arvottu paikka (ei tarkasteta laillisuutta)
				# tulos[1] saaren maapalojen koordinaatit
				tulos = self.rek.recurse_new_random_coord_for_capital_on_island(city.x,city.y)
				
				# Saarella ei ole tilaa actorille, seuraava kaupunki kehiin
				if not tulos:
					continue
				
				# Kaydaan max. 500 kertaa arvotusi maapaloja lapi
				#	-> yritetaan loytaa laillinen arvottu maapala actorille
				ok = False
				tries = 0
				while not ok and tries < 500:
					tries += 1
					tulos[0] = random.choice(tulos[1]) 
					if not self.actorgctat(tulos[0]):
						ok=True
				if tries == 500:
					ok = False
						
				# Lasketaan saarella paivitettavissa paivitettavissa olevien
				# (lvl < 6) sotilaiden maara
				voimalista = []
				soldiercounter = 0
				soldiercounter2 = 0
				ykkoscount = 0
				for gctee in tulos[1]:
					hei = self.actorgctat(gctee)
					if hei:
						if hei.side==self.turn and not hei.capital and not hei.dead:
							soldiercounter2 += 1
							# Ei lasketa kutosia paivitettaviks
							if hei.voima == 1:
								ykkoscount += 1
							if hei.voima < 6:
								soldiercounter += 1
								voimalista.append(hei.voima)

				# Onko saarella paivitettavia sotilaita?
				if soldiercounter != 0:
					# Jos saarella on omia sotilaita niin on todennakoisempaa
					# paivittaa omia sotilaita
					# Eli on 66% mahdollisuus etta paivitetaan sotilaita
					# jos sotilaita on jo ennestaan
					if random.randint(1,3) != 2:
						ok = False
				
				vapaat_maat = []
				for gctee in tulos[1]:
					if not self.actorgctat(gctee):
						vapaat_maat.append(gctee)
				
				# Onko sotilata?
				if soldiercounter2 != 0:
					# Lasketaan saaren vapaiden maiden ja sotilaiden suhde
					suhde = len(vapaat_maat) / soldiercounter2
					# Jos vapaata maata on kolme tai enemman per sotilas niin...
					if suhde >= 3:
						ok = False
						while not ok and tries < 500:
							tries += 1
							tulos[0] = random.choice(tulos[1]) 
							if not self.actorgctat(tulos[0]):
								ok=True
					# Jos sotilaita on taas joka toiselle tai jokaselle
					# palalle
					if suhde <= 2:
						ok = False
									
				# Jos on paivitettavia sotilaita ja valloituskohteista yli puolet
				# vaatii sellaisia ja on massia & tuloa niin PRIORITEETTI
				# numero yksi on paivittaa niita saatana

				paatos = False
				tooweakcount = 0
				a_searched = []
				if soldiercounter > 0:
					urpo = TActor(0,0,self.turn,voima=0,capital=False)
					for pala in tulos[1]:
						xy = pala.split(" ")
						xy[0] = int(xy[0])
						xy[1] = int(xy[1])
						edm = self.get_right_edm(xy[1])
						for i in xrange(6):
							if self.validxy(xy[0]+edm[i][0],xy[1]+edm[i][1]):
								if self.gct(xy[0]+edm[i][0],xy[1]+edm[i][1]) in a_searched:
									continue
								if self.data[self.gct(xy[0]+edm[i][0],xy[1]+edm[i][1])] != self.turn:
									a_searched.append(self.gct(xy[0]+edm[i][0],xy[1]+edm[i][1]))
									urpo.x,urpo.y,side = xy[0],xy[1],self.turn
									found_hardguy = soldiercounter
									for haastaja in voimalista:
										urpo.voima = haastaja
										if self.is_blocked(urpo,xy[0]+edm[i][0],xy[1]+edm[i][1])[3] == "tooweak":
											found_hardguy -= 1
									if found_hardguy == 0:
										tooweakcount += 1
					if (float(tooweakcount) / float(len(a_searched))) >= 0.3:
						ok = False
						paatos = True
					if urpo:
						urpo = None
				
				# Jos sotilaita ei ole yhtaan niin sitte PRIORITEETTI numero
				# yksi on sellasen osto
				if soldiercounter2 == 0:
					ok = True

				# Kaikista tarkeinta on kattoa ettei menna yli varojen
				# Onko nettotulot nollis? Jos on niin stoppia
				if (city.income - city.expends) < 1:
					return
				
				# Onko rahavarannot nollil? Jos on niin stoppia
				if city.massit < 1:
					return
					
				if ok:
					# Paadyttiin ostamaan ukkelipukkeli
					m11 = random.randint(0,1)
					m22 = random.randint(0,1)
					# Ostetaan sitten kaikil rahoil ;D
					while city.massit > m11 and (city.income-city.expends) > m22:
						ok2 = False
						while not ok2 and tries < 500:
							tries += 1
							tulos[0] = random.choice(tulos[1]) 
							if not self.actorgctat(tulos[0]):
								ok2=True
						if ok2:
							city.massit -= 1
							city.expends += 1
							# Jaba valtaa ruudun
							city.income -= 1
							# /Jaba
							tulos1 = tulos[0].split(" ")
							self.actors.add(TActor(int(tulos1[0]),int(tulos1[1]),city.side,voima=1,capital=False))
					# Jos ei iha kaikil masseil ostettu sotureita niin paivitetaa niita
					if m11 or m22:
						self.update_own_soldiers(city,tulos,ykkoscount,soldiercounter2,paatos)
				if not ok:
					self.update_own_soldiers(city,tulos,ykkoscount,soldiercounter2,paatos)
	def update_own_soldiers(self,city,tulos,ykkoscount,soldiercounter2,paatos):
		# Paivitetaan sotureita niin kauan etta massia on 0 tai 1
		tries = 0
		critical_cash = 0 #random.randint(0,1)
		# Jos halutaan lopettaa yksikoiden paivitys
		running = True
		while city.massit > critical_cash and running:
			tries += 1
			# Sate kertaa yritetaan
			if tries == 100:
				running = False
			for ukko in self.actors:
				# Halutaan lopettaa yksikoiden paivitys
				if not running:
					continue
				# Nettotase pitaa olla suurempi kuin 0
				if (city.income - city.expends) > 0:
					# Onko elossa oleva oman puolen actori sotilas ja menevan kaupungin saarella
					if self.gct(ukko.x,ukko.y) in tulos[1] and not ukko.capital and not ukko.dead and ukko.side == city.side:
						# Ei paiviteta kutosia...
						# Ja ykkosille paremmat tsanssit paivitykseen, jos on muitakin kuin ykkosia
						# Jos paatos tehty tarpeelle parempia sotilaita niin niita kylla hommataan
						if ukko.voima < 6:
							# Noniin
							
							# Ykkosia loytyy
							if ykkoscount > 0 and (soldiercounter2-ykkoscount) > 0:
								# Ei olla itse ykkone
								if ukko.voima != 1:
									# Ei ole pattitilannetta (=pakollista tarvetta paivitetylle)
									if not paatos:
										# 33% mahdollisuus etta paivitetaan ei-ykkonen
										if random.randint(1,3) != 2:
											# Ykkosille enemman prioriteettia
											continue
							
							city.expends += 1
							city.massit -= 1
							ukko.voima += 1
							if city.massit <= critical_cash:
								running = False
							if (city.income - city.expends) == critical_cash:
								running = False
	def check_and_mark_if_someone_won(self):
		no_losers = [z for z in self.playerlist if not z.lost]
		if len(no_losers) == 1:
			no_losers[0].won = True
			return True
		return False

	def load_map(self,mapo):
		try:
			if self.map_edit_mode:
				self.map_edit_info = [0,0,1]
			filu = open(mapo,"r")
			for y,rivi in enumerate(filu.xreadlines()):
				if y < 6:
					rivi2 = rivi[:-1]
					if rivi2 == "player":
						if not self.map_edit_mode:
							self.playerlist.append(TPlayer("Player %d"%(y+1),y+1,self.screen,None))
						else:
							self.map_edit_info[0] += 1
					if rivi2 == "ai":
						if not self.map_edit_mode:
							self.playerlist.append(TPlayer("%s (cpu)"%(random.choice(self.cpu_names)),y+1,self.screen,TAi(self)))
						else:
							self.map_edit_info[1] += 1
				else:
					if len(rivi) > 0:
						rivi2 = rivi[:-1]
						rivi2 = rivi2.split("|")
						hei = self.ec(rivi2[0])
						self.data[self.gct(hei[0],hei[1])] = int(rivi2[1])
			filu.close()
		except:
			pass
	def has_anyone_lost_the_game(self):
		for possible_new_loser in self.playerlist:
			if self.count_capitals_on_world(possible_new_loser.id) == 0 and not possible_new_loser.lost:
				possible_new_loser.lost = True
	def count_capitals_on_world(self,pid):
		tulos = 0
		for actor in self.actors:
			if actor.capital and actor.side == pid and not actor.dead:
				tulos += 1
		return tulos
	def show_own_units_that_can_move(self):
		for actor in self.actors:
			if not actor.moved and actor.side == self.turn and not actor.capital:
				if self.seenxy(actor.x,actor.y):
					pixelX,pixelY = self.hexMapToPixel(actor.x-self.cursor.scroll_x,actor.y)
					pygame.draw.circle(self.screen,(255,255,20),(pixelX+20,pixelY+20),20,3)
		pygame.display.flip()
		time.sleep(0.5)
		self.drawmap()
	def salary_time_to_capitals_by_turn(self,sidelist,just_do_math=False):
		koordilista = []
		mahdollinen_kuolema = []
		kuolema = []
		koordilista = Set([])
		for kaupunki in self.actors:
			mahdollinen_kuolema = []
			koordilista.clear()
			tulot = 0
			menot = 0
			if not kaupunki.dead and kaupunki.capital and kaupunki.side in sidelist:
				self.rek.crawl(kaupunki.x,kaupunki.y,koordilista,[kaupunki.side])
				tulot = len(koordilista)
				for otus in self.actors:
					# Vieko otus tai capital hyvaa tilaa?
					if self.gct(otus.x,otus.y) in koordilista and not otus.capital:
						#muutos -= 1
						menot += 1
						#print self.gct(kaupunki.x,kaupunki.y) + " laskua lisaa"
					if not otus.dead and not otus.capital and otus.side == kaupunki.side:
						if self.gct(otus.x,otus.y) in koordilista:
							mahdollinen_kuolema.append(otus)
							#muutos -= otus.voima
							menot += otus.voima
				kaupunki.income = tulot
				kaupunki.expends = menot
				#print tulot
				if not just_do_math:
					kaupunki.massit += (kaupunki.income - kaupunki.expends)
					if kaupunki.massit < 0:
						kuolema.extend(mahdollinen_kuolema)
						
		if not just_do_math:
			
			while kuolema:
				tmp = kuolema.pop()
				if self.seenxy(tmp.x,tmp.y):
					pixelX,pixelY = self.hexMapToPixel(tmp.x-self.cursor.scroll_x,tmp.y)
					self.screen.blit(self.pics.gi("skull"),(pixelX+10,pixelY+10))
					if tmp in self.actors:
						self.actors.discard(tmp)
			tmp = None
					
			if kuolema:
				pygame.display.flip()
				time.sleep(1)
			kuolema = []
			mahdollinen_kuolema = []
	def pixelToHexMap(self,(x1,y1)):
		x=x1
		y=y1
		gridX = x/hex_system.GRID_WIDTH
		gridY = y/hex_system.GRID_HEIGHT
		gridPixelX = x%hex_system.GRID_WIDTH
		gridPixelY = y%hex_system.GRID_HEIGHT
		if gridY&1:
			hexMapX=gridX+hex_system.gridOddRows[gridPixelY][gridPixelX][0]
			hexMapY=gridY+hex_system.gridOddRows[gridPixelY][gridPixelX][1]
		else:
			hexMapX=gridX+hex_system.gridEvenRows[gridPixelY][gridPixelX][0]
			hexMapY=gridY+hex_system.gridEvenRows[gridPixelY][gridPixelX][1]
		return (hexMapX,hexMapY)
	def text_at(self,teksti,coords,wipe_background=True,fontti=font2,vari=(255,255,255),flippaa=False):
		text = fontti.render(teksti,1,vari)
		koko = fontti.size(teksti)
		if wipe_background:
			pygame.draw.rect(self.screen,(0,0,0),(coords[0],coords[1],koko[0],koko[1]))
		self.screen.blit(text,(coords[0],coords[1]))
		if flippaa:
			pygame.display.flip()
	def draft_soldier(self,x,y):
		if self.data[self.gct(x,y)] != self.turn:
			return
			
		paivita = self.actorat(x,y)
		if paivita:
			if paivita.capital:
				return
			if paivita.voima == 6:
				return

		tulos = self.rek.count_capitals_on_island(x,y)
		if len(tulos[0]) == 1:
			actor = self.actorgctat(tulos[0][0])
			if actor:
				if actor.capital:
					if actor.massit > 0:
						actor.massit -= 1
						if not paivita:
							self.actors.add(TActor(x,y,actor.side,voima=1,capital=False))
						else:
							paivita.voima += 1
						self.salary_time_to_capitals_by_turn([self.turn],True)
	def end_turn(self):
		# CPU INTENSIVE?
		self.destroy_lonely_capitals()
		# CPU INTENSIVE?
		self.has_anyone_lost_the_game()
		# CPU INTENSIVE?
		# CPU INTENSIVE?
		
		# AT LAST BREAK THE FUCKING LOOP
		if self.check_and_mark_if_someone_won():
			self.turn = 0
			#self.playerlist = []
			self.data = {}
			self.actors.clear()
			self.fillmap(0)
			return
		
		for peluri in self.playerlist:
			if peluri.won:
				return
		
		self.turn += 1
		self.clean_deaders()
		
		# Check if all players are scheduled already
		if len(self.playerlist)+1 <= self.turn:
			# Naytetaan viimeisen pelaajan siirrot
			time.sleep(1.25)
			self.turn = 1
			for actori in self.actors:
				actori.moved = False
		
		# Eka tuhotaan ne omat mihin ei varaa (ja paiv. oma massitil.)
		self.salary_time_to_capitals_by_turn([self.turn],False)
		# Sitten paivitetaan kaikkien massitilanteet
		self.salary_time_to_capitals_by_turn(self.get_player_id_list(),True)
		# Is the current player holding an instance of
		# artificial intelligence? If so, act too.
		
		if len(self.playerlist) < self.turn:
			#print "Pelaajat loppuu kesken..."
			return
		
		if not self.playerlist:
			#print "Pelaajat loppuu kesken..."
			return
		
		if not self.get_player_by_side(self.turn):
			return
		
		yksikko = self.get_player_by_side(self.turn)
		
		if yksikko.ai_controller and not yksikko.lost:
			# Act here
			kolorissi = (self.sc["making_moves_text_color"][0],self.sc["making_moves_text_color"][1],self.sc["making_moves_text_color"][2])
			self.text_at("Player %s is making moves..."%(yksikko.nimi),
			(self.sc["making_moves_text_topleft_corner"][0],self.sc["making_moves_text_topleft_corner"][1]), flippaa = True, fontti=font3, wipe_background = False,
			vari = kolorissi)

			self.draw_scoreboard(True)
			self.buy_units_by_turn()
			act_dict = yksikko.ai_controller.act(self.ai_recursion_depth)


			self.drawmap()
			
			if self.show_cpu_moves_with_lines:
				for key,value in act_dict.iteritems():
					rivi1 = key.split(" ")
					rivi2 = value.split(" ")
					if self.seenxy(int(rivi1[0]),int(rivi1[1])):
						if self.seenxy(int(rivi2[0]),int(rivi1[1])):
							pixelX1,pixelY1 = self.hexMapToPixel(int(rivi1[0])-self.cursor.scroll_x,int(rivi1[1]))
							pixelX2,pixelY2 = self.hexMapToPixel(int(rivi2[0])-self.cursor.scroll_x,int(rivi2[1]))
							pygame.draw.line(self.screen, (255,0,0), (pixelX1+20,
							pixelY1+20),(pixelX2+20,pixelY2+20),2)
							if _DEBUG > 1:
								print rivi1,"",rivi2
			
			pygame.display.flip()
			
			# End of AI act
			self.end_turn()
		else:
			self.draw_scoreboard(True)
			# Pelaaja joka on havinny pelin ei pelaa
			if yksikko.lost:
				self.end_turn()
