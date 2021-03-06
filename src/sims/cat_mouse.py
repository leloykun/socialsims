import os
import time
import multiprocessing as mp

from .utils import to_ordinal, process

from ..agent import Agent
from ..world import World
from ..qlearn import QLearn
from ..cell import CasualCell
from ..agent import DumbPrey as Mouse
from ..environment import Environment

sim_name = 'cat_mouse'
output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname( __file__ ))),
                          'data/raw/{}/'.format(sim_name))

max_visual_depth = 4


class Cat(Agent):
    colour = 'red'
    visual_depth = 2

    def __init__(self):
        self.ai = QLearn(actions=list(range(8)))
        self.ai.agent = self

        self.eaten = 0
        self.fed = 0

        self.last_action = None
        self.last_state = None

    def update(self):
        state = self.calc_state()
        reward = -1

        if self.cell == self.world.mouse.cell:
            self.fed += 1
            reward = 50
            self.world.mouse.cell = self.env.get_random_avail_cell()

        if self.last_state is not None:
            self.ai.learn(self.last_state,
                          self.last_action,
                          reward,
                          state)

        state = self.calc_state()

        action = self.ai.choose_action(state)
        self.last_state = state
        self.last_action = action

        self.go_in_direction(action)

    # TODO: consider wrapping here
    def calc_state(self):
        mouse = self.world.mouse
        if abs(self.cell.x - mouse.cell.x) <= self.visual_depth and \
           abs(self.cell.y - mouse.cell.y) <= self.visual_depth:
            return ((self.cell.x - mouse.cell.x),
                    (self.cell.y - mouse.cell.y))
        else:
            # default
            return (100, 100)

    def going_to_obstacle(self, action):
        cell = self.world.get_point_in_direction(self.cell.x,
                                                 self.cell.y,
                                                 action)
        return self.world.get_cell(cell[0], cell[1]).wall

    def get_data(self):
        pass


def worker(params):
    alpha, gamma, trials, steps = params

    env = Environment(World(os.path.join(os.path.dirname(os.path.dirname( __file__ )),
                                         'worlds/box10x10.txt'),
                            CasualCell))

    cat = Cat()
    env.add_agent(cat)
    cat.ai.alpha = alpha / 10
    cat.ai.gamma = gamma / 10
    cat.ai.temp = 0.4
    env.world.cat = cat

    mouse = Mouse()
    env.add_agent(mouse)
    mouse.move = True
    env.world.mouse = mouse

    # env.show()

    env.world.fed = 0
    prev_fed = 0
    result = [alpha, gamma]
    while env.world.fed < trials:
        env.update(0, env.world.cat.fed)

        if env.world.fed is not prev_fed and (
                env.world.fed + 1) % steps == 0:
            result.append(env.world.age)
        prev_fed = env.world.fed

    return result


def run(params, grid_params=False, test=False, to_save=True):
    runs, trials, steps = process(params)

    if test:
        worker((5, 5, trials, steps))
        return

    for depth in range(1, max_visual_depth + 1):
        Cat.visual_depth = depth
        print("   visual depth:", Cat.visual_depth)

        for run in range(1, runs + 1):
            run_start = time.time()

            params = []
            if grid_params:
                for alpha in range(11):
                    for gamma in range(11):
                        params.append((alpha, gamma, trials, steps))
            else:
                params = [(5, 5, trials, steps)]

            with mp.Pool(mp.cpu_count()) as pool:
                results = pool.map(worker, params)

            if to_save:
                with open(os.path.join(output_dir, "depth{}/run{}.txt".format(depth, run)), 'w') as f:
                    f.write('\n'.join(' '.join(map(str, result)) 
                                      for result in results))

            print("      ", end="")
            print(to_ordinal(run), "runtime:", time.time() - run_start, "secs")
