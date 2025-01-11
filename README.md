# Auto Classify Media

## Description
Monitor your folder for new media files and automatically classify them into their respective media types such as movies, TV shows, audiobooks, and other media types using an LLM. This is helpful in automatically organizing torrent downloads. 

It supports type specific functionalities like automatically sending ebooks to your kindle, changing file permissions, etc with media handlers that are easy to build upon.

## Installation
Create a virtual environment preferably:
```bash
python3 -m venv venv
source venv/bin/activate
```
Install the necessary dependencies: `pip install -r requirements.txt`  
Specify Gemini API key, media paths and secrets in a `.env` file. See config.py for all supported environment variables.

## Usage
Run it in the background with nohup:
```bash
sudo nohup ./venv/bin/python3 -u main.py >> out.log 2>&1 &
```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
