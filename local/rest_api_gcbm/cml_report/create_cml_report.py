from genericpath import isdir
import os
import pandas as pd
import tabulate
import zipfile

#  Unzip file
zip = os.path.join('..','..','..','GCBM_Demo_Run.zip')
with zipfile.ZipFile(zip,'r') as zip_ref:
    zip_ref.extractall(os.path.join('..','..','..','GCBM'))

# Define input template as dataframes
GCBM_template_path = os.path.join('..','..','..','GCBM')
inputs = os.listdir(os.path.join(GCBM_template_path,'layers','tiled'))
api_inputs = pd.DataFrame({"Data Files":inputs})
configs = os.listdir(os.path.join(GCBM_template_path,'config'))
api_configs = pd.DataFrame({"Config files":configs})
output_config = f"Your output configuration will be in ```output.zip``` file which consists of the ```gcbm_output.db``` database and a directory for each metric calculated during the simulation."
with open(os.path.join('GCBM_summary.txt'),'w') as outfile:
    outfile.write(api_inputs.to_markdown(index=False)+'\n\n')
    outfile.write(api_configs.to_markdown(index=False)+'\n\n')
    outfile.write(output_config)
