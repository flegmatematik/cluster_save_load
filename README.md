# cluster_save_load
## GUIDE

### 1. COPY oif_classes.py to your object_in_fluid directory
contains file oif_classes.py which should just be copied into your object_in_fluid directory.
(it is HIGHLY recommended that you backup your original oif_classes.py file.)

your oif_classes.py file should be located in YOUR_WORK_DIRECTORY/src/python/object_in_fluid/oif_classes.py 

### 2. ADD class names defined in oif_classes.py to your __init__.py file
for fully working workspace, place import classes through your __init__.py file in this fashion:
  your init file should be found at path: 
    YOUR_WORK_DIRECTORY/src/python/object_in_fluid/__init__.py 
    (be aware to not modify __init__.py file in espressomd folder)
  
  afterwards, all relevant class names should be copied as command argument:
    from .oif_classes import ( ... 
    
   all classes introduced in loffler/clusters addon:
      OifCluster, StarCluster, DiamondCluster, BiCluster, ChainCluster, DifferentSizesCluster
      
  example:
    from .oif_classes import ( ... (previous class names) ..., OifCluster, StarCluster, DiamondCluster, BiCluster, ChainCluster, DifferentSizesCluster )

### 3. RUNNING test.py script

This repository should contain test.py or similar script, which is 100% runable
Please, copy this script to your work directory


example of running test.py in your work folder (test_save.py must be located in your work dir):
./pypresso test_save.py sim_id 70


and to load the cluster:
./pypresso test_load.py sim_id 71

where in method call  
load_cluster(directory) 
directory variable must point to the output directory of test_save.py script

#### command breakdown:

'.' = unix shell command for running scripts

'/pypresso' = python espresso launcher

'test_save.py' = name of the script located in your current working folder

'sim_id 70' = these are 2 arguments, but work as one. First argument states the name of input argument, and the second its value. Can be interpreted as "sim_id = 70"
  
  argument value of sim_id MUST BE changed every run, as the script creates files in output folder.
    the folder name should be equal to "sim70" for arguments sim_id 70



### DISCLAIMER:
This guide is provided as is. Changes in this repository may result in this guide being not up to date. 

