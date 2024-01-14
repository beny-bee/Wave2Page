# Wave2Page
Intelligent System Project (ISP) - Master in Artificial Intelligence

## About
Wave2Page is an innovative project initiated by students of UPC, focusing on converting music into sheet notation and offering various audio services based on AI technology. Our mission is to bridge the gap between audio and musical notation, making it easier for musicians and enthusiasts to transcribe and understand music. We leverage the latest AI advancements to provide accurate and efficient services.

## Authors
- Gerard Carvaca
- Benjami Parellada
- Armando Rodriguez

## Directory 
- **app:** user interface code and files.
- **data:** examples provided as samples. It contains 3 folders providing several **songs** already separated by the system, the corresponding **midi** files and the generated music **sheets**.
- **src:** all the source code that makes up the system. It contains the functions that call the application and that compose the functionalities of the system.
- **youtube-extension:**  implementation of the google chrome extension. It must be compiled directly from the Chrome browser itself, in the configuration/extensions tab.
- The requirements.txt and environment-cuda.yml files are necessary for the correct installation of the repository. Their uses are explained in the next section.


## Running interface for the first time
These sections show how to create virtual environment for
our script and how to install dependencies. The first thing to do is to install Python 3.11. Then follow this instructions:

1. Install MuseScore 4 on your distribution: https://musescore.org/en/download

2. Open folder in terminal
```bash
cd <root_folder_of_project>/
```
3. Create virtual env
```bash
python3 -m venv venv/
```
4. Open virtual env
```bash
source venv/bin/activate
```
5. Install required dependencies
```bash
pip install -r requirements.txt
```

## Execute code
1. Open folder in terminal
```bash
cd <root_folder_of_project>/
```

2. Running the interface code of Flask.
 ```bash
 python3 app/app.py 
 ```

3. Close virtual environment
```bash
deactivate
```

## Windows environment using Anaconda

1. Create Anaconda environment
```bash
conda create --name wave2page
```
2. Open environment
```bash
conda activate wave2page
```
3. Install required dependencies
```bash
conda env update --file environment-cuda.yml --prune
pip install -r requirements.txt
```
4. Close environment
```bash
conda deactivate
```
