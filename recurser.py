from sets import Set
import random

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

_DEBUG =0

class TRecurser:
	def __init__(self,board):
		self.board = board
		self.recursed_land = Set([])
		self.recursed_own_land_count = 0
	def count_capitals_on_island(self,x,y):
		# Initialize list to be used in crawling
		land_area_rec = Set([])
		capitals_coord_list = []
		puolisko = self.board.data[self.board.gct(x,y)]
		# Crawl from (x,y), save crawling to land_area_rec and
		# crawl for playerid found in map data at (x,y)
		self.crawl(x,y,land_area_rec,[self.board.data[self.board.gct(x,y)]])
		# Lets iterate through crawled places
		for coordinate in land_area_rec:
			# Check if current coordinate has a capital
			# (data can take the coordinate-string)
			actorinssi = self.board.actorgctat(coordinate)
			if (actorinssi):
				if actorinssi.capital:
					if actorinssi.side != puolisko:
						self.board.actors.remove(actorinssi)
					else:
						capitals_coord_list.append(coordinate)
		return [capitals_coord_list,land_area_rec]
	def recurse_new_random_coord_for_capital_on_island(self,x,y):
		land_area_rec = Set([])
		self.crawl(x,y,land_area_rec,[self.board.data[self.board.gct(x,y)]])
		# Check if island has area to affor capital
		if len(land_area_rec) > 1:
			# It has enough area
			return [random.choice(list(land_area_rec)),list(land_area_rec)]
		else:
			# Not enough area, be careful with handling the None
			return None
	def is_the_whole_earth_connected(self,max_x=30):
		# Figure out if every land is connected to other
		# 1) Count land area 2) Recurse through one random land
		# 3) If recurse count == land area -> one big continent
		land_area = self.board.count_world_area()
		if _DEBUG > 1:
			print "World area: %d" % land_area
		land_area_rec = Set([])
		
		if _DEBUG > 1:
			print playerlist
		for x in xrange(max_x):
			for y in xrange(14):
				if self.board.data[self.board.gct(x,y)] > 0:
					break
					
		if self.board.data[self.board.gct(x,y)] == 0:
			return False
					
		self.crawl(x,y,land_area_rec,[1,2,3,4,5,6])
		
		if len(land_area_rec) == land_area:
			return True
		else:
			return False
	def count_own_islands(self):
		# Count how many islands does player control
		laskuri = 0
		recursed_islands = Set([])
		for x in xrange(30):
			for y in xrange(14):
				if self.board.data[self.board.gct(x,y)] == self.board.turn:
					if self.board.gct(x,y) not in recursed_islands:
						self.recursed_own_land_count = 0
						self.crawl(x,y,recursed_islands,[self.board.turn])
						laskuri += 1
		return laskuri                         
	def recurse_own_island(self,x,y):
		# Count and recurse through own islands lands
		self.recursed_land.clear()
		self.recursed_own_land_count = 0
		self.crawl(x,y,self.recursed_land,[self.board.turn])
		return self.recursed_own_land_count
	def recurse_any_island(self,x,y):
		# Count and recurse through own islands lands
		xychosen = self.board.data[self.board.gct(x,y)]
		self.recursed_land.clear()
		self.recursed_own_land_count = 0
		self.crawl(x,y,self.recursed_land,[xychosen])
		return self.recursed_own_land_count
	def crawl(self,x,y,recursion_list,find_list):
		#SetHmmset SETS for recursion_list?? find_list???
		'''
		x,y -> coordinates to start "crawling"
		recursion_list -> list to hold already "crawled" coordinates
		find_list -> list of playerid-lands to be searched
		'''
		edm = self.board.get_right_edm(y)
		if self.board.validxy(x,y):
		# Onko oma maa (eli onko maan omistaja kuin board.turn)
		# koska nyt on menossa tan ai-instanssin vuoro
			if self.board.data[self.board.gct(x,y)] in find_list:
				# Katotaan ettie ruutu ole jo rekursoitu
				if self.board.gct(x,y) not in recursion_list:
					self.recursed_own_land_count += 1
					recursion_list.add(self.board.gct(x,y))
					for i in xrange(6):
						self.crawl(x+edm[i][0],y+edm[i][1],recursion_list,find_list)
