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
boundary_particle_type = 10
boundary_particle_type_constant=100

for boundary in boundaries:
  system.lbboundaries.add(lbboundaries.LBBoundary(shape=boundary))
  system.constraints.add(shape=boundary, particle_type=boundary_particle_type_constant+boundary_particle_type, penetrable=False)

# cell constants
cell_radius = 5.0

# create the template for cell
typeCell = oif.OifCellType(nodes_file="input/sphere1524nodes.dat",
                           triangles_file="input/sphere1524triangles.dat",
                           check_orientation=False,
                           system=system,
                           ks=0.005,
                           kb=0.005,
                           kal=0.02,
                           kag=0.7,
                           kv=0.9,
                           normal=True,
                           resize=[cell_radius, cell_radius, cell_radius])

typeCell2 = oif.OifCellType(nodes_file="input/sphere1524nodes.dat",
                           triangles_file="input/sphere1524triangles.dat",
                           check_orientation=False,
                           system=system,
                           ks=0.005,
                           kb=0.005,
                           kal=0.02,
                           kag=0.7,
                           kv=0.9,
                           normal=True,
                           resize=[cell_radius, cell_radius, cell_radius])



# fluid
lbf = espressomd.lb.LBFluid(agrid=2,
                            dens=1.0,
                            visc=1.5,
                            tau=system.time_step)
system.actors.add(lbf)
gammaFriction = typeCell.suggest_LBgamma(visc = 1.5, dens = 1.0)
system.thermostat.set_lb(LB_fluid=lbf,
                         seed=123,
                         gamma=gammaFriction)

cluster = oif.BiCluster(cell_type=typeCell, radius=cell_radius, cluster_centroid=[boxX/2,boxY/2,boxZ/2-7])
cluster2 = oif.BiCluster(cell_type=typeCell2, radius=cell_radius, cluster_centroid=[boxX/2,boxY/2,boxZ/2+7], starting_id = 2)
cluster.add_cells(cluster2.cells)

# enables soft-sphere interactions
cluster.set_soft_sphere_interactions(system=system)

# enables morse interactions
cluster.set_morse_interactions(system=system)

# enables soft-sphere interactions between particles of the same cell/object
cluster.set_self_cell_soft_sphere_interactions(system=system)

# deforms the cluster
cluster.deform(system=system, vtk_directory=vtk_directory, max_deformation_n = 70)
print("deform done")

cluster.save_cluster(directory + "/save")

exit()
    

