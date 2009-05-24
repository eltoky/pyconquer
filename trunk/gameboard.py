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
#    Copyright Conquer Development Team (http://code.google.com/p/pyconquer/)
#
#------------------------------------------------------------------------

_DEBUG = 0

# Six direction neighbourhood matrix for even y coordinates (0, 2, 4, ..., n % 2 = 0)
edm_eveny = (
(1,0),
(0,1),
(-1,1),
(-1,0),
(-1,-1),
(0,-1)
)

# Six direction neighbourhood matrix for odd y coordinates (0, 2, 4, ..., n % 2 = 1)
edm_oddy = (
(1,0),
(1,1),
(0,1),
(-1,0),
(0,-1),
(1,-1)
)

# Load four different fonts.
# FIXME: There could be a class that is a font container
font = pygame.font.Font(None, 12)
font2 = pygame.font.Font(None, 16)
font3 = pygame.font.Font(None, 24)
font4 = pygame.font.Font("yanone_regular.otf",20)

# The Game Board, ultimate class for game board and its logic
class TGB:
	def __init__(self,screen,ih,gp):
		# DATA is dictionary which has board pieces.
		# Keys: "x y" -> Use function gct to generate coordinate-text
		# Values: playerid; 0 = Empty Space, 1-6 are player id:s
		self.data = {}
		
		# How many "extra"-recursions cpu will make (max.) trying to figure out a good move
		self.ai_recursion_depth = 7
		
		# Pretty self-explanatory
		self.show_cpu_moves_with_lines = True
		
		# Pygame screen surface passed as "pointer" for drawing methods
		self.screen = screen
		
		# Fill the whole map with Empty Space. Now the DATA has coordinate keys and values
		self.fillmap(0)
		
		# Pointer to Picture Handler container class which has used pictures
		self.pics = ih
		
		# Current path
		self.gamepath = gp + os.sep
		
		# Instance of recurser engine
		self.rek = TRecurser(self)
		
		# Instance of cursor
		self.cursor = TCursor(self)
		self.cursor.x = 10
		self.cursor.y = 10
		
		# map_edit_info[0] = human player count in editable map
		# map_edit_info[1] = cpu player count in editable map
		# map_edit_info[2] = selected land in map editor
		self.map_edit_info = []
		self.map_edit_mode = False
		
		# Current turn
		self.turn = 1
		
		# List for cpu player names and load the names
		self.cpu_names = []
		self.load_cpu_names()
		
		# Tuple that is used at sorting scorelist
		self.pisteet_s = ()
		
		# If the game (actual map view) is running, gamerunning is True
		self.gamerunning = False
		
		# Skin configuration dictionary
		self.sc = {}
		
		# Actors set (set for optimization purposes) which holds every
		# instance of Actor-class (Soldiers and Dumps at the moment)
		self.actors = Set([])
		
		# Load the skin configuration file
		self.load_skin_file("skin")
		
		# List of current players in a game
		self.playerlist = []
	def load_cpu_names(self):
		# Read names from file to cpu name list
		file = open(self.gamepath+"cpu_player_names","r")
		for line in file.readlines():
			if line.endswith("\n"):
				self.cpu_names.append(line[:-1])
			else:
				self.cpu_names.append(line)
		file.close()
	def write_edit_map(self,filunimi):
		# Write edited map to file.
		# First six lines in map file are reserved for player info.
		file = open(filunimi,"w\n")
		# Add human players
		for i in range(self.map_edit_info[0]):
			file.write("player\n")
		# Add CPU players
		for i in range(self.map_edit_info[1]):
			file.write("ai\n")
		# Add absent players: 6 - ((Human Players) + (Cpu Players))
		# If 0 then "none\n" does not get written
		if (self.map_edit_info[0]+self.map_edit_info[1]) > 0:
			for i in range(6-(self.map_edit_info[0]+self.map_edit_info[1])):
				file.write("none\n")
		# Iterate keys and values in board DATA and write them (separated with |)
		for k1,k2 in self.data.iteritems():
			file.write("%s|%d\n"%(k1,k2))
		file.close() 
	def read_scenarios(self):
		# Get list of the scenario - folder's files
		return os.listdir(os.path.join(self.gamepath,"scenarios"))
	def load_skin_file(self,filename1):
		# Load configuration file and read it into sc - dictionary
		file = open(filename1,"r")
		for line in file.xreadlines():
			if not line:
				# Empty line, go to next
				continue
			else:
				if line[0] == "#":
					# Line is comment, go to next line
					continue
				if line.isspace():
					# Line is empty, go to next line
					continue
			
			# Copy the line, pretty useless expression		
			rivi = line
			
			# Cut newlines
			if rivi.endswith("\r\n"):
				rivi = rivi[:-1]
			if rivi.endswith("\n"):
				rivi = rivi[:-1]
			
			# Make lowercase and split
			rivi = rivi.lower()
			rivi = rivi.split(" ")
			
			# Configuration options into sc, read the skin file for more info
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
		
		# Instance of pygame's Clock
		clock = pygame.time.Clock()
		
		# The Main Loop to run a game
		while self.gamerunning:
			
			# Limit fps to 30, smaller resource usage
			clock.tick(30)
			
			# Iterate through events
			for eventti in pygame.event.get():
				# Mouse click
				if eventti.type == pygame.MOUSEBUTTONDOWN:
					x1,y1=self.pixelToHexMap(eventti.pos)
					# Scrolling included in calculations
					x1 += self.cursor.scroll_x
					# Coordinates into cursor's memory
					self.cursor.x,self.cursor.y = x1,y1
					self.cursor.mouse_pos = eventti.pos
					
					# Left mouse button = cursor's click
					if eventti.button == 1:
						self.cursor.click()
					# Right mouse button = draft and update soldiers if
					# NOT in map editing mode
					if not self.map_edit_mode:
						if eventti.button == 3:
							self.draft_soldier(self.cursor.x,self.cursor.y)
				# Key press
				if eventti.type == pygame.KEYDOWN:
					if eventti.key == pygame.K_LEFT:
						# Scroll screen left
						self.cursor.scroll(-1)
					if eventti.key == pygame.K_RIGHT:
						# Scroll screen right
						self.cursor.scroll(1)
						
					if not self.map_edit_mode:
						if eventti.key == pygame.K_m:
							self.show_own_units_that_can_move()
						if eventti.key == pygame.K_e:
							self.end_turn()
					else:
						# In map editor mode, UP and DOWN keys change
						# selected land
						if eventti.key == pygame.K_UP:
							self.map_edit_info[2] += 1
							if self.map_edit_info[2] > 6:
								self.map_edit_info[2] = 6
						if eventti.key == pygame.K_DOWN:
							self.map_edit_info[2] -= 1
							if self.map_edit_info[2] < 0:
								self.map_edit_info[2] = 0
				# Draw the scoreboard without calculating and sorting scores
				self.draw_scoreboard(False)
				# Draw the map
				self.drawmap()
				# Show the drawed content
				pygame.display.flip()
	def new_game(self,scenariofile="unfair",randommap = False, randomplayers_cpu = 3, humanplayers = 3):
		"""
		Makes everything ready for a new game. Call new_game before calling start_game.
		
		scenariofile -> Filename for scenario if randommap is set to False
		randomplayers_cpu -> CPU Player count in random generated map
		humanplayers -> Human Player count in random generated map
		"""
		
		# Status Quo Ante (bellum), Settings before war ;)
		self.turn = 1
		self.pisteet_s = ()
		self.playerlist = []
		self.map_edit_mode = False
		self.cursor.scroll_x = 0

		# If map is randomly generated, add players		
		if randommap:
			for i in xrange(humanplayers):
				self.playerlist.append(TPlayer("Player %d"%(i+1),i+1,self.screen,None))
			for i in xrange(randomplayers_cpu):
				self.playerlist.append(TPlayer("%s (cpu)"%(random.choice(self.cpu_names)),i+(humanplayers+1),self.screen,TAi(self)))
				
		# Clear data and actors from possible previous maps
		self.data = {}
		self.actors.clear()

		if randommap:
			# Generate random map
			self.generate_map(50,13)
		else:
			# Read a scenario
			self.load_map(os.path.join(self.gamepath,"scenarios")+os.sep+scenariofile)
			
		# Add resource dumps
		self.fill_dumps()
		
		# Calculate income and expends, and do changes for first players supplies
		self.salary_time_to_dumps_by_turn([1],False)
		
		# JUST ONLY calculate everyones supply income and expends
		self.salary_time_to_dumps_by_turn(self.get_player_id_list(),True)

		self.drawmap()
		# Calculate and sort scores and draw scores
		self.draw_scoreboard(True)
		
		pygame.display.flip()
		
		# If the first player is computer, make it act
		if self.playerlist[0].ai_controller:
			# The AI routines for CPU Player are called from it's AI-Controller
			self.playerlist[0].ai_controller.act(self.ai_recursion_depth)
			# FIXME, cpu intensive? Well anyway, make sure that dumps are on their places
			self.fill_dumps()
			# Next player's turn
			self.end_turn()
	def get_player_id_list(self):
		# Make a player-id - list and return it
		return [iteraatio.id for iteraatio in self.playerlist]
	def get_right_edm(self,y):
		# Selected right neighbourhood coordinate matrix
		if (y % 2) == 1:
			return edm_oddy
		else:
			return edm_eveny
	def get_player_by_name(self,playername):
		for player in self.playerlist:
			if player.nimi == playername:
				return player
		return None
	def gct(self,x,y):
		# One of the most called functions
		return "%d %d" % (x,y)
	def count_world_specific(self,id_list):
		laskuri = 0
		for key,value in self.data.iteritems():
			if value in id_list:
				laskuri += 1
		return laskuri
	def text_input(self, caption,(x1,y1),(w1,h1),onlynumbers=False):
		# Make an input-box and prompt it for input
		curstr = []
		pygame.draw.rect(self.screen,(30,30,30),(x1,y1,w1,h1))
		self.text_at(caption,(x1+w1/4,y1),fontti=font2,wipe_background=False)
		pygame.display.flip()
		while 1 != 0:
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
		# Count whole world's land count
		laskuri = 0
		for key,value in self.data.iteritems():
			if value > 0:
				laskuri += 1
		return laskuri
	def destroy_lonely_dumps(self):
		# Lonely soldiers will be terminated as well
		# Lets iterate through the set copy as we may alter the original set
		for actor in self.actors.copy():
			# Only alive soldiers
			if not actor.dead:
				# Select right matrix depending if actor.y is odd or even
				edm = self.get_right_edm(actor.y)
				found = False
				# If we find one (or more) friendly land next to soldier
				# or resource dump, actor will not be terminated.
				for i in xrange(6):
					# First check if coordinates are not out of borders
					if self.validxy(actor.x+edm[i][0],actor.y+edm[i][1]):
						if self.data[self.gct(actor.x+edm[i][0],actor.y+edm[i][1])] == actor.side:
							# If there is friendly land next to actor,
							# it is not isolated
							found = True
							break
				if not found:
					# Oh my :( The actor is isolated and it is discarded
					self.actors.discard(actor)
	def seenxy(self,x,y):
		# Return boolean value if the coordinate is seen by player
		# (not scrolled out of borders)
		return (x >= (0+self.cursor.scroll_x) and x <= (14+self.cursor.scroll_x))
	def validxy(self,x,y):
		# Valid coordinate is a coordinate which is found in data
		return self.data.has_key(self.gct(x,y))
	def try_to_conquer(self,actori,x2,y2,only_simulation):
		# This function is called everytime an actor tries to attack
		if actori.moved:
			# The soldier has already moved
			return
		
		# Tulos[0] -> Boolean value whether the target land is blocked
		# Tulos[1] ja Tulos[2] -> if target land is blocked, these
		# hold the coordinates for the reason of block.
		tulos = self.is_blocked(actori,x2,y2)
		
		# Is there an actor at target land?
		target = self.actorat(x2,y2)

		# The target is not blocked
		if not tulos[0]:
			
			# Check for lvl6 - battles
			# There is a target and no simulation is used
			# (meaning that try_to_conquer is not used in ai calculations)
			if target and not only_simulation:
				# Target is hostile and not a dump
				if not target.dump and target.side != actori.side:
					# Attacker and defender are level 6 soldiers
					if actori.level == 6 and target.level == 6:
						# 50% chance to win or loose
						if random.randint(1,2) == 1:
							# Attacker lost
							actori.x,actori.y,actori.dead=0,0,True
							self.actors.discard(actori)
							return

			# Both simulation and real attack makes changes to
			# land owner policy
			self.data[self.gct(x2,y2)] = actori.side

			# If simulating for AI, we don't want to make
			# changes directly to actors.
			if not only_simulation:
				# Not simulating, not blocked, attacker conquered
				# target land.
				actori.x,actori.y = x2,y2
				actori.moved = True
				if target:
					# If there was an actor (unit/dump) at target
					# land, it is discarded (destroyed)
					target.dead = True
					self.actors.discard(target)
				# Fix this to check one island (x2,y2) if dump merging needed
				self.fill_dumps()
		else:
			# Target is blocked, show the reason for blocking
			# but only if attacker is human player and seen on the screen
			if self.seenxy(tulos[1],tulos[2]) and not self.get_player_by_side(actori.side).ai_controller:
				# Clear selected actor
				self.cursor.chosen_actor = None
				# Convert (scrolled) hex map coordinates into screen pixels
				# and draw circle there
				pixelX,pixelY = self.hexMapToPixel(tulos[1]-self.cursor.scroll_x,tulos[2])
				pygame.draw.circle(self.screen,(0,255,0),(pixelX+20,pixelY+20),30,2)
				self.text_at(self.block_desc(tulos[3]),(pixelX,pixelY+15),fontti=font2)
				pygame.display.flip()
				# Little time to actually see it
				time.sleep(0.45)
				self.drawmap()
				pygame.display.flip()
	def block_desc(self,r):
		# Get reason for being blocked
		if r == "tooweak": return "Your soldier is too weak!"
		if r == "sameside": return "Target is friendly!"
		if r == "alreadymoved": return "Soldier has already moved!"
		if r == "spaceisnotlegal": return "Target is not land!"
		if r == "ownspacealreadyoccupied": return "Target is friendly!"
		if r == "outofisland": return "Out of soldiers reach!"
		return "Blocked."
	def get_player_by_side(self,side):
		# Self - explanatory
		for player in self.playerlist:
			if player.id == side:
				return player
		return None
	def merge_dumps(self,dump_coords,island_area):
		uusisumma = 0
		deletelist = []
		if len(dump_coords) > 1 and island_area:
			puoli = self.actorgctat(dump_coords[0]).side
			for coord in dump_coords:
				kalu = self.actorgctat(coord)
				if kalu:
					x11,y11 = self.ec(island_area[0])
					if kalu.dump and kalu.side==self.data[self.gct(x11,y11)]:
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
				new_shared_resource_dump = TActor(x11,y11,puoli,level=0,dump=True)
				new_shared_resource_dump.massit = uusisumma
				self.actors.add(new_shared_resource_dump)
	def fill_dumps(self):
		# Fill dumps should be called when lands are conquered
		# CPU INTENSIVE?

		# Keep count of already searched lands
		searched = Set([])
		
		# Get list of current non-lost players
		pelaajat = self.get_player_id_list()
		
		# Iterate DATA (coordinate and its player id)
		for xy,xy_pid in self.data.iteritems():

			# Is the coordinate already crawled
			if xy in searched:
				continue
				
			# Fill Dumps only for existing and not lost players
			if xy_pid not in pelaajat:
				continue

			x,y = self.ec(xy)			
						
			# Not empty space
			if xy_pid > 0:
				# Ask if the island has Dump and get also crawled coordinates
				# search_dumps[0] -> list of coordinates for islands dump(s)
				# search_dumps[1] -> set of coordinates (islands every land coordinate)
				search_dumps = self.rek.count_dumps_on_island(x,y)
				
				# Update crawled coordinates
				searched.update(search_dumps[1])

				# Check if the island has not Dump yet, island has at least
				# 2 pieces of land and island is owned by existing player.
				if not search_dumps[0] and len(search_dumps[1]) > 1:
					
					# Find a new place for dump:
					#	- get a random coordinate from crawled island
					paikka = random.choice(list(search_dumps[1]))
					
					if paikka:
						# If a place was found for dump, we'll add
						# a new dump in actors.
						kalu = paikka.split(" ")
						self.actors.add(TActor(int(kalu[0]),int(kalu[1]),self.data[paikka],dump=True))

				# More than one dump on island?
				elif len(search_dumps[0]) > 1:
					# Then we'll merge dumps on the island
					self.merge_dumps(search_dumps[0],list(search_dumps[1]))
	def fillmap(self, piece):
		# Self - explanatory
		self.data = {}
		for x in xrange(30):
			for y in xrange(14):
				self.data[self.gct(x,y)] = piece
	def actorgctat(self,gctee):
		# Self - explanatory
		gctee = gctee.split(" ")
		return self.actorat(int(gctee[0]),int(gctee[1]))
	def actorat(self,x,y):
		# Search actor - instances by coordinates
		for actori in self.actors:
			if actori.x==x and actori.y==y:
				return actori
		# No actor found, return None
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
					self.actors.add(TActor(x,y,self.data[self.gct(x,y)],level=random.randint(1,3)))
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
		# This function is obsolete
		return self.data.values().count(for_who)
	def ec(self,gctee):
		# Self - explanatory
		tmp = gctee.split(" ")
		return (int(tmp[0]),int(tmp[1]))
	def draw_scoreboard(self,update=False):
		"""
		Draw Scoreboard
		update -> If true, scores are calculated and sorted
		"""
		if update:
			# Update scores
			scores = {}
			for peluri in self.playerlist:
				if not peluri.lost:
					# Count existing players land count
					scores[peluri] = self.whole_map_situation_score(peluri.id)
			# Sort points
			self.pisteet_s = sorted(scores.iteritems(), key=itemgetter(1))
			
		# Iterate every player
		for player in self.playerlist:
			# Check if a player has won
			if player.won:
				# a Player has won, show the information
				self.cursor.chosen_actor = None
				self.cursor.chosen_dump = None
				if player.ai_controller:
					self.text_at("Player %s won the game!" % player.nimi,(200,200),fontti=font4,vari=(255,255,255)) 
				else:
					self.text_at("You (%s) won the game!" % player.nimi,(200,200),fontti=font4,vari=(255,255,255))

		counter = 0
		# Draw the scores, counter puts text in right row.
		# Skin configuration file is used here
		for jau in reversed(self.pisteet_s):
			# I splitted the lines here, see the last comma
			self.screen.blit(self.pics.gi("%d"%jau[0].id),(self.sc["scoreboard_text_topleft_corner"][0],
			self.sc["scoreboard_text_topleft_corner"][1]+35*counter-13))
			
			self.text_at("%d     %s" % (jau[1],jau[0].nimi),(self.sc["scoreboard_text_topleft_corner"][0]+15,
			
			self.sc["scoreboard_text_topleft_corner"][1]+35*counter),vari=(self.sc["scoreboard_text_color"][0],
			self.sc["scoreboard_text_color"][1],self.sc["scoreboard_text_color"][2]),fontti=font4,wipe_background = False)
			
			counter += 1
		try:
			# Lost players are discarded from playerlist, so next line
			# may make and error. Thats why the try - expression.
			tahko = self.get_player_by_side(self.turn)
			# Human player
			if not tahko.ai_controller:
				if not tahko.lost:
					# Human player's turn, tell it
					self.text_at("Your (%s) turn" % (tahko.nimi),(630,300),vari=(0,0,0),
					fontti=font3,wipe_background = False)
				else:
					# The human player has lost, tell it
					self.text_at("You (%s) lost..." % (tahko.nimi),(635,300),vari=(0,0,0),
					fontti=font3,wipe_background = False)
		except:
			# Error concured, well do nothing about it...
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
		# Extra drawing routines for scenario editing mode
		
		# Text for selected map tile
		if self.map_edit_info[2] == 0:
			teksti = "Eraser"
		else:
			if self.map_edit_info[2] <= (self.map_edit_info[0] + self.map_edit_info[1]):
				teksti = "Player #%d land" % self.map_edit_info[2]
			else:
				# Land without player in the map, good for connecting player
				# islands in own maps.
				teksti = "Land #%d without player" % self.map_edit_info[2]

		# Show the selected map tile text		
		self.text_at("Selected:",(620,80), fontti = font4, wipe_background=False,vari=(0,0,0))
		self.text_at(teksti,(620,100), fontti = font4, wipe_background=False,vari=(0,0,0))
		
		# Draw players captions in the scenario
		counter = 0
		for i in xrange(0,self.map_edit_info[0]):
			counter += 1
			self.text_at("Player #%d = Human"%counter,(620,130+counter*20), fontti = font4, wipe_background=False,vari=(0,0,0))
		for i in xrange(0,self.map_edit_info[1]):
			counter += 1
			self.text_at("Player #%d = CPU" % counter,(620,130+counter*20), fontti = font4, wipe_background=False,vari=(0,0,0))
		if (6-counter) > 0:
			for i in range(0,(6-counter)):
				counter += 1
				self.text_at("Player #%d = No player" % counter,(620,130+counter*20), fontti = font4, wipe_background=False,vari=(0,0,0))
	def drawmap(self):
		"""
		Game window's drawing routines
		"""
		
		# Draw the correct interface
		if not self.map_edit_mode:
			# Game interface
			self.screen.blit(self.pics.gi("interface"),(0,0))
			self.draw_scoreboard(False)
		else:
			# Map editing interface
			self.screen.blit(self.pics.gi("mapedit"),(0,0))
			self.draw_map_edit_utilities()
		
		# Loop pieces to be drawn (horizontally there is scrolling too)
		for x in xrange(self.cursor.scroll_x,15+self.cursor.scroll_x):
			for y in xrange(14):
				# There is land to draw
				if self.data[self.gct(x,y)] > 0:
					
					# Get pixel coordinates
					pixelX,pixelY = self.hexMapToPixel(x-self.cursor.scroll_x,y)
					
					# Draw the piece
					self.screen.blit(self.pics.gi(str(self.data[self.gct(x,y)])),(pixelX,pixelY))
					
					# Check if actor is found at the coordinates
					actor = self.actorat(x,y)
					if actor:
						if actor.dump:
							# a Resource Dump was found
							self.screen.blit(self.pics.gi("dump"),(pixelX+3,pixelY+5))
							
							# If the dump is on our side and we are not AI controlled, then we'll
							# draw the supply count on the dump.
							if actor.side == self.turn and not self.get_player_by_side(actor.side).ai_controller:
								self.text_at("%d"%actor.massit,(pixelX+14,pixelY+17),fontti=font2)
						else:
							# a Soldier was found
							# Make a text for soldier-> level and X if moved
							teksti = "%d" % actor.level
							if actor.moved:
								teksti = teksti + "X"
							# Draw soldier
							self.screen.blit(self.pics.gi("soldier"),(pixelX+10,pixelY+10))
							# Draw text for the soldier
							self.text_at(teksti,(pixelX+20,pixelY+20),fontti=font)
		# If an actor is selected, then we'll draw red box around the actor
		if self.cursor.chosen_actor:
			pixelX,pixelY = self.hexMapToPixel(self.cursor.x-self.cursor.scroll_x,self.cursor.y)
			pygame.draw.rect(self.screen,self.cursor.get_color(),(pixelX,pixelY,40,40),2)
		
		# If an dump is chosen, we'll draw information about it:
		#   Income, Expends, Supplies
		if self.cursor.chosen_dump:
			kolorissi = (self.sc["unit_status_text_color"][0],self.sc["unit_status_text_color"][1],self.sc["unit_status_text_color"][2])
			x1,y1 = self.sc["unit_status_text_topleft_corner"][0],self.sc["unit_status_text_topleft_corner"][1]
			self.text_at("Resource dump",(x1,y1+30),fontti=font4,wipe_background=False,vari=kolorissi)
			self.text_at("Income: %d" % self.cursor.chosen_dump.income,(x1,y1+50),fontti=font4,wipe_background=False,vari=kolorissi)
			self.text_at("Expends: %d" % self.cursor.chosen_dump.expends,(x1,y1+70),fontti=font4,wipe_background=False,vari=kolorissi)
			self.text_at("Supplies: %d" % self.cursor.chosen_dump.massit,(x1,y1+90),fontti=font4,wipe_background=False,vari=kolorissi)
			self.screen.blit(self.pics.gi("dump"),(x1,y1))
	def get_human_and_cpu_count(self):
		# This is very ugly piece of code.
		# It ask for scenario editing and random generated map,
		# how many human and cpu players will participate.
		# FIXME: make this look good...
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
		# Check is coordinate(x,y) is blocked for actor actori
		
		defender = self.actorat(x,y)
		if defender:
			# There is a defending unit at target
			if actori.level < 6:
				if defender.level >= actori.level:
					return [True,x,y,"tooweak"]
					
			if defender.dump and actori.level < 2:
				return [True,x,y,"tooweak"]
			if actori.side == defender.side:
				return [True,x,y,"sameside"]

		# Soldier can move only once a turn
		if actori.moved:
			return [True,x,y,"alreadymoved"]
			
		# Empty Space can't be conquered
		if self.data[self.gct(x,y)] == 0:
			return [True,x,y,"spaceisnotlegal"]

		# One can't conquer his own soldiers			
		if self.data[self.gct(x,y)] == self.turn:
			if defender:
				return [True,x,y,"ownspacealreadyoccupied"]
			
		# Set that holds recursed land piece coordinates	
		crawl_list = Set([])
		
		# Recurse every land on the island where attacking soldier is
		self.rek.crawl(actori.x,actori.y,crawl_list,[self.turn])
		
		found = False
		edm = self.get_right_edm(y)
		for i in xrange(6):
			if self.validxy(x+edm[i][0],y+edm[i][1]):
				# Next to target must be own land. The land must be
				# from the same island as the actor is from.
				if self.gct(x+edm[i][0],y+edm[i][1]) in crawl_list:
					found = True
		if not found:
			# No adjacent lands found, can't conquer places out of
			# soldier's reach
			return [True, x, y, "outofisland"]
			
		# Check for enemy unit blockers
		for i in xrange(6):
		# Is the coordinate valid?
			if self.validxy(x+edm[i][0],y+edm[i][1]):
			# Is the targets neighbour same side as the target
				if self.data[self.gct(x+edm[i][0],y+edm[i][1])] == self.data[self.gct(x,y)]:
					# Has the neighbourds adjacent own piece a soldier defending?
					defenderi = self.actorat(x+edm[i][0],y+edm[i][1])
					if defenderi:
						# Yes it has
						if defenderi.side != actori.side:
							if defenderi.dump:
								# Dump can defend against level 1 soldiers
								if actori.level == 1:
									# Attacker is level 1, blocked = True
									return [True, x+edm[i][0], y+edm[i][1],"tooweak"]
							if actori.level < 6:
								# Attacker's level is under 6, check if
								# defender is weaker. (level 6 can attack
								# where-ever it wants)
								if defenderi.level >= actori.level:
									# Attacker's soldier is weaker than defender,
									# blocked=True
									return [True, x+edm[i][0], y+edm[i][1],"tooweak"]
		# Found nothing that could block attacker,
		# blocked = False !!! The move is legal.
		return [False,0,0,"legal"]
	def generate_map(self,minsize,max_x):
		# Generate simple random map
		self.fillmap(0)
		ok = False
		while not ok:
			self.fill_random_boxes(1,[1,2,3,4,5,6],max_x)
			if self.rek.is_the_whole_earth_connected(max_x=max_x) and self.count_world_area() >= minsize:
				ok = True
		self.fill_dumps()
		self.salary_time_to_dumps_by_turn(self.get_player_id_list(),True)
	def clean_deaders(self):
		# Clean dead actors, this is obsolete
		for actori in self.actors.copy():
			if actori.dead:
				self.actors.discard(actori)
	def buy_units_by_turn(self):
		"""
		This function buys and updates soldiers for CPU Players.
		FIXME: The right place for this would be ai.py
		"""
		
		# This is VERY MESSY function, cleaning will be done sometime
		
		# Iterate through a copy as original actors is probably going to be modified
		for city in self.actors.copy():

			# Alive Dump & current turn player's & has (supplies > 0)
			if not city.dead and city.dump and city.massit > 0 and city.side == self.turn:
				
				# Has the island space for a new soldier?
				# tulos[0] new random place for actor (not checked if legal)
				# tulos[1] island's land coordinates
				tulos = self.rek.recurse_new_random_coord_for_dump_on_island(city.x,city.y)
				
				# No space for actor
				if not tulos:
					continue
				
				# 500 tries to find a place for actor
				ok = False
				tries = 0
				while not ok and tries < 500:
					tries += 1
					tulos[0] = random.choice(tulos[1]) 
					if not self.actorgctat(tulos[0]):
						ok=True
				if tries == 500:
					ok = False

				# Count the amount of lvl<6 soldiers on the island						
				levellista = []
				soldiercounter = 0
				soldiercounter2 = 0
				ykkoscount = 0
				for gctee in tulos[1]:
					hei = self.actorgctat(gctee)
					if hei:
						if hei.side==self.turn and not hei.dump and not hei.dead:
							soldiercounter2 += 1
							if hei.level == 1:
								ykkoscount += 1
							if hei.level < 6:
								soldiercounter += 1
								levellista.append(hei.level)

				# Does the island has upgradable soldiers (lvl<6)?
				if soldiercounter != 0:
					# When the island has soldiers, it is more likely
					# to update them. 66% chance to update existing
					# soldiers.
					if random.randint(1,3) != 2:
						ok = False
				
				vapaat_maat = []
				for gctee in tulos[1]:
					if not self.actorgctat(gctee):
						vapaat_maat.append(gctee)
				
				# Do we have any soldiers at all?
				if soldiercounter2 != 0:
					# We do, count how many free lands there are per soldier
					suhde = len(vapaat_maat) / soldiercounter2
					# If three or more, we need new soldiers
					if suhde >= 3:
						ok = False
						while not ok and tries < 500:
							tries += 1
							tulos[0] = random.choice(tulos[1]) 
							if not self.actorgctat(tulos[0]):
								ok=True
					# We have probably enough soldiers so update them
					if suhde <= 2:
						ok = False
									
				# BUT If we have upgradable soldiers AND over half of the
				# possible attack targets need better soldiers, we'll
				# update soldiers :)
				# FIXME: pretty complicated
				paatos = False
				tooweakcount = 0
				a_searched = []
				if soldiercounter > 0:
					urpo = TActor(0,0,self.turn,level=0,dump=False)
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
									for haastaja in levellista:
										urpo.level = haastaja
										if self.is_blocked(urpo,xy[0]+edm[i][0],xy[1]+edm[i][1])[3] == "tooweak":
											found_hardguy -= 1
									if found_hardguy == 0:
										tooweakcount += 1
					if (float(tooweakcount) / float(len(a_searched))) >= 0.3:
						ok = False
						paatos = True
					if urpo:
						urpo = None
				
				# But if we don't have any soldiers, we'll buy them...
				if soldiercounter2 == 0:
					ok = True

				# We still shouldn't buy too much
				if (city.income - city.expends) < 1:
					return
				
				# Not enough supplies?
				if city.massit < 1:
					return
					
				if ok:
					# Okay, WE WILL BUY NEW SOLDIERS
					m11 = random.randint(0,1)
					m22 = random.randint(0,1)
					# Little variation...
					while city.massit > m11 and (city.income-city.expends) > m22:
						ok2 = False
						while not ok2 and tries < 500:
							tries += 1
							tulos[0] = random.choice(tulos[1]) 
							if not self.actorgctat(tulos[0]):
								ok2=True
						if ok2:
							# Add new soldier and make financial calculus
							city.massit -= 1
							city.expends += 1
							city.income -= 1
							tulos1 = tulos[0].split(" ")
							self.actors.add(TActor(int(tulos1[0]),int(tulos1[1]),city.side,level=1,dump=False))
					# If we didn't buy with every supplies, we can update soldiers
					if m11 or m22:
						self.update_own_soldiers(city,tulos,ykkoscount,soldiercounter2,paatos)
				if not ok:
					self.update_own_soldiers(city,tulos,ykkoscount,soldiercounter2,paatos)
	def update_own_soldiers(self,city,tulos,ykkoscount,soldiercounter2,paatos):
		# Update soldiers with supplies
		tries = 0
		
		# When we'll stop?
		critical_cash = 0
		
		running = True
		# We'll update as long as supplies are used or panic has arisen
		while city.massit > critical_cash and running:
			tries += 1
			# We'll try one hundred times
			if tries == 100:
				running = False
			
			# Iterate through actors
			for ukko in self.actors:
				# Panic - button has been pressed ;)
				if not running:
					continue
					
				# Do we still have income...?
				if (city.income - city.expends) > 0:
					# Self - explanatory
					if self.gct(ukko.x,ukko.y) in tulos[1] and not ukko.dump and not ukko.dead and ukko.side == city.side:
						# Level 6 are not updated, level 1 have better chance to be updated.
						# But if we just need better soldiers we'll update everyone (paatos).
						if ukko.level < 6:
							# Level 1 soldiers found
							if ykkoscount > 0 and (soldiercounter2-ykkoscount) > 0:
								if ukko.level != 1:
									# No critical need for updates?
									if not paatos:
										# 33% change to update 1<lvl<6
										if random.randint(1,3) != 2:
											# Ykkosille enemman prioriteettia
											continue
							
							# Soldier is updated
							city.expends += 1
							city.massit -= 1
							ukko.level += 1
							# Panic with supplies?
							if city.massit <= critical_cash:
								running = False
							if (city.income - city.expends) == critical_cash:
								running = False
	def check_and_mark_if_someone_won(self):
		# If only one player has lost==False, he is winner
		no_losers = [z for z in self.playerlist if not z.lost]
		if len(no_losers) == 1:
			no_losers[0].won = True
			return True
		return False

	def load_map(self,mapo):
		"""
		Load a map from file
		"""
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
		# Check if anyone has recently lost the game:
		#	- not marked as lost and has 0 dumps
		for possible_new_loser in self.playerlist:
			if self.count_dumps_on_world(possible_new_loser.id) == 0 and not possible_new_loser.lost:
				possible_new_loser.lost = True
	def count_dumps_on_world(self,pid):
		# Self - explanatory
		tulos = 0
		for actor in self.actors:
			if actor.dump and actor.side == pid and not actor.dead:
				tulos += 1
		return tulos
	def show_own_units_that_can_move(self):
		# Draw own units that have not moved yet
		for actor in self.actors:
			if not actor.moved and actor.side == self.turn and not actor.dump:
				if self.seenxy(actor.x,actor.y):
					pixelX,pixelY = self.hexMapToPixel(actor.x-self.cursor.scroll_x,actor.y)
					pygame.draw.circle(self.screen,(255,255,20),(pixelX+20,pixelY+20),20,3)
		pygame.display.flip()
		time.sleep(0.5)
		self.drawmap()
	def salary_time_to_dumps_by_turn(self,sidelist,just_do_math=False):
		"""
		Calculate dumps income,expend and supplies. Kill soldiers without supplies.
		just_do_math -> if true, only income and expend are calculated
		"""
		
		koordilista = []
		mahdollinen_kuolema = []
		kuolema = []
		koordilista = Set([])
		for kaupunki in self.actors:
			mahdollinen_kuolema = []
			koordilista.clear()
			tulot = 0
			menot = 0
			if not kaupunki.dead and kaupunki.dump and kaupunki.side in sidelist:
				self.rek.crawl(kaupunki.x,kaupunki.y,koordilista,[kaupunki.side])
				tulot = len(koordilista)
				for otus in self.actors:
					# Soldiers are costly for dump
					if self.gct(otus.x,otus.y) in koordilista and not otus.dump:
						menot += 1
					if not otus.dead and not otus.dump and otus.side == kaupunki.side:
						if self.gct(otus.x,otus.y) in koordilista:
							mahdollinen_kuolema.append(otus)
							menot += otus.level
				kaupunki.income = tulot
				kaupunki.expends = menot
				if not just_do_math:
					kaupunki.massit += (kaupunki.income - kaupunki.expends)
					if kaupunki.massit < 0:
						# Not enough supplies, islands soldiers are going
						# to be terminated.
						kuolema.extend(mahdollinen_kuolema)
						
		if not just_do_math:
			
			# Kill every soldier that doesn't have enough supplies
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
		# Render text
		text = fontti.render(teksti,1,vari)
		koko = fontti.size(teksti)
		if wipe_background:
			pygame.draw.rect(self.screen,(0,0,0),(coords[0],coords[1],koko[0],koko[1]))
		self.screen.blit(text,(coords[0],coords[1]))
		if flippaa:
			pygame.display.flip()
	def draft_soldier(self,x,y):
		# Soldier drafting function used by human player
		if self.data[self.gct(x,y)] != self.turn:
			return
			
		paivita = self.actorat(x,y)
		if paivita:
			if paivita.dump:
				return
			if paivita.level == 6:
				return

		tulos = self.rek.count_dumps_on_island(x,y)
		if len(tulos[0]) == 1:
			actor = self.actorgctat(tulos[0][0])
			if actor:
				if actor.dump:
					if actor.massit > 0:
						actor.massit -= 1
						if not paivita:
							self.actors.add(TActor(x,y,actor.side,level=1,dump=False))
						else:
							paivita.level += 1
						self.salary_time_to_dumps_by_turn([self.turn],True)
	def end_turn(self):
		# CPU INTENSIVE?
		self.destroy_lonely_dumps()
		# CPU INTENSIVE?
		self.has_anyone_lost_the_game()
		
		if self.check_and_mark_if_someone_won():
			# If someone won, break the recursion loop
			self.turn = 0
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
			# Show last player's moves
			time.sleep(1.25)
			self.turn = 1
			# Every actor's "moved" is reseted
			for actori in self.actors:
				actori.moved = False
		
		# Update salaries and kill own unsupplied soldiers
		self.salary_time_to_dumps_by_turn([self.turn],False)
		# Update everyones salaries
		self.salary_time_to_dumps_by_turn(self.get_player_id_list(),True)
		
		# Check for errors
		if len(self.playerlist) < self.turn:
			return
		
		if not self.playerlist:
			return
		
		if not self.get_player_by_side(self.turn):
			return
		
		yksikko = self.get_player_by_side(self.turn)
		
		# Is the current player holding an instance of
		# artificial intelligence? If so, act too.
		if yksikko.ai_controller and not yksikko.lost:
			# Act here
			kolorissi = (self.sc["making_moves_text_color"][0],self.sc["making_moves_text_color"][1],self.sc["making_moves_text_color"][2])
			self.text_at("Player %s is making moves..."%(yksikko.nimi),
			(self.sc["making_moves_text_topleft_corner"][0],self.sc["making_moves_text_topleft_corner"][1]), flippaa = True, fontti=font3, wipe_background = False,
			vari = kolorissi)

			self.draw_scoreboard(True)
			
			# Ai buys and updates soldiers
			self.buy_units_by_turn()
			
			# Here the AI makes moves
			act_dict = yksikko.ai_controller.act(self.ai_recursion_depth)


			self.drawmap()
			
			# Draw CPU player's moves
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
			# If the human player has lost game, he is not going to play
			if yksikko.lost:
				self.end_turn()
