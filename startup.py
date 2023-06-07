#!/usr/bin/python
import os

# Update git repo
os.system("cd /usr/local/bin/scripts/mpg_aerial_survey/ && sudo git pull > /tmp/git_testing.log")

command = "python3 /usr/local/bin/scripts/mpg_aerial_survey/post_process.py"  # Replace with your desired bash command

return_code = os.system(command)