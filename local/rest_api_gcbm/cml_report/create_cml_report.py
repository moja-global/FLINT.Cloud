# from genericpath import isdir
# from operator import index
import os
# import pandas as pd
# import tabulate
import zipfile
# import json

#  Unzip file
zip = 'GCBM_Demo_Run.zip'
with zipfile.ZipFile(zip, 'r') as zip_ref:
    zip_ref.extractall('GCBM')

# # Define input template as dataframes
# GCBM_template_path = os.path.join('..','..','..','GCBM')
# inputs = os.listdir(os.path.join(GCBM_template_path,'layers','tiled'))
# api_inputs = pd.DataFrame({"Data Files":inputs})
# configs = os.listdir(os.path.join(GCBM_template_path,'config'))
# api_configs = pd.DataFrame({"Config files":configs})
# output_config = f"Your output configuration will be in ```output.zip``` file which consists of the ```gcbm_output.db``` database and a directory for each metric calculated during the simulation."

# # Simulation Information
# with open(os.path.join(GCBM_template_path,'config','localdomain.json')) as ld:
#     localdomain = json.load(ld)
# info = f" - Simulation Start Date : {localdomain['LocalDomain']['start_date']}\n - Simulation End Date : {localdomain['LocalDomain']['end_date']}"

# with open('GCBM_summary.txt','w') as outfile:
#     outfile.write(api_inputs.to_markdown(index=False)+'\n\n')
#     outfile.write(api_configs.to_markdown(index=False)+'\n\n')
#     outfile.write(output_config+'\n\n')
#     outfile.write(info)
