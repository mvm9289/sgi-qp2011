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
#t = 2.0
#q = t/4
#points = [
# [ 0, 0, 1],
# [ t, 0, 0],
# [ q, 0, 0],
# [ 0, 0, -1]
#]

# ou
t = 1.3
q = t/2
points = [
 [ 0, 0, -1 ],
 [ t, 0, -1 ],
 [ q, 0, 1 ],
 [ 0, 0, 1 ],
]

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
	
	incu = ( float(len(points)) / 4.0) / float(usamples - 1)
	incv = (2.0*math.pi) / float(vsamples)
	
	num_bezier_curves = len(points) / 4
	
	v = 0.0

	verts = []
	faces = []
	
	#samples = (usamples + num_bezier_curves - 1) / num_bezier_curves
	
	while v < 2.0*math.pi:
		control = 0
		frontera = 1.0
		indice = 0
		u = 0.0
		while control < num_bezier_curves:
			P1 = points[indice]
			P2 = points[indice + 1]
			P3 = points[indice + 2]
			P4 = points[indice + 3]
			#u = 0.0
			while u < 1.0:
				point = function_u_v(u, v, P1, P2, P3, P4)
				verts.append(point)
				u = u + incu
			#for i in range(samples):
			#	point = function_u_v(u, v, P1, P2, P3, P4)
			#	verts.append(point)
			#	u = u + incu
			if control == num_bezier_curves - 1:
				u = 1.0
				point = function_u_v(u, v, P1, P2, P3, P4)
				verts.append(point)
			else:
				u = u - 1.0
			control = control + 1
			indice = indice + 4
			
		v = v + incv
	
		
	# P[0..usamples-1]
	# Q[0..usamples-1]
	P = []
	Q = []
	for i in range(usamples + 1):
		P.append(i)
		Q.append(i)
	
	v_e = []
	v_f = []
	for i in range(len(verts)):
		v_e.append([])
		v_f.append([])
	
	for i in range(1, vsamples):
		A = (usamples + 1) * i
		for j in range(1, usamples + 1):
			B = (usamples + 1) * i + j
			faces.append([A, B, P[j], P[j - 1]])
			
			v_f[A].append(len(faces) - 1)
			v_f[B].append(len(faces) - 1)
			v_f[P[j]].append(len(faces) - 1)
			v_f[P[j - 1]].append(len(faces) - 1)
			
			v_e[A].append(B)
			v_e[A].append(P[j - 1])
			v_e[B].append(A)
			v_e[B].append(P[j])
			v_e[P[j]].append(B)
			v_e[P[j]].append(P[j - 1])
			v_e[P[j - 1]].append(A)
			v_e[P[j - 1]].append(P[j])
			
			P[j - 1] = A
			A = B
		P[usamples] = B
	
	for i in range(1, usamples + 1):
		faces.append([Q[i - 1], Q[i], P[i], P[i-1]])
		
		v_f[Q[i - 1]].append(len(faces) - 1)
		v_f[Q[i]].append(len(faces) - 1)
		v_f[P[i]].append(len(faces) - 1)
		v_f[P[i - 1]].append(len(faces) - 1)
			
		v_e[Q[i - 1]].append(Q[i])
		v_e[Q[i - 1]].append(P[i - 1])
		v_e[Q[i]].append(Q[i - 1])
		v_e[Q[i]].append(P[i])
		v_e[P[i]].append(Q[i])
		v_e[P[i]].append(P[i - 1])
		v_e[P[i - 1]].append(Q[i - 1])
		v_e[P[i - 1]].append(P[i])
	
	BPyAddMesh.add_mesh_simple('MC', verts, [], faces)
	
	return [v_e, v_f]

def compute_curvature(v_e, v_f):
	# Obtain active object
	ob = bpy.data.scenes.active.objects.active
	
	# Check thath is a mesh
	if not ob or ob.type != 'Mesh':
		BPyMessages.Error_NoMeshActive()
		return

	# Get mesh
	mesh = ob.getData(mesh = 1)
	
	curv = []
	for v in mesh.verts:
		# Compute sum angles
		alpha = 0.0
		for i in range(0, len(v_e[v.index]), 2):
			v1 = mesh.verts[v_e[v.index][i]].co - v.co
			v2 = mesh.verts[v_e[v.index][i + 1]].co - v.co
			v1.normalize()
			v2.normalize()
			dotProd = v1.dot(v2)
			alpha = alpha + math.acos(dotProd)
		print "V: ", v.index, " alpha: ", alpha
	
	mesh.vertexColors= True # Enable face, vertex colors
	for f in mesh.faces:
		for i, v in enumerate(f):
			no= v.no
			col= f.col[i]
			col.r= int((no.x+1)*128)
			col.g= int((no.y+1)*128)
			col.b= int((no.z+1)*128)


def main():
	Window.EditMode(0)
	Window.WaitCursor(1)
	
	result = bezier_curves()
	compute_curvature(result[0], result[1])
	
	Window.WaitCursor(0) 

main()