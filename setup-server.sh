(echo "Y") | sudo apt-get install python3-venv
rm -rf .env/
python3 -m venv .env
source .env/bin/activate
pip3 install -r requirements.txt
nohup python3 main.py > bot-log.txt &
tail -f bot-log.txt
