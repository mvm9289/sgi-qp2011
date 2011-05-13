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

def bezier_curves():
	#si tenemos dos curvas de bezier, la u va de 0 a 2; si 3, de 0 a 3 ...
	#cuando pasamos del 1 hay que coger la segunda curva (ejemplo: esfera)
	
	incu = ( float(len(points)) / 4.0) / float(usamples)
	incv = (2.0*math.pi) / float(vsamples)
	
	num_bezier_curves = len(points) / 4
	
	P1 = points[0]
	P2 = points[1]
	P3 = points[2]
	P4 = points[3]
	
	control = 0
	frontera = 1
	indice = 4
	u = 0
	v = 0
	
	
	while control < num_bezier_curves:
		if control > frontera:
			frontera = frontera + 1
			P1 = points[indice]
			P2 = points[indice+1]
			P3 = points[indice+2]
			P4 = points[indice+3]
			u = u -1
		u = u + incu
		control = control + incu
		print "Control: ", control, "u: ", u


def main():
	bezier_curves()


main()