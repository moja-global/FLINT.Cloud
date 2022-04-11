import os
import pandas as pd

PROJECT_ROOT = os.getcwd()
file_paths = os.path.join(PROJECT_ROOT,'input')
simulations = os.listdir(file_paths)
simulation_paths = [os.path.join(file_paths,s) for s in simulations]

for sim in simulation_paths:
    input_files = pd.DataFrame({"Input Files":[os.path.join(sim,match) for match in os.listdir(sim) if ".tiff" in match]})
    config_files = pd.DataFrame({"Config Files":[os.path.join(sim,match) for match in os.listdir(sim) if "config" in match]})
    logs = pd.DataFrame({"Log Files":[os.path.join(sim,match) for match in os.listdir(sim) if "log" in match]})
    output = os.path.join(sim,'output')
    if os.path.exists(output):
        output_msg = "Output files located in " + output
    else:
        output_msg = "We have to run the simulation first check README.md"
    sim_name = os.path.basename(sim)
    s = {"Input Files":input_files,"Config files":config_files,"Logs":logs,"Output":output_msg}
    with open(f"{sim_name}_summary.txt","w") as outfile:
        outfile.write(f"## Sim name:{sim_name}\n\n")
        outfile.write(input_files.to_markdown()+"\n\n")
        outfile.write(config_files.to_markdown()+"\n\n")
        outfile.write(logs.to_markdown())