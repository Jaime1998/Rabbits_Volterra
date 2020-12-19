'''
Implementar zorros y conejos (ecuaciones de Locka-Volterra) discretas.
Modo gráfico (gráfica de cantidad de zorros y cantidad de conejos conforme pasa el tiempo).
El usuario puede determinar las cantidades iniciales y las constantes de las ecuaciones.
a) La forma habitual.
b) Sobre un retículo de dos dimensiones. En cada celda puede haber N zorros y M conejos.
   Habitualmente N=0 o M=0. En caso contrario, los zorros se comen a los conejos (a partes iguales). 
   En cada instante de tiempo discreto, los zorros y los conejos pueden dar un pasito al azar 
   (moverse a una celda vecina). Hay que graficar el retículo y la posición de zorros y conejos.
c) Igual que b), pero las estrategias de movimiento de zorros y conejos se hacen evolutivas 
   (usando máquinas de estado; entradas=lo que hay en las casillas vecinas; salida=movimiento).
   Cada animal es un cromosoma. Los conejos se reproducen cada T1 periodos.
   Los zorros se reproducen por clonaje+mutación cada vez que comen conejos 
   (un conejo les permite generar un hijo parecido al padre). 
'''
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import time
import random
matplotlib.use('TkAgg')


class Animal:

    def __init__(self, role, matrix):

        self.role = role
        self.x = random.randint(0, len(matrix[self.role][0])-1)
        self.y = random.randint(0, len(matrix[self.role])-1)
        matrix[self.role][self.x][self.y].append(self)

    def __eq__(self, other):
        return self.role == other.role and self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.role, self.x, self.y))

    def movement(self, move, matrix):
        print("x ", self.x)
        print("y ", self.y)
        print(" ")
        matrix[self.role][self.x][self.y].remove(self)
        self.x = self.x + move[0]
        self.y = self.y + move[1]
        matrix[self.role][self.x][self.y].append(self)
        print("x ", self.x)
        print("y ", self.y)

    def pos_movement(self, matrix):
        pos = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                newX = self.x+i
                newY = self.y+j
                if (newX < len(matrix[self.role][0]) and newY < len(matrix[self.role]) and newX  >= 0 and newY >= 0):
                    pos.append([i,j])
        return pos


def eat_rabbits(rabbits, matrix):
    for x in range(len(matrix[1][0])):
        for y in range(len(matrix[1])):
            # feeding foxes
            for i in range(len(matrix[1][x][y])):
                if len(matrix[0][x][y]):
                    rabbit = matrix[0][x][y][0]
                    matrix[0][x][y].remove(rabbit)
                    rabbits.remove(rabbit)
                else:
                    continue


def locka_volterra(prey_rate, predator_sucess, predator_rate, prey_sucess, preys, predators):
    # prey formula
    prey_delta = (prey_rate * preys) - (predator_sucess * preys * predators)
    # predator formula
    predator_delta = (prey_sucess * preys * predators) - \
        (predator_rate * predators)
    return prey_delta, predator_delta


def item_a(preys, predators, time_max, prey_rate=0.2, predator_sucess=0.0025, predator_rate=0.05, prey_sucess=0.0004):
    preys_history = []
    predators_history = []
    time = 0
    preys_history.append(preys)
    predators_history.append(predators)
    # time
    while time < time_max:
        add_preys, add_predators = locka_volterra(
            prey_rate, predator_sucess, predator_rate, prey_sucess, preys, predators)
        preys = preys + add_preys
        predators = predators + add_predators
        preys_history.append(preys)
        predators_history.append(predators)
        time += 1
    return preys_history, predators_history


def draw_state(ax, board_size, matrix):
    # prepare board
    board = np.zeros((board_size, board_size, 3))
    ax.imshow(board, interpolation="nearest")

    # prepare images
    fox = plt.imread("fox.png")
    rabbit = plt.imread("rabbit.png")
    # centered position
    extent = np.array([-0.2, 0.2, -0.2, 0.2])
    for xIn in range(len(matrix[0])):
        for yIn in range(len(matrix[0][0])):
            if(len(matrix[0][xIn][yIn])):
                ax.imshow(rabbit, extent=extent +
                          [xIn-0.25, xIn-0.25, yIn+0.25, yIn+0.25])
                ax.text(xIn+0.25, yIn+0.25,
                        "=" + str(len(matrix[0][xIn][yIn])), color="w")

    for xIn in range(len(matrix[0])):
        for yIn in range(len(matrix[0][0])):
            if(len(matrix[1][xIn][yIn])):
                ax.imshow(fox, extent=extent +
                          [xIn-0.25, xIn-0.25, yIn-0.25, yIn-0.25])
                ax.text(xIn+0.25, yIn-0.25,
                        "=" + str(len(matrix[1][xIn][yIn])), color="w")

    # lines
    ax.grid(which="major", color="w", axis="both", linestyle='-', linewidth=1)
    ax.set(xticks=np.arange(0.5, board_size + 0.5, 1),
           yticks=np.arange(0.5, board_size + 0.5, 1))
    ax.axis("image")


def main():

    # # item a
    # time_max = 200
    # preys_history, predators_history = item_a(100, 50, time_max)

    # # graph

    # time = [i for i in range(0, time_max + 1)]
    # plt.plot(time, preys_history, "g", label="preys")
    # plt.plot(time, predators_history, "r", label="predators")
    # plt.legend()
    # plt.show()

    # item b
    time_max = 1000
    time = 0
    board_size = 8
    fig, ax = plt.subplots()
    fig.set_size_inches(8,8)

    matrix = [[[[] for col in range(board_size)]
               for row in range(board_size)] for role in range(2)]

    foxes = []
    rabbits = []

    for i in range(0, 100):
        rabbits.append(Animal(0, matrix))
    for i in range(0, 30):
        foxes.append(Animal(1, matrix))

    while time < time_max:

        # draw state in the board
        draw_state(ax, board_size, matrix)
        # wait until refresh board
        plt.pause(0.001)
        plt.cla()

        # foxes eat rabbits if in the same cell
        eat_rabbits(rabbits, matrix)
        # draw state in the board
        draw_state(ax, board_size, matrix)
        # wait until refresh board
        plt.pause(0.001)
        plt.cla()
        
        # animals move
        for fox in foxes:
            posible_positions = fox.pos_movement(matrix)
            move = posible_positions[random.randint(0, len(posible_positions) - 1)]
            fox.movement(move, matrix)
        
        for rabbit in rabbits:
            posible_positions = rabbit.pos_movement(matrix)
            move = posible_positions[random.randint(0, len(posible_positions) - 1)]
            rabbit.movement(move, matrix)
            print("-")
        time += 1
        print("-----------------------------------------------------------------")

    # show final state
    draw_state(ax, board_size, matrix)
    plt.title("Final State")
    plt.show()


    # item b


if __name__ == "__main__":
    main()
