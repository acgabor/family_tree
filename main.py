import os
from graphviz import Digraph
import pandas as pd

INPUT_EXCEL_PATH = 'family_tree.xls'

class FamilyTreeHandler():
    peopleAdded = []
    familiesAdded = []
    def __init__(self, inputExcelPath):
        xls = pd.ExcelFile(inputExcelPath)
        self.df_people = pd.read_excel(xls,sheet_name="people")
        self.df_families = pd.read_excel(xls,sheet_name="families")
        self.df_families['person2_id'] = self.df_families['person2_id'].fillna(0).astype("int32")
        self.df_places = pd.read_excel(xls,sheet_name="places")
        self.df_children = pd.read_excel(xls,sheet_name="children")
        self.df_events = pd.read_excel(xls,sheet_name="events")

    def main(self):
        self.dot = Digraph(comment = 'Family tree', graph_attr = {'splines':'ortho'})
        self.addPeople()
        self.show()

    def addPeople(self):
        for df_index, df_row in self.df_people.iterrows():
            self.addPerson(df_row['id'])

    def addPerson(self, person_id):
        if person_id in self.peopleAdded:
            return
        self.peopleAdded.append(person_id)
        self.addPersonNode(person_id)
        self.addFamily(person_id)

    def addFamily(self,person_id):
        family_id = self.getFamilyId(person_id)
        if not family_id:
            return
        if family_id in self.familiesAdded:
            return
        self.familiesAdded.append(family_id)

        self.addFamilyNode(family_id)
        self.addPartnerEdge(family_id,person_id)
        self.addSpouse(family_id, person_id)
        self.addChildren(family_id)

    def addSpouse(self, family_id, person_id):
        spouse_id = self.getSpouseId(family_id, person_id)
        if not spouse_id:
            return
        self.addPerson(spouse_id)
        self.addPartnerEdge(family_id,spouse_id)

    def addChildren(self, family_id):
        df_children = self.df_children[self.df_children['family_id'] == family_id]
        for df_index, df_row in df_children.iterrows():
            person_id = df_row['person_id']
            self.addPerson(person_id)
            self.addChildrenEdge(family_id, person_id)

    def getFamilyId(self, person_id):
        family = self.df_families[(self.df_families['person1_id'] == person_id) | (self.df_families['person2_id'] == person_id)]
        try:
            return int(family['id'])
        except:
            return None

    def getSpouseId(self, family_id, person_id):
        family = self.df_families[self.df_families['id'] == family_id]
        if int(family['person1_id']) == person_id:
            return int(family['person2_id'])
        elif int(family['person2_id']) == person_id:
            return int(family['person1_id'])
        else:
            return None


    ####################################################################################
    ###############              Node - Edge operations             
    ####################################################################################
    def addPersonNode(self, person_id):
        df_row = self.df_people[self.df_people['id'] == person_id]
        person_dot_id = 'p'+str(person_id)
        self.dot.node(person_dot_id, tooltip = self.getPersonTooltip(df_row), shape = 'rect', label = self.getPersonLabel(df_row))

    def addFamilyNode(self, family_id):
        family_dot_id = 'f'+str(family_id)
        self.dot.node(family_dot_id, shape = 'ellipse', color = 'yellow', label="")

    def addPartnerEdge(self, family_id, person_id):
        family_dot_id = 'f'+str(family_id)
        person_dot_id = 'p'+str(person_id)
        self.dot.edge(person_dot_id, family_dot_id, arrowhead = 'none', color = 'red')

    def addChildrenEdge(self, family_id, person_id):
        family_dot_id = 'f'+str(family_id)
        person_dot_id = 'p'+str(person_id)
        self.dot.edge(person_dot_id, family_dot_id, arrowhead = 'none', color = 'blue')

    def show(self):
        self.dot.format = 'svg'
        self.dot.render('family_tree.gv.svg', view = True)

    ####################################################################################
    #########                     string manipulation for visualization                   
    ####################################################################################
    def getPersonLabel(self,df_row):
        data = df_row.iloc[0].astype('string').fillna("")
        surname = str(data['surname'])
        firstname = str(data['firstname'])
        birth_date = str(data['birth_date'])
        death_date = str(data['death_date'])
        birth_place = str(data['birth_place_id'])
        return (
            f"{surname} {firstname}\n"
            f"{birth_date} {death_date}\n"
            f"{birth_place}"
        )

    def getPersonTooltip(self,df_row):
        data = df_row.iloc[0].astype('string').fillna("")
        surname = str(data['surname'])
        firstname = str(data['firstname'])
        notes = str(data['notes'])
        return (
            f"{surname} {firstname}\n"
            f"it still has to be implemented\n"
            f"{notes}"
        )

if not os.path.exists(INPUT_EXCEL_PATH):
    print(INPUT_EXCEL_PATH + ' is not exist. Family tree can not be created.')
    exit()

familyTreeHandler = FamilyTreeHandler(INPUT_EXCEL_PATH)
familyTreeHandler.main()