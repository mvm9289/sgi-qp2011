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

def getFaceVertices(mesh):
	face_vertices = []
	edges_faces = {}
	faces_centroid = {}
	
	for i in range(len(mesh.faces)):
		aux = Vector( 0.0, 0.0, 0.0)
		num_verts = len(mesh.faces[i].verts)
		for j in range(num_verts):
			aux = aux + mesh.faces[i].verts[j].co
			v1 = mesh.faces[i].verts[j]
			v2 = mesh.faces[i].verts[(j+1)%num_verts]
			if (v2, v1) in edges_faces:
				list = edges_faces[(v2, v1)]
				list.append(mesh.faces[i])
				edges_faces[(v2, v1)] = list
			else:
				edges_faces[(v1, v2)] = [mesh.faces[i],]
		aux = aux / num_verts
		face_vertices.append(aux)
		faces_centroid[mesh.faces[i]] = aux
	return [face_vertices, edges_faces, faces_centroid]

def getEdgeVertices(mesh, edges_faces, faces_centroid):
	edge_vertices = []
	vertices_edges = {}
	
	for i in range(len(mesh.edges)):
		aux = Vector( 0.0, 0.0, 0.0)
		if (mesh.edges[i].v1, mesh.edges[i].v2) in edges_faces:
			edge = (mesh.edges[i].v1, mesh.edges[i].v2)
		else:
			edge = (mesh.edges[i].v2, mesh.edges[i].v1)
		for face in edges_faces[edge]:
			aux = aux + faces_centroid[face]
		
		aux = (aux + mesh.edges[i].v1.co + mesh.edges[i].v2.co)/4
		edge_vertices.append(aux)
		
	return edge_vertices
		

def catmullClarkOneStep(mesh, t):
	result = getFaceVertices(mesh)
	face_vertices = result[0]
	edges_faces = result[1]
	faces_centroid = result[2]
	
	edge_vertices = getEdgeVertices(mesh, edges_faces, faces_centroid)
	
	newVertices = []
	newVertices.extend(face_vertices)
	newVertices.extend(edge_vertices)
	mesh.verts.extend(newVertices)
	
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
	
	mesh = ob.getData(mesh=1)
	t = sys.time()
	
	catmullClark(mesh, 1, 1)
	
	print 'Script executed in %.2f seconds' % (sys.time()-t)
	print
	print
	
	Window.WaitCursor(0)
	
if __name__ == '__main__':
	main()