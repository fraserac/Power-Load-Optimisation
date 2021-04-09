# -*- coding: utf-8 -*-

"""
load = sum of power output
do not exceed pmax, or lower than pmin.
Merit order important

#set up output dict ->


"""
import flask
from flask import Flask, request, jsonify
app = Flask(__name__)
from collections import OrderedDict

class PowerPlant(object):
     
    def __init__(self):
        self._name = ""
        self._pType = ""
        self._efficiency = 0.0
        self._pmin = 0.0
        self._pmax = 0.0
        self._fuels = {"default": 0.0}
        self._typeDict = {}
        self._fuelCost = {}
        self._fuelDec = {}
        self._meritVal = 0.0
        self.typeDict = {}
        self._fuelCost = 0.0
        self._fuelDec = 0.0
        self._c02Cost = 0.0
    @property        
    def name(self):
        return self._name 
    
    @name.setter
    def name(self, n):
        self._name = n
    
    @property        
    def pType(self):
        return self._pType 
    
    @pType.setter
    def pType(self, p):
        if p == 'gasfired' or p == 'turbojet' or p ==  'windturbine':
            self._pType= p
        else: 
            app.logger.error('Unrecognised fuel type: ', str(p))
    
    @property        
    def efficiency(self):
        return self._efficiency   
    
    @efficiency.setter
    def efficiency(self, eff):#
        try:
            if not eff < 0 and not eff >1:
                self._efficiency = eff 
            else:
                app.logger.error('efficiency not between 0 and 1.')
        except TypeError:
            app.logger.error('Incorrect type for efficiency. Should be float or int.')
            
        
    @property        
    def pmin(self):
        return self._pmin
    
    @pmin.setter
    def pmin(self, pmi):
        try:
            if not pmi < 0:
                self._pmin = pmi
            else:
                app.logger.error('Pmin is negative.')
        except TypeError:
            app.logger.error('Wrong type for Pmin. Should be float or int.')
 
    @property
    def pmax(self):
        return self._pmax
    
    @pmax.setter
    def pmax(self, pma):
        try:
            if not pma < 0:
                self._pmax = pma
            else:
                app.logger.error('Pmax is negative.')
        except TypeError:
            app.logger.error('Wrong type for Pmax. Should be float or int.')
            
    @property
    def fuels(self):
        return self._fuels
    
    @fuels.setter
    def fuels(self, f):
        try:
            checks =0
            for key in f:
                if not f[key] <0:
                    check+=1
            if len(f.keys()) == checks:
                self._fuels = f
            else:
                app.logger.error('fuels cost or percentage cannot be negative.')
        except TypeError:
            app.logger.error('Fuels needs to be a dictionary.')   
   
    
    def Choose_Fuel(self):
        if self._pType !=  'windturbine':
            self.typeDict = {'gasfired': self._fuels['gas(euro/MWh)'], 'turbojet': self._fuels['kerosine(euro/MWh)']}
            self._fuelCost = self.typeDict[self._pType]
        elif self._pType ==  'windturbine':
            self.typeDict = {'windturbine': self._fuels['wind(%)']/100}
            self._fuelDec = self.typeDict[self._pType]
    
    def Merit_Value(self):
        if self._pType != 'windturbine':
            self._meritVal = (1/self._efficiency*self._fuelCost) + self._c02Cost
        elif self._pType == 'windturbine':
            self._meritVal = 0 
            
    
    def Carbon_Cost(self):
        if self._pType == 'gasfired':
            self._c02Cost = 0.3*self._fuels['co2(euro/ton)']
        pass
   
    
###################################################################################
#########################

    
@app.route('/productionplan/', methods= ['GET', 'POST'])
def Production_Plan():
        
        fuelsDict ={"fuels" : {"gas(euro/MWh)" : 0, "kerosine(euro/MWh)" : 0,
                                         "co2(euro/ton)":0,"wind(%)":0}  } 
        
        pPlantsSpecsDict =  {"name" : "","type": "",
                                  "efficiency": 0.0, "pmin": 0, "pmax": 0}
        
        powerplantsDict = {"powerplants" : [pPlantsSpecsDict]*len(pPlantsSpecsDict.keys())}
        
       
        dataOuterDict = {"load" : 0, "fuels" : fuelsDict["fuels"], 
                 "powerplants" : powerplantsDict["powerplants"]}
        
        request_data = request.get_json()
        load = request_data['load']
        fuelsDict['fuels'] = request_data['fuels']
        powerplantsDict['powerplants'] = request_data['powerplants']
        dataOuterDict = {"load" : load, "fuels" : fuelsDict['fuels'], "powerplants" : powerplantsDict['powerplants']}
        
        databaseDict = {x['name'] :[] for x in powerplantsDict['powerplants']}
        
        key_list = ['name', 'p']
        
        
        nameList = [x['name'] for x in powerplantsDict['powerplants']]
        instanceDict = {}

        for i in range(len(nameList)):
            instanceDict['PowerPlant_%s' % str(i)] = PowerPlant()
            instanceDict['PowerPlant_%s' % str(i)]._name = powerplantsDict['powerplants'][i]['name']
            instanceDict['PowerPlant_%s' % str(i)]._pType =  powerplantsDict['powerplants'][i]['type']
            instanceDict['PowerPlant_%s' % str(i)]._efficiency = powerplantsDict['powerplants'][i]['efficiency'] 
            instanceDict['PowerPlant_%s' % str(i)]._pmin = powerplantsDict['powerplants'][i]['pmin']
            if instanceDict['PowerPlant_%s' % str(i)]._pType =='windturbine':
                instanceDict['PowerPlant_%s' % str(i)]._pmax = int(powerplantsDict['powerplants'][i]['pmax']*(fuelsDict['fuels']["wind(%)"]/100))
            else:
                instanceDict['PowerPlant_%s' % str(i)]._pmax = powerplantsDict['powerplants'][i]['pmax'] 
           
            instanceDict['PowerPlant_%s' % str(i)]._fuels = fuelsDict['fuels']
            instanceDict['PowerPlant_%s' % str(i)].Carbon_Cost()
            instanceDict['PowerPlant_%s' % str(i)].Choose_Fuel()
            instanceDict['PowerPlant_%s' % str(i)].Merit_Value()
            
       
        meritOrd = Merit_Order(instanceDict)
        pDict, errorCode = Unit_Commit(meritOrd, dataOuterDict['load']) 
       
       
        if flask.request.method == 'POST':
            return jsonify(pDict), errorCode

def Merit_Order(objDict):
    meritOrderUnSorted={}
    listOfObj = list(objDict.values())
    listOfObj.sort(key=lambda x: x._meritVal, reverse=False)
    return listOfObj


def Unit_Commit(mer_Ord, load): 
   errorCode =200
   maxPow = 0
   for k in range(len(mer_Ord)):
       maxPow += mer_Ord[k]._pmax
   if maxPow < load:
       app.logger.error('Load too high for available power plants to meet demand.')
       
   initialLoad = load
   pDict = [OrderedDict({'name' : "", 'p':0}) for i in range(len(mer_Ord))]
   noNeg = 'null' # used to find index where pmin exceeds load remaining to supply
   for i in range(len(mer_Ord)):
       if mer_Ord[i].pmax <= load:
           pDict[i]['name'] = mer_Ord[i]._name
           pDict[i]['p'] = mer_Ord[i]._pmax
           load -= mer_Ord[i]._pmax
       elif mer_Ord[i]._pmax > load:
           if mer_Ord[i]._pmin <= load:
               pDict[i]['name'] = mer_Ord[i]._name
               pDict[i]['p'] = load
               load =0
           elif mer_Ord[i]._pmin >load and load ==0:
               pDict[i]['name'] = mer_Ord[i]._name
               pDict[i]['p'] =0# mer_Ord[i]._pmin
           elif mer_Ord[i]._pmin >load and load >0:
               pDict[i]['name'] = mer_Ord[i]._name
               pDict[i]['p'] = load 
               load = 0
               noNeg = i
       elif load <=0: 
           pDict[i]['name'] = mer_Ord[i]._name
           pDict[i]['p'] = 0
          
   if not noNeg == 'null' and pDict[noNeg]['p'] < mer_Ord[noNeg]._pmin:
         remainder = (mer_Ord[noNeg]._pmin-abs(load))
         pDict[noNeg-1]['p'] -= remainder
         pDict[noNeg]['p'] += remainder
   elif load <0 and len(pDict) <=1:
        app.logger.error('Load is below Pmin of all plants.')
   check =0
   for i in range(len(pDict)): 
        check += pDict[i]['p'] 
   if check > initialLoad or check < initialLoad:
        app.logger.error('Final output does not match load. Internal error. ')
        errorCode =500
   return pDict, errorCode



if __name__ == '__main__':
    app.run() 
    