#!BPY 
""" 
Name: 'Informacio malla' 
Blender: 249
Group: 'Mesh' 
Tooltip: 'Put some useful info here' 
""" 
 
from Blender import Scene, Mesh, Window, sys 
import BPyMessages 
import bpy 
 
def processa_area(mesh):
	area = 0
	for i in range(len(mesh.faces)):
		area = area + mesh.faces[i].area
	return area
	
def processa_centroid(mesh):	
	cent = [0, 0, 0]
	for i in range(len(mesh.verts)):
		cent[0] = cent[0] + mesh.verts[i].co[0]
		cent[1] = cent[1] + mesh.verts[i].co[1]
		cent[2] = cent[2] + mesh.verts[i].co[2]
	cent[0] = cent[0]/len(mesh.verts)
	cent[1] = cent[1]/len(mesh.verts)
	cent[2] = cent[2]/len(mesh.verts)
	return cent

def processa_degree(mesh):
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
			
	average = max = min = len(v_e[0])
	
	for i in range(1, len(mesh.verts)):
		aux = len(v_e[i])
		if aux > max:
			max = aux
		if aux < min:
			min = aux
		average = average + aux
		
	average = average / len(mesh.verts)
	
	return [max, min, average]

def processa_convex(v1, v2, n1, n2):
	ve = v2.co - v1.co
	vcross = n1.cross(n2)
	
	if vcross[0] == 0 and vcross[1] == 0 and vcross[2] == 0:
		return 0
	
	dot = ve.dot(vcross)
	
	if dot > 0:
		return 1
	return -1

def processa_edges(mesh):
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
			res = processa_convex(mesh.verts[v1], mesh.verts[v2], e_f[(v1, v2)][0].no, e_f[(v2, v1)][0].no)
			if res == -1:
				concave = concave + 1
			elif res == 0:
				planar = planar + 1
			else:
				convex = convex + 1
			
	return [boundary, two_manifold, non_manifold, concave, convex, planar, other]

def processa_shells(mesh):
	e_f={}
	visited=[]
	
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
	pila = []
	while m < len(mesh.faces):
		shells = shells + 1
		
		f = 0
		for i in range(len(visited)):
			if visited[i] == 0:
				f = i
				break
		
		pila.append(f)
		
		while len(pila) != 0:
			f = pila.pop()
			visited[f] = 1
			m = m + 1
			n = len(mesh.faces[f].verts)
			for j in range(n):
				aux = (mesh.faces[f].verts[(j+1)%n].index, mesh.faces[f].verts[j].index)
				if aux in e_f:
					for i in range(len(e_f[aux])):
						if visited[e_f[aux][i]] == 0:
							pila.append(e_f[aux][i])
							
	return shells

def processa_euler(f, v, e, r, s):
	return ((e+r-f-v)/2)+s
	
def processa_volume_center_mass(mesh):
	Vol = 0
	Gx = 0
	Gy = 0
	Gz = 0
	
	M = [ [5,5,5] , [11,2,2] , [2,11,2] , [2,2,11] ]
	
	for f in range(len(mesh.faces)):
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
				
				Vol = Vol + w * (x*nx + y*ny + z*nz) / 3.0
				Gx = Gx + w * (x*x*nx)
				Gy = Gy + w * (y*y*ny)
				Gz = Gz + w * (z*z*nz)
				
			j = k
			
	return [Vol, Gx, Gy, Gz]

def redondeo(a):
	return int(a*1000+0.5)/1000.0

def processa_malla(me): 
        print 'Nom de la malla: ', me.name 
       # print ' V= ', len(me.verts) 
       # print ' E= ', len(me.edges) 
       # print ' F= ', len(me.faces)

    #    print 'Llista de vertexs:'
     #   for i in range(len(me.verts)):
      #          coord=me.verts[i].co
       #         print " ", i, ":", coord[0], coord[1], coord[2]

#        print 'Llista de cares:'
 #       for i in range(len(me.faces)):
  #              print " ", i, ":", 
   #             for j in range(len(me.faces[i].verts)):
    #                    print me.faces[i].verts[j].index,
     #           print

#        print "Llista d'arestes :"
 #       for i in range(len(me.edges)):
  #              print " ", i, ":", 
   #             print me.edges[i].v1.index, 
    #            print me.edges[i].v2.index
	
	
	
	print "Area de la malla :", redondeo(processa_area(me))
	
	cent = processa_centroid(me)
	print "Centroid de la malla : ", redondeo(cent[0]), " ", redondeo(cent[1]), " ", redondeo(cent[2])
	
	r = processa_degree(me)
	print "Grau: ", r[0], " ", r[1], " ", redondeo(r[2])
	
	ed = processa_edges(me)
	print "Arestes: ", ed[0]+ed[1]+ed[2]," (", ed[0], " boundary, ", ed[1], " manifold, ", ed[2], " non-manifold)"
	print "Arestes concaves ", ed[3],  ", convexes ", ed[4], ", planes ", ed[5], ", altres ", ed[6]

	f = len(me.faces)
	v = len(me.verts)
	e = len(me.edges)
	s = processa_shells(me)
	print "Euler: F: ", f, " V: ", v, " E: ", e, " R: 0 S: ", s, " H: ", processa_euler(f,v,e,0,s)
		
	r = processa_volume_center_mass(me)
	print "Volume: ", redondeo(r[0])
	print "Center mass: Gx: ", redondeo(r[1]), " Gy: ", redondeo(r[2]), " Gz: ", redondeo(r[3])

def main(): 
        # Obtenir l'objecte actiu (el darrer que hem seleccionat)
        ob = bpy.data.scenes.active.objects.active

        # Comprobar que sigui una malla  
        if not ob or ob.type != 'Mesh': 
                BPyMessages.Error_NoMeshActive() 
                return
           
        # Sortir del mode edit per si volem canviar la malla  
        Window.EditMode(0) 
        Window.WaitCursor(1) # canviar el cursor per un rellotge

        # Obtenir la mesh 
        mesh = ob.getData(mesh=1) # use Mesh API instead of old NMesh API  
        t = sys.time() 
         
        # Cridar a la funcio que processa la malla  
        processa_malla(mesh) 
         
        # Timing 
        print 'Script executat en %.2f segons' % (sys.time()-t) 

  # Restaurar cursor
        Window.WaitCursor(0) 
         
         
# This lets you can import the script without running it 
if __name__ == '__main__': 
        main() 