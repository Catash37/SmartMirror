# startup.sh
#!/bin/bash
apt-get update
apt-get install -y cmake
python -m pip install --no-cache-dir -r requirements.txt
