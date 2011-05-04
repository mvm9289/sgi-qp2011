#!BPY
"""
Name: 'Marching Cubes'
Blender: 243
Group: 'AddMesh'
"""
import BPyAddMesh
import Blender
from taulaMC import lut
from Blender import Scene, Mesh, Window, sys
import BPyMessages
import bpy

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


def computeShells(mesh):
	e_f = {}
	visited = []
	for i in range(len(mesh.faces)):
		visited.append(0)
		n = len(mesh.faces[i].verts)
		for j in range(n):
			aux = (mesh.faces[i].verts[j].index, mesh.faces[i].verts[(j+1)%n].index)
			if aux in e_f:
				e_f[aux].append(i)
			else:
				e_f[aux] = [i]
                                
	m = 0
	shells = 0
	stack = []
	shells_faces = []
	while m < len(mesh.faces):
		shells = shells + 1
		faces = []
		                
		f = 0
		for i in range(len(visited)):
			if visited[i] == 0:
				f = i
				break
               
		stack.append(f)
		while len(stack) != 0:
			f = stack.pop()
			if visited[f] == 0:
				faces.append(f)
				visited[f] = 1
				m = m + 1
				n = len(mesh.faces[f].verts)
				for j in range(n):
					aux = (mesh.faces[f].verts[(j+1)%n].index, mesh.faces[f].verts[j].index)
					if aux in e_f:
						for i in range(len(e_f[aux])):
							if visited[e_f[aux][i]] == 0:
								stack.append(e_f[aux][i])

		shells_faces.append(faces);
                                                        
	return [shells, shells_faces]

def computeGenus(f, v, e, r, s):
	return int(((e+r-f-v)/2.0) + s + 0.5)



def file_callback(filename):
	
	# Demanar isovalue
	Draw = Blender.Draw
	ISOVALUE = Draw.Create(0.0)
	if not Draw.PupBlock('Marching Cubes', [('Isovalue:', ISOVALUE,  -100, 100, 'Valor isodensitat (isovalue).'),]):
		return
	
	# Llegir dades		
	dades=[]
	file = open(filename, "r")
	N = int(file.readline())
	print "Llegint dades: ", N, "x", N, "x", N
	for i in range(N*N*N):
		dades.append(float(file.readline()))
	print "Dades llegides correctament"
	file.close()
	
	# Generar vertexs i cares
	(verts, faces) = marching_cubes(dades, N, ISOVALUE.val)
	
	# Afegir la malla a blender
	BPyAddMesh.add_mesh_simple('MC', verts, [], faces)
	
	ob = bpy.data.scenes.active.objects.active
	
	if not ob or ob.type != 'Mesh':
		BPyMessages.Error_NoMeshActive()
		return
	
	Window.EditMode(0)
	Window.WaitCursor(1)
	mesh = ob.getData(mesh=1)
	
	f = len(mesh.faces)
	v = len(mesh.verts)
	e = len(mesh.edges)
	result = computeShells(mesh)
	s = result[0]
	print "Euler:          F=", f, " V=", v, " E=", e, " R= 0  S=", s, " H=", computeGenus(f, v, e, 0, s)
	


def main():
	Blender.Window.FileSelector(file_callback, 'Tria fitxer de dades') 


main()