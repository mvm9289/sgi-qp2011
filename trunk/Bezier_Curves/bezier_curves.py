#!BPY


"""""""""""""""""""""""""""""""""
Name: Marching Cubes
Group:
			Jose Antonio Navas Molina
			Miguel Angel Vico Moya
			
"""""""""""""""""""""""""""""""""


############## IMPORTS ##############

import BPyAddMesh
import Blender
from Blender import Scene, Mesh, Window, sys, Mathutils
import BPyMessages
import bpy
import math


############## CONSTANTS ##############

SPHERE = 0 # Kmin = 0.76 Kmax = 1.54
TOP = 1 # Kmin = -9.44 Kmax = 202.1
EGG = 2 # Kmin = 0.61 Kmax = 10.88


############## PARAMETERS ##############

# ¿How many samples want to do?
USAMPLES = 20
VSAMPLES = 20

# ¿Which model want to use?
MODEL = SPHERE

# ¿Which interval of Gaussian Curvature want to analyze?
#	Recommended:
#		SPHERE: Kmin = 0.74 Kmax = 1.54
#		TOP: Kmin = -9.44 Kmax = 5.0
#		EGG: Kmin = 0.60 Kmax = 5.0
KMIN = 0.74
KMAX = 1.54


############## MODELS ##############

if MODEL == SPHERE:
	t = 0.55226
	points = [
	 [0, 0, 1],
	 [-t, 0, 1],
	 [ -1, 0, t],
	 [ -1, 0, 0],
	 [ -1, 0, 0],
	 [ -1, 0, -t],
	 [ -t, 0, -1],
	 [ 0, 0, -1]
	]
elif MODEL == TOP:
	t = 2.0
	q = t/4
	points = [
	 [ 0, 0, 1],
	 [ t, 0, 0],
	 [ q, 0, 0],
	 [ 0, 0, -1]
	]
elif MODEL == EGG:
	t = 1.3
	q = t/2
	points = [
	 [ 0, 0, -1 ],
	 [ t, 0, -1 ],
	 [ q, 0, 1 ],
	 [ 0, 0, 1 ],
	]
else:
	print "ERROR: Invalid model"


############## BEZIER CURVES ##############

def function_u(u, P1, P2, P3, P4):
	first = - (u*u*u) + 3*u*u - 3*u + 1
	second = 3*u*u*u - 6*u*u + 3*u
	third = - (3*u*u*u) + 3*u*u
	fourth = u*u*u
	return first*P1 + second*P2 + third*P3 + fourth*P4

def function_u_v(u, v, P1, P2, P3, P4):
	px = function_u(u, P1[0], P2[0], P3[0], P4[0])
	pz = function_u(u, P1[2], P2[2], P3[2], P4[2])
	return [px*math.cos(v), px*math.sin(v), pz]

def bezier_curves():
	## Generate vertices ##
	
	incu = (float(len(points))/4.0)/float(USAMPLES - 1)
	incv = (2.0*math.pi)/float(VSAMPLES)
	num_bezier_curves = len(points)/4
	
	verts = []
	
	# Top vertex
	point = function_u_v(0.0, 0.0, points[0], points[1], points[2], points[3])
	verts.append(point)
	
	# Middle vertices
	v = 0.0
	while v < 2.0*math.pi:
		control = 0
		frontera = 1.0
		indice = 0
		u = incu
		while control < num_bezier_curves:
			P1 = points[indice]
			P2 = points[indice + 1]
			P3 = points[indice + 2]
			P4 = points[indice + 3]
			while u < 1.0 - incu:
				point = function_u_v(u, v, P1, P2, P3, P4)
				verts.append(point)
				u = u + incu
			if control < num_bezier_curves - 1:
				u = u - 1.0
			control = control + 1
			indice = indice + 4
			
		v = v + incv
		
	# Bottom vertex
	baseIdx = 4*(num_bezier_curves - 1)
	point = function_u_v(1.0, 0.0, points[baseIdx], points[baseIdx + 1], points[baseIdx + 2], points[baseIdx + 3])
	verts.append(point)
	
	
	## Generate faces ##
	
	faces = []
	
	# Top faces
	for i in range(VSAMPLES - 1):
		faces.append([0, (USAMPLES - 2)*(i + 1) + 1, (USAMPLES - 2)*i + 1])
	faces.append([0, 1, (USAMPLES - 2)*(VSAMPLES - 1) + 1])
	
	# Middle faces
	P = []
	Q = []
	for i in range(1, USAMPLES - 1):
		P.append(i)
		Q.append(i)
	for i in range(1, VSAMPLES):
		A = (USAMPLES - 2)*i + 1
		for j in range(1, USAMPLES - 2):
			B = (USAMPLES - 2)*i + j + 1
			faces.append([A, B, P[j], P[j - 1]])
			P[j - 1] = A
			A = B
		P[USAMPLES - 3] = B
	for i in range(1, USAMPLES - 2):
		faces.append([Q[i - 1], Q[i], P[i], P[i-1]])
	
	# Bottom faces
	for i in range(1, VSAMPLES):
		faces.append([len(verts) - 1, (USAMPLES - 2)*i, (USAMPLES - 2)*(i + 1)])
	faces.append([len(verts) - 1, (USAMPLES - 2)*VSAMPLES, (USAMPLES - 2)])
	
	
	BPyAddMesh.add_mesh_simple('MC', verts, [], faces)


############## GAUSSIAN CURVATURE ##############

def compute_angle_and_area(F, i):
	v = F.verts[i].co
	n = len(F.verts)
	vPrev = F.verts[(i - 1)%n].co
	vNext = F.verts[(i + 1)%n].co
	return [Mathutils.AngleBetweenVecs((vPrev - v), (vNext - v))*2.0*math.pi/360.0, Mathutils.TriangleArea(vPrev, v, vNext)]

def compute_curvature():
	# Obtain active object
	ob = bpy.data.scenes.active.objects.active
	
	# Check thath is a mesh
	if not ob or ob.type != 'Mesh':
		BPyMessages.Error_NoMeshActive()
		return

	# Get mesh
	mesh = ob.getData(mesh = 1)
	
	# Compute angles and areas
	angleSum = []
	areaSum = []
	
	for i in range(len(mesh.verts)):
		angleSum.append(0.0)
		areaSum.append(0.0)
	
	for f in mesh.faces:
		for i, v in enumerate(f):
			result = compute_angle_and_area(f, i)
			angleSum[v.index] = angleSum[v.index] + result[0]
			areaSum[v.index] = areaSum[v.index] + result[1]
	
	# Compute Gaussian curvature
	K = []
	
	for i in range(len(mesh.verts)):
		K.append(0.0)
	
	Kmin = 3.0*(2.0*math.pi - angleSum[0])/areaSum[0]
	Kmax = Kmin
	
	for v in mesh.verts:
		K[v.index] = 3.0*(2.0*math.pi - angleSum[v.index])/areaSum[v.index]
		if K[v.index] < Kmin:
			Kmin = K[v.index]
		elif K[v.index] > Kmax:
			Kmax = K[v.index]
	
	#print "Kmin =", Kmin, " Kmax =", Kmax
	
	# Compute faces colors
	mesh.vertexColors = True
	
	for f in mesh.faces:
		for i, v in enumerate(f):
			no= v.no
			col= f.col[i]
			
			if KMAX - KMIN <= 0.0:
				PRB = 0.5
			else:
				PRB = (K[v.index] - KMIN)/(KMAX - KMIN)
				if PRB > 1.0:
					PRB = 1.0
				elif PRB < 0.0:
					PRB = 0.0
			
			col.r= int(PRB*256.0)
			col.g= int(0.0)
			col.b= int((1.0 - PRB)*256.0)


############## MAIN ##############

def main():
	Window.EditMode(0)
	Window.WaitCursor(1)
	
	bezier_curves()
	compute_curvature()
	
	Window.WaitCursor(0) 

main()