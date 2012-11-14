#=================================
#==== 3DMath Computing lib  ======
#=================================

import sys
from math import *

class Vector3():
	"""Vector3 Class"""
	def __init__(self,x=0,y=0,z=0):
		self.x = x
		self.y = y
		self.z = z

	def __mul__(self,other):
		rt  = Vector3()
		if isinstance(other,Vector3):
			return self.crossProduct(other)
		else :
			rt.x = self.x*other
			rt.y = self.y*other
			rt.z = self.z*other
			return rt

	def __add__(self,other):
		'''
		rt = Vector3()
		rt.x = self.x+other.x
		rt.y = self.y+other.y
		rt.z = self.z+other.z
		return rt
		'''
		return Vector3(self.x+other.x,self.y+other.y,self.z+other.z)

	def __sub__(self,other):
		rt = Vector3()
		rt.x = self.x-other.x
		rt.y = self.y-other.y
		rt.z = self.z-other.z
		return rt

	def __str__(self):
		return "%.2f %.2f %.2f"%(self.x,self.y,self.z)
	def normalise(self):
		fLen = sqrt(self.x**2 + self.y**2+self.z**2)

		if fLen > 0:
			invLen = 1/fLen
			self.x *= invLen
			self.y *= invLen
			self.z *= invLen

		return fLen

	def crossProduct(self,other):
		pro = Vector3()
		pro.x = self.y*other.z - self.z*other.y
		pro.y = self.z*other.x - self.x*other.z
		pro.z = self.x*other.y - self.y*other.x

		return pro

	def dotProduct(self,other):
		rt = Vector3()
		rt.x = self.x*other.x
		rt.y = self.y*other.y
		rt.z = self.z*other.z
		return rt

class Vector2():
	"""Vector2 Class"""
	def __init__(self):
		self.x = 0
		self.y = 0

class Quaternion():
	"""Quaternion Class"""
	def __init__(self,x=0,y=0,z=0):
		self.x = x
		self.y = y
		self.z = z
		self.w = 0
		self.ComputeQuatW()

	def __add__(self,other):
		rt = Quaternion()
		rt.w = self.w+other.w
		rt.x = self.x+other.x
		rt.y = self.y+other.y
		rt.z = self.z+other.z
		return rt
	def __mul__(self,other):

		if isinstance(other,Vector3):
			qvec = Vector3()
			qvec.x = self.x 
			qvec.y = self.y
			qvec.z = self.z
			uv = qvec.crossProduct(other);
			uuv = qvec.crossProduct(uv);
			uv = uv * (2.0 * self.w);
			uuv = uuv * 2.0;
			return other + uv + uuv;
		if isinstance(other,Quaternion):
			rt = Quaternion()
			rt.w = self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z
			rt.x = self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y
			rt.y = self.w * other.y + self.y * other.w + self.z * other.x - self.x * other.z
			rt.z = self.w * other.z + self.z * other.w + self.x * other.y - self.y * other.x
			return rt
		else:
			rt = Quaternion()
			rt.w =self.w * other
			rt.x =self.x * other
			rt.y =self.y * other
			rt.z =self.z * other
			rt.ComputeQuatW()
			return rt

	def __str__(self):
		return "%.2f %.2f %.2f %.2f"%(self.w,self.x,self.y,self.z)

	def ComputeQuatW(self):
		t = 1.0 - (self.x*self.x+self.y*self.y+self.z*self.z)
		if t > 0: self.w = -sqrt(t)
		else : self.w = 0

	def Rotate(self,v):
		temp = Vector3()
		temp.x = self.x
		temp.y = self.y
		temp.z = self.z

		uv= temp*v;
		uuv= temp*uv;
		uv= uv*self.w*2.0;
		uuv= uuv*2.0;
		uv += v
		uv += uuv
		return uv;
	
	def normalise(self):
		length = self.w*self.w+self.x*self.x+self.y*self.y+self.z*self.z
		factor = 1/sqrt(length)
		self = self * factor
		return length