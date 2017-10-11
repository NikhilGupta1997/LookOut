f = open('Files/log.txt')

for line in f:
    tokens = line.strip().split('\t')
    num_outlier = int(tokens[0].split(' ')[1])
    budget = int(tokens[1].split(' ')[1])
    algo = tokens[2].split(' ')[1]
    time = float(tokens[3].split(' ')[3])
    coverage = float(tokens[4].replace('%', '').split(' '))
    print tokens
    break
