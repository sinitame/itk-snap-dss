import os, glob, subprocess

processes = []
proc_dict = {}
python = 'python'
script_path = os.path.dirname(os.path.abspath(__file__))
deamons = glob.glob(os.path.join(script_path, "deamon_*.py"))

for deamon in deamons:
    proc = subprocess.Popen([python, deamon])
    processes.append(proc)


# Waiting for the completion of the deamons
for proc in processes:
    proc.wait()



