from __future__ import print_function, division
import time
import os, shutil
from os.path import join as pjoin
from collections import Counter
import pickle
import argparse
import ConfigParser as configparse
from draw import PygameDraw

from simulation import Simulation
from individual import Individual
from reporter import Reporter

################################################################################
# Util functions.

def draw_sim(view, sim):
    view.start_draw()
    for ind in sim.individuals.values():
        view.draw_circle((ind.x, ind.y), ind.radius, ind.genome.color, 0)

    n_genomes = len(set(ind.genome.id for ind in sim.individuals.values()))
    
    view.draw_text((10, 10), ('n_individuals: %i' % len(sim.individuals)), font=18)
    view.draw_text((10, 30), 'n_species: %i' % n_genomes)
    view.end_draw()

def prepare_dir(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)

################################################################################

def main(config, timesteps, out_dir):
    assert not os.path.exists(out_dir)
    assert timesteps > 0

    start = time.time() 
    sim = Simulation(**config)
    log = Reporter()
    view = PygameDraw(config['width']*5, config['height']*5, scale=5)
    
    prepare_dir(pjoin(out_dir, 'imgs'))
    draw_sim(view, sim)

    for i in range(timesteps):
        sim.step()
        log.addGeneration(sim)

        if i % 100  == 0:
            print('Step:', i)
            genomes = set(ind.genome.id for ind in sim.individuals.values())
            print('n_individuals:', len(sim.individuals))
            print('n_genomes:', len(genomes))
            print()

        draw_sim(view, sim)
        view.save(pjoin(out_dir, 'imgs/%06d.jpg'%i))
    
    print('Done in:', time.time() - start)

    log.save(out_dir)   
    with open(pjoin(out_dir, 'config.txt'), 'wb+') as fconfig:
        for key, value in config.items():
            fconfig.write(key+'\t'+str(value)+'\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("steps", help="Number of steps to run for.", type=int)
    parser.add_argument("config", help="Path to config file.")
    parser.add_argument("out", help="Path for output files.")
    args = parser.parse_args()

    config = configparse.ConfigParser()
    config.read(args.config)

    run_config = {
        'width': config.getint('simulation', 'width'),
        'height': config.getint('simulation', 'height'),
        'n_start': config.getint('simulation', 'n_start'),
        'p_death': config.getfloat('simulation', 'p_death'),
        'n_randseed': config.getint('simulation', 'n_randseed'),
        'p_disturbance': config.getfloat('simulation', 'p_disturbance'),
        'disturbance_power': config.getfloat('simulation', 'disturbance_power'),
        'seed_cost_multiplier': config.getfloat('simulation', 'seed_cost_multiplier'),
        'bias_power': config.getfloat('simulation', 'bias_power'),
        'n_attributes': config.getint('genome', 'n_attributes'),
        'seed_size_range': (config.getfloat('genome', 'min_seed_size'),
                            config.getfloat('genome', 'max_seed_size')),
    }

    main(run_config, args.steps, args.out)
