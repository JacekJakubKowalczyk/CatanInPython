#Author: Jacek Kowalczyk jj.kowalczyk@protonmail.com

from unittest.mock import patch
from Table import Table

class mapSetup:
   map=[3,4,5,4,3]
   fields={'wood':4, 'clay':3, 'grain':4, 'ore':3, 'sheep':4, 'desert':1}
   seed={2:1,3:2,4:2,5:2,6:2,8:2,9:2,10:2,11:2,12:1}


class Game:
    def __init__(self, playerNames, map_setup=mapSetup()):
        self.GameTable=Table(map_setup,playerNames)
        self.playerNames=playerNames

    def round_zero(self):
        order=list(self.playerNames)
        order.extend(self.playerNames[::-1])
        for player in order:
            while True:
                print(f"Player {player}, select a vertix to place the village")
                coordinates = eval(input("Enter coordinates: \n"))
                try:
                    self.GameTable.place_village(coordinates, player)
                except Exception as error:
                    print(f"Can't place a village on given coordinates, {error}")
                    continue
                else:
                    break
            while True:
                print(f"Player {player}, select an edge to place a road")
                coordinates = eval(input("Enter coordinates: \n"))
                try:
                    self.GameTable.place_road(coordinates, player)
                except Exception as error:
                    print(f"Can't place a road on given coordinates, {error}")
                    continue
                else:
                    break

    #returns winner's name if any player won, else returns None (false)
    def evaluate_winner(self):
        for player in self.GameTable.players:
            if player.victoryPointsHidden>9:
                return player.playerName
        return None
    
    def round(self):
        for player in self.playerNames:
            self.GameTable.get_player_by_name(player).cards.extend(self.GameTable.get_player_by_name(player).cards_from_this_turn)
            self.GameTable.get_player_by_name(player).cards_from_this_turn = []
            self.GameTable.give_resources(player)
            print(f"Move: {player}")
            player_input=""
            while player_input != "end":
                if self.evaluate_winner():
                    print(f"{self.evaluate_winner()} wins!")
                    break
                #player_input="end"
                #uzyj karte
                #buduj - done-
                    #droga
                    #miasto
                    #wies
                    #karta
                #handluj






def test_my_function(game):
    with patch('builtins.input', side_effect=["[0,2]", "[0,2]", "[5,2]", "[10,2]", "[3,4]", "[6,3]","[2,3]", "[4,2]"]):
        result = game.round_zero()
    assert result == None

# Run the test
if __name__ == "__main__":
    game1=Game(["Red", "Blue"])
    test_my_function(game1)
    # for i in range(12):
    #     game1.round()
    #     game1.GameTable.build_road([6,7], "Red")
    #     #game1.GameTable.build_road([2,1], "Blue")
    #     game1.GameTable.build_village([3,8], "Red")
    #     game1.GameTable.build_city([3,8], "Red")
    #     game1.GameTable.build_development("Blue")

    
    
    # xd=Table(mapSetup(),["Red", "Blue", "White", "Yellow"])
    # xd.place_village([3,6],"Blue")
    # print(xd.gameBoard.buildVertexLegal(xd.gameBoard.vertices[2][6]))

    # edge=xd.gameBoard.getEdgesOfVertex(xd.gameBoard.vertices[3][6])[0]
    # print(edge.X, edge.Y)
    # xd.place_road([6,5],"Blue")

    for i in game1.GameTable.gameBoard.vertices:
        for row in i:
            if row == None:
                print("-",end="")
            else: print("O", end="")
        print("\n")
    print(game1.GameTable.players[0].ports)
    game1.GameTable.exchange("Red","ore", "wood")
    #game1.GameTable.trade("Red","Blue","wood",1,"ore",1)
    #game1.GameTable.use_card("Red", "Monopoly")
    #game1.GameTable.use_card("Red", "Roads")
    game1.GameTable.build_road([0,3], "Red")
    game1.GameTable.build_road([1,4], "Red")
    game1.GameTable.build_road([2,3], "Red")
    game1.GameTable.build_road([2,2], "Red")
    game1.GameTable.build_road([1,2], "Red")
    game1.GameTable.build_road([0,4], "Red")
    print(game1.GameTable.longest_road_from_edge(game1.GameTable.gameBoard.edges[1][2],"Red",[],0))
    print(game1.GameTable.longest_road())
    print(game1.GameTable.players[0].longestRoad)
    game1.round()




