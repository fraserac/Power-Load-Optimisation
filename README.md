# Power Load Optimisation

This project involves building a REST api that can accept POST requests with information about load requirements and specifications of various powerplants. Upon receiving the POST, the api calculates a merit order and then uses this to optimise cost when choosing how much power each plant should be supplying in order to match the required load. **The effect of the cost of the carbon dioxide production of gas powered plants** is also included in the merit order calculation. 

# Getting it running

To run this code, you can install the dependencies via the included requirements.txt file in this repository. 

After installing flask, you can then open a powershell application.

Within powershell you will want to create a virtual environment.

In windows this can be done in the following way: 

First make sure you have virtual environments installed, then cd to the directory you have the energie_rest_api script saved in: 

# In python 2:
py -2 -m venv energyEnvironment

# In python 3:
py -3 -m venv energyEnvironment

Then use the command:

energyEnvironment\Scripts\activate

Then simply type:

flask run 


# To send a POST request, you can use Postman software. 
Set up a new POST request containing the raw json file (payload) in the body. Send to the url given by the server in the powershell console. To reach the endpoint production plan, add /productionplan to the url and send the request.

The response will contain the desired output or if the input is problematic, the powershell console will log an error message and the Postman application will receive an error response code. 
