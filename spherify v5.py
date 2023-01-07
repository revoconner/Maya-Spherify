import pymel.core as pm
import numpy as np
import math

#testing purposes
print("\n\n########### RESULTS HERE ############\n\n")

#Defining a class with global variables then aliasing with GV
class globalVar:
	def __init__(self):
		self.coords = None
		self.new_coord_tuple = None
		self.final_coord_tuple = None
		self.vertices = None
		self.sliderVal = None
		self.checkpointVal = None
		self.pivotFlag = False
		self.vert_selection = None
		self.mesh = None
		self.points = None

gv= globalVar()


#Storing the original WS of the vertices
def original_param():
	# Get the current selection
	sel = pm.ls(selection=True)
	gv.mesh = pm.ls(*sel, o=True)
	vertex = pm.polyListComponentConversion(sel, tv=True)

	gv.vert_selection = pm.filterExpand(vertex, ex=True, sm=31)

	# Filter the selection to only include vertices and faces
	try:
		gv.vertices = [v for v in gv.vert_selection]
	except:
		pm.confirmDialog(title="Error",message= "Select something first, either some vertices (at least 4) or a mesh", button="Okay")

	# Get the coordinates of the vertices
	gv.coords = []
	for v in gv.vertices:
		gv.coord = pm.xform(v, query=True, worldSpace=True, translation=True)
		gv.coords.append(gv.coord)
	#putting the points in Numpy array as well as a tuple
	gv.points = np.array(gv.coords)

original_param()

def calculate_offset():
	#putting the points in Numpy array as well as a tuple
	points = np.array(gv.coords)
	
	if gv.pivotFlag == True:
		centroid = pm.xform(gv.mesh, q=1,ws=1,rp=1)
	else:        
		#Getting the centroid
		centroid = np.mean(points, axis=0)
		print("The centroid is: "+str(centroid))

	#getting the distance of original location of vertices from the centroid
	distances = np.array([])
	for row in points:
		distance = np.linalg.norm(row - centroid)
		distances = np.append(distances, distance)

	#finding the mean distance of the centroid, we will use this as the radius
	radius = (max(distances)+min(distances))/2
	print("The radius is: " + str(radius))

	#Finding new coordinates of the vertices and adding it to a tuple with XYZ
	new_coord=[]
	count = 0
	while count < len(gv.vertices):
		x_new = ((radius/distances[count])*(gv.coords[count][0]-centroid[0]))+centroid[0]
		y_new = ((radius/distances[count])*(gv.coords[count][1]-centroid[1]))+centroid[1]
		z_new = ((radius/distances[count])*(gv.coords[count][2]-centroid[2]))+centroid[2]
		#print(x_new, y_new, z_new)
		new_coord.append(x_new)
		new_coord.append(y_new)
		new_coord.append(z_new)
		count = count+1

	gv.new_coord_tuple =[tuple(new_coord[i:i+3]) for i in range(0, len(new_coord), 3)]

#definining pivot point then rerunning the offset command
def pivot(X):
	if X == True:
		gv.pivotFlag = True
		calculate_offset()
	else:
		gv.pivotFlag = False
		calculate_offset()

#running the offset command at first without checking pivot, however pivot function is already defined above
calculate_offset()

#spherify function actually moves the vertices
def spherify(N):
	#slider percentage
	N =N/100

	#final position
	final_coord=[]
	count = 0
	while count < len(gv.vertices):
		x_new = gv.coords[count][0]+(gv.new_coord_tuple[count][0]-gv.coords[count][0])*N
		y_new = gv.coords[count][1]+(gv.new_coord_tuple[count][1]-gv.coords[count][1])*N
		z_new = gv.coords[count][2]+(gv.new_coord_tuple[count][2]-gv.coords[count][2])*N
		#print(x_new, y_new, z_new)
		final_coord.append(x_new)
		final_coord.append(y_new)
		final_coord.append(z_new)
		count = count+1

	
	gv.final_coord_tuple =[tuple(final_coord[i:i+3]) for i in range(0, len(final_coord), 3)]

	#moving the vertices
	for count in range(len(gv.vertices)):
		pm.xform(gv.vertices[count], t=(gv.final_coord_tuple[count][0], gv.final_coord_tuple[count][1], gv.final_coord_tuple[count][2]), worldSpace=1)

#wrapped for spherify function
def run_spherify_percentage(N):
	spherify(N)
	return

#wrapper for pivot function (checkbox)
def run_pivot(X):
	pivot(X)
	return

#UI
def RevUI(*args):
	if pm.window("RevBS", q=1, exists=1) == True:
		pm.deleteUI("RevBS")
	
	#main Window
	pm.window("RevBS", title="Rev's Spherify v1.0", width=450, height=200, sizeable=False)

	pm.columnLayout("AllLayout", width=450, height=200,  parent="RevBS")

	#first column - Title
	pm.columnLayout("TitleColumn", width=450, height=50,  parent="AllLayout")
	pm.text(label="SPHERIFY A MODEL FROM PIVOT OR CENTROID OF ALL VERTICES",  width=450, height=50, align="center", fn="boldLabelFont")

	#part 1
	pm.columnLayout("column1", parent="AllLayout")
	#pm.text(label="  ", width=450, height=10, align="left")
	#pm.text(label="Percentage of the spherify modifier",  width=450, height=30, backgroundColor=[0.274, 0.619, 0.920], align="center")
	#pm.text(label="  ", width=450, height=10, align="left")

	pm.rowLayout("row1", numberOfColumns=1, parent="column1")
	gv.sliderVal = pm.intSliderGrp( field=True, label="Spherify:  ", columnAlign3=('right', 'center', 'right'), columnWidth3=(50,100, 250), minValue=0, maxValue=100, fieldMinValue=0, fieldMaxValue=100, value=100, cc=run_spherify_percentage )

	#part 2
	pm.columnLayout("column2", parent="AllLayout")
	pm.text(label="  ", width=450, height=10, align="left")
	pm.text(label="Check to use the pivot point as center. By default uses the center of mass",  width=450, height=30, backgroundColor=[0.3, 0.4, 0.4], align="center")
	pm.text(label="  ", width=450, height=10, align="left")

	
	pm.rowLayout("row2", numberOfColumns=1, parent="column2")
	gv.checkpointVal = pm.checkBox("checkbox", label="Use Pivot.      (Change the slider to take effect)",  height=30, value=False, parent="row2", changeCommand=run_pivot )

	pm.showWindow("RevBS")

#Calling UI
RevUI()

#calling functions from the UI
spherify(pm.intSliderGrp(gv.sliderVal, q=1, value=1))
pivot(pm.checkBox(gv.checkpointVal, q=1, value=1))