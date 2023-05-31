#!/usr/bin/python
import os

# Open the file in write mode
file = open("/usr/local/bin/datasets/hello_world.txt", "w")

# Write the text into the file
file.write("Hello, world!")

# Close the file
file.close()

# Print a message to indicate the file creation
print("File 'hello_world.txt' created successfully.")

command = "bash /usr/local/bin/scripts/mpg_aerial_survey/startup.sh"  # Replace with your desired bash command