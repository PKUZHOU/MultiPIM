from asyncore import write


file_name = 'dimm_link_4mem1.xml'
num_dimm = 4
link_per_node = 4

def main():
    with open(file_name, 'w') as f:
        f.write('<!DOCTYPE memtopology SYSTEM "memtopology.dtd">\n')
        f.write('<memtopology>\n')

        # wirte nodes
        f.write('  <memnodes num="%d" linkspernode="%d">\n' % (num_dimm, link_per_node))
        for i in range(num_dimm):
            f.write('    <node id="%d">\n' % i)
            for j in range(link_per_node):
                f.write('        <link id="%d" tocpu="%s" />\n' % (i*link_per_node+j, 'true' if j==0 else 'false'))
            f.write('    </node>\n')
        f.write('  </memnodes>\n')

        # write interconnect
        f.write('  <meminterconnections>\n')
        for i in range(1, num_dimm):
            f.write('    <interconnection from="%d" to="%d" type="undirected" />\n' % (i*4-1, i*4+1))
        f.write('  </meminterconnections>\n')

        # write route
        f.write('  <memroutes type="static">\n')
        for i in range(num_dimm):
            for j in range(num_dimm):
                if i<j:
                    f.write('    <route src="%d" dst="%d" next="%d"/>\n' % (i, j, 4*i+3))
                elif i>j:
                    f.write('    <route src="%d" dst="%d" next="%d"/>\n' % (i, j, 4*i+1))
            f.write('\n')
        for i in range(num_dimm):
            f.write('    <cpuroute dst="%d" next="%d"/>\n' % (i, 4*i))
        f.write('  </memroutes>\n')

        f.write('</memtopology>\n')


if __name__ == '__main__':
    main()