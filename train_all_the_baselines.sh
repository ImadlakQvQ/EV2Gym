#!/bin/bash

# Define the algorithms you want to run
algorithms=("ddpg" "td3" "sac" "a2c" "ppo" "tqc" "trpo" "ars" "rppo")

# Loop through each algorithm and execute the script
for alg in "${algorithms[@]}"; do
    echo "Running with algorithm: $alg"
    python train_stable_baselines.py --alg $alg --device cuda:0 --name "${alg}_experiment" --config_file "PublicPST"

    # Optional: Check if the previous command succeeded
    if [ $? -ne 0 ]; then
        echo "Error occurred while running $alg. Exiting."
        exit 1
    fi
done

echo "All baselines have been executed."