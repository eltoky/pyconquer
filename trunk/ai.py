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

import time,random
from sets import Set

class TAi:
	def __init__(self,board):
		"""board -> TGameBoard instance which is the parent"""
		self.board = board
	def act(self,depth):
		# List of executed moves that is returned
		act_list = {}
		
		own_soldier_actor_set = Set([])
		for soldier in self.board.actors:
			if not soldier.dump and soldier.side == self.board.turn and not soldier.moved:
				own_soldier_actor_set.add(soldier)
		# More CPU, more depth
		for askellin in xrange(self.board.ai_recursion_depth):		
			# We'll iterate every actor through a copy
			for current_actor in own_soldier_actor_set.copy():
				if current_actor.dead:
					continue
				# We'll move only own soldiers that have not moved yet
				if not current_actor.dump and not current_actor.moved and current_actor.side == self.board.turn:
					# Memory for found move
					m_x = None
					m_y = None

					# Memory for found move's points
					m_p = 0
					
					# Make a copy of the original map
					varmuuskopio = self.board.data.copy()
					pisteet = []
					koords = []
					loppulaskija = 0
					found_not_brute_force_solution = False
					
					possible_moves = self.board.rek.get_island_border_lands(current_actor.x,current_actor.y)
					possible_moves = list(possible_moves)
					random.shuffle(possible_moves)
					
					for coordinate_xy in possible_moves:
						if found_not_brute_force_solution:
							continue
						x2,y2 = self.board.ec(coordinate_xy)
							
						# Player ID of the possible move's land
						pala2 = self.board.data[self.board.gct(x2,y2)]

						# Target must be enemy's land
						if ((pala2 != self.board.turn) and (pala2 != 0)):

							# Is the move possible?
							blokkastu = self.board.is_blocked(current_actor,x2,y2)
							if blokkastu[0] == False:
								
								# The move is possible, we'll simulate it
								self.board.try_to_conquer(current_actor,x2,y2,True)

								# The points of the move								
								rekursiotulos = self.board.rek.recurse_own_island(current_actor.x,current_actor.y)								
								
								# Land area of the target island
								vastustajan_saaren_vahvuus = self.board.rek.recurse_new_random_coord_for_dump_on_island(x2,y2)

								# We'll favour more to conquer from large islands
								if vastustajan_saaren_vahvuus[1]:
									rekursiotulos += len(vastustajan_saaren_vahvuus[1]) / 5
								
								# Is there an actor at target land?
								defender = self.board.actorat(x2,y2)
								if defender:
									# There is an actor at target land,
									# we'll add it into moves points
									if defender.dump and current_actor.level > 1:
										rekursiotulos += 5
										rekursiotulos += defender.supplies / 2
										rekursiotulos += (defender.income - defender.expends)
									else:
										rekursiotulos += defender.level * 2
																				
								# Put the move and it's points in memory
								pisteet.append(rekursiotulos)
								koords.append((x2,y2))

								# Restore the original map and try different moves
								self.board.data={}
								self.board.data.update(varmuuskopio)

								# Found move better than the one in memory?
								if rekursiotulos > m_p:
									# Yes it is, update
									m_p = rekursiotulos
									m_x = x2
									m_y = y2
								if len(pisteet) > depth:
									# Now we have been looking move too long
									
									if len(pisteet) > (depth*5):
										# Found no move...
										# This shouldn't be never executed
										m_x = None
										found_not_brute_force_solution = True
										own_soldier_actor_set.discard(current_actor)				
									# If the current found move is better than
									# anyone else, we'll choose it
									if rekursiotulos > max(pisteet):
										m_p = rekursiotulos
										m_x = x2
										m_y = y2
										act_list[self.board.gct(current_actor.x,current_actor.y)] = self.board.gct(m_x,m_y)
										self.board.try_to_conquer(current_actor,m_x,m_y,False)
										found_not_brute_force_solution = True
										own_soldier_actor_set.discard(current_actor)
									# Too much used time here
									loppulaskija += 1
									if loppulaskija == depth:
										# We'll choose best move we have found
										m_p = max(pisteet)
										m_x = koords[pisteet.index(m_p)][0]
										m_y = koords[pisteet.index(m_p)][1]
										act_list[self.board.gct(current_actor.x,current_actor.y)] = self.board.gct(m_x,m_y)
										self.board.try_to_conquer(current_actor,m_x,m_y,False)
										varmuuskopio = self.board.data.copy()
										found_not_brute_force_solution = True
										own_soldier_actor_set.discard(current_actor)
					if m_x and found_not_brute_force_solution==False:
						# Normally we shouldn't end up here, but if we
						# do, we choose the best current move.
						m_p = max(pisteet)
						m_x = koords[pisteet.index(m_p)][0]
						m_y = koords[pisteet.index(m_p)][1]
						act_list[self.board.gct(current_actor.x,current_actor.y)] = self.board.gct(m_x,m_y)
						self.board.try_to_conquer(current_actor,m_x,m_y,False)
						varmuuskopio = self.board.data.copy()
						own_soldier_actor_set.discard(current_actor)
		# Return dictionary of made moves
		return act_list
