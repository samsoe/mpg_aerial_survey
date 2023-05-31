#!/usr/bin/python

# Open the file in write mode
file = open("/usr/local/bin/dataset/hello_world.txt", "w")

# Write the text into the file
file.write("Hello, world!")

# Close the file
file.close()

# Print a message to indicate the file creation
print("File 'hello_world.txt' created successfully.")