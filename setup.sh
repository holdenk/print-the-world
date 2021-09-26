#!/bin/bash
set -ex
if ! command -v python3 &> /dev/null
then
  sudo apt-get install -y python3 
fi
if ! command -v pip3 &> /dev/null
then
  sudo apt-get install -y python3-pip
fi 
if ! command -v npm &> /dev/null
then
  curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
  sudo apt-get install -y nodejs
  # Update npm
  sudo npm install -g npm
fi
# Install ctmconv (oldskool not so happy with obj)
#if ! command -v ctmconv &> /dev/null
#then
#  sudo apt-get install -y openctm-tools
#fi
# Install meshlab
#if ! command -v meshlab &> /dev/null
#then
#  sudo snap install meshlab
#fi
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
# Lets also install slic3r
if ! command -v slic3r &> /dev/null
then
  sudo apt-get install -y slic3r
fi
# Lets also install printcore
if ! command -v printcore &> /dev/null
then
  sudo apt-get install -y printcore
fi
# Also set serial
if ! command -v setserial &> /dev/null
then
  sudo apt-get install -y setserial
fi
# Also mono
if ! command -v mcs &> /dev/null
then
  sudo apt-get install -y mono-complete
fi
mcs program.cs
pip3 install -U -r requirements.txt
