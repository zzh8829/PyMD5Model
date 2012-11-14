#=================================
#=======  MD5Model Example  ======
#=================================

''' 
Usage :
Space: Switch to next Animation
Mouse: Rotate on y-axis
w/s: moving in z-axis
'''

MeshFile = "model//hellknight.md5mesh"
AnimFile = [
	"model//walk.md5anim",
	"model//idle.md5anim",
	"model//attack.md5anim",
	"model//roar.md5anim",
	"model//stand.md5anim"
]

# Choose Use pre-buffer or not(in-time Buffer)
# pre-buffer may take long pre-loading time
# in-time buffer may take long time when switch animation
USE_PRE_BUFFER = True

import OpenGL
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from math import *
from MD5Model import *

gl_size = (1024,600)
gl_option = (OPENGL|DOUBLEBUF)
TITLE = "PyGame 3D Window"
FPS = 30
ID_VIEW = 0

RED   = (1.0,0.0,0.0,1.0)
GREEN = (0.0,0.0,1.0,1.0)
BLUE  = (0.0,1.0,0.0,1.0)
BLACK = (0.0,0.0,0.0,1.0)
WHITE = (1.0,1.0,1.0,1.0)

class CGame(object):
	use_all_buffer = USE_PRE_BUFFER
	def __init__(self):
		self.screen_size = gl_size
		self.display_init(self.screen_size)	
		self.running = True
		self.change = 1
		self.x_trans = 0
		self.y_trans = 0
		self.choose = 0
		self.listx = [ 0 for i in range(10)]
		self.listy = [ 0 for i in range(10)]
		self.clock = pygame.time.Clock()
		self.frame = 0
		self.show = 0

		self.mesh = MD5_Model()
		self.mesh.LoadMesh(MeshFile)
		for i in AnimFile:
			self.mesh.AddAnimation(i)

		if self.use_all_buffer: 
			self.mesh.BufferAllBone()
			self.mesh.ChooseBufferedAnimation(0)
		else :
			self.mesh.ChooseAnimation(0)
		self.rotx,self.roty = (0,0)

	def run(self):
		while self.running:
			glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
			glColor4f(*WHITE)
			self.event_handler(pygame.event.get())
			self.key_handler(pygame.key.get_pressed())
			self.timer()
			self.DrawScene()
			pygame.display.flip()
		
	def display_init(self,screen_size):
		pygame.display.init()
		self.screen = pygame.display.set_mode(screen_size,gl_option)
		pygame.display.set_caption(TITLE)
		glClearColor(*BLACK)
		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
		self.w = self.screen_size[0]
		self.h = self.screen_size[1]
		aspectRatio= self.w/self.h;
		glViewport(0,0,self.w,self.h);
		glMatrixMode(GL_PROJECTION);
		glLoadIdentity();
		gluPerspective(25.0, self.w/self.h, 1 , 10000.0)
		glEnable (GL_DEPTH_TEST);
		glMatrixMode(GL_MODELVIEW);
		glLoadIdentity();
		pygame.mouse.set_visible(False)

	def DrawScene(self):

		glPushMatrix()
		glColor4f(*WHITE)
		glTranslatef(0.0,0.0,self.listy[ID_VIEW])
		glRotate(self.rotx, 0, 1, 0)
		glRotate(-90, 1, 0, 0)
		self.mesh.Render()
		glPopMatrix()

	def timer(self):
		self.clock.tick(FPS)
		if self.frame >= self.mesh.numFrames:
			self.frame = 0
		self.mesh.SetFrame(self.frame)
		self.frame+=1
		pygame.display.set_caption(TITLE +' FPS: %d Frame: %d Anim: %s' %
			(self.clock.get_fps(),self.frame,self.mesh.Animations[self.mesh.current_animation].name))

	def key_handler(self,keys):
		if keys[ord('a')]:
			self.x_trans=-5
		if keys[ord('d')]:
			self.x_trans=5
		if keys[ord('w')]:
			self.y_trans=5
		if keys[ord('s')]:
			self.y_trans=-5
		self.listx[self.choose]+=self.x_trans
		self.listy[self.choose]+=self.y_trans
		self.x_trans = self.y_trans = 0
	
	def event_handler(self,events):
		for event in events:
			if event.type == QUIT:
				self.running = False
			if event.type == KEYUP:
				if event.key == K_ESCAPE:
					self.running = False
				elif event.key == K_SPACE:
					if self.use_all_buffer:
						self.mesh.ChooseBufferedAnimation(self.mesh.next_anim)
					else:
						self.mesh.ChooseAnimation(self.mesh.next_anim)
			if event.type == MOUSEMOTION:
				i,j = event.rel
				self.rotx += i

if __name__ == '__main__':
	game = CGame()
	game.run()
	pygame.quit()
