import argparse
from asyncore import write
from audioop import add
import  os
from random import SystemRandom
import re
import sys
import tqdm
import numpy as np
from matplotlib import pyplot as plt
import h5py

class DIMM:
    def __init__(self, id) -> None:
        self.id = id

class Thread:
    def __init__(self, tid) -> None:
        self.tid = tid
        self.reqs = []

    def record_req(self, req_type, addr):
        self.reqs.append([req_type, addr])

class PageTable:
    def __init__(self, n_dimm) -> None:
        self.map = {}
        self.n_dimm = n_dimm
        self.touch_record = {}

    def get_DIMM(self,addr):
        page_id = addr >> 12
        if page_id not in self.map.keys():
            self.map[page_id] = page_id % self.n_dimm
        return self.map[page_id]
    
    def next_touch(self, src_id, addr):
        page_id = addr >> 12
        if page_id not in self.touch_record.keys():
            self.touch_record[page_id] = True
        else:
            if self.touch_record[page_id] == False:
                return
            else:
                self.map[page_id] = src_id
                self.touch_record[page_id] = False

class System:
    def __init__(self, cfg) -> None:
        self.cfg = cfg
        self.DIMMs = {}
        # number of total dimms
        self.n_dimm = cfg.n_dimm

        self.raw_thread_map = {}
        self.threads = {}
        # number of total threads
        self.n_total_threads = 0
        self.max_threads_per_dimm = cfg.max_threads_per_dimm

        for id in range(self.n_dimm):
            self.add_DIMM(id)

        self.page_table = PageTable(self.n_dimm)

    def zsimIPC(self, fname):
        # Read the ZSIM stats file, in hdf5 format
        fzsim = h5py.File(fname,"r")

        # Get the single dataset in the file
        dset = fzsim["stats"]["root"]
        #print "dset_size: "+str(dset.size)

        findex = dset.size - 1 # We just need to access to the final stats (dont need to know intermeddiate stats)
        num_cores = dset[findex]['core'].size # get the number of cores
        print("cores: "+str(num_cores))
        self.pu_cores = num_cores
        cycles = [0] * num_cores
        instructions = [0] * num_cores
        ipc = [0] * num_cores

        for c in range(0, num_cores):
            cycles[c] = dset[findex]['core'][c]['cycles']
            instructions[c] = dset[findex]['core'][c]['instrs']
            if cycles[c] != 0:
                ipc[c] = float(instructions[c])/float(cycles[c])
                # print("[core-"+str(c)+"] cycles: "+str(cycles[c])+" instrs: "+str(instructions[c])+" IPC: "+str(ipc[c]))

        return cycles, ipc

    def add_DIMM(self, id):
        if id not in self.DIMMs.keys():
            self.DIMMs[id] = DIMM(id)

    def add_thread(self, tid):
        if tid not in self.raw_thread_map.keys():
            # map raw thread id to a logical thread id.
            self.raw_thread_map[tid] = self.n_total_threads
            self.threads[self.n_total_threads] = Thread(self.n_total_threads)
            self.n_total_threads += 1

    def record_request(self, raw_id, req_type, addr):
        # record per-thread requests
        tid = self.raw_thread_map[raw_id]
        self.threads[tid].record_req(req_type, addr)

    def show_per_core_requests(self):
        for id, dimm in self.DIMMs.items():
            print(id, len(dimm.reqs))

    def get_target_dimm(self, addr):
        #RoChBgBaCuVaCl
        offset = self.cfg.offset
        dimm_id = (addr >> offset) % self.n_dimm
        return dimm_id

    def get_toal_hops(self, req_map):
        total_hops = 0
        for src_id in range(req_map.shape[0]):
            for dst_id in range(req_map.shape[1]):
                total_hops += abs(dst_id - src_id) * req_map[src_id][dst_id]
        return total_hops

    def plot(self,req_map,req_map_name):
        # grid = plt.GridSpec(5, 5)        
        # plt.figure(figsize=(10, 6))
        # ax_1 = plt.subplot(grid[0:5,0:5])
        fig, ax = plt.subplots()  
        im=ax.imshow(req_map, cmap = "Blues")
        ax.set_xticks(np.arange(self.n_total_threads))
        ax.set_yticks(np.arange(self.n_dimm))

        ax.xaxis.set_ticks_position('top')
        ax.xaxis.set_label_position('top') 
        fig.colorbar(im,pad=0.03)
        
        # plt.grid(which="minor", color="w", linestyle='-', linewidth=10)
        # ax.tick_params(which="minor", bottom=False, left=False)
        # plt.grid(which="both")

        plt.ylabel("DIMM ID")
        plt.xlabel("Thread ID")
        plt.savefig(req_map_name)


    def calc_thread_requests(self):
        req_map = np.zeros((self.n_dimm, self.n_total_threads))
        for tid, thread in self.threads.items():
            for req in thread.reqs:
                req_type, addr = req 
                dst_id = self.get_target_dimm(addr)
                # print(dst_id,tid)
                req_map[dst_id][tid] += 1
        return req_map

    def estimate_distance_aware_heatmap(self, req_map):
        new_req_map = np.zeros_like(req_map)
        for src in range(self.n_dimm):
            for cid in range(req_map.shape[0]):
                for tid in range(req_map.shape[1]):
                    new_req_map[src][tid] +=  req_map[cid][tid] * (1 + abs(cid - src))
        return new_req_map

def main(cfg): 
    dump_file_path = cfg.dump_file
    assert(os.path.isfile(dump_file_path))
    dump_file = open(dump_file_path,'r').readlines()

    # init the memory system
    system = System(cfg)

    # load the memory requests trace
    print("Loading requests")
    for mem_acc in tqdm.tqdm(dump_file):
        acc_type, is_pim_instr, tid, addr = [int(x) for x in mem_acc.split(",")]
        assert(is_pim_instr == 1) 

        system.add_thread(tid)
        system.record_request(tid, acc_type, addr)
    
    # plot the heatmap
    if cfg.plot_heat_map:
        # heatmap 1
        req_map = system.calc_thread_requests()
        system.plot(req_map,cfg.pic_name+"_memory_access_heat_map.png")
        # heatmap 2
        req_map = system.estimate_distance_aware_heatmap(req_map)
        system.plot(req_map,cfg.pic_name+"_distance_aware_cost_map.png")
        # record distance aware heatmap

        with open(cfg.pic_name+"_distance_aware_cost_map.txt", 'w') as f:
            f.write(str(req_map.shape[0])+' '+str(req_map.shape[1])+'\n')
            for i in range(req_map.shape[0]):
                for j in range(req_map.shape[1]):
                    f.write(str(int(req_map[i][j]))+' ')
                f.write('\n')

    # cal the cycles and ipc
    if cfg.cal_cycles:
        #TODO:  implement a thread-based version 
        cycles, ipc = system.zsimIPC(cfg.h5_out)
        # extimated_inter_DIMM_cycles = system.estimate_inter_DIMM_cycles()
        # print(sum(cycles),extimated_inter_DIMM_cycles)
        # estimated_distance_aware_cycles = system.estimate_distance_aware_cycles()
        # print(estimated_distance_aware_cycles)
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dump_file",
        type=str,
        default = "results/bfs/mem_acc_dump_file_0",
        help="Path of the dump file",
    )

    parser.add_argument(
        "--n_dimm",
        type = int, 
        default= 4,
        help="number of DIMMs",
    )

    parser.add_argument(
        "--max_threads_per_dimm",
        type = int, 
        default = 4,
        help= "max number of threads per DIMM",
    )

    parser.add_argument(
        "--offset",
        type = int, 
        default = 11,
        help= "offset of the DIMM bits in address mapping",
    )

    parser.add_argument(
        "--h5_out",
        type = str, 
        default= "results/bfs/traces.out.zsim.h5",
        help="zsim stats h5",
    )

    parser.add_argument(
        "--plot_heat_map",
        type = bool, 
        default= True,
    )

    parser.add_argument(
        "--cal_cycles",
        type = bool, 
        default= False,
    )

    parser.add_argument(
        "--pic_name",
        type = str, 
        default= "heatmaps/bfs",
        help="name of png",
    )

    cfg = parser.parse_args()
    main(cfg)