import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import fio

cs2610 = [int(x.strip()) for x in fio.ReadFile('../data/CS2610.txt') if len(x.strip()) != 0]
Material = [int(x.strip()) for x in fio.ReadFile('../data/Material.txt') if len(x.strip()) != 0]

import numpy

width1 = numpy.max(cs2610) - numpy.min(cs2610)
width2 = numpy.max(Material) - numpy.min(Material)

width = max(width1, width2)

fig = plt.figure()
#fig = plt.figure(figsize=(12, 5))
fig.subplots_adjust(left=0.2, bottom=0.2, right=0.9)

#plt.title("Length distribution of the responses")

ax = fig.add_subplot(111)
ax.grid(True)

ax.set_xlim([1, 80])
ax.set_ylim([0, 0.14])
ax.hist(cs2610, bins=width/2, normed=True, color='#fec44f', alpha=0.9,label='typing')
#ax.xaxis.set_ticks(numpy.arange(0, 80, 5))
ax.set_ylabel('Probability', fontsize=20)
ax.set_xlabel('# of words', fontsize=20)

plt.tick_params(axis='both', which='major', labelsize=20)

#plt.legend()

#ax = fig.add_subplot(122)
#ax.grid(True)
ax.hist(Material, bins=width, normed=True, color='#7fcdbb', alpha=0.5, label='writing')
#ax.set_xlim([0, 80])
#ax.set_ylim([0, 0.14])
plt.legend(prop={'size':20})


plt.show()

