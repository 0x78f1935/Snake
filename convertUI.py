"""
This file has been writen to convert ui files in the folder src/data/layout
to useable format. This way QtDesigner can be used to make the design posibility more faster.
In the future those will be automatically update the program
"""
import os
from os import listdir, getcwd
from os.path import isfile, join
ui_folder = join(join(join(join(getcwd(), 'src'), "data"), "layouts"), 'ui')
layout_folder = join(join(join(getcwd(), 'src'), "data"), "layouts")
onlyfiles = [f for f in listdir(ui_folder) if f.endswith('.ui')]
for item in onlyfiles:
    location_export = join(join(join(join(getcwd(), 'src'), "data"), "layouts"), item)
    location_ui = join(join(join(join(join(getcwd(), 'src'), "data"), "layouts"), 'ui'), item)
    print(f"python -m PyQt5.uic.pyuic -x {location_ui} -o {str(location_export)[:-2]}")
    print(os.popen(f"python -m PyQt5.uic.pyuic -x {location_ui} -o {str(location_export)[:-2]}py").read())
print('Done!')