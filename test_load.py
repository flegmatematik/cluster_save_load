import espressomd
import object_in_fluid as oif

from espressomd import lb
from espressomd import lbboundaries
from espressomd import shapes
from espressomd import interactions

import math

import numpy as np
import os, glob, sys, shutil

import time

# LL, May 2021

# Adjusted morse and soft-sphere interactions between cells to avoid disruption
# Added soft-sphere interactions between particles of the same cell with adjusted parameters

# Script creates 2 adjacent cells, which are then pressed against each other 

def distance(a,b):
    return np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)

if len(sys.argv) != 3:
    print ("1 argument are expected:")
    print ("sim_id: id of the simulation")
    print (" ")

# list of expected arguments
sim_id = "ND"


# read arguments
i = 0
for i, arg in enumerate(sys.argv):
    if i%2 == 1:
        print (str(arg) + " \t" + sys.argv[i + 1])
    if arg == "sim_id":
        sim_id = sys.argv[i + 1]

# check that we have everything
if sim_id == "ND":
    print("something wrong when reading arguments, quitting.")

# create folder structure
directory = "output/sim"+str(sim_id)
os.makedirs(directory)

vtk_directory = directory + "/vtk"
os.makedirs(vtk_directory)

# channel constants
boxX = 80.0
boxY = 40.0
boxZ = 40.0

# system constants
system = espressomd.System(box_l=[boxX, boxY, boxZ])
system.cell_system.skin = 0.2
system.time_step = 0.02

# save script and arguments
shutil.copyfile(str(sys.argv[0]), directory + "/" + str(sys.argv[0]))
out_file = open(directory + "/parameters.txt", "a")
for arg in sys.argv:
    out_file.write(str(arg) + " ")
out_file.write("\n")
out_file.close()

# save oif_classes
shutil.copyfile("src/python/object_in_fluid/oif_classes.py", directory + "/oif_classes.py")

# load cluster
cluster = oif.OifCluster()
# path to save directory which contains nodes, triangles folders and data.json
cluster.load_cluster(system=system, directory='output/sim8133/save',origin=[60,25,boxZ/2])

# enables soft-sphere interactions
#cluster.set_soft_sphere_interactions(system=system)

# enables morse interactions
#cluster.set_morse_interactions(system=system)

# enables soft-sphere interactions between particles of the same cell/object
#cluster.set_self_cell_soft_sphere_interactions(system=system)

# fluid
lbf = espressomd.lb.LBFluid(agrid=2,
                            dens=1.0,
                            visc=1.5,
                            tau=system.time_step,
                            ext_force_density=[-0.001, 0.0, 0.0])
                            
system.actors.add(lbf)
gammaFriction = cluster.cells[0].cell_type.suggest_LBgamma(visc = 1.5, dens = 1.0)
system.thermostat.set_lb(LB_fluid=lbf,
                         seed=123,
                         gamma=gammaFriction)
                         
# create boundaries
boundaries = []

# bottom of the channel
tmp_shape = shapes.Rhomboid(corner=[0.0, 0.0, 0.0], a=[boxX, 0.0, 0.0], b=[0.0, boxY, 0.0], c=[0.0, 0.0, 1.0],
              direction=1)
boundaries.append(tmp_shape)
oif.output_vtk_rhomboid(rhom_shape=tmp_shape, out_file=vtk_directory+"/wallBottom.vtk")

# top of the channel
tmp_shape = shapes.Rhomboid(corner=[0.0, 0.0, boxZ-1], a=[boxX, 0.0, 0.0], b=[0.0, boxY, 0.0], c=[0.0, 0.0, 1.0],
              direction=1)
boundaries.append(tmp_shape)
oif.output_vtk_rhomboid(rhom_shape=tmp_shape, out_file=vtk_directory+"/wallTop.vtk")

# front wall of the channel
tmp_shape = shapes.Rhomboid(corner=[0.0, 0.0, 0.0], a=[boxX, 0.0, 0.0], b=[0.0, 1.0, 0.0], c=[0.0, 0.0, boxZ],
              direction=1)
boundaries.append(tmp_shape)
oif.output_vtk_rhomboid(rhom_shape=tmp_shape, out_file=vtk_directory+"/wallFront.vtk")

# back wall of the channel
tmp_shape = shapes.Rhomboid(corner=[0.0, boxY-1.0, 0.0], a=[boxX, 0.0, 0.0], b=[0.0, 1.0, 0.0], c=[0.0, 0.0, boxZ],
              direction=1)
boundaries.append(tmp_shape)
oif.output_vtk_rhomboid(rhom_shape=tmp_shape, out_file=vtk_directory+"/wallBack.vtk")

# obstacle - cylinder A
tmp_shape = shapes.Cylinder(center=[12.0, 10.0, boxZ/2.0], axis=[0.0, 0.0, 1.0], length=40.0, radius=3.0, direction=1)
boundaries.append(tmp_shape)
oif.output_vtk_cylinder(cyl_shape=tmp_shape, n=20, out_file=vtk_directory+"/cylinderA.vtk")

# obstacle - cylinder B
tmp_shape = shapes.Cylinder(center=[33.0, 20.0, boxZ/2.0], axis=[0.0, 0.0, 1.0], length=40.0, radius=3.0, direction=1)
boundaries.append(tmp_shape)
oif.output_vtk_cylinder(cyl_shape=tmp_shape, n=20, out_file=vtk_directory+"/cylinderB.vtk")

# obstacle - cylinder C
tmp_shape = shapes.Cylinder(center=[21.0, 30.0, boxZ/2.0], axis=[0.0, 0.0, 1.0], length=40.0, radius=3.0, direction=1)
boundaries.append(tmp_shape)
oif.output_vtk_cylinder(cyl_shape=tmp_shape, n=20, out_file=vtk_directory+"/cylinderC.vtk")

boundary_particle_type = 10
boundary_particle_type_constant=100

# enables cell-wall interactions
cluster.set_cell_boundary_interactions(system=system, boundary_particle_type=boundary_particle_type_constant+boundary_particle_type)
 

for boundary in boundaries:
  system.lbboundaries.add(lbboundaries.LBBoundary(shape=boundary))
  system.constraints.add(shape=boundary, particle_type=boundary_particle_type_constant+boundary_particle_type, penetrable=False)

# main integration loop

maxCycle = 1000
steps = 100
time = 0

cluster.get_vtk_cluster(vtk_directory,0)
for i in range(1, maxCycle):
    system.integrator.run(steps=100)
    cluster.get_vtk_cluster(vtk_directory,i)
    print("time: " + str(time))   
    time = time + steps
exit()
    

