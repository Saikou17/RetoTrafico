#Juan Pablo Cruz Rodriguez
from mesa import Model, DataCollector
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import *
import json
import networkx as nx

class CityModel(Model):
    """ 
        Creates a model based on a city map.

        Args:
            N: Number of agents in the simulation
    """
    def __init__(self,N):

        # Load the map dictionary. The dictionary maps the characters in the map file to the corresponding agent.
        dataDictionary = json.load(open("city_files/mapDictionary.json"))
        #Variable para inicializar el modelo
        self.initialize = False
        #Variable que guarda todos los destinos ddel mapa
        self.destinations = []
        #Variable que guarda todos los elementos de la ciudad menos los obstaculos
        self.city = []
        #Recolectar informacion acerca de los choques
        self.datacollector = DataCollector( 
                model_reporters = {
                        "Car collision": lambda m: 1 if m.checkCollision() else 0,
            })
        self.arrived = []
        
        # Load the map file. The map file is a text file where each character represents an agent.
        with open('city_files/2023_base.txt') as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0])-1
            self.height = len(lines)
            self.grid = MultiGrid(self.width, self.height, torus = False) 
            self.schedule = RandomActivation(self)

            # Goes through each character in the map file and creates the corresponding agent.
            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    if col in ["v", "^", ">", "<","*","+"]:
                        #El agente camino se inicializa con (id,model,direccion,sentido de la calle)
                        agent = Road(f"r_{r*self.width+c}", self, dataDictionary[col]["Direction"],dataDictionary[col]["Value"])
                        #Agregamos al grid
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        #Agregamos a nuestro lista de ciudad de elementos
                        self.city.append(agent)


                    elif col in ["N","n","S", "s","E","e","W","w"]:
                        #El agente semaforo se inicaliza con (id,model,direccion,sentido del semaforo,estado del semaforo,tiempo)
                        agent = Traffic_Light(f"tl_{r*self.width+c}", self,dataDictionary[col]["Direction"],dataDictionary[col]["Value"], False if col == "S" else True, int(dataDictionary[col]["Time"]))
                        #Agregamos al grid
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        #Agregamos al schedule
                        self.schedule.add(agent)
                        #Agregamos a nuestro lista de ciudad de elementos
                        self.city.append(agent)

                    elif col == "#":
                        #El agente obstaculo se inicializa con (id,model)
                        agent = Obstacle(f"ob_{r*self.width+c}", self)
                        #Agregamos al grid
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col == "D":
                        #El agente destino se inicializa con (id,model,direccion,sentido)
                        agent = Destination(f"d_{r*self.width+c}", self, dataDictionary[col]["Direction"],dataDictionary[col]["Value"])
                        #Agregamos al grid
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        #Agregamos los destinos a nuestra lista
                        self.destinations.append(agent)
                        #Agregamos a nuestra lista de ciudad
                        self.city.append(agent)
                    
                    elif col in ["1","2","3","4"]:
                        #El agente spawn se inicializa con (id,model,direccion,sentido)
                        agent = Spawn(f"s_{r*self.width+c}_{self.schedule.steps}", self, dataDictionary[col]["Direction"],dataDictionary[col]["Value"])
                        #Agregamos al grid
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        #Agregamos al schedule
                        self.schedule.add(agent)
                        #Agregamos a nuestra lista de ciudad
                        self.city.append(agent)
                        #Inicializamos cuatro coches al inicio para la prueba
                        agent = Car(f"c_{r*self.width+c}", self)
                        self.schedule.add(agent)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

        #Creamos un grafo direccionado vacio
        self.graph = nx.DiGraph()
        #Llamamos nuestra funcion de crear el grafo direccionado completo
        self.create_graph()
        self.num_agents = N
        # self.running = True

    #Funcion que revisa si hay alguna colision dentro de la simulacion
    def checkCollision(self):
        for i in range(self.width):
            for j in range(self.height):
                if len(self.grid[i][j]) >= 3:
                    for x in self.grid[i][j]:
                        if isinstance(x, Destination):
                            return False
                    print("---------------------")
                    print(f"Colition at: ({i}, {j})")
                    for x in self.grid[i][j]:
                        if not isinstance(x, Road):
                            print(x.unique_id)
                    self.running = False
                    return True
        
    def create_graph(self):
        """
        Creates a graph based on the city grid.
        """
        #Los nodos son los elementos de nuestra lista de ciudad
        for nodo in self.city:
            #Los nodos son las posiciones de nuestros elementos
            self.graph.add_node(nodo.pos)

        #Las aristas son las conexiones entre los elementos de la lista de ciudad
        for camino in self.city:
            #Conectamos si el elemento es instancia de camino , semaforo y spawn
            if isinstance(camino,Road) or isinstance(camino,Traffic_Light) or isinstance(camino,Spawn):
                #Si tienen sentido a la izquierda
                if camino.direction == "Left":
                    #Obtenemos los vecinos y el centro del agente
                    conexiones = self.grid.get_neighbors(camino.pos,moore = True,include_center=False,radius=1)
                    #Conectamos los elementos que sean menor a la posicion en x y las diagonales verificamos el sentido
                    direccion = [agente for agente in conexiones if isinstance(agente,(Road,Traffic_Light,Destination,Spawn)) and
                                 agente.pos[0]<camino.pos[0] and 
                                 ((agente.pos[1]-camino.pos[1] >= 0 and agente.sense["y"] >= 0) or (agente.pos[1]-camino.pos[1] <= 0 and agente.sense["y"] <= 0))]           
                    #Agregamos la arista o conexion
                    for i in direccion:
                        self.graph.add_edge(camino.pos,i.pos)

                #Si tienen sentido a la derecha        
                elif camino.direction == "Right":
                    #Obtenemos los vecinos y el centro del agente
                    conexiones = self.grid.get_neighbors(camino.pos,moore = True,include_center=False,radius=1)
                    #Conectamos los elementos que sean mayor a la posicion en x y las diagonales verificamos el sentido
                    direccion = [agente for agente in conexiones if isinstance(agente,(Road,Traffic_Light,Destination,Spawn)) and
                                 agente.pos[0]>camino.pos[0] and 
                                 ((agente.pos[1]-camino.pos[1] >= 0 and agente.sense["y"] >= 0) or (agente.pos[1]-camino.pos[1] <= 0 and agente.sense["y"] <= 0))]
                    #Agregamos la arista o conexion
                    for i in direccion:
                        self.graph.add_edge(camino.pos,i.pos)

                #Si tienen sentido hacia arriba
                elif camino.direction == "Up":
                    #Obtenemos los vecinos y el centro del agente
                    conexiones = self.grid.get_neighbors(camino.pos,moore = True,include_center=False,radius=1)
                    #Conectamos los elementos que sean mayor a la posicion en y y las diagonales verificamos el sentido
                    direccion = [agente for agente in conexiones if isinstance(agente,(Road,Traffic_Light,Destination,Spawn)) and
                                 agente.pos[1]>camino.pos[1] and 
                                 ((agente.pos[0]-camino.pos[0] >= 0 and agente.sense["x"] >= 0) or (agente.pos[0]-camino.pos[0] <= 0 and agente.sense["x"] <= 0))]
                    #Agregamos la arista o conexion
                    for i in direccion:
                        self.graph.add_edge(camino.pos,i.pos)

                #Si tienen sentido hacia abajo
                elif camino.direction == "Down":
                     #Obtenemos los vecinos y el centro del agente
                    conexiones = self.grid.get_neighbors(camino.pos,moore = True,include_center=False,radius=1)
                    #Conectamos los elementos que sean menor a la posicion en y y las diagonales verificamos el sentido
                    direccion = [agente for agente in conexiones if isinstance(agente,(Road,Traffic_Light,Destination,Spawn)) and
                                 agente.pos[1]<camino.pos[1] and 
                                 ((agente.pos[0]-camino.pos[0] >= 0 and agente.sense["x"] >= 0) or (agente.pos[0]-camino.pos[0] <= 0 and agente.sense["x"] <= 0))]
                    #Agregamos la arista o conexion
                    for i in direccion:
                        self.graph.add_edge(camino.pos,i.pos)

                #Si son intersecciones hacia arriba
                elif camino.direction == "IntersectionUp":
                    #Obtenemos los vecinos y el centro del agente
                    conexiones = self.grid.get_neighbors(camino.pos,moore = True,include_center=False,radius=1)
                    #Conectamos los elementos que sean mayor a la posicion en y
                    direccion = [agente for agente in conexiones if agente.pos[1]>camino.pos[1]]
                    #Agregamos la arista o conexion
                    for i in direccion:
                        self.graph.add_edge(camino.pos,i.pos)

                 #Si son intersecciones hacia abajo
                elif camino.direction == "IntersectionDown":
                    #Obtenemos los vecinos y el centro del agente
                    conexiones = self.grid.get_neighbors(camino.pos,moore = True,include_center=False,radius=1)
                    #Conectamos los elementos que sean menor a la posicion en y
                    direccion = [agente for agente in conexiones if agente.pos[1]<camino.pos[1]]
                    #Agregamos la arista o conexion
                    for i in direccion:
                        self.graph.add_edge(camino.pos,i.pos)

    def step(self):
        '''Advance the model by one step.'''
        #Activamos el primer step
        self.schedule.step()
        #Recolectamos informacion
        self.datacollector.collect(self)
        #Inicializamos el modelo
        if not self.initialize:
            self.initialize = True

        print(len(self.arrived))
        
        
            
