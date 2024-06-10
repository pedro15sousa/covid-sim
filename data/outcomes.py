#!/usr/bin/env python3

import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import warnings
from datetime import datetime, timedelta
import numpy as np
import chardet
import re

# Parameters
default_base_folder = "."
various_subfolders = ["."]
plot_output_dir_relative_to_base_folder = "Plots"
day_0 = datetime(2020, 1, 1)
num_days_to_plot = 186
png_res = 300
output_admin_unit_inc = True
output_seir = True
output_sev_inc = True
output_age_inc = True
severity_variables_to_plot = ["incSARI", "incCritical", "SARI", "Critical", "incDeath", "cumSARI", "cumCritical"]

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--basefolder", default=default_base_folder, help="Base folder where output files are located")
args = parser.parse_args()

base_folder = args.basefolder
plot_output_dir = os.path.join(base_folder, plot_output_dir_relative_to_base_folder)

def calc_plot_window(epi_curves, threshold=0, plot_from_to=None):
    if plot_from_to is not None and len(plot_from_to) != 2:
        raise ValueError("PlotFromTo must be a list of length 2")
    
    min_time = 0
    max_time = epi_curves.shape[0]
    plot_window_indices = range(min_time, max_time)
    
    if plot_from_to is None:
        if threshold > 0:
            min_time = 0
            max_time = epi_curves.shape[0]
            for timestep in range(epi_curves.shape[0]):
                if (epi_curves.iloc[timestep] > threshold).any():
                    min_time = timestep
                    break
            for timestep in range(epi_curves.shape[0] - 1, -1, -1):
                if (epi_curves.iloc[timestep] > threshold).any():
                    max_time = timestep
                    break
            if max_time - min_time <= 0:
                min_time = 0
                max_time = epi_curves.shape[0]
            if min_time == 0 and max_time == epi_curves.shape[0]:
                warnings.warn("CalcPlotWindow: cannot subset, try new threshold")
            plot_window_indices = range(min_time, max_time + 1)
    else:
        day_0 = datetime(2020, 1, 1)  # Assuming Day_0 is January 1, 2020
        start_date = datetime.strptime(plot_from_to[0], "%Y-%m-%d")
        end_date = datetime.strptime(plot_from_to[1], "%Y-%m-%d")
        start_index = (start_date - day_0).days
        end_index = (end_date - day_0).days
        plot_window_indices = range(start_index, end_index + 1)
    
    return plot_window_indices

def get_verbose_variable_string(inf_variable_string):
    inf_variable_string_long = inf_variable_string.replace("inc", "")
    inf_variable_string_long = inf_variable_string_long.replace("cum", "")
    return inf_variable_string_long

def get_inc_prev_or_cuminc_string(inf_variable_string):
    if "inc" in inf_variable_string:
        inc_prev_or_cuminc_string = "Incidence"
    elif "cum" in inf_variable_string:
        inc_prev_or_cuminc_string = "Cumulative Incidence"
    else:
        inc_prev_or_cuminc_string = "Prevalence"
    return inc_prev_or_cuminc_string

def make_scenario_plot_dir(plot_output_subdir, scenario):
    scenario_plot_dir = os.path.join(plot_output_subdir, scenario)
    os.makedirs(plot_output_dir, exist_ok=True)
    os.makedirs(plot_output_subdir, exist_ok=True)
    os.makedirs(scenario_plot_dir, exist_ok=True)
    assert os.path.exists(scenario_plot_dir), "Scenario plot directory does not exist"
    return scenario_plot_dir


# Main processing loop
for subfolder in various_subfolders:
    cur_path = os.path.join(base_folder, subfolder)
    files_to_check = [f for f in os.listdir(cur_path) if f.endswith(".avNE.severity.xls")]
    scenarios = [f.replace(".avNE.severity.xls", "") for f in files_to_check]
    
    if len(files_to_check) > 0:
        plot_output_subdir = os.path.join(plot_output_dir, subfolder)
        os.makedirs(plot_output_subdir, exist_ok=True)
    
    print(f"Processing Subfolder: {subfolder} ({len(scenarios)} scenarios)")
    
    for scenario in scenarios:
        print(f"\nScenario {scenario}: ")
        
        if output_seir or output_sev_inc:
            severity_file_name = os.path.join(cur_path, f"{scenario}.avNE.severity.xls")
            if os.path.exists(severity_file_name):
                severity_results = pd.read_csv(severity_file_name, sep="\t")
                severity_results = severity_results.dropna(axis=1, how='all')
                dates = [day_0 + timedelta(days=i) for i in range(len(severity_results))]
                
                scenario_plot_dir = make_scenario_plot_dir(plot_output_subdir, scenario)
                
                if output_seir:
                    print("SEIR, ")
                     # Make SIR plot
                    LWD = 4
                    plt.figure(figsize=(7, 7))
                    plt.plot(dates, severity_results['S'], color='green', linestyle='-', linewidth=LWD, label='Susceptible')
                    plt.plot(dates, severity_results['I'], color='red', linestyle='-', linewidth=LWD, label='Infectious')
                    plt.plot(dates, severity_results['R'], color='yellow', linestyle='-', linewidth=LWD, label='Recovered')
                    plt.plot(dates, severity_results['cumDeath'], color='black', linestyle='-', linewidth=LWD, label='Dead')
                    plt.xlabel("")
                    plt.ylabel("Prevalence")
                    plt.ylim(0, severity_results['S'].max())
                    plt.title(scenario + "\nSIR/D")
                    plt.legend(loc='upper right')
                    plt.xticks(rotation=45)
                    plt.gca().xaxis.set_major_locator(plt.MultipleLocator(30))
                    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b'))
                    plt.tight_layout()
                    plt.savefig(os.path.join(scenario_plot_dir, "SimpleSIR.png"), dpi=300)
                    plt.close()
                
                if output_sev_inc:
                    print("SeverityInc, ")
                    LWD = 4
                    # Cut off low incidence weeks
                    incVariables = ["incMild", "incILI", "incSARI", "incCritical", "incDeath"]
                    plot_window = calc_plot_window(severity_results[incVariables], threshold=1)
                    severity_results_tmp = severity_results.loc[plot_window, incVariables]
                    dates_tmp = [dates[i] for i in plot_window]

                    # Make incidence by severity plot
                    plt.figure(figsize=(7, 7))
                    plt.plot(dates_tmp, severity_results_tmp['incMild'], color='pink', linestyle='-', linewidth=LWD, label='Mild')
                    plt.plot(dates_tmp, severity_results_tmp['incILI'], color='palevioletred', linestyle='-', linewidth=LWD, label='ILI')
                    plt.plot(dates_tmp, severity_results_tmp['incSARI'], color='orange', linestyle='-', linewidth=LWD, label='SARI')
                    plt.plot(dates_tmp, severity_results_tmp['incCritical'], color='red', linestyle='-', linewidth=LWD, label='Critical')
                    plt.plot(dates_tmp, severity_results_tmp['incDeath'], color='black', linestyle='-', linewidth=LWD, label='Dead')
                    plt.xlabel("")
                    plt.ylabel("Incidence")
                    plt.ylim(0, severity_results_tmp.max().max())
                    plt.title(scenario + "\nIncidence by Disease Severity")
                    plt.legend(loc='upper right')
                    plt.xticks(rotation=45)
                    plt.gca().xaxis.set_major_locator(plt.MultipleLocator(30))
                    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b'))
                    plt.tight_layout()
                    plt.savefig(os.path.join(scenario_plot_dir, "SeverityIncidence.png"), dpi=300)
                    plt.close()

                    # Do deaths only
                    plot_window = calc_plot_window(severity_results[["incDeath"]], threshold=1)
                    dates_tmp = [dates[i] for i in plot_window]
                    plt.figure(figsize=(7, 7))
                    plt.plot(dates_tmp, severity_results.loc[plot_window, "incDeath"], color='black', linestyle='-', linewidth=LWD, label='Dead')
                    plt.xlabel("")
                    plt.ylabel("Incidence")
                    plt.title(scenario + "\nIncidence of Death")
                    plt.xticks(rotation=45)
                    plt.gca().xaxis.set_major_locator(plt.MultipleLocator(30))
                    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b'))
                    plt.tight_layout()
                    plt.savefig(os.path.join(scenario_plot_dir, "DeathIncidence.png"), dpi=300)
                    plt.close()
                    
        
        if output_age_inc:
            age_file_name = os.path.join(cur_path, f"{scenario}.avNE.age.xls")
            if os.path.exists(age_file_name):
                age_results = pd.read_csv(age_file_name, sep="\t")                
                # Clean
                if age_results.iloc[-1, 0] == "dist":
                    age_results = age_results[:-1]
                    
                scenario_plot_dir = make_scenario_plot_dir(plot_output_subdir, scenario)
                
                cases_or_deaths = ["C", "D"]
                
                def age_band_char(min_age, max_age, char="."):
                    return [f"{a}{char}{b}" for a, b in zip(min_age, max_age)]
                
                for case_or_death in cases_or_deaths:
                    case_or_death_long = "Cases" if case_or_death == "C" else "Deaths"
                    print(f"{case_or_death_long} AgeInc, ")
                    
                    cum_cases_10y_bands = pd.DataFrame(index=age_results.index, columns=age_band_char(range(0, 90, 10), list(range(10, 90, 10)) + [85]))

                    for i in range(9):
                        if i == 8:
                            cum_cases_10y_bands.iloc[:, i] = age_results[f"{case_or_death}{i*10}-{i*10+5}"]
                        else:
                            cum_cases_10y_bands.iloc[:, i] = age_results[f"{case_or_death}{i*10}-{i*10+5}"] + age_results[f"{case_or_death}{i*10+5}-{(i+1)*10}"]
                    
                    num_age_bands = 9
                    num_weeks = np.ceil(age_results.shape[0] / 7)
                    FirstAgeBand = True
                    # for ageband in range(num_age_bands):
                    #     # vec = cum_cases_10y_bands.iloc[:, ageband].diff(periods=7).dropna()
                    #     # vec = vec.iloc[np.array(days_to_consider) - 1].reset_index(drop=True)
                    #     # weekly_inc = pd.concat([weekly_inc, vec], axis=1)
                    #     # vec = cum_cases_10y_bands.iloc[days_to_consider, ageband].diff(periods=7).dropna()
                    #     vec = cum_cases_10y_bands.iloc[:, ageband].diff(periods=7)
                    #     vec = vec.iloc[days_to_consider].reset_index(drop=True)
                    #     if FirstAgeBand:
                    #         weekly_inc = vec.to_frame()
                    #         FirstAgeBand = False
                    #     else:
                    #         weekly_inc = pd.concat([weekly_inc, vec.to_frame()], axis=1)
                    #     print(weekly_inc.head(10))

                    days_to_consider = np.arange(1, age_results.shape[0], 7) - 1

                    weekly_inc_list = []
                    for ageband in range(num_age_bands):
                        vec = cum_cases_10y_bands.iloc[:, ageband].diff(periods=7)
                        vec = vec.iloc[days_to_consider]
                        vec = vec.fillna(0).astype(int)
                        
                        weekly_inc_list.append(vec)
                        
                        if FirstAgeBand:
                            weekly_inc = pd.DataFrame(vec)
                            FirstAgeBand = False
                        else:
                            # print(pd.concat([weekly_inc, vec], axis=1).values.tolist())
                            weekly_inc = pd.concat([weekly_inc, vec], axis=1)

                    weekly_inc.columns = cum_cases_10y_bands.columns[:len(weekly_inc_list)]
                    
                    weekly_inc.columns = cum_cases_10y_bands.columns
                    
                    plot_window = calc_plot_window(weekly_inc, threshold=1)
                    weekly_inc = weekly_inc.iloc[plot_window, :]
                    dates = [day_0 + timedelta(days=i*7) for i in plot_window]
                    dates = [d.strftime("%m-%d") for d in dates]
                    weekly_inc.index = dates

                    max_week_date = weekly_inc.sum(axis=1).idxmax()
                    max_week_total = weekly_inc.sum(axis=1).max()

                    print(f"Week with the highest number of {case_or_death_long}: {max_week_date}")
                    print(f"Total {case_or_death_long.lower()} in the highest week: {max_week_total}")
                    
                    plt.figure(figsize=(10, 10))
                    weekly_inc.plot(kind="bar", stacked=True, colormap="viridis", legend=False)
                    plt.legend(title="Age Group", bbox_to_anchor=(1.05, 1), loc="upper left")
                    plt.title(f"{scenario}\nWeekly {case_or_death_long} by Age")
                    plt.xlabel("Date")
                    plt.ylabel("Weekly Incidence")
                    plt.xticks(rotation=90)
                    plt.tight_layout()
                    plt.savefig(os.path.join(scenario_plot_dir, f"WeeklyIncidence{case_or_death_long}byAgeGroup_python.png"), dpi=300)
                    plt.close()

        if output_admin_unit_inc:
            severity_variable = "incCritical"
            print("Admin Level Plots: ")
            
            admin_unit_file_name = os.path.join(cur_path, f"{scenario}.avNE.severity.adunit.xls")
            print(admin_unit_file_name)
            # with open(admin_unit_file_name, "rb") as file:
            #     result = chardet.detect(file.read())

            # encoding = result["encoding"]
            # print(f"Encoding: {encoding}")
            if os.path.exists(admin_unit_file_name):
                admin_unit_results = pd.read_csv(admin_unit_file_name, sep="\t", encoding="latin1")
                
                # Clean
                admin_unit_results = admin_unit_results.dropna(axis=1, how="all")
                dates = [day_0 + timedelta(days=i) for i in range(len(admin_unit_results))]
                scenario_plot_dir = make_scenario_plot_dir(plot_output_subdir, scenario)
                
                for severity_variable in severity_variables_to_plot:
                    inf_variable_string_long = get_verbose_variable_string(severity_variable)
                    inc_prev_or_cuminc_string = get_inc_prev_or_cuminc_string(severity_variable)
                    
                    variable_pattern = "cumCritRecov_"
                    indices_of_pattern = [i for i, col in enumerate(admin_unit_results.columns) if re.search(variable_pattern, col)]
                    num_admin_units = len(indices_of_pattern)
                    admin_unit_names = [re.sub(variable_pattern, "", admin_unit_results.columns[i]) for i in indices_of_pattern]
                    admin_unit_names = [name.replace("_", " ") for name in admin_unit_names]

                    # select only cols of relevant variables (infection/ case/ Mild/ Critical etc.)
                    min_ad_unit_column = next(i for i, col in enumerate(admin_unit_results.columns) if re.search(severity_variable, col))
                    admin_unit_columns = admin_unit_results.columns[min_ad_unit_column - 1 + np.arange(num_admin_units)]
                    
                    print(f"{inf_variable_string_long} {inc_prev_or_cuminc_string}: ")
                    
                    max_num_admin_units_per_plot = 20
                    num_admin_plots = int(np.ceil(num_admin_units / max_num_admin_units_per_plot))
                    
                    for ad_plot in range(num_admin_plots):
                        min_admin_unit = ad_plot * max_num_admin_units_per_plot
                        max_admin_unit = min(min_admin_unit + max_num_admin_units_per_plot, num_admin_units)
                        cols = plt.cm.viridis(np.linspace(0, 1, max_admin_unit - min_admin_unit))
                        print(f" {min_admin_unit+1}-{max_admin_unit}", end="\t")
                        
                        admin_unit_results_tmp = admin_unit_results[admin_unit_columns[min_admin_unit:max_admin_unit]]
                        threshold = 1
                        plot_from_to = None
                        
                        plot_window = calc_plot_window(admin_unit_results_tmp, threshold=threshold, plot_from_to=plot_from_to)
                        admin_unit_results_tmp = admin_unit_results_tmp.iloc[plot_window, :]
                        dates_tmp = [dates[i] for i in plot_window]
                        
                        png_file_name = os.path.join(scenario_plot_dir, f"AdUnits_{inf_variable_string_long}_{inc_prev_or_cuminc_string}_{min_admin_unit+1}_{max_admin_unit}.png")
                        
                        if admin_unit_results_tmp.values.max() > 0:
                            plt.figure(figsize=(10, 10))
                            for i, col in enumerate(admin_unit_results_tmp.columns):
                                plt.plot(dates_tmp, admin_unit_results_tmp[col], color=cols[i], linewidth=4, label=admin_unit_names[min_admin_unit+i])
                            plt.xlabel("Date")
                            plt.ylabel(f"{inf_variable_string_long} {inc_prev_or_cuminc_string}")
                            plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
                            plt.xticks(rotation=45)
                            plt.gca().xaxis.set_major_locator(plt.MultipleLocator(30))
                            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b"))
                            plt.tight_layout()
                            plt.savefig(png_file_name, dpi=300)
                            plt.close()
                        else:
                            print(f"Didn't output {png_file_name} as only zeros")
                    
                    print()