from twitchio.ext import commands

import asyncio

import csv
import tempfile
import os
import subprocess
from obswebsocket import obsws, requests, events
import zipfile
from pathlib import Path
import threading

import time

import my_settings

printing = "Loading..."

class Bot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(token=my_settings.ACCESS_TOKEN, prefix='?', initial_channels=my_settings.CHANNEL)

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')

    @commands.command()
    async def hello(self, ctx: commands.Context):
        # Send a hello back!
        await ctx.send(f'Hello {ctx.author.name}!')

    @commands.command()
    async def printing(self, ctx: commands.Context):
        await ctx.reply(f'Currently printing {printing}')

    async def update_printing(self, printing: str):
        await self.connected_channels[0].send(f'Now printing {printing}')

    async def fetching(self, url: str):
        await self.connected_channels[0].send(f'Now fetch URL {url} for printing...')

bot = Bot()
bot_thread = threading.Thread(target=bot.run)
bot_thread.start()


time.sleep(10)

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
                if candidate["file_url"] in finished:
                    continue # Skip finished candidates
                files_printed = 0
                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        path_to_zip_file = f"{temp_dir}/a.zip"
                        asyncio.run(bot.fetching(candidate['file_url']))
                        subprocess.run(["axel", candidate['file_url'], '-o', path_to_zip_file])
                        with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
                            zip_ref.extractall(temp_dir)
                        for path in Path(temp_dir).rglob('*'):
                            conv_process = subprocess.run(["python3", "conv.py", path])
                            returncode = conv_process.returncode
                            if returncode != 0:
                                print(f"Error converting {path}")
                                continue
                            stl = f"{path}.stl"
                            cmd = [
                                "kirimoto-slicer",
                                "--load=printer.json",
                                str(stl)
                            ]
                            print(f"Running {cmd}")
                            slice_process = subprocess.run(cmd)
                            returncode = slice_process.returncode
                            if returncode != 0:
                                print(f"Error slicing {stl}")
                                continue
                            gcode = f"{path}.gcode"
                            printing = f"Printing {candidate['name']} file {gcode} from {candidate['friendly_url']}"
                            asyncio.run(bot.update_printing(printing))
                            print_proc = subprocess.run(["printcore", "/dev/ttyUSB0", gcode])
                            returncode = print_proc.returncode
                            if (returncode == 0):
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
