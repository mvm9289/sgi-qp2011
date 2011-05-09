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
from Blender import *
import BPyMessages
import bpy


############## GLOBAL VARS ##############

DATA_FILE = '/Users/mvm9289/Desktop/FIB/SGI/trunk/Marching_Cubes/examples/Blooby.txt'
INI_ISOVALUE = -10.0
FIN_ISOVALUE = 10.0


############## MARCHING CUBES ##############

def interpolate(v1, v2, isovalue):
	return ((v1 - isovalue) / (v1 -v2))

def marching_cubes(dades, N, isovalue):
	Vector = Blender.Mathutils.Vector
	verts = []
	faces = []
	vertsIndex = {}

	for i in range(N-1):
		for j in range(N-1):
			for k in range(N-1):
				# Extract values
				v0 = dades[i*N*N + j*N + k]
				v1 = dades[(i + 1)*N*N + j*N + k]
				v2 = dades[i*N*N + (j + 1)*N + k]
				v3 = dades[(i + 1)*N*N + (j + 1)*N + k]
				v4 = dades[i*N*N + j*N + k + 1]
				v5 = dades[(i + 1)*N*N + j*N + k + 1]
				v6 = dades[i*N*N + (j + 1)*N + k + 1]
				v7 = dades[(i + 1)*N*N + (j + 1)*N + k + 1]
				
				# Find MC configuration
				lutPos = 0
				if v0 < isovalue:
					lutPos = lutPos + 1
				if v1 < isovalue:
					lutPos = lutPos + 2
				if v2 < isovalue:
					lutPos = lutPos + 4
				if v3 < isovalue:
					lutPos = lutPos + 8
				if v4 < isovalue:
					lutPos = lutPos + 16
				if v5 < isovalue:
					lutPos = lutPos + 32
				if v6 < isovalue:
					lutPos = lutPos + 64
				if v7 < isovalue:
					lutPos = lutPos + 128
				
				# Create vertices and faces
				facesList = lut[lutPos]
				for f in facesList:
					facesIndex = []
					for e in f:
						falseVertex = Vector(float(i), float(j), float(k))
						realVertex = Vector(float(i), float(j), float(k))
						if e == 0: #v0  v4
							realVertex = Vector(float(i), float(j), float(k) + interpolate(v0, v4, isovalue))
							falseVertex = Vector(float(i), float(j), float(k) + 0.5)
						elif e == 1: #v4  v5
							realVertex = Vector(float(i) + interpolate(v4, v5, isovalue), float(j), float(k) + 1.0)
							falseVertex = Vector(float(i) + 0.5, float(j), float(k) + 1.0)
						elif e == 2: #v5  v1
							realVertex = Vector(float(i) + 1.0, float(j), float(k) + interpolate(v1, v5, isovalue))
							falseVertex = Vector(float(i) + 1.0, float(j), float(k) + 0.5)
						elif e == 3: #v1  v0
							realVertex = Vector(float(i) + interpolate(v0, v1, isovalue), float(j), float(k))
							falseVertex = Vector(float(i) + 0.5, float(j), float(k))
						elif e == 4: #v2  v6
							realVertex = Vector(float(i), float(j) + 1.0, float(k) + interpolate(v2, v6, isovalue))
							falseVertex = Vector(float(i), float(j) + 1.0, float(k) + 0.5)
						elif e == 5: #v6  v7
							realVertex = Vector(float(i) + interpolate(v6, v7, isovalue), float(j) + 1.0, float(k) + 1.0)
							falseVertex = Vector(float(i) + 0.5, float(j) + 1.0, float(k) + 1.0)
						elif e == 6: #v7  v3
							realVertex = Vector(float(i) + 1.0, float(j) + 1.0, float(k) + interpolate(v3, v7, isovalue))
							falseVertex = Vector(float(i) + 1.0, float(j) + 1.0, float(k) + 0.5)
						elif e == 7: #v3  v2
							realVertex = Vector(float(i) + interpolate(v3, v2, isovalue), float(j) + 1.0, float(k))
							falseVertex = Vector(float(i) + 0.5, float(j) + 1.0, float(k))
						elif e == 8: #v4  v6
							realVertex = Vector(float(i), float(j) + interpolate(v4, v6, isovalue), float(k) + 1.0)
							falseVertex = Vector(float(i), float(j) + 0.5, float(k) + 1.0)
						elif e == 9: #v5  v7
							realVertex = Vector(float(i) + 1.0, float(j) + interpolate(v5, v7, isovalue), float(k) + 1.0)
							falseVertex = Vector(float(i) + 1.0, float(j) + 0.5, float(k) + 1.0)
						elif e == 10: #v0  v2
							realVertex = Vector(float(i), float(j) + interpolate(v0, v2, isovalue), float(k))
							falseVertex = Vector(float(i), float(j) + 0.5, float(k))
						elif e == 11: #v1  v3
							realVertex = Vector(float(i) + 1.0, float(j) + interpolate(v1, v3, isovalue), float(k))
							falseVertex = Vector(float(i) + 1.0, float(j) + 0.5, float(k))
						
						vertexIndex = 0
						key = (falseVertex.x, falseVertex.y, falseVertex.z)
						if key in vertsIndex:
							vertexIndex = vertsIndex[key]
						else:
							vertsIndex[key] = len(verts)
							vertexIndex = len(verts)
							realVertex.x = (realVertex.x - N/2) * 2 / N
							realVertex.y = (realVertex.y - N/2) * 2 / N
							realVertex.z = (realVertex.z - N/2) * 2 / N
							verts.append(realVertex)
						
						facesIndex.append(vertexIndex)
				
					faces.append(facesIndex)

	return (verts, faces)


############## MAIN ##############

def main():
	# Llegir dades		
	dades=[]
	file = open(DATA_FILE, "r")
	N = int(file.readline())
	print "Llegint dades: ", N, "x", N, "x", N
	for i in range(N*N*N):
		dades.append(float(file.readline()))
	print "Dades llegides correctament"
	file.close()
	
	
	Window.EditMode(0)
	
	Window.WaitCursor(1)
	
	scene = Scene.GetCurrent()
	for obj in scene.objects:
		if obj.type == 'Mesh' and "MC" in obj.name:
			meshT = obj.getData(0, 1)
			meshT.verts.delete(range(len(meshT.verts)))
			scene.objects.unlink(obj)
	
	start = Get("staframe")
	end = Get("endframe")
	num = end - start
	current = Get("curframe")
	time = float(current - start)/num
	
	# Generar vertexs i cares
	(verts, faces) = marching_cubes(dades, N, INI_ISOVALUE - (INI_ISOVALUE - FIN_ISOVALUE)*time)
	
	# Afegir la malla a blender
	BPyAddMesh.add_mesh_simple('MC', verts, [], faces)
	
	scene.update()
	
	Window.WaitCursor(0)


main()