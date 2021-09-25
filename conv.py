import pymeshlab as ml
import sys

if len(sys.argv) != 2:
    print("Usage python conv.py inputfile")
    sys.exit(1)

input_file = sys.argv[1]
ms = ml.MeshSet()
ms.load_new_mesh(input_file)
ms.save_current_mesh(f"{input_file}.stl")
sys.exit(0)
