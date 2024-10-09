# Read the lines from a file
with open('C:\\Users\\TouKong\\Desktop\\VS Code Projects\\Hire Veterans\\Blog-URL-List-Complete.txt', 'r') as file:
    lines = file.readlines()

# Reverse the order of the lines
reversed_lines = lines[::-1]

# Write the reversed lines back to the file (or a new file)
with open('C:\\Users\\TouKong\\Desktop\\VS Code Projects\\Hire Veterans\\reversed_file.txt', 'w') as file:
    file.writelines(reversed_lines)

print("The lines have been reversed!")
