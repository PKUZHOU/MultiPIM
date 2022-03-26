

dict1 = {103:1, 93:2, 82:3, 112:4, 23:5, 102:6, 124:7, 21:8, 48:9, 109:10, 114:11, 98:12, 121:13, 94:14, 106:15}
dict2 = {64:0, 96:1, 65:2, 66:3, 32:4, 33:5, 0:6, 1:7, 67:8, 97:9, 2:10, 34:11, 98:12, 99:13, 3:14, 35:15}
dict3 = {64:0, 96:1, 65:2, 97:3, 98:4, 99:5, 32:6, 33:7, 0:8, 1:9, 2:10, 34:11, 66:12, 35:13, 67:14, 3:15}


def dump_l1cache_file(dir, core_thread_dict):
    cache_inst_set = [set() for _ in range(16)]
    for core in core_thread_dict.keys():
        with open(dir+'l1d-'+str(core)) as f:
            lines = f.readlines()
            for line in lines:
                _, _, _, addr = [int(x) for x in line.split(',')]
                cache_inst_set[core_thread_dict[core]].add(addr)
    return cache_inst_set


def compare_l1cache():
    list1 = dump_l1cache_file('/home/licong/codes/MultiPIM/tests/results/bfs/cache_dump/', dict2)
    list2 = dump_l1cache_file('/home/licong/codes/MultiPIM/tests/results/bfs/cache_dump1/', dict2)
    print('L1 comparison result')
    for i in range(16):
        print(len(list1[i].intersection(list2[i])) / max(len(list1[i]), len(list2[i])))
    for i in range(0, 16, 4):
        addrs1 = set()
        addrs2 = set()
        for j in range(0, 4):
            addrs1 = addrs1.union(list1[i+j])
            addrs2 = addrs2.union(list2[i+j])
        print(len(addrs1.intersection(addrs2)) / max(len(addrs1), len(addrs2)))
    print('-------')
    addrs1 = set()
    addrs2 = set()
    for i in range(16):
        addrs1 = addrs1.union(list1[i])
        addrs2 = addrs2.union(list2[i])
    print(len(addrs1))
    print(len(addrs2))
    print(len(addrs1.intersection(addrs2)) / max(len(addrs1), len(addrs2)))
    print('-------')


def dump_llc_file(dir, core_thread_dict):
    thread_inst_list = [set() for _ in range(16)]
    with open(dir+'l2-0') as f:
        pass


def dump_mem_ctrl_file(file_name, core_thread_dict):
    thread_inst_list = [set() for _ in range(16)]
    with open(file_name, 'r') as f:
        lines = f.readlines()
        for line in lines:
            _, _, core_id, addr = [int(x) for x in line.split(',')]
            if core_id not in core_thread_dict.keys():
                core_thread_dict[core_id] = 0
            thread_inst_list[core_thread_dict[core_id]].add(addr)
    return thread_inst_list


def compare_mem_ctrl():
    list1 = dump_mem_ctrl_file('/home/licong/codes/MultiPIM/tests/results/bfs/mem_acc_dump_file_0', dict2)
    list2 = dump_mem_ctrl_file('/home/licong/codes/MultiPIM/tests/results/bfs/mem_acc_dump_file_0_1', dict2)
    # list3 = dump_file('/home/licong/codes/MultiPIM/tests/results/bfs/mem_acc_dump_file_0_1', dict3)
    # list4 = dump_file('/home/licong/codes/MultiPIM/tests/results/bfs/mem_acc_dump_file_0', dict2)
    print('mem controller comparison result')
    for i in range(16):
        print(len(list1[i].intersection(list2[i])) / max(len(list1[i]), len(list2[i])))
    for i in range(0, 16, 4):
        addrs1 = set()
        addrs2 = set()
        for j in range(0, 4):
            addrs1 = addrs1.union(list1[i+j])
            addrs2 = addrs2.union(list2[i+j])
        print(len(addrs1.intersection(addrs2)) / max(len(addrs1), len(addrs2)))
    print('-------')
    addrs1 = set()
    addrs2 = set()
    for i in range(16):
        addrs1 = addrs1.union(list1[i])
        addrs2 = addrs2.union(list2[i])
    print(len(addrs1))
    print(len(addrs2))
    print(len(addrs1.intersection(addrs2)) / max(len(addrs1), len(addrs2)))
    print('-------')
    '''
    print('-------')
    for i in range(16):
        print(len(list2[i].intersection(list3[i])))
    print('-------')
    for i in range(16):
        print(len(list3[i].intersection(list1[i])))
    print('-------')
    '''


if __name__ == '__main__':
    compare_mem_ctrl()
    compare_l1cache()
