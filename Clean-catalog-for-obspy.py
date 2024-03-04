inp_name = 'BIN_2004_2024-2.out'
out_name = 'BIN_2004_2024-Cleaned.out'

with open(inp_name, 'r') as inp_file:
    with open(out_name, 'w') as out_file:
        i = 1
        for line in inp_file:
            
            if line == '\n':
                continue
            '''
            skip = False
            for char in ['BIN', 'IAML', 'ACTION', 'GAP']:
                if char in line:
                    skip = True
            if skip:
                continue
            if '-' not in line:
                continue
            '''
            if 'FOCMEC' in line:
                continue
            #if ' BIN ' in line:
            #    i += 1
            #if i == 205:
            #    break
            out_file.write(line)#[18:29]+'\n')
            
                
            
