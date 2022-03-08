import os
import re
import time

# get pwd as loc path
base_dir=os.getcwd()
cmdcfg_loc=base_dir+"/cmd.cfg"

alias_pim_env="bash ./run_pim.sh"

#Get all tests filename and path
files = os.listdir(base_dir)
dir_lists=[a for a in files if os.path.isdir(a) and a!="common" and a!="output"]
dir_lists_loc=[base_dir+"/"+a for a in dir_lists]

analysiscmd="python3 analysis.py --dump_file=output/mem_acc_dump_file_0"+" --pic_name="

#TODO: you should check demo runs demos nornally and insert correctly
bp_loc=base_dir+"/backprop/"
bp_cmd=bp_loc+"backprop 65536"

bfs_loc=base_dir+"/bfs/"
bfs_cmd=bfs_loc+"bfs 8 "+bfs_loc+"data/bfs/graph65536.txt"

# ./heartwall ./data/test.avi 20 4
heartwall_loc=base_dir+"/heartwall/"
heartwall_cmd=heartwall_loc+"heartwall "+heartwall_loc+"data/test.avi 20 4"

# ./hotspot 1024 1024 2 4 ./data/temp_1024 ./data/power_1024 output.out
hotspot_loc=base_dir+"/hotspot/"
hotspot_cmd=hotspot_loc+"hotspot"+" 1024 1024 2 4  "+hotspot_loc+"data/temp_1024 "+hotspot_loc+"data/power_1024 output.out"

#./3D 512 8 100 ./data/power_512x8 ./data/temp_512x8 output.out
hotspot3D_loc=base_dir+"/hotspot3D/"
hotspot3D_cmd=hotspot3D_loc+"3D 512 8 100 "+hotspot3D_loc+"data/power_512x8 "+hotspot3D_loc+"data/temp_512x8 output.out"

# ./bfs 8 data/bfs/graph65536.txt
btree_loc=base_dir+"/b+tree/"
btree_cmd=btree_loc+"b+tree.out file "+btree_loc+"data/mil.txt command "+btree_loc+"data/command.txt"

# ./kmeans_openmp/kmeans -n 4 -i ./data/kdd_cup 
kmeans_loc=base_dir+"/kmeans/"
kmeans_cmd=kmeans_loc+"kmeans_openmp/kmeans -n 4 -i "+kmeans_loc+"data/kdd_cup"

# ./lavaMD -cores 4 -boxes1d 10
lavaMD_loc=base_dir+"/lavaMD/"
lavaMD_cmd=lavaMD_loc+"lavaMD -cores 4 -boxes1d 10"

# ./myocyte.out 100 1 0 4
myocyte_loc=base_dir+"/myocyte/"
myocyte_cmd=myocyte_loc+"myocyte.out 100 1 0 4"

# ./nn filelist_4 5 30 90
nn_loc=base_dir+"/nn/"
nn_cmd=nn_loc+"nn "+nn_loc+"filelist_4 5 30 90"

#./pathfinder 100000 100 > out
pathfinder_loc=base_dir+"/pathfinder/"
pathfinder_cmd=pathfinder_loc+"pathfinder 1000 10"

# ./srad 100 0.5 502 458 4
srad_loc=base_dir+"/srad/srad_v1/"
srad_cmd=srad_loc+"srad 100 0.5 502 458 4"

cmd_list=[hotspot_cmd, bfs_cmd, kmeans_cmd, nn_cmd, bp_cmd, hotspot3D_cmd, srad_cmd,\
    pathfinder_cmd, btree_cmd, myocyte_cmd, heartwall_cmd]

def alter(file,new_str):
    file_data = ""
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            match = re.search(r'\s\s\s\scommand*', line)
            if match:
                file_data += '    command ="'+new_str+'"\n'
            else:
                file_data += line
    print(file_data)
    with open(file,"w",encoding="utf-8") as f:
        f.write(file_data)


for cmd in cmd_list:
    print(cmd)
    print("------------------")
    alter(cmdcfg_loc,cmd)
    os.system(alias_pim_env)
    os.system(analysiscmd+dir_lists[cmd_list.index(cmd)])
