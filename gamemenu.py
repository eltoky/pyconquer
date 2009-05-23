import pygame

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

class TGameMenu:
	def __init__(self,screen,bg_image,logo1,menuitems,(start_x,start_y),spacing = 50):
		self.valinta = 0
		self.menuitems = menuitems
		self.ruutu = screen
		self.used_font = pygame.font.Font("yanone_regular.otf",24)
		self.start_x = start_x
		self.start_y = start_y
		self.spacing = spacing
		self.menukuva = bg_image
		self.logo = logo1
	def draw_items(self, teksti=None):
		if self.menukuva:
			self.ruutu.blit(self.menukuva,(0,0))
		if self.logo:
			self.ruutu.blit(self.logo,(263,0))
		if teksti:
			self.text_at(teksti[0],(teksti[1],teksti[2]),self.used_font,wipe_background=True,vari=(255,255,255))
		for i,itemi in enumerate(self.menuitems):
			kolori = (0,0,0)
			if i == self.valinta:
				kolori = (255,0,0)
			teksti = itemi[0]
			if len(itemi[2]) >= 2:
				if itemi[2][0] == "value_int_editor":
					teksti = "%s (%d)" % (teksti, itemi[2][1])
				if itemi[2][0] == "value_bool_editor":	
					if itemi[2][1]:
						teksti = "%s (%s)" % (teksti, "on")
					else:
						teksti = "%s (%s)" % (teksti, "off")
			self.text_at(teksti,(self.start_x,self.start_y+self.spacing*i),
			self.used_font,vari = kolori, wipe_background=False)
			# Caption Text
		if self.menuitems[self.valinta][3]:
			self.text_at(self.menuitems[self.valinta][3],(400,75),self.used_font)
		self.text_at("Niko Reunanen, contact: nikoreunanen@gmail.com",(400,545)
		,self.used_font,vari=(50,185,10),wipe_background=False)
	def rullaa(self,dy):
		self.valinta += dy
		if self.valinta < 0: self.valinta = len(self.menuitems) - 1
		if self.valinta == len(self.menuitems): self.valinta = 0
	def edit_value(self,dv):
		if len(self.menuitems[self.valinta][2]) >= 2:
			if self.menuitems[self.valinta][2][0] == "value_int_editor":
				self.menuitems[self.valinta][2][1] += dv
				if len(self.menuitems[self.valinta][2]) >= 3:
					if self.menuitems[self.valinta][2][1] < self.menuitems[self.valinta][2][2][0]:
						self.menuitems[self.valinta][2][1] = self.menuitems[self.valinta][2][2][0]
					if self.menuitems[self.valinta][2][1] > self.menuitems[self.valinta][2][2][1]:
						self.menuitems[self.valinta][2][1] = self.menuitems[self.valinta][2][2][1]
			if self.menuitems[self.valinta][2][0] == "value_bool_editor":
				self.menuitems[self.valinta][2][1] = not self.menuitems[self.valinta][2][1]
	def get_selection(self,teksti = None):
		self.draw_items(teksti)
		kello = pygame.time.Clock()
		while 1 != 0:
			kello.tick(30)
			for e in pygame.event.get():
				if e.type == pygame.KEYDOWN:
					if e.key == pygame.K_DOWN:
						self.rullaa(1)
						self.draw_items(teksti)
					if e.key == pygame.K_UP:
						self.rullaa(-1)
						self.draw_items(teksti)
					if e.key == pygame.K_RETURN:
						tulos = self.select()
						return tulos
					if e.key == pygame.K_LEFT:
						self.edit_value(-1)
						self.draw_items(teksti)
					if e.key == pygame.K_RIGHT:
						self.edit_value(1)
						self.draw_items(teksti)
			pygame.display.flip()
	def text_at(self,teksti,coords,fontti,wipe_background=True,vari=(255,255,255),keskita=True,flippaa=False):
		text = fontti.render(teksti,1,vari)
		koko = fontti.size(teksti)
		if wipe_background:
			pygame.draw.rect(self.ruutu,(0,0,0),(coords[0]-(koko[0]/2),coords[1],koko[0],koko[1]))
		self.ruutu.blit(text,(coords[0]-(koko[0]/2),coords[1]))
		if flippaa:
			pygame.display.flip()
	def select(self):
		return self.menuitems[self.valinta][1]
