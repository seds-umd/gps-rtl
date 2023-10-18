infile = "fft4096.v"
outfile = "fft4096_processed.v"

with open(infile, 'r') as f:
    lines = f.readlines()

outlines = []

for line in lines:
    if " reg " in line:
        new_line = line[:-2] + " = 0;\n"
        outlines.append(new_line)
    else:
        outlines.append(line)

with open(outfile, 'w') as f:
    f.writelines(outlines)
