import psutil
import time

def getListOfProcessSortedByMemory():
    '''
    Get list of running process sorted by Memory Usage
    '''
    listOfProcObjects = []
    # Iterate over the list
    for proc in psutil.process_iter():
       try:
           # Fetch process details as dict
           pinfo = proc.as_dict(attrs=['pid', 'name', 'username'])
           pinfo['vms'] = proc.memory_info().vms / (1024 * 1024)
           pinfo['threads'] = proc.num_threads()
           # Append dict to list
           listOfProcObjects.append(pinfo);
       except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
           pass
    # Sort list of dict by key vms i.e. memory usage
    listOfProcObjects = sorted(listOfProcObjects, key=lambda procObj: procObj['vms'], reverse=True)
    return listOfProcObjects

def net_usage(inf = "eth0"):   #change the inf variable according to the interface
    net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[inf]
    net_in_1 = net_stat.bytes_recv
    net_out_1 = net_stat.bytes_sent
    time.sleep(1)
    net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[inf]
    net_in_2 = net_stat.bytes_recv
    net_out_2 = net_stat.bytes_sent
    #Speed in mb/sec
    return (round((net_in_2 - net_in_1)/131072, 3), round((net_out_2 - net_out_1)/131072, 3))

def readFile(filepath, s=0):
    f = open(filepath)
    f.seek(s,0)
    lines = f.readlines()
    f.close()
    return lines

def follow(f):
    f.seek(0,2)
    while True:
        line = f.readline()
        time.sleep(1)
        if not line:
            continue
        yield line
