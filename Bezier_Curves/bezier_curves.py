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
from taulaMC import lut
from Blender import Scene, Mesh, Window, sys
import BPyMessages
import bpy
import math

############## TEST CASES ##############

usamples = 20
vsamples = 20

#esfera
#t = 0.55226
#points = [
# [0, 0, 1],
# [-t, 0, 1],
# [ -1, 0, t],
# [ -1, 0, 0],
# [ -1, 0, 0],
# [ -1, 0, -t],
# [ -t, 0, -1],
# [ 0, 0, -1]
#]

# baldufa
t = 2.0
q = t/4
points = [
 [ 0, 0, 1],
 [ t, 0, 0],
 [ q, 0, 0],
 [ 0, 0, -1]
]

# ou
#t = 1.3
#q = t/2
#points = [
# [ 0, 0, -1 ],
# [ t, 0, -1 ],
# [ q, 0, 1 ],
# [ 0, 0, 1 ],
#]

############## BEZIER CURVES ##############

def function_u_coord(u, P1, P2, P3, P4):
	first = - (u*u*u) + 3*u*u - 3*u + 1
	second = 3*u*u*u - 6*u*u + 3*u
	third = - (3*u*u*u) + 3*u*u
	fourth = u*u*u
	return first*P1 + second*P2 + third*P3 + fourth*P4

def function_u_v(u, v, P1, P2, P3, P4):
	pointx = function_u_coord(u, P1[0], P2[0], P3[0], P4[0])
	pointz = function_u_coord(u, P1[2], P2[2], P3[2], P4[2])
	return [pointx * math.cos(v), pointx * math.sin(v), pointz]

def bezier_curves():
	#si tenemos dos curvas de bezier, la u va de 0 a 2; si 3, de 0 a 3 ...
	#cuando pasamos del 1 hay que coger la segunda curva (ejemplo: esfera)
	
	incu = ( float(len(points)) / 4.0) / float(usamples)
	incv = (2.0*math.pi) / float(vsamples)
	
	num_bezier_curves = len(points) / 4
	
	v = 0.0

	verts = []
	faces = []
	
	samples = (usamples + num_bezier_curves - 1) / num_bezier_curves
	
	while v < 2.0*math.pi:
		control = 0
		frontera = 1.0
		indice = 0
		while control < num_bezier_curves:
			P1 = points[indice]
			P2 = points[indice + 1]
			P3 = points[indice + 2]
			P4 = points[indice + 3]
			u = 0.0
			#while u < 1.0:
			#	point = function_u_v(u, v, P1, P2, P3, P4)
			#	verts.append(point)
			#	u = u + incu
			for i in range(samples):
				point = function_u_v(u, v, P1, P2, P3, P4)
				verts.append(point)
				u = u + incu
			u = 1.0
			point = function_u_v(u, v, P1, P2, P3, P4)
			verts.append(point)
			control = control + 1
			indice = indice + 4
			
		v = v + incv
	
		
	# P[0..usamples-1]
	# Q[0..usamples-1]
	P = []
	Q = []
	for i in range(usamples):
		P.append(i)
		Q.append(i)
	
	for i in range(1, vsamples):
		A = usamples * i
		for j in range(1, usamples):
			B = usamples * i + j
			faces.append([A, B, P[j], P[j - 1]])
			P[j - 1] = A
			A = B
		P[usamples-1] = B
	
	for i in range(1, usamples):
		faces.append([Q[i - 1], Q[i], P[i], P[i-1]])
	
	BPyAddMesh.add_mesh_simple('MC', verts, [], faces)
	print "Vert: ", verts[usamples-1]

def main():
	bezier_curves()
	Window.EditMode(0)
	Window.WaitCursor(1)

main()