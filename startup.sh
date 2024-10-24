# startup.sh
#!/bin/bash
apt-get update
sudo apt-get install build-essential cmake
sudo apt-get install libopenblas-dev liblapack-dev
sudo apt-get install libx11-dev libgtk-3-dev
sudo apt install cmake
sudo apt install libdlib-dev
python -m pip install --no-cache-dir -r requirements.txt
