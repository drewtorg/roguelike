from tile import Tile
from rect import Rect

class Map:

	def __init__(self, width, height):
		self.height = height
		self.width = width
		self.make_map()

	def __getitem__(self, key):
		return self.map[key]

	# def __getattr__(self, name):
	# 	if name == 'height':
	# 		return self.height
			
	# 	if name == 'width':
	# 		return self.width

	def make_map(self):
		self.map = [[ Tile(True)
			for y in range(self.height) ]
				for x in range(self.width) ]

		room1 = Rect(20, 15, 10, 15)
		room2 = Rect(50, 15, 10, 15)
		self.create_room(room1)
		self.create_room(room2)
		self.create_h_tunnel(25, 55, 23)

	def create_room(self, room):
		for x in range(room.x1 + 1, room.x2):
			for y in range(room.y1 + 1, room.y2):
				self.map[x][y].blocked = False
				self.map[x][y].block_sight = False

	def create_h_tunnel(self, x1, x2, y):
		for x in range(min(x1, x2), max(x1, x2) + 1):
				self.map[x][y].blocked = False
				self.map[x][y].block_sight = False

	def create_v_tunnel(self, x1, x2, y):
		for y in range(min(y1, y2), max(y1, y2) + 1):
				self.map[x][y].blocked = False
				self.map[x][y].block_sight = False
