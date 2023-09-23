import argparse
import logging
import os
import random
import time

import gym
import numpy as np
from gym_env import ev_city

import torch
import pickle

from utils.arg_parser import arg_parser

from ddpg import DDPG
from utils.noise import OrnsteinUhlenbeckActionNoise

# if gpu is to be used
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

if __name__ == "__main__":

    args = arg_parser()

    # Define the directory where to save and load models
    checkpoint_dir = args.save_dir + args.env
    # name the run accordign to time
    if args.name:
        run_name = args.name
    else:
        run_name = 'r_' + time.strftime("%Y%m%d-%H%M%S")

    log_to_wandb = args.wandb
    verbose = False
    n_transformers = args.transformers
    number_of_charging_stations = args.cs
    steps = args.steps  # 288 steps = 1 day with 5 minutes per step
    timescale = args.timescale  # (5 minutes per step)
    score_threshold = args.score_threshold  # 1
    static_prices = args.static_prices
    static_ev_spawn_rate = args.static_ev_spawn_rate
    n_trajectories = args.n_trajectories

    gym.register(id='evcity-v0', entry_point='gym_env.ev_city:EVCity')

    env = ev_city.EVCity(cs=number_of_charging_stations,
                         number_of_ports_per_cs=2,
                         number_of_transformers=n_transformers,
                         static_ev_spawn_rate=True,
                         load_ev_from_replay=False,
                         load_prices_from_replay=False,
                         static_prices=static_prices,
                         load_from_replay_path=None,
                         empty_ports_at_end_of_simulation=True,
                         generate_rnd_game=True,
                         simulation_length=steps,
                         timescale=timescale,
                         score_threshold=score_threshold,
                         save_plots=False,
                         save_replay=False,
                         verbose=verbose,)

    trajectories = []

    # Set random seed for all used libraries where possible
    # env.seed(args.seed)
    # torch.manual_seed(args.seed)
    # np.random.seed(args.seed)
    # random.seed(args.seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed(args.seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    # Define and build DDPG agent
    hidden_size = tuple(args.hidden_size)
    agent = DDPG(args.gamma,
                 args.tau,
                 hidden_size,
                 env.observation_space.shape[0],
                 env.action_space,
                 checkpoint_dir=checkpoint_dir
                 )

    if static_prices:
        prices = "static"
    else:
        prices = "dynamic"

    if static_ev_spawn_rate:
        ev_spawn_rate = "static"
    else:
        ev_spawn_rate = "dynamic"

    if args.opt_traj:
        trajecotries_type = "optimal"
    else:
        trajecotries_type = "random"


    file_name = f"{trajecotries_type}_{number_of_charging_stations}_cs_{n_transformers}_tr_{prices}_prices_{ev_spawn_rate}_ev_spawn_rate_{steps}_steps_{timescale}_timescale_{score_threshold}_score_threshold_{n_trajectories}_trajectories.pkl"
    save_folder_path = f"./trajectories/"
    if not os.path.exists(save_folder_path):
        os.makedirs(save_folder_path)

    # Initialize OU-Noise
    nb_actions = env.action_space.shape[-1]
    ou_noise = OrnsteinUhlenbeckActionNoise(mu=np.zeros(nb_actions),
                                            sigma=float(args.noise_stddev) * np.ones(nb_actions))

    # Define counters and other variables
    start_step = 0
    # timestep = start_step
    if args.load_model:
        # Load agent if necessary
        start_step, memory = agent.load_checkpoint(
            checkpoint_path=args.load_model)

    timestep = start_step // 10000 + 1
    epoch = 0

    for i in range(n_trajectories):

        trajectory_i = {"observations": [],
                        "actions": [],
                        "rewards": [],
                        "dones": [] }

        ou_noise.reset()

        epoch_return = 0

        print(f'Trajectory: {i}')
        state = torch.Tensor([env.reset()]).to(device)       

        state = torch.Tensor([env.reset()]).to(device)
        test_reward = 0
        while True:

            action = agent.calc_action(state, ou_noise)

            next_state, reward, done, stats = env.step(
                action.cpu().numpy()[0])
            test_reward += reward

            trajectory_i["observations"].append(state.cpu().numpy()[0])
            trajectory_i["actions"].append(action.cpu().numpy()[0])
            trajectory_i["rewards"].append(reward)
            trajectory_i["dones"].append(done)

            next_state = torch.Tensor([next_state]).to(device)
            state = next_state

            if done:
                break
        
        trajectory_i["observations"] = np.array(trajectory_i["observations"])
        trajectory_i["actions"] = np.array(trajectory_i["actions"])
        trajectory_i["rewards"] = np.array(trajectory_i["rewards"])
        trajectory_i["dones"] = np.array(trajectory_i["dones"])

        trajectories.append(trajectory_i)

    env.close()
    print(trajectories[:2])

    print(f'Saving trajectories to {save_folder_path+file_name}')
    f = open(save_folder_path+file_name, 'wb')
    # source, destination
    pickle.dump(trajectories, f)
    f.close()
