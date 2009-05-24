#!/usr/bin/python
# Niko Reunanen
# Conquer is strategy-flavoured game written with PyGame

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

import random,pygame,time,classcollection
from sys import path
from os import sep

_DEBUG = 0

pygame.init()
graphics_path = path[0] + sep + "images" + sep
pygame.display.set_icon(pygame.image.load(graphics_path+"soldier.png"))

from gameboard import TGB
import gamemenu

random.seed(round(time.time()))

IH = classcollection.TIH()
# Setting Release Version...
conquer_version = "0.1"

screeni = pygame.display.set_mode((800,600))
pygame.display.set_caption("Conquer " + conquer_version)
# Puristetaan tehoja irti < Translate please!!!
pygame.event.set_blocked(pygame.MOUSEMOTION)
screeni.fill((0,0,0))

# Sloppy, very sloppy... I know. Do you want to clean it?
temppi = pygame.image.load(graphics_path+"skull7.png").convert()
temppi.set_colorkey(temppi.get_at((0,0)))
IH.add_image(temppi,"skull")
temppi = pygame.image.load(graphics_path+"soldier.png").convert()
temppi.set_colorkey(temppi.get_at((0,0)))
IH.add_image(temppi,"soldier")
temppi = pygame.image.load(graphics_path+"rdump2.png").convert()
temppi.set_colorkey(temppi.get_at((0,0)))
IH.add_image(temppi,"capital")
temppi = pygame.image.load(graphics_path+"hextile2_.png").convert()
temppi.set_colorkey(temppi.get_at((0,0)))
IH.add_image(temppi,"1")
temppi = pygame.image.load(graphics_path+"hextile_.png").convert()
temppi.set_colorkey(temppi.get_at((0,0)))
IH.add_image(temppi,"2")
temppi = pygame.image.load(graphics_path+"hextile3_.png").convert()
temppi.set_colorkey(temppi.get_at((0,0)))
IH.add_image(temppi,"3")
temppi = pygame.image.load(graphics_path+"hextile4_.png").convert()
temppi.set_colorkey(temppi.get_at((0,0)))
IH.add_image(temppi,"4")
temppi = pygame.image.load(graphics_path+"hextile5_.png").convert()
temppi.set_colorkey(temppi.get_at((0,0)))
IH.add_image(temppi,"5")
temppi = pygame.image.load(graphics_path+"hextile6_.png").convert()
temppi.set_colorkey(temppi.get_at((0,0)))
IH.add_image(temppi,"6")
IH.add_image(pygame.image.load(graphics_path+"teksti.png").convert(),"logo")
IH.add_image(pygame.image.load(graphics_path+"mapedit.png").convert(),"mapedit")

gb = TGB(screeni,IH,path[0])
# Jos on customoitu skini niin pitaahan tietaa
paska = graphics_path+gb.sc.get("interface_filename","leiska.png")
IH.add_image(pygame.image.load(paska).convert(),"interface")
paska = graphics_path+gb.sc.get("menu_interface_filename","menu.png")
IH.add_image(pygame.image.load(paska).convert(),"menu_interface")

# We have nothing to lose if we try to use psyco.
try:
	import psyco
# If Psyco is not installed it is not a problem
except ImportError:
	if _DEBUG > 0:
		print "No psyco found, ok"
else:
	psyco.full()

mainmenu = gamemenu.TGameMenu(screeni, IH.gi("menu_interface"),IH.gi("logo"),
[("Play Scenario",0,[],"Play a premade map (scenarios-folder)"),
("Play Random Island",1,[],"Generate and play a random map"),
("Options",2,[],None),
("Map Editor",3,[],"Edit your own scenario"),
("Quit",4,[],None)],
(800/2-10,200), spacing = 60)

optionsmenu = gamemenu.TGameMenu(screeni, IH.gi("menu_interface"),IH.gi("logo"),
[("Show CPU moves with lines",0,["value_bool_editor",gb.show_cpu_moves_with_lines],"(Use left and right arrow key) Show CPU soldiers moves with lines."),
("CPU AI Recursion Depth",1,["value_int_editor",gb.ai_recursion_depth,[1,20]],"(Use left and right arrow key) Increase AI Recursion Depth: computer may play better but uses more CPU."),
("Return",2,[],None)],
(800/2-10,200), spacing = 60)

main_loop_running = True
while main_loop_running:
	tulos = mainmenu.get_selection()
	if tulos == 0:
		
		# Luodaan menu jossa listataan loydetyt skenaariot <- Translate please!!!
		scenarios = gb.read_scenarios()
		tuleva = []
		tuleva.append(("Back to Menu",0,[],None))
		for i,scenario in enumerate(scenarios):
			tuleva.append((scenario,i+1,[],None))
		newgamemenu = gamemenu.TGameMenu(screeni, IH.gi("menu_interface"),IH.gi("logo"),
		tuleva,
		(800/2-10,200), spacing = 30)
		
		muisti = newgamemenu.get_selection()
		if muisti > 0:
			gb.map_edit_mode = False
			gb.new_game(randommap = False, skenariofilu = newgamemenu.menuitems[muisti][0])
			gb.start_game()
	if tulos == 1:
		m1,m2 = gb.get_human_and_cpu_count()
		gb.map_edit_mode = False
		gb.new_game(randommap = True, humanplayers = m1, randomplayers_cpu = m2)
		gb.start_game()
	if tulos == 2:
		while 1:
			tulos2 = optionsmenu.get_selection()
			if tulos2 == 2:
				break
	if tulos == 3:
		# FIX!!! Vaha jarkevamma nakoseks <- Translate!!!
		m1,m2 = gb.get_human_and_cpu_count()
		gb.fillmap(0)
		gb.map_edit_mode = True
		gb.map_edit_info = [m1,m2,1]
		gb.actors.clear()
		gb.start_game()
		gb.map_edit_mode = False
		gb.map_edit_info = []
	if tulos == 4:
		main_loop_running = False
