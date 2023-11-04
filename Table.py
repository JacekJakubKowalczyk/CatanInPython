import random
from boardSetup import Board, squash_dict

class Player:
    def __init__(self, name="Player"):
        self.playerName=name
        self.resources={"wood":10, "clay":10, "grain":1, "ore":1, "sheep":1}
        self.cards=["Monopoly", "Roads"]
        self.cards_from_this_turn=[]
        self.ports = []
        self.knights=0
        self.longestRoad = False
        self.largestArmy = False
        self.victoryPointsShown = 0
        self.victoryPointsHidden = 0

class CardDeck:
    def __init__(self):
        self.cards={"Knight":14,"VictoryPoint":5,"YearOfPlenty":2, "Monopoly":2, "Roads":2}
        temp=squash_dict(self.cards)
        random.shuffle(temp)
        self.cards=temp
    
    def draw_card(self):
        return(self.cards.pop(0))

class Table:
    def __init__(self,map_setup,playerNames):
        self.players=[]
        self.longestRoadLength=0
        self.cards=CardDeck()

        if len(playerNames)<2 or len(playerNames)>4:
            raise Exception("Between two and four players required to play a game of Catan")
        else:
            for name in playerNames:
                self.players.append(Player(name))
            self.gameBoard=Board(map_setup)
    
    def place_village(self, vertex_coordinates, player):
        if(self.gameBoard.buildVertexLegal(self.gameBoard.vertices[vertex_coordinates[0]][vertex_coordinates[1]])):
            self.gameBoard.vertices[vertex_coordinates[0]][vertex_coordinates[1]].add_village(player)
            if self.gameBoard.vertices[vertex_coordinates[0]][vertex_coordinates[1]].portType:
                self.get_player_by_name(player).ports.append(self.gameBoard.vertices[vertex_coordinates[0]][vertex_coordinates[1]].portType)
        else: raise Exception("Failed to place village, illegal field")

    def place_city(self, vertex_coordinates, player):
        if(self.gameBoard.buildVertexLegal(self.gameBoard.vertices[vertex_coordinates[0]][vertex_coordinates[1]])):
            self.gameBoard.vertices[vertex_coordinates[0]][vertex_coordinates[1]].add_city(player)
        else: raise Exception("Failed to place village, illegal field")

    def place_road(self, edge_coordinates, player):
        if self.gameBoard.buildRoadLegal(self.gameBoard.edges[edge_coordinates[0]][edge_coordinates[1]], player):
            self.gameBoard.edges[edge_coordinates[0]][edge_coordinates[1]].add_road(player)
        else: raise Exception("Failed to place road, illegal field")

    def add_resources(self, color, resource, number):
        for player in self.players:
            if player.playerName == color:
                player.resources[resource]+=number
                print(f"Giving player {color} {number} {resource}")

    def move_bandit(self,player, coordinates):
        neighbour_vertices = self.gameBoard.getVertices(self.gameBoard.hexagons[coordinates[0]][coordinates[1]])
        players_in_vertices=[]
        for vertix in neighbour_vertices:
            if vertix.village != None:
                players_in_vertices.append(vertix.village)
            elif vertix.city != None:
                players_in_vertices.append(vertix.city)
        if players_in_vertices:
            selected_player = input(f"Select the player ({players_in_vertices}) to steal resource")
            if selected_player in players_in_vertices:
                if sum(self.get_player_by_name(selected_player).resources.values())>0:
                    resources_list = squash_dict(self.get_player_by_name(selected_player).resources)
                    success=False
                    while success == False:
                        rand = random.choice(resources_list)
                        if self.get_player_by_name(selected_player).resources[rand]>0:
                            self.get_player_by_name(selected_player).resources[rand]-=1
                            success = True
                            self.get_player_by_name(player).resources[rand]+=1
                            print(f"Transfering random resource from player {selected_player} to player {player}")
                else: print(f"Player {selected_player} does not have any resources!")
            else: print("Wrong selection")
        else: print("Hex with no players on vertices was selected")
    
    def give_resources(self, player_name):
        roll=random.randrange(1,7)+random.randrange(1,7)
        print(f"Rolled: {roll}")
        if roll == 7:
            for player in self.players:
                no_resources = sum(player.resources.values())
                if no_resources>7:
                    to_drop=int(no_resources/2)
                    while to_drop>0:
                        print(f"Resources remaining to be dropped: {to_drop}")
                        selected_to_drop = input("Choose resource to drop")
                        if selected_to_drop in (player.resources.keys()):
                            if player.resources[selected_to_drop] > 0:
                                player.resources[selected_to_drop] -= 1
                                to_drop-=1
                            else: print(f"You don't have resource {selected_to_drop}")
                        else: print (f"{selected_to_drop} is not correct selection")
            coordinates = eval(input("Select hex to move Bandit"))
            self.move_bandit(player_name, coordinates)
        else:
            for row in self.gameBoard.hexagons:
                for hex in row:
                    if hex == None:
                        continue
                    elif hex.seed == roll and hex.bandit == False:
                        for vertix in self.gameBoard.getNeighbourVertices(hex):
                            if vertix.city != None:
                                self.add_resources(vertix.city,hex.resource,2)
                            elif vertix.village != None:
                                self.add_resources(vertix.village,hex.resource,1)

    def get_player_by_name(self, selected_player):
        for player in self.players:
            if player.playerName == selected_player:
                return player
            
    def substract_resources(self, selected_player, resources):
        for player in self.players:
            if player.playerName == selected_player:
                for resource in resources.keys():
                    player.resources[resource] -= resources[resource]

    #counting points:

    def count_points(self):
        for player in self.players:
            player_name=player.playerName
            player_points=0
            #count villages and cities
            for row in self.gameBoard.hexagons:
                for hex in row:
                    if hex.village == player_name:
                        player_points += 1
                    elif hex.city == player_name:
                        player_points += 2
            #count knight and road cards:
            if player.longestRoad == True:
                player_points+=2
            if player.largestArmy == True:
                player_points +=2
            player.victoryPointsShown = player_points
            for card in player.cards:
                if card == "Victory Point":
                    player_points +=1
            player.victoryPointsHidden = player_points

    def longest_road_from_edge(self, edge, player, marked, length):
        #if edge has no road, or is already marked, then return lenght as is
        if edge.road != player or (edge.X, edge.Y) in marked:
            return length
        #otherwise, mark the edge...
        else:
            new_marked = list(marked)
            new_marked.append((edge.X, edge.Y))
        #...find its vertices...
            vertices = self.gameBoard.getVertexEnds(edge)
            new_length = int(length)
            for vertex in vertices:
                #print(vertex.X, vertex.Y)
        #... if other's player city is interupting the road, add 1 to lenght and stop exploring this vertix
                if vertex.city not in (None, player) or vertex.village not in (None, player):
                    return length + 1
        #otherwise explore all roads going from the vertix     
                else:
                    edges=self.gameBoard.getEdgesOfVertex(vertex)
                    for new_edge in edges:
                        #print(f"going to edge {new_edge.X}, {new_edge.Y}")
                        explored = self.longest_road_from_edge(new_edge, player, new_marked, length + 1)
                        if new_length<explored:
                            #print(f"end, {explored}")
                            new_length = explored
        return new_length




    
    def longest_road(self):
        longest = 0
        for row in self.gameBoard.edges:
            for edge in row:
                if edge:
                    if edge.road == None: 
                        continue
                    else:
                        player_color=edge.road
                        longest_found=self.longest_road_from_edge(edge,player_color,[],0)
                        if longest_found>longest: 
                            longest = longest_found
                            awarded_player=player_color
        if longest>4:
            if self.longestRoadLength<5:
                print(f"Longest road of lenght {longest} has been just build by player {awarded_player}, assigning card")
                self.get_player_by_name(awarded_player).longestRoad = True
                self.longestRoadLength = longest
            else:
                if longest > self.longestRoadLength:
                    for player in self.players:
                        if player.longestRoad == True:
                            if player.playerName != awarded_player:
                                player.longestRoad = False
                                self.get_player_by_name(awarded_player).longestRoad = True
                                print(f"Player {awarded_player} has built a road longer than previous longest road holder (player {player.playerName}). Current length is {longest} (prev: {self.longestRoadLength}).")
                            else:
                                print(f"Player {awarded_player} is already holding longest road, it is now length {longest} (prev: {self.longestRoadLength})")
        self.longestRoadLength = longest
        return longest








            
#player actions
#building

    def build_road(self, coordinates, player):
        if self.get_player_by_name(player).resources["clay"]>0 and self.get_player_by_name(player).resources["wood"]>0:
            try:
                self.place_road(coordinates, player)
                self.substract_resources(player,{"wood":1, "clay":1})
                print(f"Road built succesfully for player {player} at edge {coordinates}")
                self.longest_road()
            except Exception as error:
                print("Failed to build road")
                print(f"{error}")
        else: print("Not enough resources")

    def build_village(self, coordinates, player):
        if self.get_player_by_name(player).resources["clay"]>0 and self.get_player_by_name(player).resources["wood"]>0 and self.get_player_by_name(player).resources["grain"]>0 and self.get_player_by_name(player).resources["sheep"]>0:
            neighbour_edges=self.gameBoard.getEdgesOfVertex(self.gameBoard.vertices[coordinates[0]][coordinates[1]])
            connected = False
            for edge in neighbour_edges:
                if edge.road == player:
                    connected = True
            if connected:
                try:
                    self.place_village(coordinates, player)
                    self.substract_resources(player,{"wood":1, "clay":1, "grain":1, "sheep":1})
                    print(f"Village built succesfully for player {player} at edge {coordinates}")
                except Exception as error:
                    print("Failed to build village")
                    print(f"{error}")
            else: print("Vertix not connected to the road")
        else: print("Not enough resources")

    def build_city(self, coordinates, player):
        if self.get_player_by_name(player).resources["ore"]>2 and self.get_player_by_name(player).resources["grain"]>1:
            try:
                self.place_city(coordinates, player)
                self.substract_resources(player,{"ore":3, "grain":2})
                print(f"City built succesfully for player {player} at edge {coordinates}")
            except Exception as error:
                print("Failed to build city")
                print(f"{error}")
        else: print("Not enough resources")
    
    def build_development(self, player):
        if self.get_player_by_name(player).resources["ore"]>0 and self.get_player_by_name(player).resources["sheep"]>0 and self.get_player_by_name(player).resources["grain"]>0:
            try:
                draw = self.cards.draw_card()
                self.get_player_by_name(player).cards_from_this_turn.append(draw)
                self.substract_resources(player,{"ore":1, "grain":1, "sheep":1})
                print(f"Card drawn succesfully for player {player}")
            except Exception as error:
                print("Failed to draw card")
                print(f"{error}")
        else: print("Not enough resources")


#trade
    def exchange(self, player, resource_from, resource_to):
        print()
        if resource_from in self.get_player_by_name(player).ports:
            if self.get_player_by_name(player).resources[resource_from]>1:
                self.get_player_by_name(player).resources[resource_from]-=2
                self.get_player_by_name(player).resources[resource_to]+=1
                print(f"Exchanging 2 units of {resource_from} into 1 unit of {resource_to} for player {player} in {resource_from} port")
            else: print(f"You need 2 units of resource {resource_from} to exchange in {resource_from} port")
        elif "ex" in self.get_player_by_name(player).ports:
            if self.get_player_by_name(player).resources[resource_from]>2:
                self.get_player_by_name(player).resources[resource_from]-=3
                self.get_player_by_name(player).resources[resource_to]+=1
                print(f"Exchanging 3 units of {resource_from} into 1 unit of {resource_to} for player {player} in 3:1 port")
            else: print(f"You need 3 units of resource {resource_from} to exchange in 3:1 port")
        else:
            if self.get_player_by_name(player).resources[resource_from]>3:
                self.get_player_by_name(player).resources[resource_from]-=4
                self.get_player_by_name(player).resources[resource_to]+=1
                print(f"Exchanging 4 units of {resource_from} into 1 unit of {resource_to} for player {player}")
            else: print(f"You need 4 units of resource {resource_from} to exchange without ports")

    def trade(self, player_offering, player_accepting, resource_offering, no_offering, resource_accepting, no_accepting):
        if self.get_player_by_name(player_offering).resources[resource_offering]<no_offering:
            print(f"You dont have {no_offering} units of {resource_offering} to trade")
        elif self.get_player_by_name(player_accepting).resources[resource_accepting]<no_accepting:
            print(f"Player {player_accepting} does not have {no_accepting} units of {resource_accepting} to trade")
        else:
            end = False
            while end == False:
                answer = input(f"Does player {player_accepting} accepts the trade offer of {player_offering}'s {no_offering} units of {resource_offering} for {player_accepting}'s {no_accepting} units of {resource_offering}? (Yes/No)")
                if answer not in ("Yes", "No"):
                    print("Wrong input")
                else:
                    if answer =="Yes":
                        self.get_player_by_name(player_offering).resources[resource_offering]-=no_offering
                        self.get_player_by_name(player_accepting).resources[resource_accepting]-=no_accepting
                        self.get_player_by_name(player_offering).resources[resource_accepting]+=no_accepting
                        self.get_player_by_name(player_accepting).resources[resource_offering]+=no_offering
                        print(f"{player_offering} {no_offering} unit(s) of {resource_offering} traded with {player_accepting} for {no_accepting} unit(s) of {resource_accepting}")
                    else:
                        print(f"Player {player_accepting} did not accept trade offer")
                    end = True

#using cards

    def use_card(self, player_name, card):
        if card in self.get_player_by_name(player_name).cards:
            self.get_player_by_name(player_name).cards.remove(card)
            
            #knight
            if card == "Knight":
                while True:
                    try:
                        coordinates = eval(input("Select coordinates to move bandit"))
                        self.move_bandit(player_name, coordinates)
                        self.get_player_by_name(player_name).knights+=1
                        break
                    except Exception as ex:
                        print(ex)
                        continue
                #evaluate if largest army happened
                if self.get_player_by_name(player_name).knights>2:
                    other_knights=0
                    for player in self.players:
                        if player !=self.get_player_by_name(player_name):
                            if other_knights<player.knights:
                                other_knights = player.knights
                            if player.knights<self.get_player_by_name(player_name).knights & player.largestArmy == True:
                                player.largestArmy=False
                                self.get_player_by_name(player_name).largestArmy=True
                                print(f"Player {player_name} wins card Largest Army from player {player.playerName}, as he has now {self.get_player_by_name(player_name).knights} knights.")
                    if other_knights<3:
                        self.get_player_by_name(player_name).largestArmy=True
                        print(f"Player {player_name} wins card Largest Army, as he has first gathered army of {self.get_player_by_name(player_name).knights} knights.")
                    

            #monopoly
            if card == "Monopoly":
                while True:
                    try:
                        res = input("Select resource")
                        if res in self.players[0].resources.keys():
                            stolen = 0
                            for player in self.players:
                                if player.playerName != player_name:
                                    stolen += player.resources[res]
                                    player.resources[res] = 0
                            print(f"Stealing all (total: {stolen}) units of {res} from all the players and giving it to {player_name}")
                            self.get_player_by_name(player_name).resources[res]+=stolen
                        else:
                            print("Wrong input")
                            continue
                    except Exception as ex:
                        print(ex)
                        continue
                    else: 
                        break


            if card == "Roads":
                roads_placed=0
                while roads_placed<2:
                    while True:
                        print(f"Player {player_name}, select an edge to place a road")
                        coordinates = eval(input("Enter coordinates: \n"))
                        try:
                            self.place_road(coordinates, player_name)
                        except Exception as error:
                            print(f"Can't place a road on given coordinates, {error}")
                            continue
                        else:
                            roads_placed+=1
                            break
            

        else:
            print(f"You don't have card {card}")
