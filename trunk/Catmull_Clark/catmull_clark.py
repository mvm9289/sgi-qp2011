#!BPY


"""""""""""""""""""""""""""""""""
Name: CatmullClark
Group:
			Jose Antonio Navas Molina
			Miguel Angel Vico Moya
			
"""""""""""""""""""""""""""""""""


############## IMPORTS ##############

from Blender import *
from Blender.Mathutils import *
import BPyMessages
import bpy


############## AUXILIARY TOPOLOGIES ##############

def computeVF(mesh):
	VF = [ [] for i in range(len(mesh.verts))]
	for f in mesh.faces:
		for v in f.verts:
			VF[v.index].append(f.index)
	
	return VF

def computeVEandEIndex(mesh):
	VE = [ [] for i in range(len(mesh.verts)) ]
	Eidx = {}
	for e in mesh.edges:
		VE[e.v1.index].append(e.index)
		VE[e.v2.index].append(e.index)
		
		key1 = (e.v1.index, e.v2.index)
		key2 = (e.v2.index, e.v1.index)
		Eidx[key1] = e.index
		Eidx[key2] = e.index
		
	return [VE, Eidx]

def computeEF(mesh):
	EF = {}
	for e in mesh.edges:
		EF[(e.v1.index, e.v2.index)] = []
	for f in mesh.faces:
		numFaceVerts = len(f.verts)
		for j in range(numFaceVerts):
			j1 = (j + 1)%numFaceVerts
			key1 = (f.verts[j].index, f.verts[j1].index)
			key2 = (f.verts[j1].index, f.verts[j].index)
			if key1 in EF:
				EF[key1].append(f.index)
			elif key2 in EF:
				EF[key2].append(f.index)
	
	return EF


############## CATMULL CLARK ##############

def getFaceVertices(mesh):
	face_vertices = []
	
	for f in mesh.faces:
		aux = Vector( 0.0, 0.0, 0.0)
		num_verts = len(f.verts)
		for v in f.verts:
			aux = aux + v.co	
		aux = aux / num_verts
		face_vertices.append(aux)
		
	return face_vertices

def getEdgeVertices(mesh, V, EF, t):
	edge_vertices = []
	
	for e in mesh.edges:
		key1 = (e.v1.index, e.v2.index)
		key2 = (e.v2.index, e.v1.index)
		if key1 in EF:
			edge = key1
		elif key2 in EF:
			edge = key2
		
		aux = Vector( 0.0, 0.0, 0.0)
		for j in range(len(EF[edge])):
			aux = aux + mesh.verts[V + EF[edge][j]].co
		
		aux = (aux + e.v1.co + e.v2.co)/4
		midpoint = (e.v1.co + e.v2.co)/2
		
		aux = (1 - t)*midpoint + t*aux
		 
		edge_vertices.append(aux)
		
	return edge_vertices

def computeF(mesh, V, faces):
	centroid = Vector( 0.0, 0.0, 0.0 )
	for f in faces:
		centroid = centroid + mesh.verts[V + f].co
	centroid = centroid/len(faces)
	
	return centroid

def computeR(mesh, edges):
	centroid = Vector( 0.0, 0.0, 0.0 )
	for e in edges:
		midpoint = (mesh.edges[e].v1.co + mesh.edges[e].v2.co)/2
		centroid = centroid + midpoint
	centroid = centroid/len(edges)
	
	return centroid

def getVertexVertices(mesh, V, VF, VE):
	vertex_copy = []
	
	for v in mesh.verts:
		vertex_copy.append(v.co)
		
	for i in range(V):
		F = computeF(mesh, V, VF[mesh.verts[i].index])
		R = computeR(mesh, VE[mesh.verts[i].index])
		n = len(VE[mesh.verts[i].index])
		vertex_copy[i] = (F + 2*R + (n - 3)*mesh.verts[i].co)*(1.0/n)
	
	return vertex_copy

def updateFaces(mesh, V, F, Eidx):
	aux = []
	for f in mesh.faces:
		numFaceVerts = len(f.verts)
		i1 = V + f.index # Centroid index
		for j in range(numFaceVerts):
			j1 = (j + 1)%numFaceVerts
			j2 = (j + 2)%numFaceVerts
			
			key1 = (f.verts[j].index, f.verts[j1].index)
			key2 = (f.verts[j1].index, f.verts[j2].index)
			
			i2 = mesh.verts[V + F + Eidx[key1]].index
			i3 = f.verts[j1].index
			i4 = mesh.verts[V + F + Eidx[key2]].index
			aux.append([i1, i2, i3, i4])
	
	mesh.faces.extend(aux)
	mesh.faces.delete(1, range(F))

def catmullClarkOneStep(mesh, t):
	oldNumV = len(mesh.verts)
	oldNumE = len(mesh.edges)
	oldNumF = len(mesh.faces)
	
	VF = computeVF(mesh)
	result = computeVEandEIndex(mesh)
	VE = result[0]
	Eidx = result[1]
	EF = computeEF(mesh)
	
	face_vertices = getFaceVertices(mesh)
	mesh.verts.extend(face_vertices)
	
	edge_vertices = getEdgeVertices(mesh, oldNumV, EF, t)
	mesh.verts.extend(edge_vertices)
	
	vertex_vertices = getVertexVertices(mesh, oldNumV, VF, VE)
	for v in mesh.verts:
		v.co = (1 - t)*v.co + t*vertex_vertices[v.index]
	
	updateFaces(mesh, oldNumV, oldNumF, Eidx)
	
def catmullClark(mesh, n, t):
	for i in range(n):
		catmullClarkOneStep(mesh, t)


############## MAIN ##############

def main():
	ob = bpy.data.scenes.active.objects.active
	
	if not ob or ob.type != 'Mesh':
		BPyMessages.Error_NoMeshActive()
		return
	
	Window.EditMode(0)
	
	Window.WaitCursor(1)
	
	me = ob.getData(mesh=1)
	t = sys.time()
	
	#print 'Mesh name: ', me.name
	#print 
	#print ' V= ', len(me.verts) 
	#print ' E= ', len(me.edges) 
	#print ' F= ', len(me.faces)

	#print 'Vertex list:'
	#for i in range(len(me.verts)):
	#        coord=me.verts[i].co
	#        print " ", i, ":", coord[0], coord[1], coord[2]

	#print 'Faces list:'
	#for i in range(len(me.faces)):
	#        print " ", i, ":", 
	#        for j in range(len(me.faces[i].verts)):
	#                print me.faces[i].verts[j].index,
	#        print

	#print "Edges list:"
	#for i in range(len(me.edges)):
	#        print " ", i, ":", 
	#        print me.edges[i].v1.index, 
	#        print me.edges[i].v2.index
	
	catmullClark(me, 1, 1)
	
	print 'Script executed in %.2f seconds' % (sys.time()-t)
	print
	print
	
	Window.WaitCursor(0)
	
if __name__ == '__main__':
	main()