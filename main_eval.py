from EVsSimulator import ev_city
from baselines.gurobi_models import ev_city_model, ev_city_power_tracker_model, ev_city_profit_maximization

import numpy as np
import matplotlib.pyplot as plt

# main funtion for testing
if __name__ == "__main__":

    verbose = False
    save_plots = True
    replay_path = None
    replay_path = "./replay/replay_ev_city_30_2024-01-08_15-10-38-827430_replay.pkl"

    env = ev_city.EVCity(config_file = "config_files/config.yaml",                         
                         load_from_replay_path=replay_path,                         
                         generate_rnd_game=True,                                                  
                         verbose=verbose,
                         render_mode=True,
                         )

    new_replay_path = f"replay/replay_{env.sim_name}.pkl"    
    
    state = env.reset()

    rewards = []    

    for i in range(env.simulation_length):        
        # all ports are charging instantly
        actions = np.ones(env.number_of_ports)
        # actions = np.random.rand(env.number_of_ports) * -2 + 1
        if verbose:
            print(f'Actions: {actions}')

        new_state, reward, done, _ = env.step(
            actions, visualize=True)  # takes action
        rewards.append(reward)

        if verbose:
            print(f'Reward: {reward} \t Done: {done}')

        # input("Press Enter to continue...")        
        if done:
            print(f'End of simulation at step {env.current_step}')
            break

    # env.plot()
    
    # exit()
    # Solve optimally
    #Power tracker optimizer
    math_model = ev_city_power_tracker_model.EV_City_Math_Model(sim_file_path=new_replay_path)
    #Profit maximization optimizer
    # math_model = ev_city_profit_maximization.EV_City_Math_Model(sim_file_path=new_replay_path)
    # Old optimizer (V2G), probably not compatible now
    # math_model = ev_city_model.EV_City_Math_Model(sim_file_path=f"replay/replay_ev_city_100_2023-07-26_14-19.pkl")
    opt_actions = math_model.get_actions()
    print(f'Optimal actions: {opt_actions.shape}')

    # Simulate in the gym environment and get the rewards

    env = ev_city.EVCity(config_file = "config_files/config.yaml",                         
                         load_from_replay_path=new_replay_path,                                                                                                
                         verbose=verbose,
                         render_mode=True,
                         )
    state = env.reset()    
    rewards_opt = []

    for i in range(env.simulation_length):        
        # all ports are charging instantly
        # print(f'Optimal actions: {opt_actions[:,:,i]}')
        # print(f'Optimal actions: {opt_actions[:,:,i].T.reshape(-1)}')
        actions = opt_actions[:,:,i].T.reshape(-1)        
        if verbose:
            print(f' OptimalActions: {actions}')

        new_state, reward, done, _ = env.step(
            actions, visualize=True)  # takes action
        rewards_opt.append(reward)

        if verbose:
            print(f'Reward: {reward} \t Done: {done}')

        if done:
            break    

    if save_plots:
        plt.figure(figsize=(10, 10))
        # Plot the commulative reward in subplot 1
        plt.subplot(2, 1, 1)
        plt.plot(np.cumsum(rewards))
        plt.plot(np.cumsum(rewards_opt))
        plt.legend(['Charge Immediately', 'Optimal'])
        plt.ylabel('Cumulative reward')
        # plt.xticks(np.arange(0, steps, 1))
        plt.title('Cumulative reward')

        # Plot the reward per step in subplot 2
        plt.subplot(2, 1, 2)
        plt.plot(rewards)
        plt.plot(rewards_opt)
        plt.legend(['Charge Immediately', 'Optimal'])
        plt.xlabel('Time step')
        plt.ylabel('Reward')
        # plt.xticks(np.arange(0, steps, 1))
        plt.title('Reward per time step')

        plt.tight_layout()    
        plt.savefig(f'plots/{env.sim_name}/RewardsComparison.html',
                    format='svg', dpi=600, bbox_inches='tight')
        
