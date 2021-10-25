import pymeshlab as ml
import sys

if len(sys.argv) != 2:
    print("Usage python conv.py inputfile")
    sys.exit(1)

input_file = sys.argv[1]
ms = ml.MeshSet()
ms.load_new_mesh(input_file)
# Make it fit
biggest = max(ms.current_mesh().bounding_box().dim_y(), ms.current_mesh().bounding_box().dim_x(), ms.current_mesh().bounding_box().dim_z())
scale = 100 / biggest
ms.apply_filter('matrix_set_from_translation_rotation_scale', scalex=scale, scaley=scale, scalez=scale)
ms.apply_filter('transform_rotate', rotaxis='X axis', angle=90)
ms.save_current_mesh(f"{input_file}.stl")
sys.exit(0)
