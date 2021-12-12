# Family tree
- This readme contains description for ubuntu os. Some of the points can be different on Windows (installation steps can be seen later).

## Output example
<p align="center">
  <img src="output_example.jpg" width="350" title="output example">
</p>

## Clone the repo
```
git clone git@github.com:acgabor/family_tree.git
```

## Install packages (python3.6.9)
[Graphviz](https://graphviz.org/)
```
sudo apt-get install xdg-utils  # only if missing
pip3 install graphviz
pip3 install pandas
pip3 install openpyxl
pip3 install xlrd
sudo apt install graphviz
```

## Create exe (Optional)
```
cd /tmp
git clone https://github.com/pyinstaller/pyinstaller
cd pyinstaller/bootloader
sudo apt-get install build-essential zlib1g-dev
sudo python3 ./waf all
pip3 install pyinstaller
bash create_exe.sh
```

## Fill out template
- Rename input_template_family_tree.xls to family_tree.xls or modify "input_excel_path" in the config file

## Set config.json
- It contains user defined settings
- It is automatically created if not exists

## Limitations of current version
- Only one marriage can be handled for one person

# Install on Windows
## Download and install python3
## Install packages
```
pip install pyinstaller
pip install pandas
pip install openpyxl
pip install xlrd
pip install graphviz
```
## Download [graphviz](https://graphviz.org/download/) and install
- During installation, add graphviz to system path
## Run create_exe.bat