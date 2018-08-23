#!/usr/bin/env python
from __future__ import print_function, division
from os import path
import argparse

# 2/3 compatability
try:
    import ConfigParser as configparser
except ImportError:
    import configparser

from ecosim.main import main

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("steps", help="Number of steps to run for.", type=int)
    parser.add_argument("out", help="Path for output files.")
    parser.add_argument("config", help="Path to config file.")

    # parser.add_argument('--bias_map', help='path to a binary array in .npy format.')
    parser.add_argument('--draw_scale', type=float, default=3.0,
                        help='world to pixel scale, default=3')
    parser.add_argument('--log_interval', type=int, default=100,
                        help='number of iterations between print, default=10')
    parser.add_argument('--archive_interval', type=int, default=10000,
                        help='number of iterations between each archive, default=1000')
    parser.add_argument('--img_interval', type=int, default=100,
                        help='number of iterations between each image, default=100')
    args = parser.parse_args()

    config = configparser.ConfigParser(allow_no_value=True)

    if not path.exists(args.config):
        raise ValueError('That is not a valid to a config file:'+args.config)

    config.read(args.config)

    run_config = {
        'width': config.getint('simulation', 'width'),
        'height': config.getint('simulation', 'height'),
        'n_start': config.getint('simulation', 'n_start'),
        'p_death': config.getfloat('simulation', 'p_death'),
        'n_randseed': config.getint('simulation', 'n_randseed'),
        # 'bias_areas':  parse_bias_areas(config.get('simulation', 'bias_areas')),
        'bias_map': config.get('simulation', 'bias_map'),
        'p_disturbance': config.getfloat('simulation', 'p_disturbance'),
        'disturbance_power': config.getfloat('simulation', 'disturbance_power'),
        'seed_cost_multiplier': config.getfloat('simulation', 'seed_cost_multiplier'),
        'growth_cost_multiplier': config.getfloat('simulation', 'growth_cost_multiplier'),
        'n_attributes': config.getint('genome', 'n_attributes'),
        'seed_size_range': (config.getfloat('genome', 'min_seed_size'),
                            config.getfloat('genome', 'max_seed_size')),
    }
    main(run_config, args.steps, args.out, args.log_interval, args.img_interval,\
         args.draw_scale, args.archive_interval)
