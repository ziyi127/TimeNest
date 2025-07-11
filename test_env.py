import sys
print("Python路径:", sys.path)
print("Python版本:", sys.version)
try:
    import pandas
    print("pandas版本:", pandas.__version__)
except ImportError:
    print("pandas未安装")