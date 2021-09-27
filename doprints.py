import csv
import tempfile
import os
import subprocess
#from obswebsocket import obsws, requests
import zipfile
from pathlib import Path

count = 0
try:
    with open("count") as countin:
        count = int(next(countin))
except:
    pass

recording_file = None
        
def on_event(message):
    print(u"Got message: {}".format(message))
    try:
        if message.getRecordingFilename():
            recording_file = message.getRecordingFilename()
    except:
        pass

candidates = None
#obs_client = obswebsocket.obsws("localhost", 4444, "secret")
#obs_client.register(on_event)
with open('candidates.csv', newline='') as infile:
    dialect = csv.Sniffer().sniff(infile.read(1024))
    infile.seek(0)
    candidates = csv.DictReader(infile, dialect=dialect)
    try:
        open('done.csv')
    except:
        with open('done.csv', "w") as donefile:
            fieldnames = ['file_url', 'friendly_url', 'name', 'id', 'recording_file']
            done_writer = csv.DictWriter(donefile, fieldnames = fieldnames, dialect=dialect)
            done_writer.writeheader()
        
    with open('done.csv', "a") as donefile:
        recording_file = None
        #obs_client.call(requests.StartRecordig())
        count = count + 1
        with open("count", "w") as countout:
            countout.write(str(count))
            fieldnames = ['file_url', 'friendly_url', 'name', 'id', 'recording_file']
            done_writer = csv.DictWriter(donefile, fieldnames = fieldnames, dialect=dialect)
            for candidate in candidates:
                files_printed = 0
                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        path_to_zip_file = f"{temp_dir}/a.zip"
                        subprocess.run(["axel", candidate['file_url'], '-o', path_to_zip_file])
                        with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
                            zip_ref.extractall(temp_dir)
                        for path in Path(temp_dir).rglob('*'):
                            subprocess.run(["python3", "conv.py", path])
                        for stl in Path(temp_dir).rglob('*.stl'):
                            subprocess.run([
                                "slic3r",
                                "--gcode-flavor",
                                "marlin",
                                "--avoid-crossing-perimeters",
                                "--no-gui",
                                "--nozzle-diameter",
                                "0.4",
                                "--filament-diameter",
                                "1.75",
                                "--temperature",
                                "210",
                                "--bed-temp"
                                "70",
                                "--support-material",
                                "--support-material-threshold",
                                "0",
                                "--retract-length",
                                "6",
                                "--retract-speed",
                                "70",
                                
                                "--end-gcode",
"""M107               ; disable cooling fan
M106 P0 S0         ; disable cooling fan
M104 S0            ; shut down hot end
M140 S0            ; shut down bed
G92 E1             ; set filament position
G1 E-1 F300        ; retract filament
G28 X              ; home X axis
G1 Y50 F1000       ; lift y axis
M84                ; disable stepper motors
""",
                                stl])
                        for gcode in Path(temp_dir).rglob('*.gcode'):
                            shifted = f"skew+{gcode}"
                            combined = f"combined+{gcode}"
                            subprocess.run(["./program.exe", gcode, f"skew+{gcode}", "0", "0", "45"])
                            with open("start.gcode") as start_in:
                                with open(combined, "w") as combined_out:
                                    with open(shifted) as shifted_in:
                                        for line in start_in:
                                            combined_out.write(line)
                                            for line in shifted_in:
                                                combined_out.write(line)
                            ret = subprocess.run(["printcore", "/dev/ttyUSB0", combined])
                            if (ret == 0):
                                files_printed = files_printed + 1
                finally:
                    pass
#            obs_client.call(requests.StopRecording())
#        while recording_file is None:
