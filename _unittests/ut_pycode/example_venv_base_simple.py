import sys
print("example_venv_base_simple.py", "execution")
path = sys.base_prefix if hasattr(sys, "base_prefix") else sys.prefix
print(path, sys.prefix)
