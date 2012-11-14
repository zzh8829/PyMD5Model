#=================================
#====  MD5Mesh/Anim Loader  ======
#=================================

import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *
from types import *
from math import *
from Math3D import *

class MD5_Bone():
	def __init__(self):
		self.index = 0 
		self.name = ""
		self.parent_index = 0
		self.flag = 0
		self.frame_offset = 0
		self.start_index = 0
		self.parent = ""

		self.position = Vector3()
		self.orientation = Quaternion()

class MD5_Bound():
	def __init__(self):
		self.min = Vector3()
		self.max = Vector3()

class MD5_Vert():
	def __init__(self):
		self.index = 0
		self.u = 0
		self.v = 0
		self.weight_index = 0
		self.weight_count = 0
		
		self.normal = Vector3()
		self.pos = Vector3()

class MD5_Tri():
	def __init__(self):
		self.index = 0
		self.x = 0
		self.y = 0
		self.z = 0

class MD5_Weight():
	def __init__(self):
		self.index = 0
		self.bone_index = 0
		self.bias = 0
		self.position = Vector3()

class MD5_Mesh():
	def __init__(self):
		self.index = 0

		self.shader = ""
		self.textid = 0

		self.numverts = 0 
		self.numtris = 0 
		self.numweights = 0
		self.verts = []
		self.tris = []
		self.weights = []

		self.Tex = []
		self.Index = []
		self.Vertex = []
		self.VertexBuffer = []

class MD5_Child():
	def __init__(self):
		self.index = 0
		self.next = 0

class MD5_BaseFrame():
	def __init__(self):
		self.position = []
		self.orientation = []

class MD5_Frame():
	def __init__(self):
		self.num = 0
		self.data = []

class MD5_Animation():
	def __init__(self):
		self.name = ""
		self.numFrames = 0
		self.numJoints = 0
		self.frameRate = 0
		self.numAnimatedComponents = 0
		self.bone = []
		self.boneBuffer = []
		self.bound = []
		self.baseframe = []
		self.frame =[]
		self.next = 0

		self.animTime = 0
	def Update(self,dTime):
		self.animTime+= dTime
		self.current_frame = self.animTime*self.frameRate%self.numFrames

	def PreBuildSkeleton(self,frame):
		self.boneBuffer.append([])
		for i in range(self.numJoints):
			j = 0
			bone = MD5_Bone()
			bone.flag = self.bone[i].flag
			bone.start_index = self.bone[i].start_index
			bone.parent_index = self.bone[i].parent_index
			base = self.baseframe[i]
			bone.position = base.position+Vector3()
			bone.orientation = base.orientation+Quaternion()
			if bone.flag & 1: 
				bone.position.x=frame.data[ bone.start_index+j ]
				j+=1
			if bone.flag & 2: 
				bone.position.y=frame.data[ bone.start_index+j ]
				j+=1
			if bone.flag & 4: 
				bone.position.z=frame.data[ bone.start_index+j ]
				j+=1
			if bone.flag & 8: 
				bone.orientation.x=frame.data[ bone.start_index+j ]
				j+=1	
			if bone.flag & 16: 
				bone.orientation.y=frame.data[ bone.start_index+j ]
				j+=1
			if bone.flag & 32: 
				bone.orientation.z=frame.data[ bone.start_index+j ]
				j+=1
			bone.orientation.ComputeQuatW()
			if bone.parent_index != -1:
				parentBone = self.boneBuffer[frame.num][bone.parent_index]
				rotPos = parentBone.orientation*bone.position
				bone.position = parentBone.position+rotPos
				bone.orientation = parentBone.orientation*bone.orientation
			self.boneBuffer[frame.num].append(bone)

class MD5_Model():
	def __init__(self):

		self.numJoints = 0
		self.numMeshes = 0
		self.numAnim = 0

		self.Bones = []
		self.Meshes = []
		self.Animations = []

		self.current_animation = 0
		self.current_frame = 0
		self.next_anim = 0

		self.LocalToWorldMatrix =  glGetFloatv( GL_MODELVIEW_MATRIX )

	def LoadMesh(self,filename):

		print ("Loading Mesh %s"%filename)
		meshfile = open(filename,"r")
		lines = meshfile.readlines()
		meshfile.close()
		tot_lines = len(lines)
		mesh_num = 0

		for line_num in range(0,tot_lines):
			cur_line = lines[line_num]
			words = cur_line.split()
			if not words: continue

			if words[0] == "MD5Version":
				MD5Version = int(words[1])
				print(words[0],MD5Version)

			elif words[0] == "numJoints":
				self.numJoints = int(words[1])
				print(words[0],self.numJoints)

			elif words[0] == "numMeshes":
				self.numMeshes = int(words[1])
				print(words[0],self.numMeshes)

			elif words[0] == "joints":

				for bone_num in range(self.numJoints):
					newBone = MD5_Bone()
					self.Bones.append(newBone)
					line_num+=1
					cur_line = lines[line_num]
					words = cur_line.split()

					while not words:
						line_num+=1
						cur_line = lines[line_num]
						words = cur_line.split()

					newBone.index = bone_num
					newBone.name = words[0][1:-1]
					newBone.parent_index = int(words[1])
					if newBone.parent_index>=0:
						newBone.parent = self.Bones[newBone.parent_index].name

					newBone.position.x = float(words[3])
					newBone.position.y = float(words[4])
					newBone.position.z = float(words[5])	
					newBone.orientation.x = float(words[8])
					newBone.orientation.y = float(words[9])
					newBone.orientation.z = float(words[10])
					newBone.orientation.ComputeQuatW()
					
			elif words[0] == "mesh":
				newMesh = MD5_Mesh()
				newMesh.index = mesh_num
				while not words or words[0]!="}":
					line_num += 1
					cur_line = lines[line_num]
					words = cur_line.split()
					if not words: continue

					if words[0] == "shader":
						if(words[1]=="\"\""):
							newMesh.textid = 0
							print ("No Shader Image")
						else :
							newMesh.shader = str(words[1])[1:-1]
							print("shader",newMesh.shader)
							try:
								surf = pygame.image.load(newMesh.shader)
							except:
								surf = pygame.image.load(newMesh.shader+".bmp")

							image = pygame.image.tostring(surf,'RGBA',1)
							width = surf.get_width()
							height = surf.get_height()
							texid = newMesh.textid = glGenTextures(1)
							glBindTexture(GL_TEXTURE_2D, texid)
							glPixelStorei(GL_UNPACK_ALIGNMENT,1)
							glTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE );
							glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR );
							glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR );			
							glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA,GL_UNSIGNED_BYTE, image)
							
					elif words[0] == "numverts":
						newMesh.numverts = int(words[1])
						print("numverts",newMesh.numverts)
						newMesh.Tex = np.array(range(newMesh.numverts*2),dtype='f')
						for vert_num in range(newMesh.numverts):
							newMesh.verts.append(MD5_Vert())

							line_num+=1
							cur_line = lines[line_num]
							words = cur_line.split()

							while not words:
								line_num+=1
								cur_line = lines[line_num]
								words = cur_line.split()

							newMesh.verts[vert_num].index = int(words[1])
							newMesh.verts[vert_num].u = float(words[3])
							newMesh.verts[vert_num].v = float(words[4])
							newMesh.verts[vert_num].weight_index = int(words[6])
							newMesh.verts[vert_num].weight_count = int(words[7])
							newMesh.Tex[vert_num*2] = float(words[3])
							newMesh.Tex[vert_num*2+1] = float(words[4])

					elif words[0] == "numtris":
						newMesh.numtris = int(words[1])
						print("numtris",newMesh.numtris)
						newMesh.Index  = np.array(range(newMesh.numtris*3),dtype='i')
						for tri_num in range(newMesh.numtris):
							newMesh.tris.append(MD5_Tri())

							line_num+=1
							cur_line = lines[line_num]
							words = cur_line.split()

							while not words:
								line_num+=1
								cur_line = lines[line_num]
								words = cur_line.split()

							newMesh.tris[tri_num].index = int(words[1])
							newMesh.tris[tri_num].x = float(words[2])
							newMesh.tris[tri_num].y = float(words[3])
							newMesh.tris[tri_num].z = float(words[4])
							newMesh.Index[tri_num*3]=int(words[2])
							newMesh.Index[tri_num*3+1]=int(words[3])
							newMesh.Index[tri_num*3+2]=int(words[4])

					elif words[0] == "numweights":
						newMesh.numweights = int(words[1])
						print("numweights",newMesh.numweights)
						for weight_num in range(newMesh.numweights):
							newMesh.weights.append(MD5_Weight())

							line_num+=1
							cur_line = lines[line_num]
							words = cur_line.split()

							while not words:
								line_num+=1
								cur_line = lines[line_num]
								words = cur_line.split()

							newMesh.weights[weight_num].index = int(words[1])
							newMesh.weights[weight_num].bone_index = int(words[2])
							newMesh.weights[weight_num].bias = float(words[3])
							newMesh.weights[weight_num].position.x = float(words[5])
							newMesh.weights[weight_num].position.y = float(words[6])
							newMesh.weights[weight_num].position.z = float(words[7])
				
				self.BuildMesh(newMesh,self.Bones)
				self.Meshes.append(newMesh)
				mesh_num+=1
		print ("LoadMesh Finished")

	def AddAnimation(self,filename):

		print ("Adding Animation %s"%filename)
		animfile = open(filename,"r")
		lines = animfile.readlines()
		animfile.close()
		tot_lines = len(lines)
		newAnim = MD5_Animation()
		newAnim.name = filename.split('.')[0]
		line_num = 0
		for line_num in range(0,tot_lines):
			cur_line = lines[line_num]
			words = cur_line.split()
			if not words: continue

			if words[0] == "MD5Version":
				MD5Version = int(words[1])
				print(words[0],MD5Version)
			elif words[0] == "numFrames":
				newAnim.numFrames = int(words[1])
				print(words[0],newAnim.numFrames)
			elif words[0] == "numJoints":
				newAnim.numJoints = int(words[1])
				print(words[0],newAnim.numJoints)
			elif words[0] == "frameRate":
				newAnim.frameRate = int(words[1])
				print(words[0],newAnim.frameRate)
			elif words[0] == "numAnimatedComponents":
				newAnim.numAnimatedComponents = int(words[1])
				print(words[0],newAnim.numAnimatedComponents)
			elif words[0] == "hierarchy":
				for bone_num in range(newAnim.numJoints):

					newBone = MD5_Bone()
					line_num+=1
					cur_line = lines[line_num]
					words = cur_line.split()
					while not words:
						line_num+=1
						cur_line = lines[line_num]
						words = cur_line.split()
					newBone.index = bone_num
					newBone.name = words[0]
					newBone.parent_index = int(words[1])
					newBone.flag = int(words[2])
					newBone.start_index = int(words[3])
					newAnim.bone.append(newBone)

			elif words[0] == "bounds":
				for i in range(newAnim.numFrames):
					line_num+=1
					cur_line = lines[line_num]
					words = cur_line.split()
					newBound = MD5_Bound()
					newBound.min = Vector3(float(words[1]),float(words[2]),float(words[3]))
					newBound.max = Vector3(float(words[6]),float(words[7]),float(words[8]))
					newAnim.bound.append(newBound)

			elif words[0] == "baseframe":
				for i in range(newAnim.numJoints):
					line_num+=1
					cur_line = lines[line_num]
					words = cur_line.split()
					newBaseframe = MD5_BaseFrame()
					newBaseframe.position = Vector3(float(words[1]),float(words[2]),float(words[3]))
					newBaseframe.orientation = Quaternion(float(words[6]),float(words[7]),float(words[8]))
					newAnim.baseframe.append(newBaseframe)

			elif words[0] == "frame":
				newFrame = MD5_Frame()
				newFrame.num = int(words[1])
				line_num+=1
				cur_line = lines[line_num]
				words = cur_line.split()
				while words[0]!="}":
					for i in words:
						newFrame.data.append(float(i))
					line_num+=1
					cur_line = lines[line_num]
					words = cur_line.split()
				newAnim.frame.append(newFrame)
				newAnim.PreBuildSkeleton(newFrame)
			
		self.Animations.append(newAnim)
		self.numAnim+=1
		print ("AddAnimation Finished")

	def BufferBone(self,index):
		for m in range(self.numMeshes):
			self.Meshes[m].VertexBuffer = []
			for f in range(self.Animations[index].numFrames):
				vBuffer = np.array(range(self.Meshes[m].numverts*3),dtype='f')
				for i in range(self.Meshes[m].numverts):
					finalPos = Vector3()
					for j in range(self.Meshes[m].verts[i].weight_count):
						wei = self.Meshes[m].weights[self.Meshes[m].verts[i].weight_index + j]
						joi = (self.Animations[index].boneBuffer[f])[wei.bone_index]
						rotPos = joi.orientation.Rotate(wei.position);
						finalPos = finalPos + (rotPos + joi.position) * wei.bias
					vBuffer[i*3] = finalPos.x
					vBuffer[i*3+1] = finalPos.y
					vBuffer[i*3+2] = finalPos.z
				self.Meshes[m].VertexBuffer.append(vBuffer)
	def BufferAllBone(self):
		print ("Building Animation...")
		for m in range(self.numMeshes):
			self.Meshes[m].VertexBufferAll = []
			for a in range(self.numAnim):
				VertexBuffer = []
				for f in range(self.Animations[a].numFrames):
					vBuffer = np.array(range(self.Meshes[m].numverts*3),dtype='f')
					pBuffer = []
					oBuffer = []
					for i in range(self.Meshes[m].numverts):
						finalPos = Vector3()
						for j in range(self.Meshes[m].verts[i].weight_count):
							wei = self.Meshes[m].weights[self.Meshes[m].verts[i].weight_index + j]
							joi = (self.Animations[a].boneBuffer[f])[wei.bone_index]
							rotPos = joi.orientation.Rotate(wei.position);
							finalPos = finalPos + (rotPos + joi.position) * wei.bias
						vBuffer[i*3] = finalPos.x
						vBuffer[i*3+1] = finalPos.y
						vBuffer[i*3+2] = finalPos.z
					VertexBuffer.append(vBuffer)
				self.Meshes[m].VertexBufferAll.append(VertexBuffer)
		print ("Buffer Finished")
	def SetFrame(self,index):
		self.current_frame = index
		for m in range(self.numMeshes):
			self.Meshes[m].Vertex = self.Meshes[m].VertexBuffer[index]
	def ChooseBufferedAnimation(self,index):
		self.next_anim = (index+1)%self.numAnim
		self.current_animation = index
		self.numFrames = self.Animations[index].numFrames
		for m in range(self.numMeshes):
			self.Meshes[m].VertexBuffer = self.Meshes[m].VertexBufferAll[index]

	def ChooseAnimation(self,index):
		self.next_anim = (index+1)%self.numAnim
		self.current_animation = index
		self.numFrames = self.Animations[index].numFrames
		self.BufferBone(index)

	def Render(self):
		glPushMatrix()
		glMultMatrixf(self.LocalToWorldMatrix)
		for i in range(self.numMeshes):
			self.RenderMesh(self.Meshes[i])

		glPopMatrix()

	def RenderMesh(self,mesh):

		glEnable(GL_TEXTURE_2D)
		glBindTexture( GL_TEXTURE_2D, mesh.textid );
		glEnableClientState( GL_TEXTURE_COORD_ARRAY );
		glFrontFace(GL_CCW)
		glTexCoordPointer( 2, GL_FLOAT, 0, mesh.Tex );
		glEnableClientState( GL_VERTEX_ARRAY );
		glVertexPointer( 3, GL_FLOAT, 0, mesh.Vertex);	
		glDrawElements( GL_TRIANGLES,mesh.numtris*3, GL_UNSIGNED_INT, mesh.Index );
		glDisableClientState( GL_TEXTURE_COORD_ARRAY );
		glDisableClientState( GL_VERTEX_ARRAY );
		glBindTexture( GL_TEXTURE_2D, 0 );
		glDisable(GL_TEXTURE_2D)

	def BuildMesh(self,mesh,bones):
		mesh.Vertex = np.array(range(mesh.numverts*3),dtype='f')
		for i in range(mesh.numverts):
			finalPos = Vector3()
			for j in range(mesh.verts[i].weight_count):
				wei = mesh.weights[mesh.verts[i].weight_index + j]
				joi = bones[wei.bone_index]
				rotPos = joi.orientation.Rotate(wei.position);
				finalPos = finalPos + (rotPos + joi.position) * wei.bias
			mesh.Vertex[i*3] = finalPos.x
			mesh.Vertex[i*3+1] = finalPos.y
			mesh.Vertex[i*3+2] = finalPos.z
