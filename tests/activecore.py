#!/usr/bin/python
import h5py
import numpy as np
import sys
import os
from subprocess import call
# import commands
import re
import matplotlib.pyplot as plt

CoreInstr=[]
CoreIndex=[]
CoreCycles=[]
CoreIPC=[]

# Print TRACE IPC stats
def traceIPC(fname):
    inputFile = open(fname, "r")

    delta = 0
    intial = 0
    final = 0
    intr = 0
    totalInstructions = 0
    misses = 0
    #print fname

    for line in inputFile:
        match = re.search(r'\d\s\d\s\d+\s\w\s', line)
        if(match):
            try:
                instr = int (match.group().split()[2])
                type = match.group().split()[3]
                totalInstructions+=instr
                if(type != "P"):
                    totalInstructions+=1
                misses += 1
            except:
                print("Error at line - "+line)
    print("[overall-ROI] instrs: "+str(totalInstructions)+" misses: "+str(misses)+" MPKI: "+str(float(misses*1000)/float(totalInstructions)))

# Print ZSIM IPC stats
def zsimIPC(fname):
    # Read the ZSIM stats file, in hdf5 format
    fzsim = h5py.File(fname,"r")

    # Get the single dataset in the file
    dset = fzsim["stats"]["root"]
    #print "dset_size: "+str(dset.size)

    findex = dset.size - 1 # We just need to access to the final stats (dont need to know intermeddiate stats)
    num_cores = dset[findex]['core'].size # get the number of cores
    print("cores: "+str(num_cores))
    cycles = [0] * num_cores
    instructions = [0] * num_cores
    ipc = [0] * num_cores
    for c in range(0, num_cores):
        cycles[c] = dset[findex]['core'][c]['cycles']
        instructions[c] = dset[findex]['core'][c]['instrs']
        if cycles[c] != 0:
            ipc[c] = float(instructions[c])/float(cycles[c])
            print("[core-"+str(c)+"] cycles: "+str(cycles[c])+" instrs: "+str(instructions[c])+" IPC: "+str(ipc[c]))
            CoreIndex.append(c)
            CoreCycles.append(cycles[c])
            CoreInstr.append(instructions[c])
            CoreIPC.append(round(ipc[c],3))
    print("[overall] cycles: "+str(np.sum(cycles))+" instrs: "+str(np.sum(instructions))+" IPC: "+str(float(np.sum(instructions))/float(np.sum(cycles))))

# Draw
def draw():
    CoreStr=[str(CoreIndex[i]) for i in range(0,len(CoreIndex))]

    fig, ax1 = plt.subplots()
   
    ax1.plot(CoreStr, CoreIPC, label='ipc', color='#1b71f1', linewidth=2, marker='o',  markersize=7, linestyle='dashed')
    ax1.set_ylabel("ipc", fontsize='xx-large')
    ax1.set_ylim(0,1)
    for a, b in zip(CoreStr, CoreIPC):
        plt.text(a, b, b, ha='center', va='bottom', fontsize=10)
    
    ax2 = ax1.twinx()
    x1=range(len(CoreStr))
    x2=[i+0.35 for i in x1]
    p1=plt.bar(x1, CoreInstr, width=0.3, color="y")
    p2=plt.bar(x2, CoreCycles, width=0.3, color="b")
    plt.xticks([i+0.2 for i in x1],CoreStr)
    plt.xlabel('CoreIndex')
    ax2.legend([p1, p2], ["InstrCounts", "CycleCounts"], loc='upper right')
    ax2.set_ylabel('Counts')
    plt.title('Core Stats')

    plt.savefig("core1.png")


#####################################################
# MAIN
#####################################################
# The imput is two files: zsim stats, and the trace
if len(sys.argv) != 3:
    print("./activecore.py zsim.h5 trace.out")
    sys.exit();

print("## ZSIM Stats (from the whole ROI)##")
zsimIPC(sys.argv[1])
#traceIPC(sys.argv[2])
draw()


