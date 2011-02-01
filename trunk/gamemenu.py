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
#    Copyright Conquer Development Team (http://code.google.com/p/pyconquer/)
#
#------------------------------------------------------------------------

class TGameMenu:
	def __init__(self,screen,bg_image,logo1,menuitems,(start_x,start_y),spacing = 50):
		# Currently selected menuitem's index
		self.valinta = 0
		# List of menuitems
		self.menuitems = menuitems
		# Pointer to pygame screen
		self.ruutu = screen
		# Font to be used with the menu
		self.used_font = pygame.font.Font("yanone_regular.otf",24)
		# Coordinates where to render the menu
		self.start_x = start_x
		self.start_y = start_y
		# Space between menuitems
		self.spacing = spacing
		# Background picture is oddly here as well the top logo
		self.menukuva = bg_image
		self.logo = logo1
	def draw_items(self, teksti=None):
		# If images and/or text are supplied, draw them
		if self.menukuva:
			self.ruutu.blit(self.menukuva,(0,0))
		#Logo in BackGround now
		#if self.logo:			
			#self.ruutu.blit(self.logo,(263,0))
		if teksti:
			self.text_at(teksti[0],(teksti[1],teksti[2]),self.used_font,wipe_background=True,vari=(255,255,255))
		
		# Iterate through menu items
		for i,itemi in enumerate(self.menuitems):
			# FIXME: skinnable colors
			
			# Menu item color is white
			kolori = (0,0,0)
			shadow = True
			if i == self.valinta:
				# Selected menu item is red
				shadow = False
				kolori = (255,255,255)
			
			# Text to be rendered
			teksti = itemi[0]
			
			# Check if menu items are value editors
			if len(itemi[2]) >= 2:
				if itemi[2][0] == "value_int_editor":
					teksti = "%s (%d)" % (teksti, itemi[2][1])
				if itemi[2][0] == "value_bool_editor":	
					if itemi[2][1]:
						teksti = "%s (%s)" % (teksti, "on")
					else:
						teksti = "%s (%s)" % (teksti, "off")
			
			# Draw the menu item text
			self.text_at(teksti,(self.start_x,self.start_y+self.spacing*i),
			self.used_font,vari = kolori, wipe_background=False, drop_shadow = shadow)
			
		# Caption Text
		if self.menuitems[self.valinta][3]:
			# It has caption text, draw it
			self.text_at(self.menuitems[self.valinta][3],(400,75),self.used_font)
			
		# Some info :)
		self.text_at("Contact:", (400,520), self.used_font, vari = (50,185,10), wipe_background = False)
		self.text_at("Conquer Dev Team http://pyconquer.googlecode.com/",(400,545)
		,self.used_font,vari=(50,185,10),wipe_background=False)
	def rullaa(self,dy):
		# Change the selected menu item
		self.valinta += dy
		if self.valinta < 0: self.valinta = len(self.menuitems) - 1
		if self.valinta == len(self.menuitems): self.valinta = 0
	def edit_value(self,dv):
		# This is totally unreadable :D
		# Well it edits values in their border values
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
		"""
		Render the menu as long as user selects a menuitem
		teksti -> optional text to be rendered
		"""
		
		# Draw the items
		self.draw_items(teksti)
		
		# Create instance of pygame Clock
		kello = pygame.time.Clock()
		
		# Endless loop
		while 1 != 0:
			
			# Limit fps to 30
			kello.tick(30)
			
			# Iterate through events
			for e in pygame.event.get():
				if e.type == pygame.KEYDOWN:
					if e.key == pygame.K_DOWN:
						self.rullaa(1)
						self.draw_items(teksti)
					if e.key == pygame.K_UP:
						self.rullaa(-1)
						self.draw_items(teksti)
					if e.key == pygame.K_RETURN or e.key == pygame.K_KP_ENTER:
						tulos = self.select()
						return tulos
					if e.key == pygame.K_LEFT:
						self.edit_value(-1)
						self.draw_items(teksti)
					if e.key == pygame.K_RIGHT:
						self.edit_value(1)
						self.draw_items(teksti)
			pygame.display.flip()
	def text_at(self,teksti,coords,fontti,wipe_background=True,drop_shadow=True,vari=(255,255,255),keskita=True,flippaa=False):
		text = fontti.render(teksti,1,vari)
		koko = fontti.size(teksti)
		if wipe_background:
			pygame.draw.rect(self.ruutu,(0,0,0),(coords[0]-(koko[0]/2),coords[1],koko[0],koko[1]))

		# Shadow
		if drop_shadow:
			shadow_text_ = fontti.render(teksti,1,(255 - vari[0],255 - vari[1],255 - vari[2]))
			self.ruutu.blit(shadow_text_,(coords[0]-(koko[0]/2)+1,coords[1]+1))

		self.ruutu.blit(text,(coords[0]-(koko[0]/2),coords[1]))
		if flippaa:
			pygame.display.flip()
	def select(self):
		# User selects a menu item
		return self.menuitems[self.valinta][1]
