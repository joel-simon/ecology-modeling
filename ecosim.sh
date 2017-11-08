#!/usr/bin/env python
from __future__ import print_function, division
import time
import os, shutil
from os.path import join as pjoin
from collections import Counter
import pickle
import argparse

# 2/3 compatability
try:
    import ConfigParser as configparser
except ImportError:
    import configparser

from ecosim.draw import PygameDraw
from ecosim.simulation import Simulation
from ecosim.individual import Individual
from ecosim.history import History, HistoryFull

################################################################################
# Util functions.

def draw_sim(view, sim):
    view.start_draw()
    for ind in sim.individuals.values():
        view.draw_circle((ind.x, ind.y), ind.radius, ind.genome.color, 0)
        # if ind.x - ind.radius < 0:
        #     view.draw_circle((ind.x+sim.width, ind.y), ind.radius, ind.genome.color, 0)

        # elif ind.x + ind.radius >= sim.width:
        #     view.draw_circle((ind.x-sim.width, ind.y), ind.radius, ind.genome.color, 0)

        # elif ind.y - ind.radius < 0:
        #     view.draw_circle((ind.x, ind.y+sim.width), ind.radius, ind.genome.color, 0)

        # elif ind.y + ind.radius >= sim.height:
        #     view.draw_circle((ind.x, ind.y-sim.width), ind.radius, ind.genome.color, 0)

    n_genomes = len(set(ind.genome.id for ind in sim.individuals.values()))

    # view.draw_text((10, 10), ('n_individuals: %i' % len(sim.individuals)), font=18)
    # view.draw_text((10, 30), 'n_species: %i' % n_genomes)
    view.end_draw()

def prepare_dir(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)

################################################################################

def main(config, timesteps, out_dir, log_interval, img_interval, archive_interval, map):
    if args.out is not None:
        assert not os.path.exists(out_dir)

    assert timesteps > 0

    logfull = False

    start = time.time()
    config['map'] = map
    sim = Simulation(**config)

    if logfull:
        log = HistoryFull()
    else:
        log = History()

    if args.out is not None:
        scale = 3
        view = PygameDraw(config['width']*scale, config['height']*scale, scale=scale)
        prepare_dir(pjoin(out_dir, 'imgs'))
        draw_sim(view, sim)

    for i in range(timesteps):
        sim.step()

        if args.out is not None:
            log.addGeneration(sim)

        if log_interval != -1 and i % log_interval  == 0:
            print('Step:', i)
            genomes = set(ind.genome.id for ind in sim.individuals.values())
            print('n_individuals:', len(sim.individuals))
            print('n_genomes:', len(genomes))
            print()

        if args.out is not None:
            if img_interval != -1 and i % img_interval == 0:
                if args.out is not None:
                    draw_sim(view, sim)
                    view.save(pjoin(out_dir, 'imgs/%06d.jpg'%i))

            if archive_interval != -1 and i % archive_interval == 0 and i > 0:
                log.save(pjoin(out_dir, 'archive_%i'%i), config)

    print('Done in:', time.time() - start)

    if args.out is not None:
        log.save(pjoin(out_dir, 'archive_final'), config)

        with open(pjoin(out_dir, 'config.txt'), 'w+') as fconfig:
            for key, value in config.items():
                fconfig.write(key+'\t'+str(value)+'\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("steps", help="Number of steps to run for.", type=int)
    parser.add_argument("config", help="Path to config file.")
    parser.add_argument("--out", help="Path for output files.")
    parser.add_argument('--map', help='path to a binary array in .npy format. Must have dimensions of map.')
    parser.add_argument('--log_interval', type=int, default=10, help='number of iterations between print, default=10')
    parser.add_argument('--archive_interval', type=int, default=1000, help='number of iterations between each archive, default=1000')
    parser.add_argument('--img_interval', type=int, default=100, help='number of iterations between each image, default=100')
    args = parser.parse_args()

    config = configparser.ConfigParser()
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
        'growth_cost_multiplier': config.getfloat('simulation', 'growth_cost_multiplier'),
        'bias_power': config.getfloat('simulation', 'bias_power'),
        'n_attributes': config.getint('genome', 'n_attributes'),
        'seed_size_range': (config.getfloat('genome', 'min_seed_size'),
                            config.getfloat('genome', 'max_seed_size')),
    }
    main(run_config, args.steps, args.out, args.log_interval, args.img_interval,
                                                args.archive_interval, args.map)
