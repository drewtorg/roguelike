import libtcodpy as libtcod
import math
import game
from heapq import *

class Object:
	def __init__(self, x, y, char, name, color, blocks=False, fighter=None, ai=None, item=None):
		self.x = x
		self.y = y
		self.char = char
		self.name = name
		self.color = color
		self.blocks = blocks

		self.fighter = fighter
		if self.fighter:
			self.fighter.owner = self

		self.ai = ai
		if self.ai:
			self.ai.owner = self

		self.item = item
		if self.item:
			self.item.owner = self

	def move_or_attack(self, dx, dy):
		x = self.x + dx
		y = self.y + dy

		target = None
		for object in game.Game.map.objects:
			if object.fighter and object.x == x and object.y == y:
				target = object
				break

		if target is not None:
			self.fighter.attack(target)
		else:
			self.move(dx, dy)

	def move(self, dx, dy):
		if not game.Game.map.is_blocked(self.x + dx, self.y + dy):
			self.x += dx
			self.y += dy

	def move_towards(self, target):
		result = astar(game.Game.map, (self.x, self.y), (target.x, target.y))
		move_here = result.pop()
		self.x = move_here[0]
		self.y = move_here[1]

	def distance_to(self, other):
		dx = other.x - self.x
		dy = other.y - self.y
		return math.sqrt(dx ** 2 + dy ** 2)

def heuristic(a, b):
	return (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2

def astar(array, start, goal):

	# Allows diagonal movement of enemies
	# neighbors = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
	
	# Doesn't allow diagonal movement of enemies
	neighbors = [(0,1),(0,-1),(1,0),(-1,0),(1,1)]

	close_set = set()
	came_from = {}
	gscore = {start:0}
	fscore = {start:heuristic(start, goal)}
	oheap = []

	heappush(oheap, (fscore[start], start))

	while oheap:

		current = heappop(oheap)[1]

		if current == goal:
			data = []
			while current in came_from:
				data.append(current)
				current = came_from[current]
			return data

		close_set.add(current)
		for i, j in neighbors:
			neighbor = current[0] + i, current[1] + j
			tentative_g_score = gscore[current] + heuristic(current, neighbor)
			if 0 <= neighbor[0] < len(array):
				if 0 <= neighbor[1] < len(array[0]):
					if array[neighbor[0]][neighbor[1]].blocked == True:
						continue
				else:
					# array bound y walls
					continue
			else:
				# array bound x walls
				continue

			if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
				continue

			if  tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1]for i in oheap]:
				came_from[neighbor] = current
				gscore[neighbor] = tentative_g_score
				fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
				heappush(oheap, (fscore[neighbor], neighbor))

	return False
