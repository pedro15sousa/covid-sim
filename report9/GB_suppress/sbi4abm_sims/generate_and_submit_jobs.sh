#!/bin/bash

# Determine the directory paths based on the script location
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# covid_sim_dir="/home/sj514/projects/covid-sim" 
covid_sim_dir="$(cd "$script_dir/../../.." && pwd)"
report9_dir="$covid_sim_dir/report9"
gb_suppress_dir="$report9_dir/GB_suppress"
output_dir="$gb_suppress_dir/output"
src_dir="$covid_sim_dir/src"
covidsim="$covid_sim_dir/build/src/CovidSim"

# Path to the pickle file containing the parameters
PICKLE_FILE="$script_dir/prior_thetas_100k.pkl"
echo "Pickle file: $PICKLE_FILE"

# Extract parameters using the Python script
params=$(python $script_dir/extract_params.py "$PICKLE_FILE")

# Debugging: Print the extracted parameters
echo "Extracted parameters:"
echo "$params"

# Write parameters to a parameters.txt file
parameters_file="$script_dir/parameters.txt"
echo -n "$params" | sed -e 's/tensor(\([^)]*\))/\1/g' > "$parameters_file"

# Command template
exe_path="$covidsim"
pp_file="$gb_suppress_dir/preGB_R0=2.0.txt"
p_file="$gb_suppress_dir/p_PC_CI_HQ_SD.txt"
bin_file="$report9_dir/population/GB_pop2018.bin"
network_bin="$report9_dir/population/NetworkGB_25T.bin"
output_file_name="PC_CI_HQ_SD_400_300_R0=2.6"
nr_value=1
c_value=25
clp1=400
clp2=1000
clp3=1000
clp4=1000
clp5=300
R=2.6
rs=$(echo ${R} | awk '{print $1/2}')
population_ids="98798150 729101 17389101 4797132"

# Ensure the main output directory exists
# mkdir -p "$output_dir"

create_population_binaries() {
    local R=2.6
    local rs=$(echo $R | awk '{print $1/2}')
    local cmd="'$exe_path' /c:'$c_value' /PP:'$pp_file' /P:$gb_suppress_dir/p_NoInt.txt /CLP1:'$clp1' /CLP2:'$clp2' /O:$output_dir/NoInt_R0=${R} /D:$report9_dir/population/GB_pop2018_nhs.txt /M:'$bin_file' /S:'$network_bin' /R:${rs} 98798150 729101 17389101 4797132"
    echo "Creating location binary file..."
    echo "$cmd"
    eval "$cmd"
}

# Create location binary file
# create_population_binaries

# Create a batch job file
batch_job_file="$script_dir/batch_job.sh"
echo "#!/bin/bash" > "$batch_job_file"
echo "#SBATCH --job-name=covid_sim_job" >> "$batch_job_file"
echo "#SBATCH --output=$output_dir/covid_sim_job_%A_%a.out" >> "$batch_job_file"
echo "#SBATCH --error=$output_dir/covid_sim_job_%A_%a.err" >> "$batch_job_file"
echo "#SBATCH --array=1-$(wc -l < "$parameters_file")" >> "$batch_job_file"
echo "#SBATCH --ntasks=1" >> "$batch_job_file"
echo "#SBATCH --cpus-per-task=25" >> "$batch_job_file"
# echo "#SBATCH --mem=4G" >> "$batch_job_file"
echo "#SBATCH --time=01:00:00" >> "$batch_job_file"
echo "#SBATCH -p cclake" >> "$batch_job_file"
echo "#SBATCH -A MADHAVAPEDDY-SL3-CPU" >> "$batch_job_file"
echo "" >> "$batch_job_file"

# Export necessary environment variables
echo "export OMP_NUM_THREADS=25" >> "$batch_job_file"
echo "export MKL_NUM_THREADS=25" >> "$batch_job_file"

# Add the command to run the specific job
echo 'param_line=$(sed -n "${SLURM_ARRAY_TASK_ID}p" '$parameters_file')' >> "$batch_job_file"
echo 'IFS=" " read -r relative_spatial_contact_rate_given_social_distancing delay_to_start_case_isolation prop_pop_vaccinated household_quarantine_compliance <<< "$param_line"' >> "$batch_job_file"
echo 'output_prefix="PC_CI_HQ_SD_${relative_spatial_contact_rate_given_social_distancing}_${delay_to_start_case_isolation}_${prop_pop_vaccinated}_${household_quarantine_compliance}"' >> "$batch_job_file"
echo 'output_path="'$output_dir'/${output_prefix}/'$output_file_name'"' >> "$batch_job_file"
echo 'mkdir -p "'$output_dir'/${output_prefix}"' >> "$batch_job_file"
echo 'cmd="'$exe_path' /NR:'$nr_value' /c:'$c_value' /PP:'$pp_file' /P:'$p_file' /CLP1:'$clp1' /CLP2:'$clp2' /CLP3:'$clp3' /CLP4:'$clp4' /CLP5:'$clp5' /CLP6:${relative_spatial_contact_rate_given_social_distancing} /CLP7:${delay_to_start_case_isolation} /CLP8:${prop_pop_vaccinated} /CLP9:${household_quarantine_compliance} /O:${output_path} /D:'$bin_file' /L:'$network_bin' /R:'$rs' '$population_ids'"' >> "$batch_job_file"
echo 'echo "$cmd"' >> "$batch_job_file"
echo 'eval "$cmd"' >> "$batch_job_file"

# Make the batch job file executable
chmod +x "$batch_job_file"

# Submit the batch job to Slurm
sbatch "$batch_job_file"
