import subprocess

binary_path = "bin/depict_parser"
arguments=["-f", ""]
# def depict(*args):

try:
    result = subprocess.run([binary_path] + arguments, capture_output=True, text=True, check=True)
    
    print(result.stdout)

    if result.stderr:
        print("Binary error output:")
        print(result.stderr)
except subprocess.CalledProcessError as e:
    print(f"Error running binary: {e}")
    print(f"Binary output: {e.stdout}")
    print(f"Binary error output: {e.stderr}")
except FileNotFoundError:
    print(f"Error: Binary not found at {binary_path}")