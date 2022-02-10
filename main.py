"""
(c) Script written in python 3

    Author : Emilie Launay
    Creation date : January 2022
    Last modification : January 2022
    Purpose : create an inverse method for the past incident Notre-Dame of Paris
                - by applying the inverse method of least squares

    Compilator command : python [file1].py [file2].cfg
    (last version : file1 = main_without_ihm, file2 = main_without_ihm)
"""

# | Libraries ----------------------------------------------------------------------------------------------------------
# import numpy as np
from configparser import ConfigParser  # to use config file
import os.path  # to use internal patterns
from datetime import datetime  # to know compilation time
from matplotlib.pyplot import *  # to plot
import glob


# import subprocess
# import eccodes

# | Classes ------------------------------------------------------------------------------------------------------------
# Bcolors: to color and underline the prints


class Bcolors:
    OKPINK = '\033[95m'  # pink
    OKBLUE = '\033[94m'  # blue
    OKCYAN = '\033[96m'  # cyan
    OKGREEN = '\033[92m'  # green
    WARNING = '\033[93m'  # orange
    FAIL = '\033[91m'  # red
    ENDC = '\033[0m'  # white
    BOLD = '\033[1m'  # bold
    UNDERLINE = '\033[4m'  # underline


# | Functions for least squares-----------------------------------------------------------------------------------------


# | ------------------------------------------------------- Code -------------------------------------------------------

# store the begenning simulation time ---------------------------
print(Bcolors.OKGREEN + "Simulation launched.", Bcolors.ENDC)
beg_date_simulation = datetime.now()

# Read configuration file ----------------------------------------------------------------------------------------------
print(Bcolors.OKGREEN, "\n ---", "INITIALISATION:", Bcolors.ENDC)

print("Lecture du fichier de configuration...")
if len(sys.argv) < 2:
    print(Bcolors.FAIL + ">>> ERROR: Please add a configuration file in the command line" + Bcolors.ENDC)
    exit()

if len(sys.argv) > 2:
    print(Bcolors.WARNING + ">>> WARNING: Only one configuration file is used (the one following the python file)"
          + Bcolors.ENDC)

config_file = sys.argv[1]  # config file getting from the command line

if not os.path.isfile(config_file):
    print(Bcolors.FAIL + ">>> ERROR : Configuration file does not exist, please retry with whole path"
          + Bcolors.ENDC)
    exit()

config = ConfigParser()  # define the name for ConfigParser()
config.read(config_file)  # read the config file

# Setting up the variables from the config file -----------------

# first section
input_directory = str(config['input']['input_dir'])
grib2_in_folder = str(config['input']['grib2_folder_source'])
grib2_in_folder_temp = str(config['input']['grib2_folder_temp'])

geometrical_height_folder = str(config['input']['geometrical_height_folder'])
geopotential_folder = str(config['input']['geopotential_folder'])
precipitation_tprate_folder = str(config['input']['tprate_folder'])

# second section
output_directory = str(config['output']['output_dir'])

# third section
option_rebuilt_in_one_file = config.getboolean('options', 'rebuilt_in_one_file')
option_show_HP1_before = config.getboolean('options', 'only_show_HP1_before')
option_show_HP2_before = config.getboolean('options', 'only_show_HP2_before')
option_show_SP1_before = config.getboolean('options', 'only_show_SP1_before')
option_show_SP2_before = config.getboolean('options', 'only_show_SP2_before')
option_show_SP3_before = config.getboolean('options', 'only_show_SP3_before')
option_show_HP1_after = config.getboolean('options', 'only_show_HP1_after')
option_show_HP2_after = config.getboolean('options', 'only_show_HP2_after')
option_show_SP1_after = config.getboolean('options', 'only_show_SP1_after')
option_show_SP2_after = config.getboolean('options', 'only_show_SP2_after')
option_show_SP3_after = config.getboolean('options', 'only_show_SP3_after')

print("Mise en place des chemins...")
# paths
# inout
grib_2_in_folder_path = input_directory + grib2_in_folder
grib_2_in_folder_path_temp = grib2_in_folder_temp
grib_2_out_folder_path = output_directory

filename_output_list = []

# initialisation
filename_list = []
date_list = []
stepRange_list = []
package_list = []
split_underscore = []

if os.path.exists(grib_2_in_folder_path_temp) is True:
    print(Bcolors.WARNING + ">>> WARNING: The directory already exists, older "
                            "files will be replaced by the new ones" + Bcolors.ENDC)
else:
    os.mkdir(grib_2_in_folder_path_temp)


print("Copie des fichiers grib2 INPUT/src vers _temp/src")
cmd = "cp -R " + grib_2_in_folder_path + " " + grib_2_in_folder_path_temp
os.system(cmd)
print("Copie des fichiers grib2 INPUT/SP2_3008 vers _temp/src")
cmd = "cp -R " + input_directory + geometrical_height_folder + " " + grib_2_in_folder_path_temp
os.system(cmd)
print("Copie des fichiers grib2 INPUT/HP2_129 vers _temp/src")
cmd = "cp -R " + input_directory + geopotential_folder + " " + grib_2_in_folder_path_temp
os.system(cmd)
print("Copie des fichiers grib2 INPUT/SP1_228228 vers _temp/src")
cmd = "cp -R " + input_directory + precipitation_tprate_folder + " " + grib_2_in_folder_path_temp
os.system(cmd)

for filename in glob.glob(os.path.join(grib_2_in_folder_path_temp + grib2_in_folder, "*")):
    with open(os.path.join(os.getcwd(), filename), 'r') as f:
        split_underscore = filename.split("_")
        split_point_underscore = split_underscore[len(split_underscore) - 1].split(".")
        package = split_underscore[len(split_underscore) - 3]
        package_list.append(package)
        stepRange = split_underscore[len(split_underscore) - 2][1]
        stepRange_list.append(stepRange)
        dataDateTime = split_point_underscore[len(split_point_underscore) - 2]
        date_list.append(dataDateTime)
        filename_list.append(filename)
        filename_output_list.append(package + "_" + stepRange + "_" + dataDateTime + ".txt")

print("Récupération des indices sous-package...")
indices_HP1 = [i for i, x in enumerate(package_list) if x == "HP1"]
indices_HP2 = [i for i, x in enumerate(package_list) if x == "HP2"]
indices_SP1 = [i for i, x in enumerate(package_list) if x == "SP1"]
indices_SP2 = [i for i, x in enumerate(package_list) if x == "SP2"]
indices_SP3 = [i for i, x in enumerate(package_list) if x == "SP3"]

print("Récupération des indices stepRange")
indices_01H = [i for i, x in enumerate(stepRange_list) if x == "1"]
indices_00H = [i for i, x in enumerate(stepRange_list) if x == "0"]

print("Récupération des indices dateDateTime")
indices_201904151600 = [i for i, x in enumerate(date_list) if x == "201904151600"]
indices_201904151700 = [i for i, x in enumerate(date_list) if x == "201904151700"]
indices_201904151800 = [i for i, x in enumerate(date_list) if x == "201904151800"]
indices_201904151900 = [i for i, x in enumerate(date_list) if x == "201904151900"]
indices_201904152000 = [i for i, x in enumerate(date_list) if x == "201904152000"]
indices_201904152100 = [i for i, x in enumerate(date_list) if x == "201904152100"]
indices_201904152200 = [i for i, x in enumerate(date_list) if x == "201904152200"]
indices_201904152300 = [i for i, x in enumerate(date_list) if x == "201904152300"]

if option_show_HP1_before is True:
    print("Print in HP1 for level = 20, 100 et 200")
    for i in range(len(filename_list)):
        for j in indices_HP1:
            if i == j:
                cmd = "grib_ls -p dataDate,dataTime,stepRange,name,shortName,units,level,paramId,discipline,parameterCategory,parameterNumber " \
                      "-w paramId=130/157/131/228246/228239/132/228247/228240/3031/10/228249/228241/54,level=20 " + \
                      filename_list[i]
                os.system(cmd)
                cmd = "grib_ls -p dataDate,dataTime,stepRange,name,shortName,units,level,paramId,discipline,parameterCategory,parameterNumber " \
                      "-w paramId=228246/228247/228249,level=100 " + filename_list[i]
                os.system(cmd)
                cmd = "grib_ls -p dataDate,dataTime,stepRange,name,shortName,units,level,paramId,discipline,parameterCategory,parameterNumber " \
                      "-w paramId=228239/228240/228241,level=200 " + filename_list[i]
                os.system(cmd)

if option_show_HP2_before is True:
    print("Print in HP2 for level = 20")
    for i in range(len(filename_list)):
        for j in indices_HP2:
            if i == j:
                cmd = "grib_ls -p dataDate,dataTime,stepRange,shortName,units,level,paramId,discipline,parameterCategory,parameterNumber " \
                      "-w paramId=129/260155/246/75/76/247/0/133/3017,level=20 " + filename_list[i]
                os.system(cmd)

if option_show_SP1_before is True:
    print("Print in SP1")
    for i in range(len(filename_list)):
        for j in indices_SP1:
            if i == j:
                cmd = "grib_ls -p dataDate,dataTime,stepRange,name,shortName,units,level,paramId,discipline,parameterCategory,parameterNumber " \
                      "-w paramId=151/165/166/260260/207/260065/260066/260067/167/260242/228228/3099/260087/0/228164 " + \
                      filename_list[i]
                os.system(cmd)

if option_show_SP2_before is True:
    print("Print in SP2")
    for i in range(len(filename_list)):
        for j in indices_SP2:
            if i == j:
                cmd = "grib_ls -p dataDate,dataTime,stepRange,name,shortName,units,level,paramId,discipline,parameterCategory,parameterNumber " \
                      "-w paramId=134/130/3073/3074/3075/2008/167/85001160/260083/260045/168/133 " + filename_list[i]
                os.system(cmd)

if option_show_SP3_before is True:
    print("Print in SP3")
    for i in range(len(filename_list)):
        for j in indices_SP3:
            if i == j:
                cmd = "grib_ls -p dataDate,dataTime,stepRange,name,shortName,units,level,paramId,discipline,parameterCategory,parameterNumber " \
                      "-w paramId=136/0/147/146/260097/176/177/180/181 " + filename_list[i]
                os.system(cmd)

print("")
print(Bcolors.OKGREEN + " --- MAIN :" + Bcolors.ENDC)
print(Bcolors.OKGREEN + "---" + Bcolors.ENDC + " Commencement des modifications...")
print("Ajout de Geometrical Height dans SP2 :")
print("  -> paramId=3008")
print("  -> pour stepRange=0 récupéré depuis des données du 05/05/2021 run 0600 et forcé pour 15/04/2019 run 1200")
cmd = "grib_set -s dataDate=20190415,dataTime=1600 -w dataDate=20210505,dataTime=600 " \
      + grib_2_in_folder_path_temp + geometrical_height_folder + "out_3008_00H.grib2 " + grib_2_in_folder_path_temp + geometrical_height_folder + "out_3008_ready.grib2 "
os.system(cmd)


for ind_j in indices_SP2:
    for ind_k in indices_00H:
        if ind_k == ind_j:
            if date_list[ind_k] == "201904151600":
                cmd = "cat " + filename_list[ind_k] + " " + grib_2_in_folder_path_temp + geometrical_height_folder + "out_3008_ready.grib2 > " \
                      + grib_2_in_folder_path_temp + "SP2_00H_" + date_list[ind_k] + ".grib2"
                os.system(cmd)
                cmd = "rm " + filename_list[ind_k]
                os.system(cmd)
                cmd = "mv " + grib_2_in_folder_path_temp + "SP2_00H_" + date_list[ind_k] + ".grib2 " + filename_list[
                    ind_k]
                os.system(cmd)
            elif date_list[ind_k] == "201904151700":
                cmd = "cat " + filename_list[ind_k] + " " + grib_2_in_folder_path_temp + geometrical_height_folder + "out_3008_ready.grib2 > " \
                      + grib_2_in_folder_path_temp + "SP2_00H_" + date_list[ind_k] + ".grib2"
                os.system(cmd)
                cmd = "rm " + filename_list[ind_k]
                os.system(cmd)
                cmd = "mv " + grib_2_in_folder_path_temp + "SP2_00H_" + date_list[ind_k] + ".grib2 " + filename_list[
                    ind_k]
                os.system(cmd)
            elif date_list[ind_k] == "201904151800":
                cmd = "cat " + filename_list[ind_k] + " " + grib_2_in_folder_path_temp + geometrical_height_folder + "out_3008_ready.grib2 > " \
                      + grib_2_in_folder_path_temp + "SP2_00H_" + date_list[ind_k] + ".grib2"
                os.system(cmd)
                cmd = "rm " + filename_list[ind_k]
                os.system(cmd)
                cmd = "mv " + grib_2_in_folder_path_temp + "SP2_00H_" + date_list[ind_k] + ".grib2 " + filename_list[
                    ind_k]
                os.system(cmd)
            elif date_list[ind_k] == "201904151900":
                cmd = "cat " + filename_list[ind_k] + " " + grib_2_in_folder_path_temp + geometrical_height_folder + "out_3008_ready.grib2 > " \
                      + grib_2_in_folder_path_temp + "SP2_00H_" + date_list[ind_k] + ".grib2"
                os.system(cmd)
                cmd = "rm " + filename_list[ind_k]
                os.system(cmd)
                cmd = "mv " + grib_2_in_folder_path_temp + "SP2_00H_" + date_list[ind_k] + ".grib2 " + filename_list[
                    ind_k]
                os.system(cmd)
            elif date_list[ind_k] == "201904152000":
                cmd = "cat " + filename_list[ind_k] + " " + grib_2_in_folder_path_temp + geometrical_height_folder + "out_3008_ready.grib2 > " \
                      + grib_2_in_folder_path_temp + "SP2_00H_" + date_list[ind_k] + ".grib2"
                os.system(cmd)
                cmd = "rm " + filename_list[ind_k]
                os.system(cmd)
                cmd = "mv " + grib_2_in_folder_path_temp + "SP2_00H_" + date_list[ind_k] + ".grib2 " + filename_list[
                    ind_k]
                os.system(cmd)
            elif date_list[ind_k] == "201904152100":
                cmd = "cat " + filename_list[ind_k] + " " + grib_2_in_folder_path_temp + geometrical_height_folder + "out_3008_ready.grib2 > " \
                      + grib_2_in_folder_path_temp + "SP2_00H_" + date_list[ind_k] + ".grib2"
                os.system(cmd)
                cmd = "rm " + filename_list[ind_k]
                os.system(cmd)
                cmd = "mv " + grib_2_in_folder_path_temp + "SP2_00H_" + date_list[ind_k] + ".grib2 " + filename_list[
                    ind_k]
                os.system(cmd)
            elif date_list[ind_k] == "201904152200":
                cmd = "cat " + filename_list[ind_k] + " " + grib_2_in_folder_path_temp + geometrical_height_folder + "out_3008_ready.grib2 > " \
                      + grib_2_in_folder_path_temp + "SP2_00H_" + date_list[ind_k] + ".grib2"
                os.system(cmd)
                cmd = "rm " + filename_list[ind_k]
                os.system(cmd)
                cmd = "mv " + grib_2_in_folder_path_temp + "SP2_00H_" + date_list[ind_k] + ".grib2 " + filename_list[
                    ind_k]
                os.system(cmd)
            elif date_list[ind_k] == "201904152300":
                cmd = "cat " + filename_list[ind_k] + " " + grib_2_in_folder_path_temp + geometrical_height_folder + "out_3008_ready.grib2 > " \
                      + grib_2_in_folder_path_temp + "SP2_00H_" + date_list[ind_k] + ".grib2"
                os.system(cmd)
                cmd = "rm " + filename_list[ind_k]
                os.system(cmd)
                cmd = "mv " + grib_2_in_folder_path_temp + "SP2_00H_" + date_list[ind_k] + ".grib2 " + filename_list[
                    ind_k]
                os.system(cmd)
print("  -> fin d'ajout de geometrical height dans tous les packages SP2 pour l'echéance 00H\n")
cmd = "rm -R " + grib_2_in_folder_path_temp + geometrical_height_folder
os.system(cmd)


# ======================================================================
print("Ajout de Geopotential dans HP2 :")
print("  -> paramId=129")
print("  -> données du 15/04/2019 run 1200 stepRange=0 devient données du 15/04/2019 run 1600 stepRange=4")
print("  -> données du 15/04/2019 run 1200 stepRange=1 devient données du 15/04/2019 run 1600 stepRange=5")
print("  -> données du 15/04/2019 run 1200 stepRange=2 devient données du 15/04/2019 run 1600 stepRange=6")
print("  -> données du 15/04/2019 run 1200 stepRange=3 devient données du 15/04/2019 run 1600 stepRange=7")
print("  -> données du 15/04/2019 run 1200 stepRange=4 devient données du 15/04/2019 run 1600 stepRange=8")
print("  -> données du 15/04/2019 run 1200 stepRange=5 devient données du 15/04/2019 run 1600 stepRange=9")
print("  -> données du 15/04/2019 run 1200 stepRange=6 devient données du 15/04/2019 run 1600 stepRange=10")
print("  -> données du 15/04/2019 run 1200 stepRange=7 devient données du 15/04/2019 run 1600 stepRange=11")
print("  -> données du 15/04/2019 run 1200 stepRange=8 devient données du 15/04/2019 run 1600 stepRange=12")
cmd = "grib_set -s dataTime=1600,stepRange=0 -w dataTime=1200,stepRange=4 " \
      + grib_2_in_folder_path_temp + geopotential_folder + "out_129_4.grib2 " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_1600.grib2 "
os.system(cmd)
cmd = "grib_set -s dataTime=1600,stepRange=1 -w dataTime=1200,stepRange=5 " \
      + grib_2_in_folder_path_temp + geopotential_folder + "out_129_5.grib2 " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_1700.grib2 "
os.system(cmd)
cmd = "grib_set -s dataTime=1600,stepRange=2 -w dataTime=1200,stepRange=6 " \
      + grib_2_in_folder_path_temp + geopotential_folder + "out_129_6.grib2 " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_1800.grib2 "
os.system(cmd)
cmd = "grib_set -s dataTime=1600,stepRange=3 -w dataTime=1200,stepRange=7 " \
      + grib_2_in_folder_path_temp + geopotential_folder + "out_129_7.grib2 " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_1900.grib2 "
os.system(cmd)
cmd = "grib_set -s dataTime=1600,stepRange=4 -w dataTime=1200,stepRange=8 " \
      + grib_2_in_folder_path_temp + geopotential_folder + "out_129_8.grib2 " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_2000.grib2 "
os.system(cmd)
cmd = "grib_set -s dataTime=1600,stepRange=5 -w dataTime=1200,stepRange=9 " \
      + grib_2_in_folder_path_temp + geopotential_folder + "out_129_9.grib2 " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_2100.grib2 "
os.system(cmd)
cmd = "grib_set -s dataTime=1600,stepRange=6 -w dataTime=1200,stepRange=10 " \
      + grib_2_in_folder_path_temp + geopotential_folder + "out_129_10.grib2 " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_2200.grib2 "
os.system(cmd)
cmd = "grib_set -s dataTime=1600,stepRange=7 -w dataTime=1200,stepRange=11 " \
      + grib_2_in_folder_path_temp + geopotential_folder + "out_129_11.grib2 " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_2300.grib2 "
os.system(cmd)
cmd = "grib_set -s dataTime=1600,stepRange=8 -w dataTime=1200,stepRange=12 " \
      + grib_2_in_folder_path_temp + geopotential_folder + "out_129_12.grib2 " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_00J+1.grib2 "
os.system(cmd)

for ind_k in indices_HP2:
    if date_list[ind_k] == "201904151600" and stepRange_list[ind_k] == "0":
        cmd = "cat " + filename_list[ind_k] + " " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_1600.grib2 > " \
              + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[ind_k] + ".grib2"
        os.system(cmd)
        cmd = "rm " + filename_list[ind_k]
        os.system(cmd)
        cmd = "mv " + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[
            ind_k] + ".grib2 " + filename_list[ind_k]
        os.system(cmd)
    elif date_list[ind_k] == "201904151600" and stepRange_list[ind_k] == "1":
        cmd = "cat " + filename_list[ind_k] + " " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_1700.grib2 > " \
              + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[ind_k] + ".grib2"
        os.system(cmd)
        cmd = "rm " + filename_list[ind_k]
        os.system(cmd)
        cmd = "mv " + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[
            ind_k] + ".grib2 " + filename_list[ind_k]
        os.system(cmd)
    elif date_list[ind_k] == "201904151700" and stepRange_list[ind_k] == "0":
        cmd = "cat " + filename_list[ind_k] + " " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_1700.grib2 > " \
              + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[ind_k] + ".grib2"
        os.system(cmd)
        cmd = "rm " + filename_list[ind_k]
        os.system(cmd)
        cmd = "mv " + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[
            ind_k] + ".grib2 " + filename_list[ind_k]
        os.system(cmd)
    elif date_list[ind_k] == "201904151700" and stepRange_list[ind_k] == "1":
        cmd = "cat " + filename_list[ind_k] + " " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_1800.grib2 > " \
              + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[ind_k] + ".grib2"
        os.system(cmd)
        cmd = "rm " + filename_list[ind_k]
        os.system(cmd)
        cmd = "mv " + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[
            ind_k] + ".grib2 " + filename_list[ind_k]
        os.system(cmd)
    elif date_list[ind_k] == "201904151800" and stepRange_list[ind_k] == "0":
        cmd = "cat " + filename_list[ind_k] + " " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_1800.grib2 > " \
              + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[ind_k] + ".grib2"
        os.system(cmd)
        cmd = "rm " + filename_list[ind_k]
        os.system(cmd)
        cmd = "mv " + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[
            ind_k] + ".grib2 " + filename_list[ind_k]
        os.system(cmd)
    elif date_list[ind_k] == "201904151800" and stepRange_list[ind_k] == "1":
        cmd = "cat " + filename_list[ind_k] + " " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_1900.grib2 > " \
              + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[ind_k] + ".grib2"
        os.system(cmd)
        cmd = "rm " + filename_list[ind_k]
        os.system(cmd)
        cmd = "mv " + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[
            ind_k] + ".grib2 " + filename_list[ind_k]
        os.system(cmd)
    elif date_list[ind_k] == "201904151900" and stepRange_list[ind_k] == "0":
        cmd = "cat " + filename_list[ind_k] + " " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_1900.grib2 > " \
              + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[ind_k] + ".grib2"
        os.system(cmd)
        cmd = "rm " + filename_list[ind_k]
        os.system(cmd)
        cmd = "mv " + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[
            ind_k] + ".grib2 " + filename_list[ind_k]
        os.system(cmd)
    elif date_list[ind_k] == "201904151900" and stepRange_list[ind_k] == "1":
        cmd = "cat " + filename_list[ind_k] + " " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_2000.grib2 > " \
              + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[ind_k] + ".grib2"
        os.system(cmd)
        cmd = "rm " + filename_list[ind_k]
        os.system(cmd)
        cmd = "mv " + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[
            ind_k] + ".grib2 " + filename_list[ind_k]
        os.system(cmd)
    elif date_list[ind_k] == "201904152000" and stepRange_list[ind_k] == "0":
        cmd = "cat " + filename_list[ind_k] + " " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_2000.grib2 > " \
              + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[ind_k] + ".grib2"
        os.system(cmd)
        cmd = "rm " + filename_list[ind_k]
        os.system(cmd)
        cmd = "mv " + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[
            ind_k] + ".grib2 " + filename_list[
                  ind_k]
        os.system(cmd)
    elif date_list[ind_k] == "201904152000" and stepRange_list[ind_k] == "0":
        cmd = "cat " + filename_list[ind_k] + " " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_2000.grib2 > " \
              + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[ind_k] + ".grib2"
        os.system(cmd)
        cmd = "rm " + filename_list[ind_k]
        os.system(cmd)
        cmd = "mv " + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[
            ind_k] + ".grib2 " + filename_list[
                  ind_k]
        os.system(cmd)
    elif date_list[ind_k] == "201904152000" and stepRange_list[ind_k] == "1":
        cmd = "cat " + filename_list[ind_k] + " " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_2100.grib2 > " \
              + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[ind_k] + ".grib2"
        os.system(cmd)
        cmd = "rm " + filename_list[ind_k]
        os.system(cmd)
        cmd = "mv " + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[
            ind_k] + ".grib2 " + filename_list[
                  ind_k]
        os.system(cmd)
    elif date_list[ind_k] == "201904152100" and stepRange_list[ind_k] == "0":
        cmd = "cat " + filename_list[ind_k] + " " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_2100.grib2 > " \
              + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[ind_k] + ".grib2"
        os.system(cmd)
        cmd = "rm " + filename_list[ind_k]
        os.system(cmd)
        cmd = "mv " + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[
            ind_k] + ".grib2 " + filename_list[
                  ind_k]
        os.system(cmd)
    elif date_list[ind_k] == "201904152100" and stepRange_list[ind_k] == "1":
        cmd = "cat " + filename_list[ind_k] + " " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_2200.grib2 > " \
              + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[ind_k] + ".grib2"
        os.system(cmd)
        cmd = "rm " + filename_list[ind_k]
        os.system(cmd)
        cmd = "mv " + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[
            ind_k] + ".grib2 " + filename_list[
                  ind_k]
        os.system(cmd)
    elif date_list[ind_k] == "201904152200" and stepRange_list[ind_k] == "0":
        cmd = "cat " + filename_list[ind_k] + " " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_2200.grib2 > " \
              + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[ind_k] + ".grib2"
        os.system(cmd)
        cmd = "rm " + filename_list[ind_k]
        os.system(cmd)
        cmd = "mv " + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[
            ind_k] + ".grib2 " + filename_list[
                  ind_k]
        os.system(cmd)
    elif date_list[ind_k] == "201904152200" and stepRange_list[ind_k] == "1":
        cmd = "cat " + filename_list[ind_k] + " " + grib_2_in_folder_path_temp + geopotential_folder + "out_129_ready_2300.grib2 > " \
              + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[ind_k] + ".grib2"
        os.system(cmd)
        cmd = "rm " + filename_list[ind_k]
        os.system(cmd)
        cmd = "mv " + grib_2_in_folder_path_temp + "HP2_0" + stepRange_list[ind_k] + "H_" + date_list[
            ind_k] + ".grib2 " + filename_list[ind_k]
        os.system(cmd)

print("  -> fin d'ajout de geopotential dans tous les packages HP2 pour les echéances 00H12H\n")
cmd = "rm -R " + grib_2_in_folder_path_temp + geopotential_folder
os.system(cmd)


print("Découpage de SP1 par paramId pour retirer tprate des analyses et le remplacer par les archives..")
print("  -> paramId=228228")
for ind_j in indices_SP1:
    cmd = "grib_copy " + filename_list[ind_j] + " " + grib_2_in_folder_path_temp + "SP1_0" + \
          stepRange_list[ind_j] + "H_" + date_list[ind_j] + "_[paramId].grib2 "
    os.system(cmd)
    cmd = "rm " + filename_list[ind_j]
    os.system(cmd)
    for ind_o in indices_00H:
        if ind_j == ind_o:
            cmd = "cat " + grib_2_in_folder_path_temp + "SP1_0" \
                  + stepRange_list[ind_j] + "H_" + date_list[ind_j] + "_151.grib2 " \
                  + grib_2_in_folder_path_temp + "SP1_0" \
                  + stepRange_list[ind_j] + "H_" + date_list[ind_j] + "_165.grib2 " \
                  + grib_2_in_folder_path_temp + "SP1_0" \
                  + stepRange_list[ind_j] + "H_" + date_list[ind_j] + "_166.grib2 " \
                  + grib_2_in_folder_path_temp + "SP1_0" \
                  + stepRange_list[ind_j] + "H_" + date_list[ind_j] + "_260260.grib2 " \
                  + grib_2_in_folder_path_temp + "SP1_0" \
                  + stepRange_list[ind_j] + "H_" + date_list[ind_j] + "_207.grib2 " \
                  + grib_2_in_folder_path_temp + "SP1_0" \
                  + stepRange_list[ind_j] + "H_" + date_list[ind_j] + "_167.grib2 " \
                  + grib_2_in_folder_path_temp + "SP1_0" \
                  + stepRange_list[ind_j] + "H_" + date_list[ind_j] + "_260242.grib2 " \
                  + "> " + filename_list[ind_j]
            os.system(cmd)
    for ind_o in indices_01H:
        if ind_j == ind_o:
            cmd = "cat " + grib_2_in_folder_path_temp + "SP1_0" \
                  + stepRange_list[ind_j] + "H_" + date_list[ind_j] + "_151.grib2 " \
                  + grib_2_in_folder_path_temp + "SP1_0" \
                  + stepRange_list[ind_j] + "H_" + date_list[ind_j] + "_165.grib2 " \
                  + grib_2_in_folder_path_temp + "SP1_0" \
                  + stepRange_list[ind_j] + "H_" + date_list[ind_j] + "_166.grib2 " \
                  + grib_2_in_folder_path_temp + "SP1_0" \
                  + stepRange_list[ind_j] + "H_" + date_list[ind_j] + "_260260.grib2 " \
                  + grib_2_in_folder_path_temp + "SP1_0" \
                  + stepRange_list[ind_j] + "H_" + date_list[ind_j] + "_207.grib2 " \
                  + grib_2_in_folder_path_temp + "SP1_0" \
                  + stepRange_list[ind_j] + "H_" + date_list[ind_j] + "_260065.grib2 " \
                  + grib_2_in_folder_path_temp + "SP1_0" \
                  + stepRange_list[ind_j] + "H_" + date_list[ind_j] + "_260066.grib2 " \
                  + grib_2_in_folder_path_temp + "SP1_0" \
                  + stepRange_list[ind_j] + "H_" + date_list[ind_j] + "_260067.grib2 " \
                  + grib_2_in_folder_path_temp + "SP1_0" \
                  + stepRange_list[ind_j] + "H_" + date_list[ind_j] + "_167.grib2 " \
                  + grib_2_in_folder_path_temp + "SP1_0" \
                  + stepRange_list[ind_j] + "H_" + date_list[ind_j] + "_260242.grib2 " \
                  + grib_2_in_folder_path_temp + "SP1_0" \
                  + stepRange_list[ind_j] + "H_" + date_list[ind_j] + "_3099.grib2 " \
                  + grib_2_in_folder_path_temp + "SP1_0" \
                  + stepRange_list[ind_j] + "H_" + date_list[ind_j] + "_260087.grib2 " \
                  + grib_2_in_folder_path_temp + "SP1_0" \
                  + stepRange_list[ind_j] + "H_" + date_list[ind_j] + "_0.grib2 " \
                  + grib_2_in_folder_path_temp + "SP1_0" \
                  + stepRange_list[ind_j] + "H_" + date_list[ind_j] + "_228164.grib2 " \
                  + "> " + filename_list[ind_j]
            os.system(cmd)
print("  -> fin de découpage de SP1 par paramId pour retirer tprate\n")
cmd = "rm " + grib_2_in_folder_path_temp + "SP1_0*"
os.system(cmd)

if option_rebuilt_in_one_file is True:
    print("Recontruction des analyses pour le run 1600 ech 00H06H...")
    print("  ->  run 1600 ech 00H devient run 1600 ech 00H")
    print("  ->  run 1600 ech 01H devient run 1600 ech 01H")
    print("  ->  run 1700 ech 01H devient run 1600 ech 02H")
    print("  ->  run 1800 ech 01H devient run 1600 ech 03H")
    print("  ->  run 1900 ech 01H devient run 1600 ech 04H")
    print("  ->  run 2000 ech 01H devient run 1600 ech 05H")
    print("  ->  run 2100 ech 01H devient run 1600 ech 06H")
    print("  ->  run 2200 ech 01H devient run 1600 ech 07H")
    print("  ->  run 2300 ech 01H devient run 1600 ech 08H")

    for ind_i in range(len(filename_list)):
        for ind_k in indices_01H:
            for ind_j in indices_201904152300:
                if ind_i == ind_j == ind_k:
                    cmd = "grib_set -s stepRange=8,dataTime=1600 -w stepRange=1,dataTime=2300 " \
                          + filename_list[ind_i] + " " \
                          + grib_2_in_folder_path_temp + package_list[ind_i] + "_201904151600_08H_MOD.grib2"

                    os.system(cmd)

            for ind_j in indices_201904152200:
                if ind_i == ind_j == ind_k:
                    cmd = "grib_set -s stepRange=7,dataTime=1600 -w stepRange=1,dataTime=2200 " \
                          + filename_list[ind_i] + " " \
                          + grib_2_in_folder_path_temp + package_list[ind_i] + "_201904151600_07H_MOD.grib2"

                    os.system(cmd)
            for ind_j in indices_201904152100:
                if ind_i == ind_j == ind_k:
                    cmd = "grib_set -s stepRange=6,dataTime=1600 -w stepRange=1,dataTime=2100 " \
                          + filename_list[ind_i] + " " \
                          + grib_2_in_folder_path_temp + package_list[ind_i] + "_201904151600_06H_MOD.grib2"

                    os.system(cmd)
            for ind_j in indices_201904152000:
                if ind_i == ind_j == ind_k:
                    cmd = "grib_set -s stepRange=5,dataTime=1600 -w stepRange=1,dataTime=2000 " \
                          + filename_list[ind_i] + " " \
                          + grib_2_in_folder_path_temp + package_list[ind_i] + "_201904151600_05H_MOD.grib2"

                    os.system(cmd)
            for ind_j in indices_201904151900:
                if ind_i == ind_j == ind_k:
                    cmd = "grib_set -s stepRange=4,dataTime=1600 -w stepRange=1,dataTime=1900 " \
                          + filename_list[ind_i] + " " \
                          + grib_2_in_folder_path_temp + package_list[ind_i] + "_201904151600_04H_MOD.grib2"

                    os.system(cmd)
            for ind_j in indices_201904151800:
                if ind_i == ind_j == ind_k:
                    cmd = "grib_set -s stepRange=3,dataTime=1600 -w stepRange=1,dataTime=1800 " \
                          + filename_list[ind_i] + " " \
                          + grib_2_in_folder_path_temp + package_list[ind_i] + "_201904151600_03H_MOD.grib2"

                    os.system(cmd)
            for ind_j in indices_201904151700:
                if ind_i == ind_j == ind_k:
                    cmd = "grib_set -s stepRange=2,dataTime=1600 -w stepRange=1,dataTime=1700 " \
                          + filename_list[ind_i] + " " \
                          + grib_2_in_folder_path_temp + package_list[ind_i] + "_201904151600_02H_MOD.grib2"

                    os.system(cmd)
            for ind_j in indices_201904151600:
                if ind_i == ind_j == ind_k:
                    cmd = "grib_set -s stepRange=1,dataTime=1600 -w stepRange=1,dataTime=1600 " \
                          + filename_list[ind_i] + " " \
                          + grib_2_in_folder_path_temp + package_list[ind_i] + "_201904151600_01H_MOD.grib2"

                    os.system(cmd)
        for ind_k in indices_00H:
            for ind_j in indices_201904151600:
                if ind_i == ind_j == ind_k:
                    cmd = "grib_set -s stepRange=0,dataTime=1600 -w stepRange=0,dataTime=1600 " \
                          + filename_list[ind_i] + " " \
                          + grib_2_in_folder_path_temp + package_list[ind_i] + "_201904151600_00H_MOD.grib2"
                    os.system(cmd)
    print("  -> fin de réajustement de stepRange\n")

    print("Concaténation en temps...")
    print("  HP1:")
    print("  -> HP1 run 1600 ech 00H06H")
    cmd = "cat " \
          + grib_2_in_folder_path_temp + "HP1_201904151600_00H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_201904151600_01H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_201904151600_02H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_201904151600_03H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_201904151600_04H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_201904151600_05H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_201904151600_06H_MOD.grib2 " \
          + " > " + grib_2_in_folder_path_temp + "W_fr-meteofrance,MODEL,AROME+0025+HP1+00H06H_C_LFPW_201904151600--.grib2"
    os.system(cmd)
    print("  -> HP1 run 1600 ech 07H08H")
    cmd = "cat " \
          + grib_2_in_folder_path_temp + "HP1_201904151600_07H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_201904151600_08H_MOD.grib2 " \
          + " > " + grib_2_in_folder_path_temp + "W_fr-meteofrance,MODEL,AROME+0025+HP1+07H08H_C_LFPW_201904151600--.grib2"
    os.system(cmd)
    print("  -> HP1 run 1600 ech 00H08H\n")
    cmd = "cat " \
          + grib_2_in_folder_path_temp + "HP1_201904151600_00H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_201904151600_01H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_201904151600_02H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_201904151600_03H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_201904151600_04H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_201904151600_05H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_201904151600_06H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_201904151600_07H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_201904151600_08H_MOD.grib2 " \
          + " > " + grib_2_in_folder_path_temp + "W_fr-meteofrance,MODEL,AROME+0025+HP1+00H08H_C_LFPW_201904151600--.grib2"
    os.system(cmd)
    cmd = "rm " + grib_2_in_folder_path_temp + "HP1*"
    os.system(cmd)

    print("  HP2:")
    print("  -> HP2 run 1600 ech 00H06H")
    cmd = "cat " \
          + grib_2_in_folder_path_temp + "HP2_201904151600_00H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_201904151600_01H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_201904151600_02H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_201904151600_03H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_201904151600_04H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_201904151600_05H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_201904151600_06H_MOD.grib2 " \
          + " > " + grib_2_in_folder_path_temp + "W_fr-meteofrance,MODEL,AROME+0025+HP2+00H06H_C_LFPW_201904151600--.grib2"
    os.system(cmd)

    print("  -> HP2 run 1600 ech 07H08H")
    cmd = "cat " \
          + grib_2_in_folder_path_temp + "HP2_201904151600_07H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_201904151600_08H_MOD.grib2 " \
          + " > " + grib_2_in_folder_path_temp + "W_fr-meteofrance,MODEL,AROME+0025+HP2+07H08H_C_LFPW_201904151600--.grib2"
    os.system(cmd)

    print("  -> HP2 run 1600 ech 00H08H\n")
    cmd = "cat " \
          + grib_2_in_folder_path_temp + "HP2_201904151600_00H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_201904151600_01H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_201904151600_02H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_201904151600_03H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_201904151600_04H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_201904151600_05H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_201904151600_06H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_201904151600_07H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_201904151600_08H_MOD.grib2 " \
          + " > " + grib_2_in_folder_path_temp + "W_fr-meteofrance,MODEL,AROME+0025+HP2+00H08H_C_LFPW_201904151600--.grib2"
    os.system(cmd)

    cmd = "rm " + grib_2_in_folder_path_temp + "HP2*"
    os.system(cmd)

    print("  SP1:")
    print("  -> SP1 run 1600 ech 00H06H")
    cmd = "cat " \
          + grib_2_in_folder_path_temp + "SP1_201904151600_00H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_201904151600_01H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-1.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_201904151600_02H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-2.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_201904151600_03H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-3.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_201904151600_04H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-4.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_201904151600_05H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-5.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_201904151600_06H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-6.grib2 " \
          + " > " + grib_2_in_folder_path_temp + "W_fr-meteofrance,MODEL,AROME+0025+SP1+00H06H_C_LFPW_201904151600--.grib2"
    os.system(cmd)

    print("  -> SP1 run 1600 ech 07H08H")
    cmd = "cat " \
          + grib_2_in_folder_path_temp + "SP1_201904151600_07H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-7.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_201904151600_08H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-8.grib2 " \
          + " > " + grib_2_in_folder_path_temp + "W_fr-meteofrance,MODEL,AROME+0025+SP1+07H08H_C_LFPW_201904151600--.grib2"
    os.system(cmd)

    print("  -> SP1 run 1600 ech 00H08H\n")
    cmd = "cat " \
          + grib_2_in_folder_path_temp + "SP1_201904151600_00H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_201904151600_01H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-1.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_201904151600_02H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-2.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_201904151600_03H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-3.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_201904151600_04H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-4.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_201904151600_05H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-5.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_201904151600_06H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-6.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_201904151600_07H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-7.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_201904151600_08H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-8.grib2 " \
          + " > " + grib_2_in_folder_path_temp + "W_fr-meteofrance,MODEL,AROME+0025+SP1+00H08H_C_LFPW_201904151600--.grib2"
    os.system(cmd)

    cmd = "rm " + grib_2_in_folder_path_temp + "SP1_20*"
    os.system(cmd)

    print("  SP2:")
    print("  -> SP2 run 1600 ech 00H06H")
    cmd = "cat " \
          + grib_2_in_folder_path_temp + "SP2_201904151600_00H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_201904151600_01H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_201904151600_02H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_201904151600_03H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_201904151600_04H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_201904151600_05H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_201904151600_06H_MOD.grib2 " \
          + " > " + grib_2_in_folder_path_temp + "W_fr-meteofrance,MODEL,AROME+0025+SP2+00H06H_C_LFPW_201904151600--.grib2"
    os.system(cmd)

    print("  -> SP2 run 1600 ech 07H08H")
    cmd = "cat " \
          + grib_2_in_folder_path_temp + "SP2_201904151600_07H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_201904151600_08H_MOD.grib2 " \
          + " > " + grib_2_in_folder_path_temp + "W_fr-meteofrance,MODEL,AROME+0025+SP2+07H08H_C_LFPW_201904151600--.grib2"
    os.system(cmd)

    print("  -> SP2 run 1600 ech 00H08H\n")
    cmd = "cat " \
          + grib_2_in_folder_path_temp + "SP2_201904151600_00H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_201904151600_01H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_201904151600_02H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_201904151600_03H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_201904151600_04H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_201904151600_05H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_201904151600_06H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_201904151600_07H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_201904151600_08H_MOD.grib2 " \
          + " > " + grib_2_in_folder_path_temp + "W_fr-meteofrance,MODEL,AROME+0025+SP2+00H08H_C_LFPW_201904151600--.grib2"
    os.system(cmd)
    cmd = "rm " + grib_2_in_folder_path_temp + "SP2*"
    os.system(cmd)

    print("  SP3:")
    print("  -> SP3 run 1600 ech 00H06H")
    cmd = "cat " \
          + grib_2_in_folder_path_temp + "SP3_201904151600_00H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_201904151600_01H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_201904151600_02H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_201904151600_03H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_201904151600_04H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_201904151600_05H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_201904151600_06H_MOD.grib2 " \
          + " > " + grib_2_in_folder_path_temp + "W_fr-meteofrance,MODEL,AROME+0025+SP3+00H06H_C_LFPW_201904151600--.grib2"
    os.system(cmd)

    print("  -> SP3 run 1600 ech 07H08H")
    cmd = "cat " \
          + grib_2_in_folder_path_temp + "SP3_201904151600_07H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_201904151600_08H_MOD.grib2 " \
          + " > " + grib_2_in_folder_path_temp + "W_fr-meteofrance,MODEL,AROME+0025+SP3+07H08H_C_LFPW_201904151600--.grib2"
    os.system(cmd)

    print("  -> SP3 run 1600 ech 00H08H")
    cmd = "cat " \
          + grib_2_in_folder_path_temp + "SP3_201904151600_00H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_201904151600_01H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_201904151600_02H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_201904151600_03H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_201904151600_04H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_201904151600_05H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_201904151600_06H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_201904151600_07H_MOD.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_201904151600_08H_MOD.grib2 " \
          + " > " + grib_2_in_folder_path_temp + "W_fr-meteofrance,MODEL,AROME+0025+SP3+00H08H_C_LFPW_201904151600--.grib2"
    os.system(cmd)

    cmd = "rm " + grib_2_in_folder_path_temp + "SP3*"
    os.system(cmd)
    print("  -> fin de concaténation en temps\n")

    print("Découpage de HP1 HP2 SP1 SP2 SP3 par paramId suivant un ordre ascendant de stepRange ech 00H06H...")
    print("  HP1:")
    # 130/157/131/228246/228239/132/228247/228240/3031/10/228249/228241/54/228246/228247/228249/228239/228240/228241
    cmd = "grib_copy -B'stepRange:i asc' " \
          + grib_2_in_folder_path_temp + "W_fr-meteofrance,MODEL,AROME+0025+HP1+00H06H_C_LFPW_201904151600--.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_[paramId]_00H06H.grib2"
    os.system(cmd)

    print("  -> reconstruction de U par level : paramId=131,paramId=228246,paramId=228239")
    cmd = "cat " + grib_2_in_folder_path_temp + "HP1_131_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_228246_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_228239_00H06H.grib2 > " \
          + grib_2_in_folder_path_temp + "HP1_U_temp_00H06H.grib2"
    os.system(cmd)
    cmd = "grib_copy -B'stepRange:i asc','level:i asc' " + grib_2_in_folder_path_temp + "HP1_U_temp_00H06H.grib2 " + grib_2_in_folder_path_temp + "HP1_U_00H06H.grib2"
    os.system(cmd)

    print("  -> reconstruction de V par level : paramId=132,paramId=228247,paramId=228240")
    cmd = "cat " + grib_2_in_folder_path_temp + "HP1_132_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_228247_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_228240_00H06H.grib2 > " \
          + grib_2_in_folder_path_temp + "HP1_V_temp_00H06H.grib2"
    os.system(cmd)
    cmd = "grib_copy -B'stepRange:i asc','level:i asc' " \
          + grib_2_in_folder_path_temp + "HP1_V_temp_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_V_00H06H.grib2"
    os.system(cmd)

    print("  -> reconstruction de FF par level : paramId=10,paramId=228249,paramId=228241")
    cmd = "cat " + grib_2_in_folder_path_temp + "HP1_10_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_228249_00H06H.grib2 " + grib_2_in_folder_path_temp + "HP1_228241_00H06H.grib2 > " + grib_2_in_folder_path_temp + "HP1_FF_temp_00H06H.grib2"
    os.system(cmd)
    cmd = "grib_copy -B'stepRange:i asc','level:i asc' " + grib_2_in_folder_path_temp + "HP1_FF_temp_00H06H.grib2 " + grib_2_in_folder_path_temp + "HP1_FF_00H06H.grib2"
    os.system(cmd)

    cmd = "cat " \
          + grib_2_in_folder_path_temp + "HP1_130_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_157_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_U_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_V_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_3031_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_FF_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "HP1_54_00H06H.grib2 >" \
          + output_directory + "W_fr-meteofrance,MODEL,AROME+0025+HP1+00H06H_C_LFPW_201904151600--.grib2"
    os.system(cmd)

    cmd = "rm " + grib_2_in_folder_path_temp + "HP1*"
    os.system(cmd)
    print("  -> fin de reconcaténation de HP1\n")

    print("  HP2:")
    # 129/260155/246/75/76/247/0/133/3017
    cmd = "grib_copy -B'stepRange:i asc' " + grib_2_in_folder_path_temp + "W_fr-meteofrance,MODEL,AROME+0025+HP2+00H06H_C_LFPW_201904151600--.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_[paramId]_00H06H.grib2"
    os.system(cmd)

    cmd = "cat " \
          + grib_2_in_folder_path_temp + "HP2_129_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_260155_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_246_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_75_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_76_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_247_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_0_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_133_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "HP2_3017_00H06H.grib2 >" \
          + output_directory + "W_fr-meteofrance,MODEL,AROME+0025+HP2+00H06H_C_LFPW_201904151600--.grib2"
    os.system(cmd)

    cmd = "rm " + grib_2_in_folder_path_temp + "HP2*"
    os.system(cmd)

    print("  -> fin de reconcaténation de HP2\n")

    print("  SP1:")
    # 151/165/166/260260/207/260065/260066/260067/167/260242/228228/3099/260087/0/228164
    cmd = "grib_copy -B'stepRange:i asc' " + grib_2_in_folder_path_temp + "W_fr-meteofrance,MODEL,AROME+0025+SP1+00H06H_C_LFPW_201904151600--.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_[paramId]_00H06H.grib2"
    os.system(cmd)

    print("  -> reconstruction de tprate paramId=228228 récupéré des archives en ajustant hourOfEndOfOverallTimeInterval")
    print("    -> hourOfEndOfOverallTimeInterval 13 devient 17")
    print("    -> hourOfEndOfOverallTimeInterval 14 devient 18")
    print("    -> hourOfEndOfOverallTimeInterval 15 devient 19")
    print("    -> hourOfEndOfOverallTimeInterval 16 devient 20")
    print("    -> hourOfEndOfOverallTimeInterval 17 devient 21")
    print("    -> hourOfEndOfOverallTimeInterval 18 devient 22")

    cmd = "grib_set -s hourOfEndOfOverallTimeInterval=17 -w hourOfEndOfOverallTimeInterval=13 " + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-1.grib2 " + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-1_interval_ok.grib2"
    os.system(cmd)
    cmd = "grib_set -s hourOfEndOfOverallTimeInterval=18 -w hourOfEndOfOverallTimeInterval=14 " + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-2.grib2 " + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-2_interval_ok.grib2"
    os.system(cmd)
    cmd = "grib_set -s hourOfEndOfOverallTimeInterval=19 -w hourOfEndOfOverallTimeInterval=15 " + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-3.grib2 " + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-3_interval_ok.grib2"
    os.system(cmd)
    cmd = "grib_set -s hourOfEndOfOverallTimeInterval=20 -w hourOfEndOfOverallTimeInterval=16 " + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-4.grib2 " + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-4_interval_ok.grib2"
    os.system(cmd)
    cmd = "grib_set -s hourOfEndOfOverallTimeInterval=21 -w hourOfEndOfOverallTimeInterval=17 " + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-5.grib2 " + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-5_interval_ok.grib2"
    os.system(cmd)
    cmd = "grib_set -s hourOfEndOfOverallTimeInterval=22 -w hourOfEndOfOverallTimeInterval=18 " + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-6.grib2 " + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-6_interval_ok.grib2"
    os.system(cmd)

    cmd = "cat " + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-1_interval_ok.grib2 " \
          + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-2_interval_ok.grib2 " \
          + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-3_interval_ok.grib2 " \
          + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-4_interval_ok.grib2 " \
          + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-5_interval_ok.grib2 " \
          + grib_2_in_folder_path_temp + precipitation_tprate_folder + "out_228228_0-6_interval_ok.grib2 > " \
          + grib_2_in_folder_path_temp + "SP1_228228_00H06H_okok.grib2 "
    os.system(cmd)
    cmd = "rm -R " + grib_2_in_folder_path_temp + precipitation_tprate_folder
    os.system(cmd)

    print("  -> reconstruction de snom paramId=3099 en faux cumul")
    cmd = "grib_copy " + grib_2_in_folder_path_temp + "SP1_3099_00H06H.grib2 " + grib_2_in_folder_path_temp + "SP1_3099_00H06H_[stepRange].grib2 "
    os.system(cmd)
    for i in range(6):
        cmd = "grib_set -s stepRange=0-" + str(i + 1) + " -w stepRange=" + str(
            i + 1) + " " + grib_2_in_folder_path_temp + "SP1_3099_00H06H_" + str(i + 1) + ".grib2 " \
              + grib_2_in_folder_path_temp + "SP1_3099_00H06H_00H0" + str(i + 1) + "H.grib2"
        os.system(cmd)

    cmd = "cat " + grib_2_in_folder_path_temp + "SP1_3099_00H06H_00H01H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_3099_00H06H_00H02H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_3099_00H06H_00H03H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_3099_00H06H_00H04H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_3099_00H06H_00H05H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_3099_00H06H_00H06H.grib2 > " \
          + grib_2_in_folder_path_temp + "SP1_3099_00H06H_ok.grib2 "
    os.system(cmd)

    print("  -> reconstruction de downwards flux paramId=260087 en faux cumul")
    cmd = "grib_copy " + grib_2_in_folder_path_temp + "SP1_260087_00H06H.grib2 " + grib_2_in_folder_path_temp + "SP1_260087_00H06H_[stepRange].grib2 "
    os.system(cmd)
    for i in range(6):
        cmd = "grib_set -s stepRange=0-" + str(i + 1) + " -w stepRange=" + str(
            i + 1) + " " + grib_2_in_folder_path_temp + "SP1_260087_00H06H_" + str(i + 1) + ".grib2 " \
              + grib_2_in_folder_path_temp + "SP1_260087_00H06H_00H0" + str(i + 1) + "H.grib2"
        os.system(cmd)

    cmd = "cat " + grib_2_in_folder_path_temp + "SP1_260087_00H06H_00H01H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_260087_00H06H_00H02H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_260087_00H06H_00H03H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_260087_00H06H_00H04H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_260087_00H06H_00H05H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_260087_00H06H_00H06H.grib2 > " \
          + grib_2_in_folder_path_temp + "SP1_260087_00H06H_ok.grib2 "
    os.system(cmd)

    print("  -> reconstruction de unknown flux paramId=0 en faux cumul")
    cmd = "grib_copy " + grib_2_in_folder_path_temp + "SP1_0_00H06H.grib2 " + grib_2_in_folder_path_temp + "SP1_0_00H06H_[stepRange].grib2 "
    os.system(cmd)
    for i in range(6):
        cmd = "grib_set -s stepRange=0-" + str(i + 1) + " -w stepRange=" + str(
            i + 1) + " " + grib_2_in_folder_path_temp + "SP1_0_00H06H_" + str(i + 1) + ".grib2 " \
              + grib_2_in_folder_path_temp + "SP1_0_00H06H_00H0" + str(i + 1) + "H.grib2"
        os.system(cmd)

    cmd = "cat " + grib_2_in_folder_path_temp + "SP1_0_00H06H_00H01H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_0_00H06H_00H02H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_0_00H06H_00H03H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_0_00H06H_00H04H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_0_00H06H_00H05H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_0_00H06H_00H06H.grib2 > " \
          + grib_2_in_folder_path_temp + "SP1_0_00H06H_ok.grib2 "
    os.system(cmd)

    cmd = "cat " \
          + grib_2_in_folder_path_temp + "SP1_151_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_165_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_166_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_260260_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_207_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_260065_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_260066_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_260067_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_167_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_260242_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_228228_00H06H_okok.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_3099_00H06H_ok.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_260087_00H06H_ok.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_0_00H06H_ok.grib2 " \
          + grib_2_in_folder_path_temp + "SP1_228164_00H06H.grib2 >" \
          + output_directory + "W_fr-meteofrance,MODEL,AROME+0025+SP1+00H06H_C_LFPW_201904151600--.grib2"
    os.system(cmd)

    print("  -> fin de reconcaténation de SP1\n")
    cmd = "rm " + grib_2_in_folder_path_temp + "SP1*"
    os.system(cmd)

    print("  SP2:")
    # 134/130/3073/3074/3075/3008/167/85001160/260083/260045/168/133
    cmd = "grib_copy -B'stepRange:i asc' " + grib_2_in_folder_path_temp + "W_fr-meteofrance,MODEL,AROME+0025+SP2+00H06H_C_LFPW_201904151600--.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_[paramId]_00H06H.grib2"
    os.system(cmd)

    print("  -> reconstruction de min temperature 2m paramId=167 et typeOfStatisticalProcessing=2 et en faux cumul")
    cmd = "grib_copy -w typeOfStatisticalProcessing=2 " + grib_2_in_folder_path_temp + "SP2_167_00H06H.grib2 " + grib_2_in_folder_path_temp + "SP2_167_00H06H_temp_min_[stepRange].grib2"
    os.system(cmd)

    for i in range(0, 6, 1):
        cmd = "grib_set -s stepRange=" + str(i) + "-" + str(i + 1) + " -w stepRange=" + str(
            i + 1) + " " + grib_2_in_folder_path_temp + "SP2_167_00H06H_temp_min_" + str(i + 1) + ".grib2 " \
              + grib_2_in_folder_path_temp + "SP2_167_min_00H06H_0" + str(i) + "H0" + str(i + 1) + "H.grib2"

        os.system(cmd)

    cmd = "cat " + grib_2_in_folder_path_temp + "SP2_167_min_00H06H_00H01H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_167_min_00H06H_01H02H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_167_min_00H06H_02H03H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_167_min_00H06H_03H04H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_167_min_00H06H_04H05H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_167_min_00H06H_05H06H.grib2 > " \
          + grib_2_in_folder_path_temp + "SP2_167_min_00H06H_ok.grib2 "
    os.system(cmd)

    print("  -> reconstruction de min temperature 2m paramId=167 et typeOfStatisticalProcessing=3 et en faux cumul")
    cmd = "grib_copy -w typeOfStatisticalProcessing=3 " + grib_2_in_folder_path_temp + "SP2_167_00H06H.grib2 " + grib_2_in_folder_path_temp + "SP2_167_00H06H_temp_max_[stepRange].grib2"
    os.system(cmd)

    for i in range(0, 6, 1):
        cmd = "grib_set -s stepRange=" + str(i) + "-" + str(i + 1) + " -w stepRange=" + str(
            i + 1) + " " + grib_2_in_folder_path_temp + "SP2_167_00H06H_temp_max_" + str(i + 1) + ".grib2 " \
              + grib_2_in_folder_path_temp + "SP2_167_max_00H06H_0" + str(i) + "H0" + str(i + 1) + "H.grib2"
        os.system(cmd)

    cmd = "cat " + grib_2_in_folder_path_temp + "SP2_167_max_00H06H_00H01H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_167_max_00H06H_01H02H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_167_max_00H06H_02H03H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_167_max_00H06H_03H04H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_167_max_00H06H_04H05H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_167_max_00H06H_05H06H.grib2 > " \
          + grib_2_in_folder_path_temp + "SP2_167_max_00H06H_ok.grib2 "
    os.system(cmd)

    cmd = "cat " + grib_2_in_folder_path_temp + "SP2_167_max_00H06H_ok.grib2 " + grib_2_in_folder_path_temp + "SP2_167_min_00H06H_ok.grib2> " + \
          grib_2_in_folder_path_temp + "SP2_167_00H06H_ok.grib2"
    os.system(cmd)

    print("  -> reconstruction de total water precipitation paramId=260045 en faux cumul")
    cmd = "grib_copy " + grib_2_in_folder_path_temp + "SP2_260045_00H06H.grib2 " + grib_2_in_folder_path_temp + "SP2_260045_00H06H_[stepRange].grib2 "
    os.system(cmd)
    for i in range(6):
        cmd = "grib_set -s stepRange=0-" + str(i + 1) + " -w stepRange=" + str(
            i + 1) + " " + grib_2_in_folder_path_temp + "SP2_260045_00H06H_" + str(i + 1) + ".grib2 " \
              + grib_2_in_folder_path_temp + "SP2_260045_00H06H_00H0" + str(i + 1) + "H.grib2"
        os.system(cmd)

    cmd = "cat " + grib_2_in_folder_path_temp + "SP2_260045_00H06H_00H01H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_260045_00H06H_00H02H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_260045_00H06H_00H03H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_260045_00H06H_00H04H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_260045_00H06H_00H05H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_260045_00H06H_00H06H.grib2 > " \
          + grib_2_in_folder_path_temp + "SP2_260045_00H06H_ok.grib2 "
    os.system(cmd)

    cmd = "cat " \
          + grib_2_in_folder_path_temp + "SP2_134_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_130_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_3073_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_3074_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_3075_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_3008_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_167_00H06H_ok.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_85001160_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_260083_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_260045_00H06H_ok.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_168_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "SP2_133_00H06H.grib2 > " \
          + output_directory + "W_fr-meteofrance,MODEL,AROME+0025+SP2+00H06H_C_LFPW_201904151600--.grib2"
    os.system(cmd)

    print("  -> fin de reconcaténation de SP2\n")
    cmd = "rm " + grib_2_in_folder_path_temp + "SP2*"
    os.system(cmd)

    print("  SP3:")
    # 136/0/147/146/260097/176/177/180/181
    cmd = "grib_copy -B'stepRange:i asc' " + grib_2_in_folder_path_temp + "W_fr-meteofrance,MODEL,AROME+0025+SP3+00H06H_C_LFPW_201904151600--.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_[paramId]_00H06H.grib2"
    os.system(cmd)

    print("  -> reconstruction paramId=0/147/146/260097/176/177/180/181 en faux cumul")
    cmd = "grib_copy " + grib_2_in_folder_path_temp + "SP3_0_00H06H.grib2 " + grib_2_in_folder_path_temp + "SP3_0_00H06H_[stepRange].grib2 "
    os.system(cmd)
    cmd = "grib_copy " + grib_2_in_folder_path_temp + "SP3_147_00H06H.grib2 " + grib_2_in_folder_path_temp + "SP3_147_00H06H_[stepRange].grib2 "
    os.system(cmd)
    cmd = "grib_copy " + grib_2_in_folder_path_temp + "SP3_146_00H06H.grib2 " + grib_2_in_folder_path_temp + "SP3_146_00H06H_[stepRange].grib2 "
    os.system(cmd)
    cmd = "grib_copy " + grib_2_in_folder_path_temp + "SP3_260097_00H06H.grib2 " + grib_2_in_folder_path_temp + "SP3_260097_00H06H_[stepRange].grib2 "
    os.system(cmd)
    cmd = "grib_copy " + grib_2_in_folder_path_temp + "SP3_176_00H06H.grib2 " + grib_2_in_folder_path_temp + "SP3_176_00H06H_[stepRange].grib2 "
    os.system(cmd)
    cmd = "grib_copy " + grib_2_in_folder_path_temp + "SP3_177_00H06H.grib2 " + grib_2_in_folder_path_temp + "SP3_177_00H06H_[stepRange].grib2 "
    os.system(cmd)
    cmd = "grib_copy " + grib_2_in_folder_path_temp + "SP3_180_00H06H.grib2 " + grib_2_in_folder_path_temp + "SP3_180_00H06H_[stepRange].grib2 "
    os.system(cmd)
    cmd = "grib_copy " + grib_2_in_folder_path_temp + "SP3_181_00H06H.grib2 " + grib_2_in_folder_path_temp + "SP3_181_00H06H_[stepRange].grib2 "
    os.system(cmd)

    for i in range(6):
        cmd = "grib_set -s stepRange=0-" + str(i + 1) + " -w stepRange=" + str(i + 1) + " " \
              + grib_2_in_folder_path_temp + "SP3_0_00H06H_" + str(i + 1) + ".grib2 " \
              + grib_2_in_folder_path_temp + "SP3_0_00H06H_00H0" + str(i + 1) + "H.grib2"
        os.system(cmd)
        cmd = "grib_set -s stepRange=0-" + str(i + 1) + " -w stepRange=" + str(i + 1) + " " \
              + grib_2_in_folder_path_temp + "SP3_147_00H06H_" + str(i + 1) + ".grib2 " \
              + grib_2_in_folder_path_temp + "SP3_147_00H06H_00H0" + str(i + 1) + "H.grib2"
        os.system(cmd)
        cmd = "grib_set -s stepRange=0-" + str(i + 1) + " -w stepRange=" + str(i + 1) + " " \
              + grib_2_in_folder_path_temp + "SP3_146_00H06H_" + str(i + 1) + ".grib2 " \
              + grib_2_in_folder_path_temp + "SP3_146_00H06H_00H0" + str(i + 1) + "H.grib2"
        os.system(cmd)
        cmd = "grib_set -s stepRange=0-" + str(i + 1) + " -w stepRange=" + str(i + 1) + " " \
              + grib_2_in_folder_path_temp + "SP3_260097_00H06H_" + str(i + 1) + ".grib2 " \
              + grib_2_in_folder_path_temp + "SP3_260097_00H06H_00H0" + str(i + 1) + "H.grib2"
        os.system(cmd)
        cmd = "grib_set -s stepRange=0-" + str(i + 1) + " -w stepRange=" + str(i + 1) + " " \
              + grib_2_in_folder_path_temp + "SP3_176_00H06H_" + str(i + 1) + ".grib2 " \
              + grib_2_in_folder_path_temp + "SP3_176_00H06H_00H0" + str(i + 1) + "H.grib2"
        os.system(cmd)
        cmd = "grib_set -s stepRange=0-" + str(i + 1) + " -w stepRange=" + str(i + 1) + " " \
              + grib_2_in_folder_path_temp + "SP3_177_00H06H_" + str(i + 1) + ".grib2 " \
              + grib_2_in_folder_path_temp + "SP3_177_00H06H_00H0" + str(i + 1) + "H.grib2"
        os.system(cmd)
        cmd = "grib_set -s stepRange=0-" + str(i + 1) + " -w stepRange=" + str(i + 1) + " " \
              + grib_2_in_folder_path_temp + "SP3_180_00H06H_" + str(i + 1) + ".grib2 " \
              + grib_2_in_folder_path_temp + "SP3_180_00H06H_00H0" + str(i + 1) + "H.grib2"
        os.system(cmd)
        cmd = "grib_set -s stepRange=0-" + str(i + 1) + " -w stepRange=" + str(i + 1) + " " \
              + grib_2_in_folder_path_temp + "SP3_181_00H06H_" + str(i + 1) + ".grib2 " \
              + grib_2_in_folder_path_temp + "SP3_181_00H06H_00H0" + str(i + 1) + "H.grib2"
        os.system(cmd)

    cmd = "cat " + grib_2_in_folder_path_temp + "SP3_0_00H06H_00H01H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_0_00H06H_00H02H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_0_00H06H_00H03H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_0_00H06H_00H04H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_0_00H06H_00H05H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_0_00H06H_00H06H.grib2 > " \
          + grib_2_in_folder_path_temp + "SP3_0_00H06H_ok.grib2 "
    os.system(cmd)

    cmd = "cat " + grib_2_in_folder_path_temp + "SP3_146_00H06H_00H01H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_146_00H06H_00H02H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_146_00H06H_00H03H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_146_00H06H_00H04H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_146_00H06H_00H05H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_146_00H06H_00H06H.grib2 > " \
          + grib_2_in_folder_path_temp + "SP3_146_00H06H_ok.grib2 "
    os.system(cmd)

    cmd = "cat " + grib_2_in_folder_path_temp + "SP3_147_00H06H_00H01H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_147_00H06H_00H02H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_147_00H06H_00H03H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_147_00H06H_00H04H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_147_00H06H_00H05H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_147_00H06H_00H06H.grib2 > " \
          + grib_2_in_folder_path_temp + "SP3_147_00H06H_ok.grib2 "
    os.system(cmd)

    cmd = "cat " + grib_2_in_folder_path_temp + "SP3_260097_00H06H_00H01H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_260097_00H06H_00H02H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_260097_00H06H_00H03H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_260097_00H06H_00H04H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_260097_00H06H_00H05H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_260097_00H06H_00H06H.grib2 > " \
          + grib_2_in_folder_path_temp + "SP3_260097_00H06H_ok.grib2 "
    os.system(cmd)

    cmd = "cat " + grib_2_in_folder_path_temp + "SP3_176_00H06H_00H01H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_176_00H06H_00H02H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_176_00H06H_00H03H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_176_00H06H_00H04H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_176_00H06H_00H05H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_176_00H06H_00H06H.grib2 > " \
          + grib_2_in_folder_path_temp + "SP3_176_00H06H_ok.grib2 "
    os.system(cmd)

    cmd = "cat " + grib_2_in_folder_path_temp + "SP3_177_00H06H_00H01H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_177_00H06H_00H02H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_177_00H06H_00H03H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_177_00H06H_00H04H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_177_00H06H_00H05H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_177_00H06H_00H06H.grib2 > " \
          + grib_2_in_folder_path_temp + "SP3_177_00H06H_ok.grib2 "
    os.system(cmd)

    cmd = "cat " + grib_2_in_folder_path_temp + "SP3_180_00H06H_00H01H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_180_00H06H_00H02H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_180_00H06H_00H03H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_180_00H06H_00H04H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_180_00H06H_00H05H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_180_00H06H_00H06H.grib2 > " \
          + grib_2_in_folder_path_temp + "SP3_180_00H06H_ok.grib2 "
    os.system(cmd)

    cmd = "cat " + grib_2_in_folder_path_temp + "SP3_181_00H06H_00H01H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_181_00H06H_00H02H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_181_00H06H_00H03H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_181_00H06H_00H04H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_181_00H06H_00H05H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_181_00H06H_00H06H.grib2 > " \
          + grib_2_in_folder_path_temp + "SP3_181_00H06H_ok.grib2 "
    os.system(cmd)

    # 0/147/146/260097/176/177/180/181
    cmd = "cat " \
          + grib_2_in_folder_path_temp + "SP3_136_00H06H.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_0_00H06H_ok.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_147_00H06H_ok.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_146_00H06H_ok.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_260097_00H06H_ok.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_176_00H06H_ok.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_177_00H06H_ok.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_180_00H06H_ok.grib2 " \
          + grib_2_in_folder_path_temp + "SP3_181_00H06H_ok.grib2 > " \
          + output_directory + "W_fr-meteofrance,MODEL,AROME+0025+SP3+00H06H_C_LFPW_201904151600--.grib2"
    os.system(cmd)
    print("  -> fin de reconcaténation de SP3\n")
    cmd = "rm " + grib_2_in_folder_path_temp + "SP3*"
    os.system(cmd)

    print("  -> suppression des derniers fichiers temporaires\n")
    cmd = "rm " + grib_2_in_folder_path_temp + "W_fr*"
    os.system(cmd)
    cmd = "rm -R " + grib_2_in_folder_path_temp
    os.system(cmd)

if option_show_HP1_after is True:
    print("Print in HP1 for level = 20, 100 et 200")

    cmd = "grib_ls -p dataDate,dataTime,stepRange,name,shortName,units,level,paramId,discipline,parameterCategory,parameterNumber " \
          "-w paramId=130/157/131/228246/228239/132/228247/228240/3031/10/228249/228241/54,level=20 " + output_directory + \
          "W_fr-meteofrance,MODEL,AROME+0025+HP1+00H06H_C_LFPW_201904151600--.grib2"

    os.system(cmd)

    cmd = "grib_ls -p dataDate,dataTime,stepRange,name,shortName,units,level,paramId,discipline,parameterCategory,parameterNumber " \
          "-w paramId=228246/228247/228249,level=100 " + output_directory + \
          "W_fr-meteofrance,MODEL,AROME+0025+HP1+00H06H_C_LFPW_201904151600--.grib2"

    os.system(cmd)

    cmd = "grib_ls -p dataDate,dataTime,stepRange,name,shortName,units,level,paramId,discipline,parameterCategory,parameterNumber " \
          "-w paramId=228239/228240/228241,level=200 " + output_directory + \
          "W_fr-meteofrance,MODEL,AROME+0025+HP1+00H06H_C_LFPW_201904151600--.grib2"

    os.system(cmd)

if option_show_HP2_after is True:
    print("Print in HP2 for level = 20")
    cmd = "grib_ls -p dataDate,dataTime,stepRange,shortName,units,level,paramId,discipline,parameterCategory,parameterNumber " \
          "-w paramId=129/260155/246/75/76/247/0/133/3017,level=20 " + output_directory + \
          "W_fr-meteofrance,MODEL,AROME+0025+HP2+00H06H_C_LFPW_201904151600--.grib2"
    os.system(cmd)

if option_show_SP1_after is True:
    print("Print in SP1")
    cmd = "grib_ls -p dataDate,dataTime,stepRange,name,shortName,units,level,paramId,discipline,parameterCategory,parameterNumber " \
          "-w paramId=151/165/166/260260/207/260065/260066/260067/167/260242/228228/3099/260087/0/228164 " + output_directory + \
          "W_fr-meteofrance,MODEL,AROME+0025+SP1+00H06H_C_LFPW_201904151600--.grib2"
    os.system(cmd)

if option_show_SP2_after is True:
    print("Print in SP2")
    cmd = "grib_ls -p dataDate,dataTime,stepRange,name,shortName,units,level,paramId,discipline,parameterCategory,parameterNumber " \
          "-w paramId=134/130/3073/3074/3075/3008/167/85001160/260083/260045/168/133 " + output_directory + \
          "W_fr-meteofrance,MODEL,AROME+0025+SP2+00H06H_C_LFPW_201904151600--.grib2"
    os.system(cmd)

if option_show_SP3_after is True:
    print("Print in SP3")
    cmd = "grib_ls -p dataDate,dataTime,stepRange,name,shortName,units,level,paramId,discipline,parameterCategory,parameterNumber " \
          "-w paramId=136/0/147/146/260097/176/177/180/181 " + output_directory + \
          "W_fr-meteofrance,MODEL,AROME+0025+SP3+00H06H_C_LFPW_201904151600--.grib2"
    os.system(cmd)

print("Fin de reconstruction du fichier d'analyses")
print("  -> fichiers disponibles dans OUTPUT du 15/04/2019 run 1600 ech 00H06H.")
