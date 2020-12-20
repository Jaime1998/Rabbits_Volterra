'''
Integrantes:
Emily Esmeralda Carvajal Camelo 1630436
Jaime Cuartas Granada 1632664

Curso: Vida artificial
Titulo: Proyecto de software: Implementar zorros y conejos


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
import copy
import getopt
import sys
matplotlib.use('TkAgg')


class Animal:

    def __init__(self, role, matrix, gen1=0, gen2=0):

        self.role = role
        self.x = random.randint(0, len(matrix[self.role][0])-1)
        self.y = random.randint(0, len(matrix[self.role])-1)
        self.chromosome = [gen1, gen2]
        matrix[self.role][self.x][self.y].append(self)

    def __eq__(self, other):
        return self.role == other.role and self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.role, self.x, self.y))

    def natural_movement (self, matrix):
        pos = self.pos_movement(matrix)
        move = ()
        better_move = (-100,[0,0])
        for xy in pos:
            move = (self.func_cost(matrix, xy), xy)
            if(better_move[0] < move[0]):
                better_move = move
        return better_move[1]

    def func_cost (self, matrix, pos):
        return self.chromosome[0]*len(matrix[0][self.x+pos[0]][self.y+pos[1]]) - self.chromosome[1]*len(matrix[1][self.x+pos[0]][self.y+pos[1]])

    def movement(self, move, matrix):
        matrix[self.role][self.x][self.y].remove(self)
        self.x = self.x + move[0]
        self.y = self.y + move[1]
        matrix[self.role][self.x][self.y].append(self)


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
                    rabbits.remove(rabbit)
                    del matrix[0][x][y][0]
                else:
                    continue

def eat_rabbits_item_c(rabbits, foxes, matrix, sigma=0.05, mu=0.2):
    for x in range(len(matrix[1][0])):
        for y in range(len(matrix[1])):
            # feeding foxes
            for i in range(len(matrix[1][x][y])):
                if len(matrix[0][x][y]):
                    rabbit = matrix[0][x][y][0]
                    rabbits.remove(rabbit)
                    del matrix[0][x][y][0]
                    gen1 = 0
                    gen2 = 0
                    if(random.uniform(0,1) <= mu):
                        gen1 = sigma*np.random.randn()
                    if(random.uniform(0,1) <= mu):
                        gen2 = sigma*np.random.randn()
                    foxes.append(Animal(1, matrix, matrix[1][x][y][i].chromosome[0] + gen1, matrix[1][x][y][i].chromosome[1] + gen2))
                else:
                    continue

def reproduction_rabbit (rabbits, matrix, gamma=0.1):

    for i in range(len(rabbits)//2):
        mixRabbits = np.random.permutation(rabbits)
        parent1 = mixRabbits[0]
        parent2 = mixRabbits[1]
        alpha = np.random.uniform(-gamma, gamma+1, 2)
        chromosome1 = alpha*parent1.chromosome + (1-alpha)*parent2.chromosome
        chromosome2 = alpha*parent2.chromosome + (1-alpha)*parent1.chromosome
        rabbits.append(Animal(0, matrix, chromosome1[0], chromosome1[1]))
        rabbits.append(Animal(0, matrix, chromosome2[0], chromosome2[1]))


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
                ax.text(xIn+0.1, yIn+0.25,
                        "=" + str(len(matrix[0][xIn][yIn])), color="w")

    for xIn in range(len(matrix[0])):
        for yIn in range(len(matrix[0][0])):
            if(len(matrix[1][xIn][yIn])):
                ax.imshow(fox, extent=extent +
                          [xIn-0.25, xIn-0.25, yIn-0.25, yIn-0.25])
                ax.text(xIn+0.1, yIn-0.25,
                        "=" + str(len(matrix[1][xIn][yIn])), color="w")

    # lines
    ax.grid(which="major", color="w", axis="both", linestyle='-', linewidth=1)
    ax.set(xticks=np.arange(0.5, board_size + 0.5, 1),
           yticks=np.arange(0.5, board_size + 0.5, 1))
    ax.axis("image")


def item_b(n_rabbits, n_foxes, sleep, board_size, matrix, time_max):
    time = 0
    foxes = []
    rabbits = []
    fig, ax = plt.subplots()
    fig.set_size_inches(8,8)

    for i in range(0, n_rabbits):
        rabbits.append(Animal(0, matrix))
    for i in range(0, n_foxes):
        foxes.append(Animal(1, matrix))

    while time < time_max:

        # draw state in the board
        draw_state(ax, board_size, matrix)
        # wait until refresh board
        plt.pause(sleep)
        plt.cla()

        # foxes eat rabbits if in the same cell
        eat_rabbits(rabbits, matrix)
        # draw state in the board
        draw_state(ax, board_size, matrix)
        # wait until refresh board
        plt.pause(sleep)
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
        time += 1

def item_c(n_rabbits, n_foxes, sleep, board_size, matrix, time_max, t_reproduction_rabbit):
    time = 0
    foxes = []
    rabbits = []
    fig, ax = plt.subplots()
    fig.set_size_inches(8,8)

    for i in range(0, n_rabbits):
        rabbits.append(Animal(0, matrix, random.uniform(-10, 10), random.uniform(-10, 10)))
    for i in range(0, n_foxes):
        foxes.append(Animal(1, matrix, random.uniform(-10, 10), random.uniform(-10, 10)))

    while time < time_max:

        if((time % t_reproduction_rabbit) == 0):
            reproduction_rabbit(rabbits, matrix)
        
        # draw state in the board
        draw_state(ax, board_size, matrix)
        # wait until refresh board
        plt.pause(sleep)
        plt.cla()

        # foxes eat rabbits if in the same cell
        eat_rabbits_item_c(rabbits, foxes, matrix)
        # draw state in the board
        draw_state(ax, board_size, matrix)
        # wait until refresh board
        plt.pause(sleep)
        plt.cla()
        
        # animals move
        for fox in foxes:
            move = fox.natural_movement(matrix)
            fox.movement(move, matrix)
        
        for rabbit in rabbits:
            move = rabbit.natural_movement(matrix)
            rabbit.movement(move, matrix)
        time += 1

def are_numbers(array):
    for i in array:
        if(not i.isnumeric()):
            return False
    return True

def main():

    try:
        myopts, args = getopt.getopt(sys.argv[1:], "a:b:c:")
    except getopt.GetoptError as e:
        print(str(e))
        print("""Usage: %s 
        -a numberFoxes,numberRabbits,times (For item a, Lotka-Volterra)
        -b numberFoxes,numberRabbits,times,boardSize,pausaStep (for item b, reticle without reproduction)
        -c numberFoxes,numberRabbits,times,boardSize,pausaStep,timeReproductionRabbits (for item c, reticle with reproduction)
        
        """ % sys.argv[0])
        sys.exit(2)
    
    for option, argument in myopts:
        if ((option == "-a") and (3==len(argument.split(",")) and are_numbers(argument.split(",")))):
            options = argument.split(",")
            n_foxes = int(options[0])
            n_rabbits = int(options[1])
            time_max = int(options[2])
            
            preys_history, predators_history = item_a(n_rabbits, n_foxes, time_max)
            time = [i for i in range(0, time_max + 1)]
            plt.plot(time, preys_history, "g", label="preys")
            plt.plot(time, predators_history, "r", label="predators")
            plt.legend()
            plt.show()

        elif ((option == "-b") and (5==len(argument.split(",")) and are_numbers(argument.split(",")))):
            options = argument.split(",")
            n_foxes = int(options[0])
            n_rabbits = int(options[1])
            time_max = int(options[2])
            board_size = int(options[3])
            sleep = float(options[4])
            
            matrix = [[[[] for col in range(board_size)]
                    for row in range(board_size)] for role in range(2)]

            item_b(n_rabbits, n_foxes, sleep, board_size, matrix, time_max)

        elif ((option == "-c") and (6==len(argument.split(",")) and are_numbers(argument.split(",")))) :
            options = argument.split(",")
            n_foxes = int(options[0])
            n_rabbits = int(options[1])
            time_max = int(options[2])
            board_size = int(options[3])
            sleep = float(options[4])
            t1ReproductionRabbits = int(options[5])
            
            matrix = [[[[] for col in range(board_size)]
                    for row in range(board_size)] for role in range(2)]
            
            item_c(n_rabbits, n_foxes, sleep, board_size, matrix, time_max, t1ReproductionRabbits)

        else:
            print("""Usage: %s 
            -a numberFoxes,numberRabbits,times (For item a, Lotka-Volterra)
            -b numberFoxes,numberRabbits,times,boardSize,pausaStep (for item b, reticle without reproduction)
            -c numberFoxes,numberRabbits,times,boardSize,pausaStep,timeReproductionRabbits (for item c, reticle with reproduction)
            
            """ % sys.argv[0])
            sys.exit(2)




if __name__ == "__main__":
    main()
