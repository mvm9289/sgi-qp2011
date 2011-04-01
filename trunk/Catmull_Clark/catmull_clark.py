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
	vertex_faces = {}
	
	for i in range(len(mesh.faces)):
		aux = Vector( 0.0, 0.0, 0.0)
		num_verts = len(mesh.faces[i].verts)
		
		# Compute VF's
		for j in range(num_verts):
			# Create V{F}
			if mesh.faces[i].verts[j] in vertex_faces:
				vertex_faces[mesh.faces[i].verts[j]].append(mesh.faces[i])
			else:
				vertex_faces[mesh.faces[i].verts[j]] = [mesh.faces[i],]
				
			aux = aux + mesh.faces[i].verts[j].co
			v1 = mesh.faces[i].verts[j]
			v2 = mesh.faces[i].verts[(j+1)%num_verts]
			
			# Create E{F}
			if (v2, v1) in edges_faces:
				list = edges_faces[(v2, v1)]
				list.append(mesh.faces[i])
				edges_faces[(v2, v1)] = list
			else:
				edges_faces[(v1, v2)] = [mesh.faces[i],]
			
		aux = aux / num_verts
		face_vertices.append(aux)
		faces_centroid[mesh.faces[i]] = aux
	return [face_vertices, edges_faces, faces_centroid, vertex_faces]

def getEdgeVertices(mesh, edges_faces, faces_centroid):
	edge_vertices = []
	vertex_edges = {}
	
	for i in range(len(mesh.edges)):
		# Create V{E}
		if mesh.edges[i].v1 in vertex_edges:
			vertex_edges[mesh.edges[i].v1].append(mesh.edges[i])
		else:
			vertex_edges[mesh.edges[i].v1] = [mesh.edges[i],]
		if mesh.edges[i].v2 in vertex_edges:
			vertex_edges[mesh.edges[i].v2].append(mesh.edges[i])
		else:
			vertex_edges[mesh.edges[i].v2] = [mesh.edges[i],]
		
		# Compute VE's	
		aux = Vector( 0.0, 0.0, 0.0)
		if (mesh.edges[i].v1, mesh.edges[i].v2) in edges_faces:
			edge = (mesh.edges[i].v1, mesh.edges[i].v2)
		else:
			edge = (mesh.edges[i].v2, mesh.edges[i].v1)
		for face in edges_faces[edge]:
			aux = aux + faces_centroid[face]
		
		aux = (aux + mesh.edges[i].v1.co + mesh.edges[i].v2.co)/4
		edge_vertices.append(aux)
		
	return [edge_vertices, vertex_edges]

def computeF(faces, faces_centroid):
	centroid = Vector( 0.0, 0.0, 0.0 )
	for face in faces:
		centroid = centroid + faces_centroid[face]
	centroid = centroid/len(faces)
	
	return centroid

def computeR(edges):
	centroid = Vector( 0.0, 0.0, 0.0 )
	for edge in edges:
		midpoint = (edge.v1.co + edge.v2.co)/2
		centroid = centroid + midpoint
	centroid = centroid/len(edges)
	
	return centroid

def getVertexVertices(mesh, vertex_faces, vertex_edges, faces_centroid):
	vertex_copy = []
	
	for v in mesh.verts:
		vertex_copy.append(v.co)
		
	for i in range(len(mesh.verts)):
		F = computeF(vertex_faces[mesh.verts[i]], faces_centroid)
		R = computeR(vertex_edges[mesh.verts[i]])
		n = len(vertex_edges[mesh.verts[i]])
		vertex_copy[i] = (F + 2*R + (n - 3)*mesh.verts[i].co)*(1.0/n)
	
	return vertex_copy
		

def catmullClarkOneStep(mesh, t):
	result = getFaceVertices(mesh)
	face_vertices = result[0]
	edges_faces = result[1]
	faces_centroid = result[2]
	vertex_faces = result[3]
	
	result = getEdgeVertices(mesh, edges_faces, faces_centroid)
	edge_vertices = result[0]
	vertex_edges = result[1]
	
	vertex_vertices = getVertexVertices(mesh, vertex_faces, vertex_edges, faces_centroid)
	
	for i in range(len(mesh.verts)):
		mesh.verts[i].co = vertex_vertices[i]
	
	#mesh.verts.extend(face_vertices)
	#mesh.verts.extend(edge_vertices)
	
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
	t = sys.time()
	
	print 'Mesh name: ', me.name
	print 
	print ' V= ', len(me.verts) 
	print ' E= ', len(me.edges) 
	print ' F= ', len(me.faces)

	print 'Vertex list:'
	for i in range(len(me.verts)):
	        coord=me.verts[i].co
	        print " ", i, ":", coord[0], coord[1], coord[2]

	print 'Faces list:'
	for i in range(len(me.faces)):
	        print " ", i, ":", 
	        for j in range(len(me.faces[i].verts)):
	                print me.faces[i].verts[j].index,
	        print

	print "Edges list:"
	for i in range(len(me.edges)):
	        print " ", i, ":", 
	        print me.edges[i].v1.index, 
	        print me.edges[i].v2.index
	
	catmullClark(me, 1, 1)
	
	print 'Script executed in %.2f seconds' % (sys.time()-t)
	print
	print
	
	Window.WaitCursor(0)
	
if __name__ == '__main__':
	main()