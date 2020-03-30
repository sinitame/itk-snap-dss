import os, glob, subprocess


python = 'python'
script_path = os.path.dirname(os.path.abspath(__file__))
deamons = glob.glob(os.path.join(script_path, "deamon_*.py"))

print(deamons)

for deamon in deamons:
    proc = subprocess.Popen([python, deamon])



