import os
from graphviz import Digraph
import pandas as pd
import json
import traceback
import numpy as np

class MyException(Exception):
    pass

class ConfigHandler():
    configPath = "config.json"
    config = None
    def __init__(self):
        if not os.path.exists(self.configPath):
            self.writeConfig()
        self.readConfig()
        self.checkInputs()

    def writeConfig(self):
        self.config = {
            "input_excel_path": "family_tree.xls",
            "events_to_show": {
                "comment": "here you can define the list of events, you want to visualize. If you set it to 'all' then each events will be listed",
                "example1": ["occupation","foglalkozas"],
                "example2": ["all"],
                "event_types": ["all"],
            },
            "show_notes": {
                "comment": "set this value to True if you want to show the notes as well",
                "example1": False,
                "example2": True,
                "value": False,
            },
            "output_format": {
                "comment": "the output format can be set here e.g. pdf, svg.",
                "format": "pdf"
            },
            "colors": {
                "male_background": "#B0E0E6",
                "female_background": "#FFC0CB"
            }
        } 
        with open(self.configPath, 'w') as f:
            json.dump(self.config, f, indent=2)

    def readConfig(self):
        with open(self.configPath, 'r') as f:
            self.config = json.load(f)

    def checkInputs(self):
        if not os.path.exists(self.config["input_excel_path"]):
            print(self.config["input_excel_path"] + ' is not exist. Family tree can not be created.')
            raise MyException

class FamilyTreeHandler(ConfigHandler):
    peopleAdded = []
    familiesAdded = []
    def __init__(self):
        super().__init__()
        xls = pd.ExcelFile(self.config["input_excel_path"])
        self.df_people = pd.read_excel(xls,sheet_name="people")
        self.df_families = pd.read_excel(xls,sheet_name="families")
        self.df_families['person2_id'] = self.df_families['person2_id'].fillna(0).astype("int32")
        self.df_places = pd.read_excel(xls,sheet_name="places")
        self.df_children = pd.read_excel(xls,sheet_name="children")
        self.df_events = pd.read_excel(xls,sheet_name="events")

    def main(self):
        self.filterEvents()
        self.assignPlaces()
        self.dot = Digraph('Family tree')#, graph_attr = {'splines':'ortho'})
        self.addPeople()
        self.show()

    def filterEvents(self):
        events = self.config["events_to_show"]["event_types"]
        if len(events) == 1:
            if events[0].lower() == "all":
                return
        self.df_events = self.df_events[self.df_events["type"].isin(events)]

    def assignPlaces(self):
        self.df_people = self.assignPlace(self.df_people, 'birth_place_id', 'birth_place')
        self.df_people = self.assignPlace(self.df_people, 'death_place_id', 'death_place')
        self.df_people = self.assignPlace(self.df_people, 'burial_place_id', 'burial_place')
        self.df_events = self.assignPlace(self.df_events, 'place_id', 'place')

    def assignPlace(self, df, id_column_name, new_column_name):
        return df.merge(
            self.df_places[['id', 'name']].rename(columns ={"name":new_column_name}),
            how = 'left',
            left_on = id_column_name,
            right_on = 'id'
        ).drop(['id_y',id_column_name],axis='columns').rename(columns ={"id_x":'id'})

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
        self.addFamilyEdge(family_id,person_id)
        self.addSpouse(family_id, person_id)
        self.addChildren(family_id)

    def addSpouse(self, family_id, person_id):
        spouse_id = self.getSpouseId(family_id, person_id)
        if not spouse_id:
            return
        self.addPerson(spouse_id)
        self.addFamilyEdge(family_id,spouse_id)
        self.addMarriageEdge(person_id,spouse_id)

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
    #https://www.graphviz.org/doc/info/attrs.html
    def addPersonNode(self, person_id):
        df_row = self.df_people[self.df_people['id'] == person_id]
        if str(df_row['sex'].iloc[0]) == 'female':
            color = self.config["colors"]["female_background"]
        else:
            color = self.config["colors"]["male_background"]
        person_dot_id = 'p'+str(person_id)
        self.dot.node(person_dot_id, 
            tooltip = '', #self.getPersonTooltip(df_row),
            shape = 'rect',
            label = self.getPersonLabel(df_row),
            fillcolor=color,
            style='filled'
        )

    def addFamilyNode(self, family_id):
        family_dot_id = 'f'+str(family_id)
        self.dot.node(family_dot_id, shape = 'ellipse', color = 'black', label="")

    def addFamilyEdge(self, family_id, person_id):
        family_dot_id = 'f'+str(family_id)
        person_dot_id = 'p'+str(person_id)
        self.dot.edge(person_dot_id, family_dot_id, color = 'black')

    def addMarriageEdge(self, person1_id, person2_id):
        person1_dot_id = 'p'+str(person1_id)
        person2_dot_id = 'p'+str(person2_id)
        self.dot.edge(person1_dot_id, person2_dot_id, arrowhead='none', color = 'black', constraint='false')

    def addChildrenEdge(self, family_id, person_id):
        family_dot_id = 'f'+str(family_id)
        person_dot_id = 'p'+str(person_id)
        self.dot.edge(family_dot_id, person_dot_id, color = 'black')

    def show(self):
        self.dot.format = self.config["output_format"]["format"]
        self.dot.render('family_tree', view = True)

    ####################################################################################
    #########                     string manipulation for visualization                   
    ####################################################################################
    def getPersonLabel(self,df_row):
        person = df_row.iloc[0].replace(np.nan,'',regex=True)
        name = self.getNameString(person)
        birth_date = self.getDateTimeString(person['birth_date'], '%Y.%m.%d')
        death_date = self.getDateTimeString(person['death_date'], '%Y.%m.%d')
        events = self.getEventsString(person)
        birth_place = str(person['birth_place'])

        return (
            f"{name}\n"
            f"{birth_date} - {death_date}\n"
            f"{birth_place}\n"
            f"{events}"
        )

    def getPersonTooltip(self,df_row):
        # it is not used right now
        data = df_row.iloc[0].astype('string').fillna("")
        surname = str(data['surname'])
        firstname = str(data['firstname'])
        notes = str(data['notes'])
        return (
            f"{surname} {firstname}\n"
            f"it still has to be implemented\n"
            f"{notes}"
        )

    def getEventsString(self, person):
        person_id = person['id']
        events = self.df_events[self.df_events['person_id'] == person_id]
        eventsString = ""
        for index, row in events.iterrows():
            eventsString += self.getEventString(row)
        return eventsString

    def getEventString(self, event_row, errorValue = ''):
        event_row = event_row.replace(np.nan,'',regex=True)
        type = str(event_row['type'])
        value = self.getStringWithPrefixIfNotEmpty(str(event_row['value'])," - ")
        date = self.getDateTimeString(event_row['date'], '%Y.%m.%d')
        date = self.getStringWithPrefixIfNotEmpty(date," - ")
        if self.config["show_notes"]["value"]:
            note = self.getStringWithPrefixIfNotEmpty(str(event_row['note'])," - ")
        else:
            note = ""
        place = self.getStringWithPrefixIfNotEmpty(str(event_row['place'])," - ")

        return (
            f"{type}{date}{value}{place}{note}\n"
        )

    def getStringWithPrefixIfNotEmpty(self, inputValue, prefix):
        if inputValue != "":
            return prefix + inputValue
        else:
            return inputValue

    def getNameString(self, person, errorValue = ''):
        try:
            surname = person['surname']
            firstname = person['firstname']
            birth_surname = person['birth_surname']
            birth_firstname = person['birth_firstname']
            name = surname + " " + firstname
            if birth_surname != '':
                name += "\n(" + birth_surname + " " + birth_firstname + ")"
            return name
        except:
            return errorValue

    def getDateTimeString(self, value, format, errorValue = ''):
        try:
            return str(value.strftime(format))
        except:
            return errorValue

try:
    familyTreeHandler = FamilyTreeHandler()
    familyTreeHandler.main()
except:
    traceback.print_exc()
    input("Press Enter to exit...")
