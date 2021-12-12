# Family tree
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
sudo apt install graphviz       # only if visualization is not working
```

## Fill out template
- Rename input_template_family_tree.xls to family_tree.xls or modify "input_excel_path" in the config file

## Set config.json
- It contains user defined settings
- It is automatically created if not exists

## Limitations of current version
- Only one marriage can be handled for one person