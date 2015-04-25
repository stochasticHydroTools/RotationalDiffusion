''' Script to compare MSD calculated using different points 
for different gravities.
'''
import cPickle
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np
import os
import sys
sys.path.append('..')

from config_local import DATA_DIR
import boomerang as bm

def calculate_boomerang_parallel_mobility_coh(n_samples, sample_file):
  ''' 
  Calculate the boomerang parallel mobility by taking GB samples from
  file and averaging.
  '''
  parallel_mobility = 0.
  with open(sample_file, 'r') as f:
    line = f.readline()
    # Skip parameters. 
    while line != 'Location, Orientation:\n':
      line = f.readline()
    for k in range(n_samples):
      sample = bm.load_equilibrium_sample(f)
      coh = bm.calculate_boomerang_coh(sample[0], sample[1])
      mobility = bm.boomerang_mobility_at_arbitrary_point(
        [sample[0]], [sample[1]],
        coh)
      parallel_mobility += mobility[0, 0] + mobility[1, 1]
    
  parallel_mobility /= (2*n_samples)
  return parallel_mobility

def calculate_boomerang_parallel_mobility_tip(n_samples, sample_file):
  ''' 
  Calculate the boomerang parallel mobility by taking GB samples from
  file and averaging.
  '''
  parallel_mobility = 0.
  with open(sample_file, 'r') as f:
    line = f.readline()
    # Skip parameters. 
    while line != 'Location, Orientation:\n':
      line = f.readline()
    for k in range(n_samples):
      sample = bm.load_equilibrium_sample(f)
      tip = bm.get_boomerang_r_vectors(sample[0], sample[1])[0]
      mobility = bm.boomerang_mobility_at_arbitrary_point(
        [sample[0]], [sample[1]],
        tip)
      parallel_mobility += mobility[0, 0] + mobility[1, 1]
    
  parallel_mobility /= (2*n_samples)
  return parallel_mobility


def calculate_boomerang_parallel_mobility_cp(n_samples, sample_file):
  ''' 
  Calculate the boomerang parallel mobility by taking GB samples from
  file and averaging.
  '''
  parallel_mobility = 0.
  with open(sample_file, 'r') as f:
    line = f.readline()
    # Skip parameters. 
    while line != 'Location, Orientation:\n':
      line = f.readline()
    for k in range(n_samples):
      sample = bm.load_equilibrium_sample(f)
      mobility = bm.boomerang_mobility(
        [sample[0]], [sample[1]])
      parallel_mobility += mobility[0, 0] + mobility[1, 1]
    
  parallel_mobility /= (2*n_samples)
  return parallel_mobility

def calculate_boomerang_asymptotic_tip_zz(n_samples, sample_file):
  ''' Calculate asymptotic ZZ MSD '''
  zz_msd = 0.
  with open(sample_file, 'r') as f:
    line = f.readline()
    # Skip parameters. 
    while line != 'Location, Orientation:\n':
      line = f.readline()
    for k in range(n_samples):
      sample = bm.load_equilibrium_sample(f)
      sample_2 = bm.load_equilibrium_sample(f)
      zz_msd += (sample[0][2] - sample_2[0][2])**2
    
  zz_msd /= (n_samples)
  return zz_msd

  

if __name__ == '__main__':
  
  gfactor = 20.0
  scheme = 'RFD'
  dt = 0.01
  N = 500000
  end = 30.0
  runs = 8
  data_name = 'final'
  translation_end = 25.

  colors = ['r', 'g', 'b', 'm']
  symbols = ['s', 'o', 'd', '^', 'v', 'h']
  labels = ['cross point', 'tip', 'CoH']
  
  point_ctr = 0
  for out_name in ['', 'tip', 'CoH']:
    if out_name:
      file_name = 'boomerang-msd-dt-%s-N-%s-end-%s-scheme-%s-g-%s-runs-%s-%s-%s.pkl' % (
        (dt, N, end, scheme, gfactor, runs, data_name, out_name))
    else:
      file_name = 'boomerang-msd-dt-%s-N-%s-end-%s-scheme-%s-g-%s-runs-%s-%s.pkl' % (
        (dt, N, end, scheme, gfactor, runs, data_name))
  
    file_name = os.path.join('.', 'data', file_name)

    with open(file_name, 'rb') as f:
      msd_statistics = cPickle.load(f)
      msd_statistics.print_params()

    # Add xx and yy to get translational data (D parallel).
    for sch in msd_statistics.data:
      for t in msd_statistics.data[scheme]:
        for k in range(len(msd_statistics.data[scheme][dt][1])):
          msd_statistics.data[sch][t][1][k][0][0] = (
            msd_statistics.data[sch][t][1][k][0][0] +
            msd_statistics.data[sch][t][1][k][1][1])
          msd_statistics.data[sch][t][2][k][0][0] = np.sqrt(
            msd_statistics.data[sch][t][2][k][0][0]**2 +
            msd_statistics.data[sch][t][2][k][1][1]**2)

    series_len = len(msd_statistics.data[scheme][dt][1])

    plt.errorbar([msd_statistics.data[scheme][dt][0][k] for k in range(series_len)],
                 [msd_statistics.data[scheme][dt][1][k][0][0] for k in range(series_len)],
                 yerr = 2.*np.array(
                   [msd_statistics.data[scheme][dt][2][k][0][0] for k in range(series_len)]),
                 c=colors[point_ctr],
                 marker=symbols[point_ctr],
                 label=labels[point_ctr] + ' parallel')

    plt.errorbar([msd_statistics.data[scheme][dt][0][k] for k in range(series_len)],
                 [msd_statistics.data[scheme][dt][1][k][2][2] for k in range(series_len)],
                 yerr = 2.*np.array(
                   [msd_statistics.data[scheme][dt][2][k][2][2] for k in range(series_len)]),
                 c=colors[point_ctr],
                 marker=symbols[point_ctr + 3],
                 label=labels[point_ctr] + ' perpendicular')
    point_ctr += 1

  sample_file = os.path.join(DATA_DIR, 'boomerang',
                             'boomerang-samples-g-%s-old.txt' % gfactor)
  mu_coh = calculate_boomerang_parallel_mobility_coh(10000, sample_file)
  mu_tip = calculate_boomerang_parallel_mobility_tip(100, sample_file)
  mu_cp = calculate_boomerang_parallel_mobility_cp(100, sample_file)

  zz_msd = calculate_boomerang_asymptotic_tip_zz(100, sample_file)
  
  print "parallel diffusivity  for g = ", gfactor, " is ", mu_coh*bm.KT

  plt.plot([0., translation_end], [0, 4.*bm.KT*mu_coh*translation_end], 'k-',
           lw=2, label='CoH Theory')
  # plt.plot([0., translation_end], [0, 4.*bm.KT*mu_tip*translation_end], 'k--',
  #          lw=2, label='tip Theory')
  # plt.plot([0., translation_end], [0, 4.*bm.KT*mu_cp*translation_end], 'k:',
  #          lw=2, label='cp Theory')
  plt.legend(loc='best', prop={'size': 10})
  plt.xlim([0., translation_end])
  plt.ylim([0., translation_end])
  plt.savefig(os.path.join('.', 'figures', 
                           'PointMSDComparison-g-%s.pdf' % gfactor))
