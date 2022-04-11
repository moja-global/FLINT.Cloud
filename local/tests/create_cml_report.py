import os
import pandas as pd
import tabulate

GCBM_template_path = os.path.join('..','..','GCBM')
docker_path = os.path.join('app','input','your_sim_name')
inputs = os.listdir(os.path.join(GCBM_template_path,'layers','tiled'))
api_inputs = pd.DataFrame({"Data Files":[os.path.join('@','input','simulation_name',file) for file in inputs]})
configs = os.listdir(os.path.join(GCBM_template_path,'config'))
api_configs = pd.DataFrame({"Config files":[os.path.join('@','input','simulation_name',file) for file in configs]})
with open(os.path.join('..','rest_api_gcbm',"GCBM_summary.txt"),'w') as outfile:
    outfile.write(api_inputs.to_markdown(index=False)+'\n\n')
    outfile.write(api_configs.to_markdown(index=False)+'\n\n')
    
