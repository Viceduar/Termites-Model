import pygame
import random


pygame.init()

#CONFIGURACIÓN DE SCREEN
screen_width = 800 #Ancho
screen_height = 600 #Alto
screen = pygame.display.set_mode((screen_width, screen_height))

layer1 = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA) # Capa para termitas
layer1.fill((0,0,0,0))

layer2 = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA) # Capa para astillas
layer2.fill((0,0,0,0))

#CONFIGURACIÓN DE CUADRICULA
grid_width = 150
grid_height = 100
cell_width = screen_width / grid_width
cell_height = screen_height / grid_height

#CONFIGURACIÓN DE TERMITAS
termite_color = (25, 130, 196) #Color predeterminado
termite_color_c = (242, 66, 54) #Color al cargar astilla
termites_quantity = 200 #Cantidad total de termitas
time = 50 #Tiempo para moverse (1000 = 1segundo)
directions = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)] #Posibles direcciones

#CONFIGURACIÓN DE ASTILLAS
woodchip_color = (255, 202, 58) #Color predeterminado
density = 0.2 #Densidad de población de astillas

class Woodchips:

    def __init__(self):
        '''
        Determina las posiciones de las astillas en la cuadricula 
        aleatoriamente dependiendo de la densidad configurada.
        '''
        
        #Generar posiciones
        positions = [[False for _ in range(grid_width)] for _ in range(grid_height) ]
        for row in range(grid_height):
            for col in range(grid_width):
                x = random.uniform(0, 1)
                if x < density:
                    positions[row][col] = True
        

        self.positions = positions


    def draw_a_woodchip(self, posX, posY):
        '''
        Dibuja en layer2 una astilla y guarda su posición.
        '''

        self.positions[posY][posX] = True
        pygame.draw.rect(layer2, woodchip_color, (posX * cell_width, posY * cell_height, cell_width, cell_height), 0)

    def draw_woodchips(self):
        '''
        Dibuja todas las astillas guardadas.
        '''
        
        for y in range(grid_height):
            for x in range(grid_width):
                if self.positions[y][x]:
                    self.draw_a_woodchip(x, y)
    
    def delete_a_woodchip(self, posX, posY):
        '''
        Elimina la astilla coloriandola de negro y elimina su posición.
        '''
        
        self.positions[posY][posX] = False
        pygame.draw.rect(layer2, 'black', (posX * cell_width, posY * cell_height, cell_width, cell_height), 0)

class Termite:
     
    '''
    Tiene el rol de agente con los siguiente parametros

    posX [int]
    posY [int]
    carry [bool]
    direction [tuple]
    move_timer [clock]
    '''

    def __init__(self, posX, posY):
         '''
         Construye una termita con su posición (x,y) en la cuadricula.
         '''
        
         self.posX = posX
         self.posY = posY
         self.carry = False
         self.direction = random.choice(directions)
         self.move_timer = pygame.time.get_ticks() + time

    def draw_termite(self):
        '''
        Dibuja a la termita en su posición (posX, posY),
        y determina el color dependiendo si carga una astilla o no.
        '''

        color = termite_color_c if self.carry else termite_color
        pygame.draw.rect(layer1, color, (self.posX * cell_width, self.posY * cell_height, cell_width, cell_height), 0)

    def theres_a_woodchip(self):
        '''
        Determina si hay una astilla a la casilla a la que se movera.
        '''

        x, y =  (self.posX + self.direction[0])%grid_width, (self.posY + self.direction[1])%grid_height 
        return woodchips.positions[y][x]

    def change_direction_safe(self):
        '''
        Cambia la dirección a una en la que no haya una astilla.
        '''

        self.change_direction( self.look_for_safe_cell() )

    def look_for_safe_cell(self):
        '''
        Determina en que casillas-vecinas no hay astillas.
        '''
        
        cells = set()
        for d in directions:
             x = (self.posX + d[0])%grid_width 
             y = (self.posY + d[1])%grid_height
             if woodchips.positions[y][x]:
                 cells.add( d )
        return cells

    def change_direction(self, cell = set()):
        '''
        Cambia dirección aleatoriamente descartando el conjunto cell

        cell [set]
        '''
        
        new_dir = list( set(directions).difference(cell) )
        if len( new_dir ) > 0:
            self.direction = random.choice( new_dir )
        else:
            self.direction = (0,0)
 
    def on_woodchip(self):
        '''
        Determina si en la posición actual de la termita hay una astilla.
        '''

        if woodchips.positions[self.posY][self.posX]:
            self.carry = True
            woodchips.delete_a_woodchip(self.posX, self.posY)

    def move(self):
        '''
        Actualiza la posición de la termita después de move_timer/1000 segundos.
        '''

        current_time = pygame.time.get_ticks()
        if current_time >= self.move_timer:
            self.on_woodchip()

            if self.carry and self.theres_a_woodchip():
                self.carry = False
                self.change_direction_safe()
                woodchips.draw_a_woodchip(self.posX, self.posY)
            
            self.posX = (self.posX + self.direction[0])%grid_width
            self.posY = (self.posY + self.direction[1])%grid_height

            self.change_direction()

            self.move_timer = pygame.time.get_ticks() + time
        
#INICIACIÓN DE ASTILLAS
woodchips = Woodchips()
woodchips.draw_woodchips()

pygame.display.flip()

#INICIACIÓN DE TERMITAS
free_cells = set() #Cuadriculas que no tienen astillas
termites = set() #Conjunto de termitas

for row in range(grid_height): #Determinar las cuadriculas que no tengan astillas 
    for col in range(grid_width):
        if not woodchips.positions[row][col]:
            free_cells.add((col, row))

for _ in range(termites_quantity): #Generar termitas aleatoriamente en las casillas libres
    pos = random.choice( list(free_cells) )
    termites.add( Termite(pos[0], pos[1]) )
    free_cells.discard( pos )


clock = pygame.time.Clock()
running = True
pause = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pause = not pause

    if not pause:
        screen.fill('black')
        layer1.fill((0,0,0,0))

        for t in termites:
            t.move()
            t.draw_termite()

        screen.blit(layer2, (0,0))
        screen.blit(layer1, (0,0))
        pygame.display.flip()


    clock.tick(60)

pygame.quit()