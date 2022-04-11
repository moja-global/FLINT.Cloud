import os
import pandas as pd

GCBM_template_path = os.path.join('..','..','GCBM')
docker_path = os.path.join('app','input','your_sim_name')
inputs = os.listdir(os.path.join(GCBM_template_path,'layers','tiled'))
api_inputs = pd.DataFrame({"Data Files":[os.path.join('@','input','simulation_name',file) for file in inputs]})
configs = os.listdir(os.path.join(GCBM_template_path,'config'))
api_configs = pd.DataFrame({"Config files":[os.path.join('@','input','simulation_name',file) for file in os.listdir(configs)]})
with open("GCBM_summary.txt",'w') as outfile:
    outfile.write("## GCBM Model"+'\n')
    outfile.write("### After your reproduce the GCBM Demo Run you docker image will have this structure"+'\n')
    outfile.write(api_inputs.to_markdown()+"\n\n")
    outfile.write(api_configs.to_markdown()+"\n\n")
    outfile.write(f"your output configuration will be in {os.path.join('@','input','output.zip')}")
    
