import os
import re
import time

# YOU should fill your path here!
base='/home/yf/app/multipim1/MultiPIM/'

# YOU need not code next
base_dir=base+'tests/benchmarks/Polybench'
cmdcfg_loc=base+'tests/cmd.cfg'
memtrace_loc=base+'tests/output'
analysis_loc=base+'tests/analysis.py'


alias_pim_env="bash run_pim.sh"
analysiscmd="python3 "+analysis_loc+" --dump_file="+memtrace_loc+"/mem_acc_dump_file_0"+" --pic_name="


dir_lists=['linear-algebra/kernels','linear-algebra/solvers','datamining','stencils']
dir_list=['datamining']
def filter(s):
    if s!='Makefile.dep' and s!='Makefile' and s[-2:]!='.h' and s[-2:]!='.c':
        return True

# how to hack cmd.cfg ?
# only need to fix cmd.cfg and 'sh run_pim.sh'

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


for dir in dir_lists:
    path=base_dir+'/'+dir
    if os.path.isdir(path):
        for fpathe,dirs,fs in os.walk(path):
            for f in fs:
                if filter(f):
                    print(f)
                    print("----------------------")
                    
                    # walk demos and hack cmd.cfg
                    alter(cmdcfg_loc,os.path.join(fpathe,f))

                    # run zsim and get memtrace
                    # step1. source env
                    # step2. run zsim
                    os.system(alias_pim_env)
                    # print(alias_pim_env)

                    # use memtrace to draw
                    # print(analysiscmd+f)
                    os.system(analysiscmd+f)