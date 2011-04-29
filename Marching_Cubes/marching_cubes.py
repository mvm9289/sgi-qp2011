#!BPY
"""
Name: 'Marching Cubes'
Blender: 243
Group: 'AddMesh'
"""
import BPyAddMesh
import Blender
from taulaMC import lut

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
				
				print "Voxel: ", i, " ", j , " ", k
				print v0, " ", v1, " ", v2, " ", v3, " ", v4, " ", v5, " ", v6, " ", v7 
				
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
					
				print ltPos
				
				fList = lut[ltPos]
				print fList
				for f in fList:
					fIndex = []
					for e in f:
						v = Vector(float(i - N/2), float(j - N/2), float(k - N/2))
						if e == 0:
							v.z = v.z + 0.5
						if e == 1:
							v.z = v.z + 1.0
							v.x = v.x + 0.5
						if e == 2:
							v.z = v.z + 0.5
							v.x = v.x + 1.0
						if e == 3:
							v.x = v.x + 0.5
						if e == 4:
							v.y = v.y + 1.0
							v.z = v.z + 0.5
						if e == 5:
							v.y = v.y + 1.0
							v.z = v.z + 1.0
							v.x = v.x + 0.5
						if e == 6:
							v.y = v.y + 1.0
							v.z = v.z + 0.5
							v.x = v.x + 1.0
						if e == 7:
							v.y = v.y + 1.0
							v.x = v.x + 0.5
						if e == 8:
							v.y = v.y + 0.5
							v.z = v.z + 1.0
						if e == 9:
							v.y = v.y + 0.5
							v.x = v.x + 1.0
							v.z = v.z + 1.0
						if e == 10:
							v.y = v.y + 0.5
						if e == 11:
							v.y = v.y + 0.5
							v.x = v.x + 1.0
						
						vIndex = 0
						if (v.x, v.y, v.z) in vertsIndex:
							vIndex = vertsIndex[(v.x, v.y, v.z)]
						else:
							vertsIndex[(v.x, v.y, v.z)] = len(verts)
							vIndex = len(verts)
							verts.append(v)
						
						fIndex.append(vIndex)
				
					faces.append(fIndex)

	for v in verts:
		print v
	for f in faces:
		print f
	return (verts, faces)



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


def main():
	Blender.Window.FileSelector(file_callback, 'Tria fitxer de dades') 


main()