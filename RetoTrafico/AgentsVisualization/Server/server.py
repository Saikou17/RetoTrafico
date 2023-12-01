# TC2008B. Sistemas Multiagentes y Gráficas Computacionales
# Python flask server to interact with Unity. Based on the code provided by Sergio Ruiz.
# Juan Pablo Cruz Rodriguez A01783208. October 2023git 
#Juan Pablo Robles Arenas A01374091

from flask import Flask, request, jsonify
# from randomAgents.model import RandomModel
from randomAgents.model2 import CityModel
# from randomAgents.agent import RandomAgent, ObstacleAgent
from randomAgents.agent2 import Car, Road, Traffic_Light, Destination, Spawn, Obstacle


app = Flask("Traffic example")

@app.route('/init', methods=['POST'])
def initModel():
    global currentStep, cityModel

    if request.method == 'POST':
       
        currentStep = 0

        print(request.form)
    
        cityModel = CityModel()

        return jsonify({"message":"Parameters recieved, model initiated."})

@app.route('/getAgents', methods=['GET'])
def getAgents():
    global cityModel

    if request.method == 'GET':
        agentPositions = [{"id": str(agent.unique_id), "x": pos[0], "y":0, "z":pos[1]} 
                          for agents, pos in cityModel.grid.coord_iter() 
                          for agent in agents
                          if isinstance(agent, Car)]

        return jsonify({'positions':agentPositions})

@app.route('/getObstacles', methods=['GET'])
def getObstacles():
    global cityModel

    if request.method == 'GET':
        obstaclePositions = [{"id": str(agent.unique_id), "x": pos[0], "y":0, "z":pos[1]} 
                          for agents, pos in cityModel.grid.coord_iter() 
                          for agent in agents
                          if isinstance(agent, Obstacle)]
        
        return jsonify({'positions':obstaclePositions})

@app.route('/getRoads', methods=['GET'])
def getRoads():
    global cityModel

    if request.method == 'GET':
        roadPositions = [{"id": str(agent.unique_id), "x": pos[0], "y":0, "z":pos[1],"Direction":agent.direction} 
                          for agents, pos in cityModel.grid.coord_iter() 
                          for agent in agents
                          if isinstance(agent, Road)]

        return jsonify({'positions':roadPositions})

@app.route('/getTrafficLights', methods=['GET'])
def getTrafficLights():
    global cityModel

    if request.method == 'GET':
        trafficLightPositions = [{"id": str(agent.unique_id), "x": pos[0], "y":0, "z":pos[1], "Direction":agent.direction, "state":agent.state} 
                                for agents, pos in cityModel.grid.coord_iter() 
                                for agent in agents
                                if isinstance(agent, Traffic_Light)]

        return jsonify({'positions':trafficLightPositions})

@app.route('/getDestinations', methods=['GET'])
def getDestinations():
    global cityModel

    if request.method == 'GET':
        destinationPositions = [{"id": str(agent.unique_id), "x": pos[0], "y":0, "z":pos[1]} 
                                for agents, pos in cityModel.grid.coord_iter() 
                                for agent in agents
                                if isinstance(agent, Destination)]

        return jsonify({'positions':destinationPositions})

@app.route('/getSpawns', methods=['GET'])
def getSpawns():
    global cityModel

    if request.method == 'GET':
        spawnPositions = [{"id": str(agent.unique_id), "x": pos[0], "y":0, "z":pos[1]} 
                          for agents, pos in cityModel.grid.coord_iter() 
                          for agent in agents
                          if isinstance(agent, Spawn)]

        return jsonify({'positions':spawnPositions})

@app.route('/getDead', methods=['GET'])
def getDead():
    global cityModel

    if request.method == 'GET':
        deadPositions = [{"id": agent} 
                          for agent in cityModel.arrived]

        return jsonify({'positions':deadPositions})

@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, cityModel
    if request.method == 'GET':
        cityModel.step()
        currentStep += 1
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})

if __name__=='__main__':
    app.run(host="localhost", port=8585, debug=True)