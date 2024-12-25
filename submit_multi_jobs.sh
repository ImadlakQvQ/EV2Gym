#!/bin/bash

# Define algorithms and configuration files
# algorithms=("ddpg" "td3" "sac" "a2c" "ppo" "tqc" "trpo" "ars" "rppo")
algorithms=("trpo" "ars" "rppo")

config_files=("V2GProfitMax")  # Replace with actual configuration file names if needed

# Loop through each configuration file and algorithm
for config in "${config_files[@]}"; do
    for alg in "${algorithms[@]}"; do
        echo "Submitting job for algorithm: $alg with config file: $config"

        # Submit the job and pass parameters to the script
        sbatch train.sh "$alg" "$config"

        # Check if the sbatch command succeeded
        if [ $? -ne 0 ]; then
            echo "Error: Failed to submit job for algorithm: $alg with config file: $config. Skipping..."
            continue
        fi
    done
done

echo "All jobs have been submitted."
