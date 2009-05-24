from os import sep,path

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

class TActor:
	def __init__(self,x,y,side,voima=1,capital=False):
		self.x = x
		self.y = y
		self.side = side
		self.voima = voima
		self.capital = capital
		self.massit = 0
		self.moved = False
		self.dead = False
		self.income = 0
		self.expends = 0

class TCursor:
	def __init__(self,board):
		self.x = 10
		self.y = 10
		self.scroll_x = 0
		self.chosen_actor = None
		self.chosen_capital = None
		self.board = board
		self.mouse_pos = (0,0)
	def scroll(self,dx):
		self.scroll_x += dx
		if self.scroll_x > 15:
			self.scroll_x = 15
		if self.scroll_x < 0:
			self.scroll_x = 0
	def click(self): #592 444
		if not self.board.map_edit_mode:
			if self.mouse_pos[0] >= self.board.sc["button_endturn"][0][0]:
				if self.mouse_pos[1] >= self.board.sc["button_endturn"][0][1]:
					if self.mouse_pos[0] <= self.board.sc["button_endturn"][1][0]:
						if self.mouse_pos[1] <= self.board.sc["button_endturn"][1][1]:
							self.board.end_turn()
			if self.mouse_pos[0] >= self.board.sc["button_quit"][0][0]:
				if self.mouse_pos[1] >= self.board.sc["button_quit"][0][1]:
					if self.mouse_pos[0] <= self.board.sc["button_quit"][1][0]:
						if self.mouse_pos[1] <= self.board.sc["button_quit"][1][1]:
							self.chosen_actor = None
							self.chosen_capital = None
							self.board.gamerunning = False
			if self.mouse_pos[0] < 573 and self.mouse_pos[1] < 444:
				if self.chosen_actor:
					self.board.try_to_conquer(self.chosen_actor,self.x,self.y,False)
					# CPU INTENSIVE?
					self.board.destroy_lonely_capitals()
					# CPU INTENSIVE?
					self.board.has_anyone_lost_the_game()
					# CPU INTENSIVE?
					if self.board.check_and_mark_if_someone_won():
						self.turn = 0
						#self.board.playerlist = []
						self.board.data = {}
						self.board.actors.clear()
						self.board.fillmap(0)
						return
				else:
					# Katsotaan onko klikattu omaa sotilasta
					klikki = self.board.actorat(self.x,self.y)
					if klikki:
						if not klikki.capital:
							if klikki.side == self.board.turn:
								# On, valitaan se
								self.chosen_actor = klikki
								return
						else:
							if klikki.side == self.board.turn:
								self.chosen_capital = klikki
								return
			self.chosen_actor = None
			self.chosen_capital = None
		else:
			if self.mouse_pos[0] >= 620:
				if self.mouse_pos[1] >= 366:
					if self.mouse_pos[0] <= 782:
						if self.mouse_pos[1] <= 416:
							self.board.write_edit_map(self.board.gamepath + "scenarios" + sep + self.board.text_input("[SAVE MAP] Map name?",(800/2-110,300),(240,45)))
			if self.mouse_pos[0] >= 618:
				if self.mouse_pos[1] >= 429:
					if self.mouse_pos[0] <= 782:
						if self.mouse_pos[1] <= 472:
							filessi = self.board.gamepath + "scenarios" + sep + self.board.text_input("[LOAD MAP] Map name?",(800/2-110,300),(240,45))
							if path.exists(filessi):
								self.board.load_map(filessi)
			if self.mouse_pos[0] >= 607:
				if self.mouse_pos[1] >= 560:
					if self.mouse_pos[0] <= 792:
						if self.mouse_pos[1] <= 591:
							self.board.gamerunning = False
			if self.mouse_pos[0] < 573 and self.mouse_pos[1] < 444:
				self.board.data[self.board.gct(self.x,self.y)] = self.board.map_edit_info[2]
	def get_color(self):
		if self.chosen_actor:
			return (255,0,0)
		else:
			return (255,255,255)
			
class TPlayer:
	def __init__(self,nimi1,id1,screen1,ai):
		self.nimi = nimi1
		self.id = id1
		self.screen = screen1
		self.lost = False
		self.won = False
		self.ai_controller = ai
		
class TIH:
	def __init__(self):
		self.images = {}
	def add_image(self,image,id):
		self.images[id] = image
	# Get Image
	def gi(self,id):
		if self.images.has_key(id):
			return self.images[id]
		else:
			# Menis aika huonosti taalla
			return None
