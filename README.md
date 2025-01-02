# Auto Classify Media

## Description
Monitor your folder for new media files and automatically classify them into their respective media types such as movies, TV shows, audiobooks, and other media types using an LLM. This is helpful in automatically organizing torrent downloads. It also supports changing permissions of the new media before moving it into its directory.

## Installation
To install the necessary dependencies, run: `pip install -r requirements.txt`  
Specify Gemini API key and media paths in a `.env` file.

## Usage
Run it in the background with nohup:
```bash
sudo nohup ./venv/bin/python3 -u main.py >> out.log 2>&1 &
```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
