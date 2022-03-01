import argparse
from audioop import add
import  os
import re
import sys
import tqdm
import numpy as np
from matplotlib import pyplot as plt

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

        for id in range(self.n_dimm):
            self.add_DIMM(id)

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

    def plot(self,req_map):
        fig, ax = plt.subplots()  
        im=ax.imshow(req_map)
        ax.set_xticks(np.arange(self.n_dimm))
        ax.set_yticks(np.arange(self.n_dimm))
        fig.colorbar(im,pad=0.03)
        plt.ylabel("src ID")
        plt.xlabel("dst ID")
        plt.savefig("req_map.png")


    def calc_inter_DIMM_requests(self):
        req_map = np.zeros((self.n_dimm, self.n_dimm))
        for src_id, dimm in self.DIMMs.items():
            for req in dimm.reqs:
                req_type, addr = req
                dst_id = self.get_target_dimm(addr)
                req_map[src_id][dst_id] += 1

        print(req_map)
        return req_map

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
    
    req_map = system.calc_inter_DIMM_requests()
    # plot the heatmap
    system.plot(req_map)
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dump_file",
        type=str,
        default = "output/mem_acc_dump_file_0",
        help="Path of the dump file",
    )

    parser.add_argument(
        "--n_dimm",
        type = int, 
        default= 8,
        help="number of DIMMs",
    )

    cfg = parser.parse_args()
    main(cfg)

