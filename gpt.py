# gpt.py
import os
import re

# Output file name
output_file = "combined_minified.py"

# Directories and files to ignore
ignore_dirs = {"__pycache__", "env"}
ignore_files = {"__init__.py", output_file}

def minify_python_code(code):
    # Remove comments
    code = re.sub(r'#.*', '', code)
    # Remove empty lines
    code = os.linesep.join([s for s in code.splitlines() if s.strip()])
    return code

def combine_files(root_dir):
    with open(output_file, 'w') as outfile:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
            for filename in filenames:
                if filename.endswith('.py') and filename not in ignore_files:
                    file_path = os.path.join(dirpath, filename)
                    with open(file_path, 'r') as infile:
                        code = infile.read()
                        minified_code = minify_python_code(code)
                        outfile.write(f"# {filename}\n")  # Add a comment with the file name
                        outfile.write(minified_code + "\n\n")

if __name__ == "__main__":
    combine_files(".")
