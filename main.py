import os
from graphviz import Digraph
import pandas as pd

INPUT_EXCEL_PATH = 'family_tree.xls'

class FamilyTreeHandler():
    def __init__(self, inputExcelPath):
        xls = pd.ExcelFile(inputExcelPath)
        self.df_people = pd.read_excel(xls,sheet_name="people")
        self.df_families = pd.read_excel(xls,sheet_name="families")
        self.df_places = pd.read_excel(xls,sheet_name="places")
        self.df_children = pd.read_excel(xls,sheet_name="children")
        self.df_events = pd.read_excel(xls,sheet_name="events")

    def addPeopleNodes(self):
        p1 = str(self.df_people.iloc[0]['id'])
        self.dot.node(p1, p1, tooltip = '', shape = 'rect', fillcolor = "red")
        '''
        p2 = str(self.df_people.iloc[1]['id'])
        with self.dot.subgraph() as subs:
            subs.attr(rank = 'same')
            subs.node(p2, p2, tooltip = '', shape = 'rect', fillcolor = "red")
            subs.edge(p1, p2, arrowhead = 'none', color = "black:invis:black")
        '''

    def main(self):
        self.dot = Digraph(comment = 'Ancestry', graph_attr = {'splines':'ortho'})
        self.addPeopleNodes()
        self.show()

    def show(self):
        self.dot.format = 'svg'
        self.dot.render('family_tree.gv.svg', view = True)

if not os.path.exists(INPUT_EXCEL_PATH):
    print(INPUT_EXCEL_PATH + ' is not exist. Family tree can not be created.')
    exit()

familyTreeHandler = FamilyTreeHandler(INPUT_EXCEL_PATH)
familyTreeHandler.main()
