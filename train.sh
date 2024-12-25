#!/bin/bash
#SBATCH --account=def-bboulet     # Set account
#SBATCH --gpus-per-node=1         # Number of GPU(s) per node
#SBATCH --output=log_job/%j.out   # Log save location; file name is the job number
#SBATCH --cpus-per-task=4        # CPU cores/threads
#SBATCH --mem=80G                 # Memory per node
#SBATCH --time=2-00:00            # Set the maximum time for the job

# Load required modules
module load StdEnv/2023 gcc/12.3 cuda/12.2 arrow/17.0 rust/1.70.0 python/3.10.13

# Activate virtual environment
source venv/bin/activate

# Ensure required arguments are passed
if [ $# -lt 2 ]; then
    echo "Usage: $0 <algorithm> <config_file>"
    exit 1
fi

# Read arguments
alg="$1"
config_file="$2"

echo "Debug: Algorithm = $alg"
echo "Debug: Config file = $config_file"

# Construct the name parameter
name="${alg}_${config_file}_experiment"

# Run the Python script with the provided parameters
python train_stable_baselines.py --alg "$alg" --device cuda:0 --name "$name" --config_file "$config_file"

# Print a completion message
echo "Running with algorithm: $alg and config file: $config"
echo "Job completed."
