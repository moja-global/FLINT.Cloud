import os


def get_container_id():
    """
      Return the container id corresponding to the image gcbm-api
    """
    container_id = "" 
    os.system('docker ps >> simulation.txt')
    with open('simulation.txt') as file_handle:
        lines = file_handle.readlines()
        for line in lines:
            if 'gcbm-api' in line:
                container_id = line.split()[0]
    os.system('rm simulation.txt')
    return container_id

  
def get_simulation_status():
    """
      If the container gcbm-api is running, the associated logs are returned
    """
    container_id = get_container_id()
    logs_file_name = container_id + ".txt"
    if container_id != '':
        logs_cmd = "docker logs " + container_id + " > " + logs_file_name +  " 2>&1"
        os.system(logs_cmd)
        logs = []
        with open(logs_file_name) as file_handle:
            logs = file_handle.readlines()
        #os.system('rm ' + logs_file_name)
        return {'container_running': True, 'logs': logs}
    return {'container_running': False}

print(get_simulation_status())
