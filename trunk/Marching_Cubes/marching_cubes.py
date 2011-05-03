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
				v0 = dades[i*N*N + j*N + k]
				v1 = dades[(i + 1)*N*N + j*N + k]
				v2 = dades[i*N*N + (j + 1)*N + k]
				v3 = dades[(i + 1)*N*N + (j + 1)*N + k]
				v4 = dades[i*N*N + j*N + k + 1]
				v5 = dades[(i + 1)*N*N + j*N + k + 1]
				v6 = dades[i*N*N + (j + 1)*N + k + 1]
				v7 = dades[(i + 1)*N*N + (j + 1)*N + k + 1]
				
				ltPos = 0
				if v0 < isovalue:
					ltPos = ltPos + 1
				if v1 < isovalue:
					ltPos = ltPos + 2
				if v2 < isovalue:
					ltPos = ltPos + 4
				if v3 < isovalue:
					ltPos = ltPos + 8
				if v4 < isovalue:
					ltPos = ltPos + 16
				if v5 < isovalue:
					ltPos = ltPos + 32
				if v6 < isovalue:
					ltPos = ltPos + 64
				if v7 < isovalue:
					ltPos = ltPos + 128
				
				fList = lut[ltPos]
				for f in fList:
					fIndex = []
					for e in f:
						v = Vector(float(i - N/2), float(j - N/2), float(k - N/2))
						vertex = Vector(float(i - N/2), float(j - N/2), float(k - N/2))
						if e == 0:
							#v0  v4
							vertex.z = vertex.z + interpolate(v0, v4, isovalue)
							v.z = v.z + 0.5
						if e == 1:
							#v4  v5
							vertex.z = vertex.z + 1.0
							vertex.x = vertex.x + interpolate(v4, v5, isovalue)
							v.z = v.z + 1.0
							v.x = v.x + 0.5
						if e == 2:
							#v5  v1
							vertex.z = vertex.z + interpolate(v1, v5, isovalue)
							vertex.x = vertex.x + 1.0
							v.z = v.z + 0.5
							v.x = v.x + 1.0
						if e == 3:
							#v1  v0
							vertex.x = vertex.x + interpolate(v0, v1, isovalue)
							v.x = v.x + 0.5
						if e == 4:
							#v2  v6
							vertex.y = vertex.y + 1.0
							vertex.z = vertex.z + interpolate(v2, v6, isovalue)
							v.y = v.y + 1.0
							v.z = v.z + 0.5
						if e == 5:
							#v6  v7
							vertex.y = vertex.y + 1.0
							vertex.z = vertex.z + 1.0
							vertex.x = vertex.x + interpolate(v6, v7, isovalue)
							v.y = v.y + 1.0
							v.z = v.z + 1.0
							v.x = v.x + 0.5
						if e == 6:
							#v7  v3
							vertex.y = vertex.y + 1.0
							vertex.z = vertex.z + interpolate(v3, v7, isovalue)
							vertex.x = vertex.x + 1.0
							v.y = v.y + 1.0
							v.z = v.z + 0.5
							v.x = v.x + 1.0
						if e == 7:
							#v3  v2
							vertex.y = vertex.y + 1.0
							vertex.x = vertex.x + interpolate(v3, v2, isovalue)
							v.y = v.y + 1.0
							v.x = v.x + 0.5
						if e == 8:
							#v4  v6
							vertex.y = vertex.y + interpolate(v4, v6, isovalue)
							vertex.z = vertex.z + 1.0
							v.y = v.y + 0.5
							v.z = v.z + 1.0
						if e == 9:
							#v5  v7
							vertex.y = vertex.y + interpolate(v5, v7, isovalue)
							vertex.x = vertex.x + 1.0
							vertex.z = vertex.z + 1.0
							v.y = v.y + 0.5
							v.x = v.x + 1.0
							v.z = v.z + 1.0
						if e == 10:
							#v0  v2
							vertex.y = vertex.y + interpolate(v0, v2, isovalue)
							v.y = v.y + 0.5
						if e == 11:
							#v1  v3
							vertex.y = vertex.y + interpolate(v1, v3, isovalue)
							vertex.x = vertex.x + 1.0
							v.y = v.y + 0.5
							v.x = v.x + 1.0
						
						vIndex = 0
						if (v.x, v.y, v.z) in vertsIndex:
							vIndex = vertsIndex[(v.x, v.y, v.z)]
						else:
							vertsIndex[(v.x, v.y, v.z)] = len(verts)
							vIndex = len(verts)
							verts.append(vertex)
						
						fIndex.append(vIndex)
				
					faces.append(fIndex)

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