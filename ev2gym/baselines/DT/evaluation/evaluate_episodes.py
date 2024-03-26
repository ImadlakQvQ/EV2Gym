import numpy as np
import torch
from ev2gym.models import ev2gym_env
import os
from icecream import ic
import tqdm

def evaluate_episode(
        env,
        state_dim,
        act_dim,
        model,
        max_ep_len=1000,
        device='cuda',
        target_return=None,
        mode='normal',
        state_mean=0.,
        state_std=1.,
):

    model.eval()
    model.to(device=device)

    state_mean = torch.from_numpy(state_mean).to(device=device)
    state_std = torch.from_numpy(state_std).to(device=device)

    state = env.reset()

    # we keep all the histories on the device
    # note that the latest action and reward will be "padding"
    states = torch.from_numpy(state).reshape(1, state_dim).to(device=device, dtype=torch.float32)
    actions = torch.zeros((0, act_dim), device=device, dtype=torch.float32)
    rewards = torch.zeros(0, device=device, dtype=torch.float32)
    target_return = torch.tensor(target_return, device=device, dtype=torch.float32)
    sim_states = []

    episode_return, episode_length = 0, 0
    for t in range(max_ep_len):

        # add padding
        actions = torch.cat([actions, torch.zeros((1, act_dim), device=device)], dim=0)
        rewards = torch.cat([rewards, torch.zeros(1, device=device)])

        action = model.get_action(
            (states.to(dtype=torch.float32) - state_mean) / state_std,
            actions.to(dtype=torch.float32),
            rewards.to(dtype=torch.float32),
            target_return=target_return,
        )
        actions[-1] = action
        action = action.detach().cpu().numpy()

        state, reward, done, _ = env.step(action)

        cur_state = torch.from_numpy(state).to(device=device).reshape(1, state_dim)
        states = torch.cat([states, cur_state], dim=0)
        rewards[-1] = reward

        episode_return += reward
        episode_length += 1

        if done:
            break

    return episode_return, episode_length


def evaluate_episode_rtg(
        exp_prefix,
        state_dim,
        act_dim,
        model,
        max_ep_len=1000,
        scale=1000.,
        state_mean=0.,
        state_std=1.,
        device='cuda',
        target_return=None,
        mode='normal',
        n_test_episodes=10,
        config_file="config_files/config.yaml",
    ):

    model.eval()
    model.to(device=device)

    state_mean = torch.from_numpy(state_mean).to(device=device)
    state_std = torch.from_numpy(state_std).to(device=device)

    test_rewards = []
    test_stats = []
    highest_opt_ratio = np.NINF

    # number_of_charging_stations = 10
    # n_transformers = 1    

    # eval_replay_path = "./replay/" + \
    #     f'{number_of_charging_stations}cs_{n_transformers}tr/'
    # eval_replay_files = [f for f in os.listdir(
    #     eval_replay_path) if os.path.isfile(os.path.join(eval_replay_path, f))]
    
    global_target_return = 0
    env = ev2gym_env.EV2Gym(config_file=config_file,
                    # load_from_replay_path=eval_replay_path +
                    # eval_replay_files[test_cycle],
                    save_replay=False,
                    generate_rnd_game=True,
                    # extra_sim_name=exp_prefix
                    )
    
    #use tqdm with a fancy bar
    for test_cycle in tqdm.tqdm(range(n_test_episodes)):    

        # if test_cycle == 0:                        
        #     env.set_save_plots(True)          
        # else:
        #     env.set_save_plots(False)
            
        state, _ = env.reset()

        # we keep all the histories on the device
        # note that the latest action and reward will be "padding"
        states = torch.from_numpy(state).reshape(1, state_dim).to(device=device, dtype=torch.float32)
        actions = torch.zeros((0, act_dim), device=device, dtype=torch.float32)
        rewards = torch.zeros(0, device=device, dtype=torch.float32)        

        ep_return = global_target_return        
        target_return = torch.tensor(ep_return, device=device, dtype=torch.float32).reshape(1, 1)
        timesteps = torch.tensor(0, device=device, dtype=torch.long).reshape(1, 1)

        sim_states = []

        episode_return, episode_length = 0, 0
        for t in range(max_ep_len):

            # add padding
            actions = torch.cat([actions, torch.zeros((1, act_dim), device=device)], dim=0)
            rewards = torch.cat([rewards, torch.zeros(1, device=device)])

            action = model.get_action(
                (states.to(dtype=torch.float32) - state_mean) / state_std,
                actions.to(dtype=torch.float32),
                rewards.to(dtype=torch.float32),
                target_return.to(dtype=torch.float32),
                timesteps.to(dtype=torch.long),
            )
            actions[-1] = action
            action = action.detach().cpu().numpy()
            
            state, reward, done, truncated, stats = env.step(action)

            cur_state = torch.from_numpy(state).to(device=device).reshape(1, state_dim)
            states = torch.cat([states, cur_state], dim=0)
            rewards[-1] = reward

            if mode != 'delayed':
                pred_return = target_return[0,-1] - (reward/scale)
            else:
                pred_return = target_return[0,-1]
            target_return = torch.cat(
                [target_return, pred_return.reshape(1, 1)], dim=1)
            timesteps = torch.cat(
                [timesteps,
                torch.ones((1, 1), device=device, dtype=torch.long) * (t+1)], dim=1)

            episode_return += reward
            episode_length += 1

            if done:
                test_stats.append(stats)
                test_rewards.append(episode_return)
                break
        
    stats = {}
    for key in test_stats[0].keys():
        stats[key] = np.mean([test_stats[i][key]
                                for i in range(len(test_stats))])
        
    # # get all values of a key in a list
    # opt_tracking_error = [1 - min(1,abs(test_stats[i]['opt_tracking_error'] - test_stats[i]['tracking_error']) /
    #                         (test_stats[i]['tracking_error']+0.000001))
    #                         for i in range(len(test_stats))]                 

    #drop key 'opt_profits' from dict stats
    # print('stats', stats)

    # ic(opt_tracking_error)
    
    # if np.mean(opt_tracking_error) > highest_opt_ratio:
    #     highest_opt_ratio = np.mean(opt_tracking_error)
        # agent.save_checkpoint(timestep, memory, run_name+"_best")
        # time_last_checkpoint = time.time()
        # logger.info('Saved model at {}'.format(time.strftime(
        #     '%a, %d %b %Y %H:%M:%S GMT', time.localtime())))

    # stats['mean_opt_ratio'] = np.mean(opt_tracking_error)
    # stats['std_opt_ratio'] = np.std(opt_tracking_error)
    # stats['highest_opt_ratio'] = highest_opt_ratio
    stats['mean_test_return'] = np.mean(test_rewards)

    return stats #, episode_length