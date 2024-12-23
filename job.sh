#!/bin/bash
#SBATCH --account=def-bboulet     # set account
#SBATCH --gpus-per-node=1         # Number of GPU(s) per node
#SBATCH --output=log_job/%j.out      # log 保存地址 文件为job number
#SBATCH --cpus-per-task=6         # CPU cores/threads
#SBATCH --mem=80G               # memory per node
#SBATCH --time=1-00:00            # set the time for tasks 

module load StdEnv/2023  gcc/12.3 cuda/12.2 arrow/17.0 rust/1.70.0 python/3.10.13 
cd /project/def-bboulet/imadlak/program/EV2GYM                                   
source ev/bin/activate                                                         

export WANDB_MODE=offline         # set wandb to offline mode

# Define the algorithms and configuration files
algorithms=("ddpg" "td3" "sac" "a2c" "ppo" "tqc" "trpo" "ars" "rppo")
config_files=("PublicPST" "V2GProfitMax" "V2GProfitPlusLoads") # 替换为实际配置文件名

# Loop through each configuration file and algorithm
for config in "${config_files[@]}"; do
    for alg in "${algorithms[@]}"; do
        echo "Running with algorithm: $alg and config file: $config"
        python train_stable_baselines.py --alg $alg --device cuda:0 --name "${alg}_${config}_experiment" --config_file "$config"

        # Check if the previous command succeeded
        if [ $? -ne 0 ]; then
            echo "Error occurred while running $alg with config file $config. Skipping to the next combination."
            continue
        fi
    done
done

echo "All baselines and configurations have been executed."
