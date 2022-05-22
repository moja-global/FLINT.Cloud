import rasterio as rst
import os
import json

def get_provider_config(project_dir):
   with open(f"{os.getcwd()}/input/{project_dir}/templates/provider_config.json", "r+") as gpc:
        lst = []
        data = json.load(gpc)
        print(type(gpc))
        
        for file in os.listdir(f"{os.getcwd()}/input/{project_dir}/disturbances/"):
            d = dict()
            d["name"] = file[:-10]
            d["layer_path"] = "../layers/tiles" + file
            d["layer_prefix"] = file[:-5]
            lst.append(d)    
        gpc.seek(0)
        data["Providers"]["RasterTiled"]["layers"] = lst

        for file in os.listdir(f"{os.getcwd()}/input/{project_dir}/classifiers/"):
            d = dict()
            d["name"] = file[:-10]
            d["layer_path"] = "../layers/tiles" + file
            d["layer_prefix"] = file[:-5]
            lst.append(d)    
        gpc.seek(0)
        data["Providers"]["RasterTiled"]["layers"] = lst

        for file in os.listdir(f"{os.getcwd()}/input/{project_dir}/miscellaneous/"): 
            d = dict()
            d["name"] = file[:-10]
            d["layer_path"] = "../layers/tiles" + file
            d["layer_prefix"] = file[:-5]
            lst.append(d)    
        gpc.seek(0)
        data["Providers"]["RasterTiled"]["layers"] = lst
        

        Rasters = []
        cellLatSize = []
        cellLonSize = []

        get_provider_config()
