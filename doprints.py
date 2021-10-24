import csv
import tempfile
import os
import subprocess
from obswebsocket import obsws, requests, events
import zipfile
from pathlib import Path
import threading

count = 0
try:
    with open("count") as countin:
        count = int(next(countin))
except:
    pass

global recording_file
recording_file = None
        
def on_event(message):
    global recording_file
    if not isinstance(message, events.StreamStatus):
        print(u"Got message: {}".format(message))
        try:
            if message.getRecordingFilename():
                recording_file = message.getRecordingFilename()
                print(f"updated recording file name to {recording_file}")
        except BaseException as err:
            print(f"Error {err} updating")
            pass

use_slic3r = False
shift = use_slic3r
candidates = None
obs_client = obsws("localhost", 4444, "secret")
obs_client.connect()
obs_client.register(on_event)

endG = """M107               ; disable cooling fan
M106 P0 S0         ; disable cooling fan
M104 S0            ; shut down hot end
M140 S0            ; shut down bed
G92 E1             ; set filament position
G1 E-1 F300        ; retract filament
G28 X              ; home X axis
G1 Y50 F1000       ; lift y axis
M84                ; disable stepper motors
"""

finished = {}

# Load already finished
try:
    with open('done.csv') as donefile:
    dialect = csv.Sniffer().sniff(infile.read(1024))
    infile.seek(0)
    done_candidates = csv.DictReader(infile, dialect=dialect)
    for candidate in done_candidates:
        finished[candidate['file_url']] = 1
except:
    pass

startsG = ""
with open("start.gcode") as start_in:
    for line in start_in:
        startsG = f"startsG\n{line}"
with open('candidates.csv', newline='') as infile:
    dialect = csv.Sniffer().sniff(infile.read(1024))
    infile.seek(0)
    candidates = csv.DictReader(infile, dialect=dialect)
    # Write out the header if the done file doesn't exist yet.
    try:
        open('done.csv')
    except:
        with open('done.csv', "w") as donefile:
            fieldnames = ['file_url', 'friendly_url', 'name', 'id', 'recording_file']
            done_writer = csv.DictWriter(donefile, fieldnames = fieldnames, dialect=dialect)
            done_writer.writeheader()
        
    with open('done.csv', "a") as donefile:
        recording_file = None
        obs_client.call(requests.StartRecording())
        count = count + 1
        with open("count", "w") as countout:
            countout.write(str(count))
            fieldnames = ['file_url', 'friendly_url', 'name', 'id', 'recording_file']
            done_writer = csv.DictWriter(donefile, fieldnames = fieldnames, dialect=dialect)
            for candidate in candidates:
                if candidate["file_url"] in done_candidates:
                    continue # Skip finished candidates
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
                            cmd = []
                            if use_slic3r:
                                cmd = [
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
                                    "180",
                                    "--bed-temperature",
                                    "70",
                                    "--support-material",
                                    "--support-material-threshold",
                                    "0",
                                    "--retract-length",
                                    "6",
                                    "--retract-speed",
                                    "70",
                                    "--start-gcode",
                                    "",
                                    "--end-gcode",
                                    endG,
                                    str(stl)]
                            else:
                                cmd = [
                                    "kirimoto-slicer",
                                    "--load=printer.json",
                                    str(stl)
                                ]
                            print(f"Running {cmd}")
                            subprocess.run(cmd)
                        for gcode in Path(temp_dir).rglob('*.gcode'):
                            combined = f"{gcode}.combined.gcode"
                            if shift:
                                shifted = f"{gcode}.skew.gcode"
                                subprocess.run(["./program.exe", gcode, shifted, "0", "0", "45"])
                                with open("start.gcode") as start_in:
                                    with open(combined, "w") as combined_out:
                                        with open(shifted) as shifted_in:
                                            for line in start_in:
                                                combined_out.write(line)
                                            for line in shifted_in:
                                                combined_out.write(line)
                            else:
                                combined = gcode
                            ret = subprocess.run(["printcore", "/dev/ttyUSB0", combined])
                            if (ret == 0):
                                files_printed = files_printed + 1
                finally:
                    pass
            obs_client.call(requests.StopRecording())
        while True:
            import time
            time.sleep(10)
            print(f"Waiting for recording file to exist {recording_file}....")
            if recording_file is not None:
                print(f"Huzzah recorded as {recording_file}")
                break
            else:
                print(f"No recording in {recording_file}")
        done_writer.write(candidate['file_url'], candidate['friendly_url'], candidate['name'], candidate['name'], count, recording_file)
