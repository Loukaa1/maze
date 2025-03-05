from jinja2 import Environment, FileSystemLoader
import random
import matplotlib.pyplot as plt
import networkx as nx
# import pygraphviz

class Cellule:
    def __init__(self, murNord, murEst, murSud, murOuest, x, y):
        self.murs={'N':murNord,'E':murEst, 'S':murSud,'O':murOuest}
        self.x = x
        self.y = y

#    def __repr__(self):
#        return str([v for v in self.murs.values()])[1:-1]
        
    def get_class_from_cell(self) :
        l = " ".join([direction for direction in self.murs if self.murs[direction] is True])
        return l
    
        
    
    
class Labyrinthe:
    def __init__(self, hauteur, largeur, hasard = False):
        self.hauteur = hauteur
        self.largeur = largeur
        self.grille=self.construire_grille(hauteur, largeur)
        self.creer_labyrinthe(0, 0, hauteur, largeur, hasard = hasard)
        self.graphe = None
        self.court_chemin = []
        self.generer_graphe()
        self.generer_html()

    
    def __repr__(self):
        return str("\n".join([str(ligne) for ligne in self.grille]))

    def construire_grille(self, hauteur, largeur):
        """
        Permet de construire une grille de dimension hauteur x \
        largeur où toutes les cellules ont 4 murs.

        Args:
            hauteur (int): la hauteur de la grille
            largeur (int): la largeur de la grille

        Returns:
            table: un tableau de tableaux
        """
        grille = []
        for j in range(hauteur):
            ligne = []
            for i in range(largeur):
                cellule = Cellule(True, True, True, True, x=i, y=j)
                ligne.append(cellule)
            grille.append(ligne)
        return grille
    
    def creer_passage(self, c1_lig, c1_col, c2_lig, c2_col):
        """Creer un passage entre deux cellules

        Args:
            c1_lig (int): le numéro de ligne de la cellule 1
            c1_col (int): le numéro de colonne de la cellule 1
            c2_lig (int): le numéro de ligne de la cellule 2
            c2_col (int): le numéro de colonne de la cellule 2
        """
        #print(f"creer_passage(c1_l={c1_lig}, c1_c={c1_col}, c2_l={c2_lig}, c2_c={c2_col})")
        cellule1 = self.grille[c1_lig][c1_col]
        cellule2 = self.grille[c2_lig][c2_col]
        # cellule2 au Nord de cellule1
        if c1_lig - c2_lig == 1 and c1_col == c2_col:
            cellule1.murs['N'] = False
            cellule2.murs['S'] = False
        # cellule2 à l'Ouest de cellule1
        elif c1_col - c2_col == 1 and c1_lig == c2_lig:
            cellule1.murs['O'] = False
            cellule2.murs['E'] = False
        # cellule2 au Sud de cellule1
        elif c1_lig - c2_lig == -1 and c1_col == c2_col:
            cellule1.murs['S'] = False
            cellule2.murs['N'] = False
        # cellule2 à l'Est de cellule1
        elif c1_col - c2_col == -1 and c1_lig == c2_lig:
            cellule1.murs['E'] = False
            cellule2.murs['O'] = False
        
    def creer_labyrinthe(self, ligne, colonne, hauteur, largeur, hasard = False, nb_portes = 3):
        if hauteur == 1 : # Cas de base
            for k in range(colonne, colonne + largeur-1):
                self.creer_passage(ligne, k, ligne, k+1)
        elif largeur == 1: # Cas de base
            for k in range(ligne, ligne + hauteur -1):
                self.creer_passage(k, colonne, k+1, colonne)
        else: # Appels récursifs
            if hauteur >= largeur :
                # création du passage
                if not hasard :
                    self.creer_passage(ligne+hauteur//2, colonne, ligne+hauteur//2-1, colonne)
                else :
                    #plusieurs portes en fonction de nb_portes
                    if nb_portes < hauteur:
                        for n in range(nb_portes) :
                            position = random.randint(colonne, colonne+largeur-1)
                            self.creer_passage(ligne+hauteur//2, position , ligne+hauteur//2-1, position)
                    else :
                        position = random.randint(colonne, colonne+largeur-1)
                        self.creer_passage(ligne+hauteur//2, position , ligne+hauteur//2-1, position)
                
                # ------ RECURSIF
                #partie Nord
                self.creer_labyrinthe(ligne, colonne, hauteur//2, largeur, hasard = hasard)
                #partie Sud
                self.creer_labyrinthe(ligne + hauteur//2, colonne, hauteur-hauteur//2, largeur, hasard = hasard)
            else :
                # création du passage
                if not hasard :
                    self.creer_passage(ligne, colonne+largeur//2, ligne, colonne+largeur//2-1)
                else :
                    position = random.randint(ligne, ligne+hauteur-1)
                    self.creer_passage(position, colonne+largeur//2, position, colonne+largeur//2-1)
                # ------ RECURSIF
                #partie Ouest
                self.creer_labyrinthe(ligne, colonne, hauteur, largeur//2, hasard = hasard)
                #partie Est
                self.creer_labyrinthe(ligne, colonne + largeur//2, hauteur, largeur-largeur//2, hasard = hasard)
                
    def generer_graphe(self) :
        G1 = nx.Graph()
        self.graphe = G1
        for i in range(len(self.grille)) :
            for j in range(len(self.grille[i])) :
                G1.add_node((i, j))
        for j, ligne in enumerate(self.grille) :
            for i, cellule in enumerate(ligne) :
                mur = cellule.murs
                if not mur['E'] :
                    G1.add_edge((i, j), (i+1, j))
                if not mur['S'] :
                    G1.add_edge((i, j), (i, j+1))
                    
    def plus_court_chemin(self):
        entree = list(self.graphe.nodes)[0]
        sortie = list(self.graphe.nodes)[-1]
        chemin = nx.shortest_path(self.graphe, entree, sortie)
        self.court_chemin = chemin
        return chemin
                  
                
            
                
    def generer_html(self):
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('maze.template')
        html_template = template.render(maze=self)
        html_rendu = 'maze.html'
        with open(html_rendu, 'w') as hr:
            hr.write(html_template)
            
    def show_graphe(self) :
        start = list(self.graphe.nodes)[0]
        end = sortie = list(self.graphe.nodes)[-1]
        options = {
            "font_size": 6,
            "node_size": 220,
            "edgecolors": "tab:blue",
            "alpha": 0.7,
            "linewidths": 1,
            "width": 1,
        }
        
        plt.figure(figsize=(25,25))
        pos = nx.nx_agraph.graphviz_layout(self.graphe)
        court_chemin = self.plus_court_chemin()
        color_map=['#FFA500' if node in court_chemin else '#A0CBE2' for node in self.graphe]
        print(color_map)
        nx.draw(self.graphe, pos, node_color=color_map, with_labels=True, **options) 
        plt.show()


# G = nx.cycle_graph(24)
# color_map=['#FFA500' if node==0 else '#A0CBE2' for node in G]
# pos = nx.circular_layout(G)
# nx.draw(G, pos, node_color=color_map, node_size=800, cmap=plt.cm.Blues)
# plt.show()
#     

#cellule = Cellule(murNord=True, murEst=False, murSud=True, murOuest=True)
h=15
w=15
labyrinthe = Labyrinthe(h, w, hasard = True)