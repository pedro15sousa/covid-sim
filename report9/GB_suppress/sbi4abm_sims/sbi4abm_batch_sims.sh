#!/bin/bash

# Determine the directory paths based on the script location
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
covid_sim_dir="$(cd "$script_dir/../../.." && pwd)"
report9_dir="$covid_sim_dir/report9"
gb_suppress_dir="$report9_dir/GB_suppress"
output_dir="$gb_suppress_dir/output"
src_dir="$covid_sim_dir/src"
covidsim="$covid_sim_dir/build/src/CovidSim"

# Path to the pickle file containing the parameters
PICKLE_FILE="$script_dir/prior_thetas.pkl"

# Extract parameters using the Python script
params=$(python $script_dir/extract_params.py "$PICKLE_FILE")

# Debugging: Print the extracted parameters
echo "Extracted parameters:"
echo "$params"

# Command template
exe_path="$covidsim"
pp_file="$gb_suppress_dir/preGB_R0=2.0.txt"
p_file="$gb_suppress_dir/p_PC_CI_HQ_SD.txt"
bin_file="$report9_dir/population/GB_pop2018.bin"
network_bin="$report9_dir/population/NetworkGB_54T.bin"
output_file_name="PC_CI_HQ_SD_400_300_R0=2.6"
nr_value=1
# c_value=250
c_value=54
clp1=400
clp2=1000
clp3=1000
clp4=1000
clp5=300
R=2.6
population_ids="98798150 729101 17389101 4797132"

counter=0

# Ensure the main output directory exists
mkdir -p "$output_dir"

# Create a batch job file
batch_job_file="$script_dir/batch_job.sh"
echo "#!/bin/bash" > "$batch_job_file"
echo "#SBATCH --job-name=covid_sim_job" >> "$batch_job_file"
echo "#SBATCH --output=$output_dir/covid_sim_job_%A_%a.out" >> "$batch_job_file"
echo "#SBATCH --error=$output_dir/covid_sim_job_%A_%a.err" >> "$batch_job_file"
echo "#SBATCH --array=1-$(wc -l < <(echo "$params"))" >> "$batch_job_file"
echo "#SBATCH --ntasks=1" >> "$batch_job_file"
echo "#SBATCH --cpus-per-task=54" >> "$batch_job_file"
echo "#SBATCH --mem=4G" >> "$batch_job_file"
echo "#SBATCH --time=01:00:00" >> "$batch_job_file"
echo "" >> "$batch_job_file"

# Export necessary environment variables
echo "export OMP_NUM_THREADS=54" >> "$batch_job_file"
echo "export MKL_NUM_THREADS=54" >> "$batch_job_file"

# Generate commands and append to the batch job file
while IFS= read -r line; do
    # Debugging: Print the current line being processed
    echo "Processing line: $line"
    
    # Convert tensor values to plain numbers using sed
    line=$(echo "$line" | sed -e 's/tensor(\([^)]*\))/\1/g')
    
    IFS=' ' read -r relative_spatial_contact_rate_given_social_distancing prop_pop_vaccinated household_quarantine_compliance delay_to_start_case_isolation <<< "$line"
    rs=$(echo ${R} | awk '{print $1/2}')
    output_prefix="PC_CI_HQ_SD_${relative_spatial_contact_rate_given_social_distancing}_${prop_pop_vaccinated}_${household_quarantine_compliance}_${delay_to_start_case_isolation}"
    output_path="${output_dir}/${output_prefix}/${output_file_name}"

    # Create the specific output directory
    mkdir -p "${output_dir}/${output_prefix}"

    cmd="${exe_path} /NR:${nr_value} /c:${c_value} /PP:${pp_file} /P:${p_file} /CLP1:${clp1} /CLP2:${clp2} /CLP3:${clp3} /CLP4:${clp4} /CLP5:${clp5} /CLP6:${relative_spatial_contact_rate_given_social_distancing} /CLP7:${delay_to_start_case_isolation} /CLP8:${prop_pop_vaccinated} /CLP9:${household_quarantine_compliance} /O:${output_path} /D:${bin_file} /L:${network_bin} /R:${rs} ${population_ids}"
    echo "$cmd"
    echo "$cmd" >> "$batch_job_file"
    counter=$((counter + 1))
done < <(echo "$params")

echo "Total number of commands echoed: $counter"

# Make the batch job file executable
chmod +x "$batch_job_file"

# Submit the batch job to Slurm
# sbatch "$batch_job_file"
