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

	// ompliu AQUI la taula de vèrtexs i de cares

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