"""
load = sum of power output
do not exceed pmax, or lower than pmin.
Merit order important

#set up output dict ->


"""
import flask
from flask import Flask, request, jsonify
app = Flask(__name__)
import pandas as pd
import operator
  
@app.route('/productionplan/', methods= ['GET', 'POST'])
def Production_Plan():
    
        fuelsDict ={"fuels" : {"gas(euro/MWh)" : 0, "kerosine(euro/MWh)" : 0,
                                         "co2(euro/ton)":0,"wind(%)":0}  } 
        
        pPlantsSpecsDict =  {"name" : "","type": "",
                                  "efficiency": 0.0, "pmin": 0, "pmax": 0}
        
        powerplantsDict = {"powerplants" : [pPlantsSpecsDict]*4}
        
       
        dataOuterDict = {"load" : 0, "fuels" : fuelsDict["fuels"], 
                 "powerplants" : powerplantsDict["powerplants"]}
        
        request_data = request.get_json()
        load = request_data['load']
        fuelsDict['fuels'] = request_data['fuels']
        powerplantsDict['powerplants'] = request_data['powerplants']
        dataOuterDict = {"load" : load, "fuels" : fuelsDict['fuels'], "powerplants" : powerplantsDict['powerplants']}
        
        databaseDict = {x['name'] :[] for x in powerplantsDict['powerplants']}
        
            
        #permList = OnoffPermuter(databaseDict, len(powerplantsDict['powerplants']))
        
        
        # list comprehension combined with dict comprehension?
        
        key_list = ['name', 'p']
        
        
        nameList = [x['name'] for x in powerplantsDict['powerplants']]
        
        costEff=Build_Cost_Eff(nameList, powerplantsDict, fuelsDict['fuels'])
        #euro per ton of co2 and wind% passed through
        merCond ={'co2(euro/ton)': fuelsDict['fuels']['co2(euro/ton)'], 'wind(%)': fuelsDict['fuels']['wind(%)']}
        meritOrd = Merit_Order(merCond, costEff, nameList, powerplantsDict)
        
        #Tomorrow use meritOrd to assign power load, use load - sum(pmin) so need powerplantsDict
        
        
        pList = UnitCommit(meritOrd, powerplantDict) #must contain all names!

        listOut = [{key_list[0]: nameList[idx], key_list[1]: pList[idx]} for idx in range(len(nameList))]
       
        if flask.request.method == 'POST':
            return jsonify(listOut), 200
        
        
        
        
def Build_Cost_Eff(names, powDict, costs):
    #Here extract relevant info
    #first extract from fuels gas, kerosine info
    #attach to key: name of powerplant
    #for wp1, wp2 do same operation except divide % by 100
   
    typeDict = {'gasfired': costs['gas(euro/MWh)'], 'turbojet': costs['kerosine(euro/MWh)'], 'windturbine': costs['wind(%)']/100}
    costEff = {x : [] for x in names}
    for items in powDict['powerplants']: 
        costEff[items['name']].append(items['type'])
        costEff[items['name']].append(items['efficiency'])
        for key in typeDict:
            if costEff[items['name']][0] == key:
                costEff[items['name']].append(typeDict[key])
    return costEff
   

def Merit_Order(merCond, costEff, names, powDict):  # take in dict containing cost per MWh and eff for given name 
    meritOrderUnSorted={}
    keyToDel = []
    for key in costEff:
        name = key
        costPMWh = costEff[key][2]
        meritCoEf = 1/costEff[key][1]
        meritOrderUnSorted[name] = costPMWh*meritCoEf
    for key in meritOrderUnSorted:
        if meritOrderUnSorted[key] ==0:
            keyToDel.append(key)
    for i in keyToDel:
        del meritOrderUnSorted[i]
    merOrd = sorted(meritOrderUnSorted.items(), key=operator.itemgetter(1))
    return merOrd


def Unit_Commit(mOrd, pDict):
    # Ignores spinning reserve principle, load - sum pmin of all in merit OrderedDict, from first to last of merit 
    #order if PMax of an item < than load -sum pmin, then next item. If PMax of new item is more than needed, just use amount 
    #needed
    #Unit Commit output can pretty much go straight into listOut without total cost 
    pass

#Finally, tests, and error handling. 
#Docker file
#toml file. 
#C02 addition, maybe websocket
   

if __name__ == '__main__':
    app.run() 
    