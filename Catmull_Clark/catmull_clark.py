#!BPY

"""
Name: CatmullClark
Group:
			Jose Antonio Navas Molina
			Miguel Angel Vico Moya
"""

from Blender import *
from Blender.Mathutils import *
import BPyMessages
import bpy

def computeVF(mesh):
	VF = [ [] for i in range(len(mesh.verts))]
	for i in range(len(mesh.faces)):
		for j in range(len(mesh.faces[i].verts)):
			VF[mesh.faces[i].verts[j].index].append(i)
	
	return VF

def computeVEandEIndex(mesh):
	VE = [ [] for i in range(len(mesh.verts)) ]
	Eidx = {}
	for i in range(len(mesh.edges)):
		VE[mesh.edges[i].v1.index].append(i)
		VE[mesh.edges[i].v2.index].append(i)
		
		key1 = (mesh.edges[i].v1.index, mesh.edges[i].v2.index)
		key2 = (mesh.edges[i].v2.index, mesh.edges[i].v1.index)
		Eidx[key1] = i
		Eidx[key2] = i
		
	return [VE, Eidx]

def computeEF(mesh):
	EF = {}
	for i in range(len(mesh.edges)):
		EF[(mesh.edges[i].v1.index, mesh.edges[i].v2.index)] = []
	for i in range(len(mesh.faces)):
		numFaceVerts = len(mesh.faces[i].verts)
		for j in range(numFaceVerts):
			j1 = (j + 1)%numFaceVerts
			key1 = (mesh.faces[i].verts[j].index, mesh.faces[i].verts[j1].index)
			key2 = (mesh.faces[i].verts[j1].index, mesh.faces[i].verts[j].index)
			if key1 in EF:
				EF[key1].append(i)
			elif key2 in EF:
				EF[key2].append(i)
	
	return EF

def getFaceVertices(mesh):
	face_vertices = []
	
	for i in range(len(mesh.faces)):
		aux = Vector( 0.0, 0.0, 0.0)
		num_verts = len(mesh.faces[i].verts)
		for j in range(num_verts):
			aux = aux + mesh.faces[i].verts[j].co	
		aux = aux / num_verts
		face_vertices.append(aux)
		
	return face_vertices

def getEdgeVertices(mesh, V, EF, t):
	edge_vertices = []
	
	for i in range(len(mesh.edges)):
		aux = Vector( 0.0, 0.0, 0.0)
		if (mesh.edges[i].v1.index, mesh.edges[i].v2.index) in EF:
			edge = (mesh.edges[i].v1.index, mesh.edges[i].v2.index)
		else:
			edge = (mesh.edges[i].v2.index, mesh.edges[i].v1.index)
		for j in range(len(EF[edge])):
			aux = aux + mesh.verts[V + EF[edge][j]].co
		
		aux = (aux + mesh.edges[i].v1.co + mesh.edges[i].v2.co)/4
		midpoint = (mesh.edges[i].v1.co + mesh.edges[i].v2.co)/2
		
		aux = (1 - t)*midpoint + t*aux
		 
		edge_vertices.append(aux)
		
	return edge_vertices

def computeF(mesh, V, faces):
	centroid = Vector( 0.0, 0.0, 0.0 )
	for face in faces:
		centroid = centroid + mesh.verts[V + face].co
	centroid = centroid/len(faces)
	
	return centroid

def computeR(mesh, edges):
	centroid = Vector( 0.0, 0.0, 0.0 )
	for edge in edges:
		midpoint = (mesh.edges[edge].v1.co + mesh.edges[edge].v2.co)/2
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
	for i in range(F):
		numFaceVerts = len(mesh.faces[i].verts)
		i1 = V + i # Centroid index
		for j in range(numFaceVerts):
			j1 = (j + 1)%numFaceVerts
			j2 = (j + 2)%numFaceVerts
			
			key1 = (mesh.faces[i].verts[j].index, mesh.faces[i].verts[j1].index)
			key2 = (mesh.faces[i].verts[j1].index, mesh.faces[i].verts[j2].index)
			
			i2 = mesh.verts[V + F + Eidx[key1]].index
			i3 = mesh.faces[i].verts[j1].index
			i4 = mesh.verts[V + F + Eidx[key2]].index
			mesh.faces.extend([i1, i2, i3, i4])
	
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
	for i in range(len(mesh.verts)):
		mesh.verts[i].co = (1 - t)*mesh.verts[i].co + t*vertex_vertices[i]
	
	updateFaces(mesh, oldNumV, oldNumF, Eidx)
	
def catmullClark(mesh, n, t):
	for i in range(n):
		catmullClarkOneStep(mesh, t)

def main():
	ob = bpy.data.scenes.active.objects.active
	
	if not ob or ob.type != 'Mesh':
		BPyMessages.Error_NoMeshActive()
		return
	
	Window.EditMode(0)
	
	Window.WaitCursor(1)
	
	me = ob.getData(mesh=1)
	#t = sys.time()
	
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
	
	#print 'Script executed in %.2f seconds' % (sys.time()-t)
	#print
	#print
	
	Window.WaitCursor(0)
	
if __name__ == '__main__':
	main()