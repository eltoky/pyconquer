_DEBUG = 0

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

import time,random

class TAi:
	def __init__(self,board):
		'''board -> TGameBoard instance which is the parent'''
		self.board = board
		# Dict joka kertoo mitka koordinaatit on jo rekursoitu
		# recurse_own_land - funktiolla
	def act(self,depth):
		# Lista suoritetuille liikkeille joka palautetaan
		act_list = {}
		# Pisteita voisi saada pinta-alan lisaksi siita
		# jos sattuu imasee vihun sotilaan
		if _DEBUG > 0:
			print "It is me, the computer here!"
		# 1. Pystyyko suoraan yhdistaa ison alueen
		# Jos len(pisteet) > depth niin valittu siirto on keskimaaraista
		# tuottavampi siirto.
		# Pisteiden keskiarvonnan laskentaan otetaan pisteet ylos
		# Vanha lauta talteen
		for current_actor in self.board.actors.copy():
			if current_actor.dead:
				continue
			if ((current_actor.capital == False) and (current_actor.moved == False) and (current_actor.side == self.board.turn)):
				# Muistipaikat loydetylle siirrolle
				m_x = None
				m_y = None
				# Aloituspisteena toimii oman saaren koko
				# NOLLA NYT
				#m_p = self.board.rek.recurse_own_island(current_actor.x,current_actor.y)
				m_p = 0
				# Onko aloituspalan playerid oma ja onko sotilas siina ja onko se jo liikkunut
				varmuuskopio = self.board.data.copy()
				pisteet = []
				koords = []
				loppulaskija = 0
				found_not_brute_force_solution = False
				# Sotilaan siirtoja katellaan
				kalunimimuna1 = range(30)
				random.shuffle(kalunimimuna1)
				for x2 in kalunimimuna1:
					if found_not_brute_force_solution:
						continue
					kalunimimuna2 = range(14)
					random.shuffle(kalunimimuna2)
					for y2 in kalunimimuna2:
						if found_not_brute_force_solution:
							continue
						# Mahdollisen siirron pala
						pala2 = self.board.data[self.board.gct(x2,y2)]
						#actorinssi_vihu = self.board.actorat(x2,y2)
						# Halutaan valloittaa viholliselta
						if ((pala2 != self.board.turn) and (pala2 != 0)):
							# Jos siirto sinne on mahdollista
							blokkastu = self.board.is_blocked(current_actor,x2,y2)
							if _DEBUG > 1:
								print blokkastu
							if blokkastu[0] == False:
								# Yritetaan vallata vihollisen vallattavissa oleva maa
								self.board.try_to_conquer(current_actor,x2,y2,True)
								
								# ITSE KAIKEN PAHAN ALKU JA JUURI
								# SIIRRON PISTEET
								rekursiotulos = self.board.rek.recurse_own_island(current_actor.x,current_actor.y)
								
								vastustajan_saaren_vahvuus = self.board.rek.recurse_new_random_coord_for_capital_on_island(x2,y2)
								
								#pelaaja_uhri = self.board.get_player_by_side(pala2)
								# Mukana pelissa olevan vihollisen telomisesta saa lisapisteita
								# ja mita vahvempi at the moment, sita enemma bointsei
								#if pelaaja_uhri:
								#	if not pelaaja_uhri.lost:
								#		rekursiotulos += 2
								if vastustajan_saaren_vahvuus[1]:
									rekursiotulos += len(vastustajan_saaren_vahvuus[1]) / 5
								
								# Kuinka moneen omaan palaan kyseinen pala koskee (ohuiden
								# reittiviivojen poistoa?)
								kosketuscount = 0
								edu = self.board.get_right_edm(y2)
								for ite in range(6):
									if self.board.validxy(x2+edu[ite][0],y2+edu[ite][1]):
										if self.board.data[self.board.gct(x2+edu[ite][0],y2+edu[ite][1])] == self.board.turn:
											kosketuscount += 1
								if kosketuscount == 2:
									rekursiotulos += 5
								if kosketuscount == 3:
									rekursiotulos += 4
								if kosketuscount == 4:
									rekursiotulos += 2
								if kosketuscount == 5:
									rekursiotulos += 7
								if kosketuscount == 6:
									rekursiotulos += 15
								
								defender = self.board.actorat(x2,y2)
								if defender:
									if defender.capital and current_actor.voima > 1:
										rekursiotulos += 6
										rekursiotulos += defender.massit
										rekursiotulos += (defender.income - defender.expends)
										if rekursiotulos < 6:
											rekursiotulos = 6
									else:
										rekursiotulos += defender.voima * 2
								# KAIKEN PAHAN ALKU JA JUURI LOPPUU
										
										
								# Laitetaan uusi pistetilanne keskiarvolistaan
								pisteet.append(rekursiotulos)
								koords.append((x2,y2))

								#print "Tyhjennetaan datat"
								self.board.data={}
								self.board.data.update(varmuuskopio)

								# Onko loydetty siirto tehokkaampi kuin muistissa oleva?
								if _DEBUG > 1:
									print "Rekursiotulos: %d m_p: %d   soldier at %d,%d (target: %d,%d)" % (rekursiotulos,m_p,current_actor.x,current_actor.y,x2,y2)
								if rekursiotulos > m_p:
									# On, paivitetaan
									m_p = rekursiotulos
									m_x = x2
									m_y = y2
									if _DEBUG > 0:
										print "Rekursiotulos: %d m_p: %d   soldier at %d,%d (target: %d,%d)" % (rekursiotulos,m_p,current_actor.x,current_actor.y,x2,y2)
										print "Len(pisteet) = %d" % len(pisteet)
								if len(pisteet) > depth:
									if _DEBUG > 1:
										print "Mentiin jatkoajalle"
									if len(pisteet) > (depth*5):
										m_x = None
										print "Nyt en tieda mihin menen."
										if _DEBUG > 0:
											print "Nyt loppu hermot kesken"
											time.sleep(1)
										found_not_brute_force_solution = True
									# Katotaan onko siirto keskimaaraista parempi
									# Ei silti ihan susinta tulosta vaikka ylittaa keskiarvon
									if _DEBUG > 0:
										print "Rekursiotulos: %d  Max(pisteet): %d" % (rekursiotulos,max(pisteet))
									if rekursiotulos > max(pisteet):
										m_p = rekursiotulos
										m_x = x2
										m_y = y2
										act_list[self.board.gct(current_actor.x,current_actor.y)] = self.board.gct(m_x,m_y)
										self.board.try_to_conquer(current_actor,m_x,m_y,False)
										found_not_brute_force_solution = True
										if _DEBUG > 0:
											print "Lokaali maksimi vie voiton"  
											time.sleep(1)
									#Jos liikaa jauhetaan niin otetaan paras loydetyista
									loppulaskija += 1
									if loppulaskija == depth:
										m_p = max(pisteet)
										m_x = koords[pisteet.index(m_p)][0]
										m_y = koords[pisteet.index(m_p)][1]
										act_list[self.board.gct(current_actor.x,current_actor.y)] = self.board.gct(m_x,m_y)
										self.board.try_to_conquer(current_actor,m_x,m_y,False)
										varmuuskopio = self.board.data.copy()
										if _DEBUG > 0:
											print "LoppuLaskija vie voiton"
											time.sleep(1)
										found_not_brute_force_solution = True
				if found_not_brute_force_solution == True and _DEBUG > 0:
					print "Nyt ei kaytetty brutee ;)"
				if m_x and found_not_brute_force_solution==False:
					if _DEBUG > 0:
						if len(pisteet) > 0:
							print "Brute Force -> list has %d values" % (len(pisteet))
						print "Brute Force -> maximum value wins now..."
					time.sleep(1)
					m_p = max(pisteet)
					m_x = koords[pisteet.index(m_p)][0]
					m_y = koords[pisteet.index(m_p)][1]
					act_list[self.board.gct(current_actor.x,current_actor.y)] = self.board.gct(m_x,m_y)
					self.board.try_to_conquer(current_actor,m_x,m_y,False)
					varmuuskopio = self.board.data.copy()
		return act_list
