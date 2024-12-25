#!/bin/bash

algorithms=("ddpg" "td3" "sac" "a2c" "ppo" "tqc" "trpo" "ars" "rppo")
config_files=("V2GProfitMax" "V2GProfitPlusLoads") # 替换为实际配置文件名

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