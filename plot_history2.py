from __future__ import print_function, division
import sys
import pickle
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

from os.path import join as pjoin

n = 50 # how many genomes to color individually

history, genomes = pickle.load(open(sys.argv[1], 'rb'))
print('Loaded History.')

n_gens = len(history)
n_steps = 1000
step_size = max(1, int(n_gens/n_steps))

print('step_size:', step_size)

genome_colors = {}
for gid, genome in genomes.items():
	r, g, b = genome.color
	genome_colors[gid] = (float(r)/255, float(g)/255, float(b)/255)

def n_most_common_genomes():
	max_total_area = Counter()
	for g in history[::step_size]:
		for gid, count, area in g:
			max_total_area[gid] = max(area*count, max_total_area.get(gid, 0))	
	top_genomes = zip(*max_total_area.most_common(n))[0]
	return top_genomes


# Get genomes we will plot seperately.
top_genomes = n_most_common_genomes()

# Map these from genome_id to index.
top_genome_ordering = dict(zip(top_genomes, range(len(top_genomes))))

top_genome_colors = [genome_colors[gid] for gid in top_genomes]
top_genome_colors.append((.3, .3, .3))

# Create array to store plotting.
X_area = np.zeros((n+1, n_steps))
X_count = np.zeros((n+1, n_steps))

for i in range(n_steps):
	g = i * step_size
	for genome_id, count, area in history[g]:
		if genome_id in top_genome_ordering:
			X_area[top_genome_ordering[genome_id], i] = area*count
			X_count[top_genome_ordering[genome_id], i] = count
		else:
			X_area[-1, i] = area*count
			X_count[-1, i] = count

for i in range(n_steps):
	X_area[:, i] /= X_area[:,i].sum()

print('Structured data for plotting.')

x = np.arange(n_steps) * step_size

f, axarr = plt.subplots(2, sharex=True, figsize=(20, 12))
axarr[0].stackplot(x, X_area, colors=top_genome_colors)
axarr[0].set_title('Species Total Area')
axarr[0].set_xlabel('Generations')
axarr[0].set_ylabel('Total Area of Species')
axarr[0].set_ylim([0, 1])

axarr[1].stackplot(x, X_count, colors=top_genome_colors)
axarr[1].set_title('Species Abundance')
axarr[1].set_xlabel('Generations')
axarr[1].set_ylabel('Abundance of Species')

plt.show()