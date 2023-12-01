"""
Juan Pablo Cruz Rodriguez A01783208
Juan Pablo RObles Arenas A01374091
"""

from mesa import Agent
import random
import networkx as nx
import matplotlib.pyplot as plt


class Car(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of eight directions
        acciones: List of actions that the agent can take
        1. Move forward
        2. See the traffic light
        3. See the destination
        4. See the obstacle
        5. Stop at traffic light
        6. Wait one step
    """
    def __init__(self, unique_id, model):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
        #Creamos un estadp que indique en que sentido va el carro: Izquierda, Derecha, Arriba o Abajo
        self.direction = ""
        #Creamos un estado que indique como se encuentra el carro: Estatico o Movimiento
        self.state = "Movimiento"
        #Inicializamos una variable como None , la cual guardara el destino aleatorio del carro
        self.destination = None
        #Variable para iniciar la simulacion
        self.iniciar = False
        #Variable que guarda la vision del carro
        self.vision = []
        #Guardamos la ruta al destino
        self.route = []
        
        
    #Funcion para iniializar la simulacion
    def Check_Model_Initialize(self):
        
        self.destination = random.choice(self.model.destinations)
        self.route = nx.shortest_path(self.model.graph, source=self.pos, target=self.destination.pos)
        self.route = self.route[1:]

    def recalculate_route(self,next):

        self.route = nx.shortest_path(self.model.graph, source=next, target=self.destination.pos)

    #Funcion que se llama cuando las celdas 
    def move(self):
        """
        Determina si el agente puede moverse en la dirección elegida
        """
        self.see_enviroment()
        
        if self.state == "Movimiento":

            if any(isinstance(a, Car) for a in self.vision):
                self.move_around()
            
            elif any(isinstance(a,Traffic_Light) for a in self.vision):
                self.see_traffic_light()
            
            else:
                self.model.grid.move_agent(self,self.route[0])
                self.route.pop(0)   

        elif self.state == "Estatico":

            if any(isinstance(a, Car) for a in self.vision):
                self.move_around()
            
            elif any(isinstance(a,Traffic_Light) for a in self.vision):
                self.see_traffic_light()

            else:
                self.state = "Movimiento"
                self.model.grid.move_agent(self,self.route[0])
                self.route.pop(0)
            

    def move_around(self):
        """
        Determina si el agente puede moverse en la dirección elegida
        """
        possible_path = []
        empty_spaces = [empty for empty in self.vision if empty.pos in list(self.model.graph.successors(self.pos)) ]
        for empty in empty_spaces:
            cell_contents = self.model.grid.get_cell_list_contents([empty.pos])
            if not any(isinstance(c,(Car,Destination,Obstacle)) for c in cell_contents):
                possible_path.append(empty.pos)

        if possible_path == []:
            self.state = "Estatico"
        else:
            self.state = "Movimiento"
            next_move = random.choice(possible_path)
            self.model.grid.move_agent(self,next_move)
            self.recalculate_route(next_move)


    def stop(self):
        """ 
        Determines if the agent should stop at the traffic light
        """
        pass
    
    #Funcion que usamos para guardar informacion de nuestra vision y direccion
    def see_enviroment(self):
        """ 
        Determines if the agent can see the enviroment
        """
        self.vision = self.model.grid.get_neighbors(self.pos,moore=True,include_center=True,radius=1)
        self.direction = [center.direction for center in self.vision if center.pos == self.pos and not isinstance(center,Car)][0]

        if self.direction == "Left":
            self.vision = [vision for vision in self.vision if vision.pos[0]<self.pos[0] and vision.pos != self.pos]
        elif self.direction == "Right":
            self.vision = [vision for vision in self.vision if vision.pos[0]>self.pos[0] and vision.pos != self.pos]
        elif self.direction == "Up":
            self.vision = [vision for vision in self.vision if vision.pos[1]>self.pos[1] and vision.pos != self.pos]
        elif self.direction == "Down":
            self.vision = [vision for vision in self.vision if vision.pos[1]<self.pos[1] and vision.pos != self.pos]
        elif self.direction == "Intersection":
            self.vision = [vision for vision in self.vision if vision.pos[1]>self.pos[1] and vision.pos != self.pos]
        elif self.direction == "Destination":
            self.model.arrived.append(self.unique_id)
            self.model.grid.remove_agent(self)
            self.state = "Destino Alcanzado"


    
    def see_traffic_light(self):
        """ 
        Determines if the agent can see the traffic light
        """
        ligths = [lights for lights in self.vision if isinstance(lights,Traffic_Light) and lights.pos in list(self.model.graph.successors(self.pos)) ]

        if ligths == []:
            self.model.grid.move_agent(self,self.route[0])
            self.route.pop(0) 
        else:
            if ligths[0].state == False:
                self.state = "Estatico"
            else:
                self.state = "Movimiento"
                self.model.grid.move_agent(self,self.route[0])
                self.route.pop(0) 


    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        
        print(self.model.arrived)

        if self.iniciar == False:
            self.Check_Model_Initialize()
            self.iniciar = True
        
        elif self.state == "Destino Alcanzado":
            return None

        else:
            self.move()
                
        

class Traffic_Light(Agent): 
    """
    Traffic light. Where the traffic lights are in the grid.
    """
    def __init__(self, unique_id, model, direction, sense, state = False, timeToChange = 10):
        super().__init__(unique_id, model)
        """
        Creates a new Traffic light.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            state: Whether the traffic light is green or red
            timeToChange: After how many step should the traffic light change color 
        """
        self.direction = direction
        self.sense = sense
        self.state = state
        self.timeToChange = timeToChange

    def step(self):
        """ 
        To change the state (green or red) of the traffic light in case you consider the time to change of each traffic light.
        """
        if self.model.schedule.steps % self.timeToChange == 0:
            self.state = not self.state

class Destination(Agent):
    """
    Destination agent. Where each car should go.
    """
    def __init__(self, unique_id, model,direction,sense):
        super().__init__(unique_id, model)
        self.direction = direction
        self.sense = sense

    def step(self):
        pass

class Obstacle(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Road(Agent):

    """
    Road agent. Determines where the cars can move, and in which direction.
    """
    def __init__(self, unique_id, model, direction, sense):
        """
        Creates a new road.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            direction: Direction where the cars can move
        """
        #FUncion para inicializar el agente
        super().__init__(unique_id, model)
        #Variable que guarda la direccion del agente
        self.direction = direction
        #Variable que guarda el sentido (valor 1 o -1)
        self.sense = sense

    def step(self):
        pass

class Spawn(Agent):
    
        """
        Spawn agent. Determines where the cars can move, and in which direction.
        """
        def __init__(self, unique_id, model, direction, sense):
            """
            Creates a new road.
            Args:
                unique_id: The agent's ID
                model: Model reference for the agent
                direction: Direction where the cars can move
            """
            #FUncion para inicializar el agente
            super().__init__(unique_id, model)
            #Variable que guarda la direccion del agente
            self.direction = direction
            #Variable que guarda el sentido (valor 1 o -1)
            self.sense = sense
    
            self.steps_since_last_spawn = 0  # Contador de pasos

        def step(self):
            # Incrementa el contador de pasos en cada paso
            self.steps_since_last_spawn += 1

            # Verifica si han pasado 10 pasos
            if self.steps_since_last_spawn >= 2:
                # Crea un nuevo agente de carro
                new_car = Car(f"c_{self.pos[1]*self.model.width+self.pos[0]}_{self.model.schedule.steps}", self.model)
                # Coloca el nuevo agente en una posición aleatoria del grid
                self.model.grid.place_agent(new_car,self.pos)
                # Añade el nuevo agente al horario
                self.model.schedule.add(new_car)

                # Reinicia el contador de pasos
                self.steps_since_last_spawn = 0

        
