# Wave2Page
Supervised and Experiential Learning (SEL) - Master in Artificial Intelligence

## Authors
- Sonia Rabanaque
- Armando Rodriguez
- Pablo Ruiz
- Hasnain Shafqat

## Running interface for the first time
These sections show how to create virtual environment for
our script and how to install dependencies. The first thing to do is to install Python 3.9.
1. Open folder in terminal
```bash
cd <root_folder_of_project>/
```
2. Create virtual env
```bash
python3 -m venv venv/
```
3. Open virtual env
```bash
source venv/bin/activate
```
4. Install required dependencies
```bash
pip install -r requirements.txt
```

## Execute code
- Or open the already hosted public application:

    https://xd.streamlit.app/

1. Open folder in terminal
```bash
cd <root_folder_of_project>/
```
2. Running the interface code. The localhost will be automatically opened.
 ```bash
 streamlit run interface.py 
 ```
 Use ```--server.headless true``` if you don't want to get the browser opened automatically.
 
3. Close virtual environment
```bash
deactivate
```

### Auxiliar things to remove

pip install git+https://github.com/CarlGao4/demucs#egg=demucs