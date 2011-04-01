#!BPY 

"""
Name: InfoMesh 
Group:
	Jose Antonio Navas Molina
	Miguel Angel Vico Moya

"""
 
from Blender import Scene, Mesh, Window, sys 
import BPyMessages 
import bpy 
 
def computeArea(mesh):
	area = 0
	for i in range(len(mesh.faces)):
		area = area + mesh.faces[i].area
	
	return area
	
def computeCentroid(mesh):	
	cent = [0, 0, 0]
	for i in range(len(mesh.verts)):
		cent[0] = cent[0] + mesh.verts[i].co[0]
		cent[1] = cent[1] + mesh.verts[i].co[1]
		cent[2] = cent[2] + mesh.verts[i].co[2]
	
	cent[0] = cent[0]/len(mesh.verts)
	cent[1] = cent[1]/len(mesh.verts)
	cent[2] = cent[2]/len(mesh.verts)
	
	return cent

def computeDegree(mesh):
	v_e={}
	
	for i in range(len(mesh.edges)):
		if mesh.edges[i].v1.index in v_e:
			v_e[mesh.edges[i].v1.index].append(mesh.edges[i])
		else:
			v_e[mesh.edges[i].v1.index] = [mesh.edges[i]]
		if mesh.edges[i].v2.index in v_e:
			v_e[mesh.edges[i].v2.index].append(mesh.edges[i])
		else:
			v_e[mesh.edges[i].v2.index] = [mesh.edges[i]]
			
	max = min = len(v_e[0])
	average = 0.0
	average = average + len(v_e[0])
	
	for i in range(1, len(mesh.verts)):
		aux = len(v_e[i])
		if aux > max:
			max = aux
		if aux < min:
			min = aux
		average = average + aux
		
	average = average/len(mesh.verts)
	
	return [max, min, average]

def isConvexEdge(v1, v2, n1, n2):
	n1.normalize()
	n2.normalize()
	ve = v2.co - v1.co
	ve.normalize()
	
	vcross = n1.cross(n2)
	if vcross.length < 0.001:
		return 0
	
	dot = ve.dot(vcross)
	if dot > 0:
		return 1
	
	return -1

def computeEdges(mesh):
	e_f={}
	
	for i in range(len(mesh.faces)):
		n = len(mesh.faces[i].verts)
		for j in range(n):
			aux = (mesh.faces[i].verts[j].index, mesh.faces[i].verts[(j+1)%n].index)
			if aux in e_f:
				e_f[aux].append(mesh.faces[i])
			else:
				e_f[aux] = [mesh.faces[i]]

	boundary = two_manifold = non_manifold = 0
	other = convex = concave = planar = 0
	
	for i in range(len(mesh.edges)):
		v1 = mesh.edges[i].v1.index
		v2 = mesh.edges[i].v2.index
		
		aux = 0
		if (v1, v2) in e_f:
			aux = len(e_f[(v1, v2)])
		if (v2, v1) in e_f:
			aux = aux + len(e_f[(v2,v1)])
	
		if aux > 2:
			non_manifold = non_manifold + 1
			other = other + 1
		elif aux < 2:
			boundary = boundary + 1
			other = other + 1
		else:
			two_manifold = two_manifold + 1
			res = isConvexEdge(mesh.verts[v1], mesh.verts[v2], e_f[(v1, v2)][0].no, e_f[(v2, v1)][0].no)
			if res == -1:
				concave = concave + 1
			elif res == 0:
				planar = planar + 1
			else:
				convex = convex + 1
			
	return [boundary, two_manifold, non_manifold, concave, convex, planar, other]

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
	
def computeVolumeCenterMassCells(mesh, shells):
	totalVol = 0
	Gx = 0
	Gy = 0
	Gz = 0
	cells = len(shells)
	
	M = [ [5,5,5] , [11,2,2] , [2,11,2] , [2,2,11] ]

	for s in range(len(shells)):
		vol = 0
		for fs in range(len(shells[s])):
			f = shells[s][fs]
			i = mesh.faces[f].verts[0]
			j = mesh.faces[f].verts[1]
			for v in range(2,len(mesh.faces[f].verts)):
				k = mesh.faces[f].verts[v]
				nx = (j.co[1] - i.co[1]) * (k.co[2] - j.co[2]) - (k.co[1] - j.co[1]) * (j.co[2] - i.co[2])
				ny = (k.co[0] - j.co[0]) * (j.co[2] - i.co[2]) - (j.co[0] - i.co[0]) * (k.co[2] - j.co[2])
				nz = (j.co[0] - i.co[0]) * (k.co[1] - j.co[1]) - (k.co[0] - j.co[0]) * (j.co[1] - i.co[1])
				
				for l in range(4):
					w = 0
					if l == 0:
						w = -27.0/96.0
					else:
						w = 25.0/96.0
					
					x = (M[l][0] * i.co[0] + M[l][1] * j.co[0] + M[l][2] * k.co[0] )/15.0
					y = (M[l][0] * i.co[1] + M[l][1] * j.co[1] + M[l][2] * k.co[1] )/15.0
					z = (M[l][0] * i.co[2] + M[l][1] * j.co[2] + M[l][2] * k.co[2] )/15.0
					
					vol = vol + w * (x*nx + y*ny + z*nz) / 3.0
					Gx = Gx + w * (x*x*nx)
					Gy = Gy + w * (y*y*ny)
					Gz = Gz + w * (z*z*nz)
					
				j = k

		if vol < 0:
			cells = cells - 1
		totalVol = totalVol + vol
			
	return [totalVol, Gx, Gy, Gz, cells]

def round(a):
	return int(a*1000+0.5)/1000.0

def meshProcessing(me): 
	print 'Mesh name: ', me.name
	print 
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
	
	
	result = round(computeArea(me))
	print "Surface area:  ", result
	
	result = computeCentroid(me)
	print "Mesh centroid:  (", round(result[0]), ", ", round(result[1]), ", ", round(result[2]), ")"
	
	result = computeDegree(me)
	print "Vertex degree:  max=", result[0], " min=", result[1], " average=", round(result[2])
	
	result = computeEdges(me)
	print "Edges:          total=", result[0]+result[1]+result[2]," boundary=", result[0], " manifold=", result[1], " non-manifold=", result[2]
	print "                concave=", result[3],  " convex=", result[4], " planar=", result[5], " other=", result[6]

	non_manifold = 0
	if result[6] > 0:
		non_manifold = 1

	f = len(me.faces)
	v = len(me.verts)
	e = len(me.edges)
	result = computeShells(me)
	s = result[0]
	print "Euler:          F=", f, " V=", v, " E=", e, " R= 0  S=", s, " H=", computeGenus(f, v, e, 0, s)
		
	result = computeVolumeCenterMassCells(me, result[1])
	print "Center of mass: (", round(result[1]), ", ", round(result[2]), ", ", round(result[3]), ")"
	print "Volume:        ", round(result[0])
	if non_manifold:
		print "Cells:          Undetermined (Non-manifold)"
	else:
		print "Cells:         ", result[4]
	
	print

def main(): 
	# Obtain active object
	ob = bpy.data.scenes.active.objects.active
	
	# Check thath is a mesh  
	if not ob or ob.type != 'Mesh': 
		BPyMessages.Error_NoMeshActive() 
		return
	
	# Exit from mode edit to edit mesh (if needed)  
	Window.EditMode(0)

	# Change cursor
	Window.WaitCursor(1)
	
	# Get mesh 
	mesh = ob.getData(mesh=1)
	t = sys.time()
	
	# Mesh processing
	meshProcessing(mesh)
	
	# Timing
	print 'Script executed in %.2f seconds' % (sys.time()-t)
	print
	print
	
	# Restore cursor
	Window.WaitCursor(0) 
         
         
# This lets you can import the script without running it 
if __name__ == '__main__':
	main() 