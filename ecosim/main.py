import time
from os import path, makedirs
import shutil

from ecosim.draw import PygameDraw
from ecosim.simulation import Simulation
from ecosim.history import History, HistoryFull

################################################################################
# Util functions.

def draw_sim(view, sim):
    view.start_draw()
    for ind in sim.individuals.values():
        view.draw_circle((ind.x, ind.y), ind.radius, ind.genome.color, 0)

    view.end_draw()

def prepare_dir(dir):
    if path.exists(dir):
        shutil.rmtree(dir)
    makedirs(dir)

################################################################################

def main(config, timesteps, out_dir, log_interval, img_interval, draw_scale, \
         archive_interval):

    if out_dir is not None:
        assert not path.exists(out_dir)

    assert timesteps > 0

    logfull = False

    start = time.time()

    sim = Simulation(config)

    if logfull:
        log = HistoryFull()
    else:
        log = History()

    if out_dir is not None:
        scale = draw_scale
        width = int(config['width']*scale)
        height = int(config['height']*scale)
        view = PygameDraw(width, height, scale=scale)
        prepare_dir(path.join(out_dir, 'imgs'))
        draw_sim(view, sim)

        with open(path.join(out_dir, 'config.txt'), 'w+') as fconfig:
            for key, value in config.items():
                fconfig.write(key+'\t'+str(value)+'\n')

    for i in range(timesteps):
        sim.step()

        if out_dir is not None:
            log.addGeneration(sim)

        if log_interval != -1 and i % log_interval  == 0:
            print('Step:', i)
            genomes = set(ind.genome.id for ind in sim.individuals.values())
            print('n_individuals:', len(sim.individuals))
            print('n_genomes:', len(genomes))
            print()

        if out_dir is not None:
            if img_interval != -1 and i % img_interval == 0:
                if out_dir is not None:
                    draw_sim(view, sim)
                    view.save(path.join(out_dir, 'imgs/%06d.jpg'%i))

            if archive_interval != -1 and i % archive_interval == 0 and i > 0:
                log.save(path.join(out_dir, 'archive_%i'%i), config)

    print('Done in:', time.time() - start)

    if out_dir is not None:
        log.save(path.join(out_dir, 'archive_final'), config)

