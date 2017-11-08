python -m cProfile -o run.prof ecosim.sh 200 examples/profile.config
snakeviz run.prof
