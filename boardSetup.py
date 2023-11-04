import random

PortVertices = {(0,4):"ore",(0,5):"ore",(0,7):"ex", (0,8):"ex",(1,1):"grain",(1,2): "grain", (1,11):"sheep",(2,11):"sheep", (3,11):"ex",(4,11):"ex", (5,7):"ex",(5,8):"ex",(5,5):"clay",(5,4):"clay",(4,2):"wood",(4,1):"wood",(2,0):"ex",(3,0):"ex"}

class Board:
    def __init__(self, layout=None):
        self.numRows=len(layout.map)
        self.numColumns=max(layout.map)
        self.hexagons = [[None for x in range(self.numColumns)] for x in range(self.numRows)] 
        self.edges = [[None for x in range(self.numColumns*2+2)] for x in range(self.numRows*2+2)] 
        self.vertices = [[None for x in range(self.numColumns*2+2)] for x in range(self.numRows*2+2)]
        
        #fill Hexagons based on map
        fields=squash_dict(layout.fields)
        seed=squash_dict(layout.seed)
        for i in range(self.numRows):
           numZeros=self.numRows-layout.map[i]
           add = numZeros % 2
           for j in range(int(numZeros/2)+add, self.numColumns-int(numZeros/2)):
                    random_field = random.choice(fields)
                    if random_field == "desert":
                        random_seed = None
                    else:
                        random_seed = random.choice(seed)
                    self.hexagons[i][j]=Hexagon(i,j,random_seed, random_field)
                    fields.remove(random_field)
                    if random_field != "desert":
                        seed.remove(random_seed)
        
        #fill Edges and Vertices
        for row in self.hexagons:
            for hex in row:
                if hex == None: continue
                edgeLocations = self.getEdgeLocations(hex)
                vertexLocations = self.getVertexLocations(hex)
                for xLoc,yLoc in edgeLocations:
                    if self.edges[xLoc][yLoc] == None:
                        self.edges[xLoc][yLoc] = Edge(xLoc,yLoc)
                for xLoc,yLoc in vertexLocations:
                    if self.vertices[xLoc][yLoc] == None:
                        self.vertices[xLoc][yLoc] = Vertex(xLoc,yLoc)
        
        #Create Ports
        for row in self.vertices:
            for vertex in row:
                if vertex:
                    if (vertex.X, vertex.Y) in PortVertices.keys():
                        vertex.portType = PortVertices[(vertex.X, vertex.Y)]

    # used to initially create vertices
    def getVertexLocations(self, hex):
        vertexLocations=[]
        x=hex.X
        y=hex.Y
        offset= 0 - (x % 2)
        vertexLocations.append((x, 2*y+offset))
        vertexLocations.append((x, 2*y+1+offset))
        vertexLocations.append((x, 2*y+2+offset))
        vertexLocations.append((x+1, 2*y+offset))
        vertexLocations.append((x+1, 2*y+1+offset))
        vertexLocations.append((x+1, 2*y+2+offset))
        return vertexLocations
    
    # used to initially create edges
    def getEdgeLocations(self, hex):
        edgeLocations = []
        x = hex.X
        y = hex.Y
        offset= 0 - (x % 2)
        edgeLocations.append((2*x,2*y+offset))
        edgeLocations.append((2*x,2*y+1+offset))
        edgeLocations.append((2*x+1,2*y+offset))
        edgeLocations.append((2*x+1,2*y+2+offset))
        edgeLocations.append((2*x+2,2*y+offset))
        edgeLocations.append((2*x+2,2*y+1+offset))
        return edgeLocations
    
    #get vertices of created hex
    def getVertices(self, hex):
        hexVertices=[]
        x = hex.X
        y = hex.Y
        offset = 0 - (x % 2)
        hexVertices.append(self.vertices[x][2*y+offset]) # top left vertex
        hexVertices.append(self.vertices[x][2*y+1+offset]) # top vertex
        hexVertices.append(self.vertices[x][2*y+2+offset]) # top right vertex
        hexVertices.append(self.vertices[x+1][2*y+offset]) # bottom left vertex
        hexVertices.append(self.vertices[x+1][2*y+1+offset]) # bottom vertex
        hexVertices.append(self.vertices[x+1][2*y+2+offset]) # bottom right vertex
        return hexVertices

    #get edges of created hex
    def getEdges(self, hex):
        hexEdges = []
        x = hex.X
        y = hex.Y
        offset= 0 - (x % 2)
        hexEdges.append(self.edges[2*x][2*y+offset])
        hexEdges.append(self.edges[2*x][2*y+1+offset])
        hexEdges.append(self.edges[2*x+1][2*y+offset])
        hexEdges.append(self.edges[2*x+1][2*y+2+offset])
        hexEdges.append(self.edges[2*x+2][2*y+offset])
        hexEdges.append(self.edges[2*x+2][2*y+1+offset])
        return hexEdges
    
    #get neigbours of a hex
    def getNeighbours(self, hex):
        neighbours=[]
        x = hex.X
        y = hex.Y
        offset= 1
        if x > 0: # North
            hexOne = self.hexagons[x-1][y]
            if hexOne != None: neighbours.append(hexOne)
        if x > 0: #North-east(even)/North-west(odd)
            hexTwo = self.hexagons[x-1][y+offset]
            if hexTwo != None: neighbours.append(hexTwo)
        if (y+1) < len(self.hexagons[x]): #east
            hexThree = self.hexagons[x][y+1]
            if hexThree != None: neighbours.append(hexThree)
        if (y+offset) >= 0 and (y+offset) < len(self.hexagons[x]): #South-east (even)/South-west (odd)
            if (x+1) < len(self.hexagons):
                hexFour = self.hexagons[x+1][y+offset]
                if hexFour != None: neighbours.append(hexFour)
        if (x+1) < len(self.hexagons): #down
            hexFive = self.hexagons[x+1][y] 
            if hexFive != None: neighbours.append(hexFive)
        if y > 0: #West
            hexSix = self.hexagons[x][y-1] 
            if hexSix != None: neighbours.append(hexSix)
        return neighbours
    
    def getNeighbourVertices(self, vertex):
        neighbours = []
        x = vertex.X
        y = vertex.Y
        offset = -1
        if x % 2 == y % 2: offset = 1
        # Logic from thinking that this is saying getEdgesOfVertex
        # and then for each edge getVertexEnds, taking out the three that are ==vertex
        if (y+1) < len(self.vertices[0]):
            vertexOne = self.vertices[x][y+1]
            if vertexOne != None: neighbours.append(vertexOne)
        if y > 0:
            vertexTwo = self.vertices[x][y-1]
            if vertexTwo != None: neighbours.append(vertexTwo)
        if (x+offset) >= 0 and (x+offset) < len(self.vertices):
            vertexThree = self.vertices[x+offset][y]
            if vertexThree != None: neighbours.append(vertexThree)
        return neighbours


    # returns (start, end) tuple
    def getVertexEnds(self, edge):
        x = edge.X
        y = edge.Y
        if x%2 == 1:
            vertexOne = self.vertices[int((x-1)/2)][y]
            vertexTwo = self.vertices[int((x+1)/2)][y]
        else:
            vertexOne = self.vertices[int(x/2)][y]
            vertexTwo = self.vertices[int(x/2)][y+1]
        return (vertexOne, vertexTwo)

    def getEdgesOfVertex(self, vertex):
        vertexEdges = []
        x = vertex.X
        y = vertex.Y
        offset = -1
        if x % 2 == y % 2: offset = 1
        edgeOne = self.edges[x*2][y-1]
        edgeTwo = self.edges[x*2][y]
        edgeThree = self.edges[x*2+offset][y]
        if edgeOne != None: vertexEdges.append(edgeOne)
        if edgeTwo != None: vertexEdges.append(edgeTwo)
        if edgeThree != None: vertexEdges.append(edgeThree)
        return vertexEdges

    # get hexes bordering vertex
    def getHexes(self, vertex):
        vertexHexes = []
        x = vertex.X
        y = vertex.Y
        xOffset = x % 2
        yOffset = y % 2

        if x < len(self.hexagons) and y/2 < len(self.hexagons[x]):
            hexOne = self.hexagons[x][y/2]
            if hexOne != None: vertexHexes.append(hexOne)

        weirdX = x
        if (xOffset+yOffset) == 1: weirdX = x-1
        weirdY = y/2 
        if yOffset == 1: weirdY += 1
        else: weirdY -= 1
        if weirdX >= 0 and weirdX < len(self.hexagons) and weirdY >= 0 and weirdY < len(self.hexagons):
            hexTwo = self.hexagons[weirdX][weirdY]
            if hexTwo != None: vertexHexes.append(hexTwo)

        if x > 0 and x < len(self.hexagons) and y/2 < len(self.hexagons[x]):
            hexThree = self.hexagons[x-1][y/2]
            if hexThree != None: vertexHexes.append(hexThree)

        return vertexHexes
    
    #check if building on vertex is legal
    def buildVertexLegal(self, vertex):
        neighbours=self.getNeighbourVertices(vertex)
        for neighbour in neighbours:
            if neighbour.village != None or neighbour.city !=None: return False
        return True

    #check if building road on edge is legal
    def buildRoadLegal(self, edge, player):
        if edge.road!=None:
            raise Exception("Edge already occupied")
        else:
            vertices_ends = self.getVertexEnds(edge)
            for vertex in vertices_ends:
                if vertex.city == player or vertex.village == player: return True
                else:
                    for neighbour_edge in self.getEdgesOfVertex(vertex):
                        if neighbour_edge.road == player: return True
            return False
    
    #move bandit location

    def moveBanditLocation(self, hex_location):
        for hex in self.hexagons:
            if hex != None:
                if hex.bandit == True:
                    hex.bandit == False
        self.hexagons(hex_location).bandit=True
            




    #print map
    def printMap(self):
        for row in self.hexagons:
            displayRow=[]
            for hex in row:
                if hex==None:
                    displayRow.append("-")
                else:
                    displayRow.append(hex.resource)
            print(displayRow)



      
    

class Hexagon:
    def __init__(self,X=None, Y=None, seed=None, resource=None):
        self.X=X
        self.Y=Y
        self.seed=seed
        self.resource=resource
        self.bandit=False

class Vertex:
    def __init__(self,X=None, Y=None):
        self.X=X
        self.Y=Y
        self.village=None
        self.city=None
        self.portType=None


    
    def add_village(self, player):
        if self.village != None or self.city !=None:
            raise Exception("Field's already occupied")
        else:
            self.village = player
            print(f"Building a village for player {player} on a vertex [{self.X},{self.Y}]")


    
    def add_city(self, player):
        if self.city == player:
            raise Exception(f"Player {player} already has a city on coordinates [{self.X},{self.Y}]")
        elif self.village != player:
            raise Exception(f"Player {player} does not have a village on vertex [{self.X},{self.Y}]")
        else:
            self.city = player
            self.village = None
            print(f"Building a city for player {player} on a vertex [{self.X},{self.Y}]")


    
    def add_port(self,portType):
        self.isPort=True
        self.portType=portType

class Edge:
    def __init__(self,X=None, Y=None):
        self.X=X
        self.Y=Y
        self.road=None
    
    def add_road(self,player):
        if self.road!=None:
            raise Exception("Edge already occupied")
        else:
            self.road = player
            print(f"Building a road for player {player} on a edge [{self.X},{self.Y}]")


def squash_dict(dict):
    list=[]
    for key in dict.keys():
        list+=([key]*dict[key])
    return list