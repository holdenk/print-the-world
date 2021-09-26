#!/bin/bash
set -ex
if ! command -v npm &> /dev/null
then
  curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
  sudo apt-get install -y nodejs
  # Update npm
  sudo npm install -g npm
fi
if [ ! -d KiriMotoSlicer ]; then
  git clone https://github.com/holdenk/KiriMotoSlicer.git
fi
pushd KiriMotoSlicer
# Make requirements isn't idempotent :/
if [ ! -d grid-apps ]; then
  # May fail because doesnt go to the right place.
  #make requirements
  git clone https://github.com/holdenk/grid-apps.git
  cd grid-apps && npm i && cd ..
fi
# Slice command kirimoto-slicer x3d-cm-interior-graffiti-uvs.obj.stl --deviceName="Creality.CR-30"
sudo make install
popd
sudo apt-get install -y python3 python3-pip slic3r printcore setserial mono-complete
mcs program.cs
pip3 install -U -r requirements.txt
