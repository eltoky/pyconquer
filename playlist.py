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

class TPlayList:
	def __init__(self):
		self.playlist=[]
		self.mediaID=0
		self.chan=pygame.mixer.Channel(pygame.mixer.get_num_channels()-1)
	#Add media file to play list, full or relative path
	def AddMedia(self,MediaFile):
		self.playlist.append(pygame.mixer.Sound(MediaFile))
	#Clear playlist
	def Clear(self):
		self.playlist=[]
	#Play playlist
	def Play(self,loops=0):
		self.chan.play(self.playlist[self.mediaID],loops)
	#Check if it is time to start next track
	def CheckIfNext(self):
		if not self.chan.get_busy() :
			if self.mediaID == (len(self.playlist)-1) :
				self.mediaID=0
			else:
				self.mediaID+=1
			self.chan.play(self.playlist[self.mediaID])
