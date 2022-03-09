import argparse
from audioop import add
import  os
import re
import sys
import tqdm
import numpy as np
from matplotlib import pyplot as plt
import h5py

class DIMM:
    def __init__(self, id) -> None:
        self.id = id
        self.reqs = []

    def record_req(self, req_type, addr):
        self.reqs.append([req_type, addr])

class System:
    def __init__(self, n_dimm) -> None:
        self.DIMMs = {}
        # number of total dimms
        self.n_dimm = n_dimm 
        self.pu_cores = 0

        for id in range(self.n_dimm):
            self.add_DIMM(id)

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

    def record_request(self, id, req_type, addr):
        self.DIMMs[id].record_req(req_type, addr)

    def show_per_core_requests(self):
        for id, dimm in self.DIMMs.items():
            print(id, len(dimm.reqs))

    def get_target_dimm(self, addr):
        #RoChBgBaCuVaCl
        offset = 10
        dimm_id = (addr >> offset) % self.n_dimm
        return dimm_id

    def plot(self,req_map,req_map_name):
        fig, ax = plt.subplots()  
        im=ax.imshow(req_map)
        ax.set_xticks(np.arange(self.n_dimm))
        ax.set_yticks(np.arange(self.n_dimm))
        fig.colorbar(im,pad=0.03)
        plt.ylabel("src ID")
        plt.xlabel("dst ID")
        plt.savefig(req_map_name)


    def calc_inter_DIMM_requests(self):
        req_map = np.zeros((self.n_dimm, self.n_dimm))
        for src_id, dimm in self.DIMMs.items():
            for req in dimm.reqs:
                req_type, addr = req
                dst_id = self.get_target_dimm(addr)
                req_map[src_id][dst_id] += 1

        # print(req_map)
        return req_map

    def estimate_inter_DIMM_cycles(self):
        n_ext_mem_acc = 0
        for src_id, dimm in self.DIMMs.items():
            for req in dimm.reqs:
                req_type, addr = req
                dst_id = self.get_target_dimm(addr)
                if dst_id != src_id:
                    n_ext_mem_acc += 1
        
        return n_ext_mem_acc * 8

def main(cfg): 
    dump_file_path = cfg.dump_file
    assert(os.path.isfile(dump_file_path))
    dump_file = open(dump_file_path,'r').readlines()

    # init the memory system
    system = System(cfg.n_dimm)

    # load the memory requests trace
    print("Loading requests")
    for mem_acc in tqdm.tqdm(dump_file):
        acc_type, is_pim_instr,srcId,addr = [int(x) for x in mem_acc.split(",")]
        assert(is_pim_instr == 1) 

        # even partition 
        dimm_id = srcId % cfg.n_dimm
        system.record_request(dimm_id, acc_type, addr)
    
    # plot the heatmap
    if cfg.plot_heat_map:
        req_map = system.calc_inter_DIMM_requests()
        system.plot(req_map,cfg.pic_name+".png")
    
    # cal the cycles and ipc
    if cfg.cal_cycles:
        cycles, ipc = system.zsimIPC(cfg.h5_out)
        extimated_inter_DIMM_cycles = system.estimate_inter_DIMM_cycles()
        print(sum(cycles),extimated_inter_DIMM_cycles)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dump_file",
        type=str,
        default = "results/pf/mem_acc_dump_file_0",
        help="Path of the dump file",
    )

    parser.add_argument(
        "--n_dimm",
        type = int, 
        default= 16,
        help="number of DIMMs",
    )

    parser.add_argument(
        "--h5_out",
        type = str, 
        default= "results/pf/traces.out.zsim.h5",
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
        default= True,
    )

    parser.add_argument(
        "--pic_name",
        type = str, 
        default= "heatmaps/req_map_pf.png",
        help="name of png",
    )

    cfg = parser.parse_args()
    main(cfg)