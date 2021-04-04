"""
load = sum of power output
do not exceed pmax, or lower than pmin.


#set up output dict ->


"""
import flask
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/')# homepage

#POST to route -> handle object
def hello_world():
    return 'Hello, World!'


         
@app.route('/productionplan/', methods= ['GET', 'POST'])
def productionplan():
    
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
        
        
        # list comprehension combined with dict comprehension?
        
        key_list = ['name', 'p']
        
        nameList = [x['name'] for x in powerplantsDict['powerplants']]
        
        #for loop evaluating each p 
        pList = [75, 50, 0,2,0,0]

        listOut = [{key_list[0]: nameList[idx], key_list[1]: pList[idx]} for idx in range(len(nameList))]
       
        if flask.request.method == 'POST':
            return jsonify(listOut), 200
    



if __name__ == '__main__':
    app.run() 
    """
    request_data = request.get_json()
        language = None
        framework = None
        python_version = None
        example = None
        boolean_test = None
    
        if request_data:
            if 'language' in request_data:
                language = request_data['language']
    
            if 'framework' in request_data:
                framework = request_data['framework']
    
            if 'version_info' in request_data:
                if 'python' in request_data['version_info']:
                    python_version = request_data['version_info']['python']
    
            if 'examples' in request_data:
                if (type(request_data['examples']) == list) and (len(request_data['examples']) > 0):
                    example = request_data['examples'][0]
    
            if 'boolean_test' in request_data:
                boolean_test = request_data['boolean_test']
    
        return '''
                The language value is: {}
                The framework value is: {}
                The Python version is: {}
                The item at index 0 in the example list is: {}
                The boolean value is: {}'''.format(language, framework, python_version, example, boolean_test)
       """