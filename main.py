from binarytree import Node
import graphviz
import ast

class Arbol:
    def __init__(self, valor, izquierda = None, derecha = None):
        self.valor = valor
        self.izquierda = izquierda
        self.derecha = derecha

# r = input("Ingrese r: ")
# r = "abb"
# r = "a*"
# r = "a|b"
# r = "(a|b)*abb"
r = "(b|b)*abb(a|b)*"
# r = "a+"
r = "(00)*"
# r = "0"

# w = input("Ingrese w: ")
w = "babbaaaaa"
w = "b"



padre_actual = None # instancia cabeza actual
arboles_temporales = [] # arboles temporales / hijos

alfabeto = "abcdefghijklmnopqrstuvwxyz0123456789"
operadores ="*+?"
# alfabeto = 0-25 ; operadores= 26(*), 27(+), 28(?) ; 29(.) ; 30(|)
caracteres = alfabeto + operadores + "." + "|" + "#"
SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


# print(caracteres.index(r))

# Valida si el nodo se agrega al arbol principal o a un arbol temporal
def nuevo_nodo(indice, valor, izquierda, derecha, padre_actual):
    if indice is None:
        if padre_actual is None:
            # Es la cabeza 
            padre_actual = Arbol(valor, izquierda, derecha)
        else:
            # Si hay cabeza el elemento actual hace todos los nodos pasado el hijo (derecho) de este
            padre_actual = Arbol(valor, padre_actual, derecha)
    # Arbol temporal
    else:
        # Si se debe crear un arbol temporal
        if indice == len(arboles_temporales):
            arboles_temporales.append(Arbol(valor, izquierda, derecha))
        # Si el nodo se debe agregar a un arbol temporal existente, misma logica pasada
        elif indice < len(arboles_temporales):
            if arboles_temporales[indice] is None:
                arboles_temporales[indice] = Arbol(valor, izquierda, derecha)
            else:
                arboles_temporales[indice] = Arbol(valor, arboles_temporales[indice], derecha)
    return padre_actual


# Cuenta la cantidad de parentesis abiertos y cerrados
# Analiza cuando termina una expresión 
# (c|(d|(e|f)))*abc
# (c|(d|(e|f)))*
# (d|(e|f))
# (e|f)
# abc
def expresiones_en_r(expresion_regular):
    long_exp = len(expresion_regular)
    i = 0
    while i < long_exp:
        if expresion_regular[i] == "(":
            cont_parentesis = 1
            for j in range(i+1, long_exp):
                if expresion_regular[j] == "(":
                    cont_parentesis += 1
                elif expresion_regular[j] == ")":
                    cont_parentesis -= 1

                contador = 0
                if cont_parentesis == 0 and expresion_regular[j] == ")":
                    if j + 1 < long_exp:
                        if expresion_regular[j+1] in operadores:
                            contador += 2

                    return contador + j

        elif expresion_regular[i] in alfabeto or expresion_regular[i] == "*":
            fin_exp = i
            for j in range(i+1, long_exp):
                if not (expresion_regular[j] in alfabeto or expresion_regular[j] == "*"):
                    break
                fin_exp = j
            return fin_exp
        i += 1

# Analiza cuando se debe crear un nodo del arbol y el nodo se crea con nuevo_nodo()
def analizador_expresion(expresion_regular, indice, padre_actual):
    long_exp = len(expresion_regular)
    i = 0
    while i < long_exp:
        # Si encuentra parentesis es el inicio de una expresion.
        # Contador de cuantos se han abierto o cerrado
        # La operacion tiene que dar 0, abierto +1 cerrado -1
        # Cuando eso es 0 y despues hay un *, + o ? para tomarlo en cuenta en la misma expresión y volver a analizarla con esta función
        if expresion_regular[i] == "(":
            if i == 0:
                cont_parentesis = 1
                for j in range(i+1, long_exp):
                    if expresion_regular[j] == "(":
                        cont_parentesis += 1
                    elif expresion_regular[j] == ")":
                        cont_parentesis -= 1

                    contador = 0
                    if cont_parentesis == 0:
                        if expresion_regular[j] == ")" and j + 1 < long_exp:
                            if expresion_regular[j+1] in operadores:
                                contador += 2

                        fin_exp = j + contador
                        inicio_exp = i + 1
                        padre_actual = analizador_expresion(expresion_regular[inicio_exp:fin_exp], indice, padre_actual)
                        i = j
                        break
            
            # Si encuentra otro parentesis despues de toda la expresion que condiciona el resto, se crea el temporal root, entonces se crea un arbol temporal para concatenarlo al principal
            else:
                if (expresion_regular[i-1] in operadores or expresion_regular[i-1] == ")")  or expresion_regular[i-1] in alfabeto:
                    inicio_exp = i
                    fin_exp = i + 1 + expresiones_en_r(expresion_regular[i:])
                    padre_actual = analizador_expresion(expresion_regular[inicio_exp:fin_exp], len(arboles_temporales), padre_actual)

                    if indice is None:
                        arbol_temporal_i = arboles_temporales.pop()
                    else:
                        arbol_temporal_i = arboles_temporales.pop(indice + 1)


                    if arbol_temporal_i is not None:
                        padre_actual = nuevo_nodo(indice, ".", None, arbol_temporal_i, padre_actual)

                    i = i + fin_exp + 1
        
        # Si encuentra una letra o # 
        elif expresion_regular[i] in alfabeto or expresion_regular[i] == "#":
            # Si no hay temporal head, temporal root ni current head entonces es la primera letra o es la primera letra de una expresion dentro de la expresion principal
            if ((indice is None and padre_actual is None) or i == 0) and i + 1 < long_exp and (expresion_regular[i+1] in alfabeto or expresion_regular[i+1] == "#"):
                # Para expresiones como ab* donde * se aplica solo a la ultima letra. 
                if i + 2 < long_exp and expresion_regular[i+2] in operadores:
                    padre_actual = nuevo_nodo(indice, ".", Arbol(expresion_regular[i]), Arbol(expresion_regular[i+2], Arbol(expresion_regular[i+1]), None), padre_actual)
                    i += 2
                # Si el siguiente caracter es una letra, entonces se unen ambas por medio de un punto como cabeza
                else:
                    padre_actual = nuevo_nodo(indice, ".", Arbol(expresion_regular[i]), Arbol(expresion_regular[i+1]), padre_actual)
                    i += 1
            # Si no hay temp root pero si hay current head o estamos en un lugar dentro de una expresion que no sea la posicion inicial se agrega un punto y el hijo izquierdo es el arbol actual, el derecho es letra actual
            elif (indice is None and padre_actual is not None) or i != 0:
                padre_actual = nuevo_nodo(indice, ".", None, Arbol(expresion_regular[i]), padre_actual)
            else:
                padre_actual = nuevo_nodo(indice, expresion_regular[i], None, None, padre_actual)


            # Para verificar si hay un operador *, + o ? en la expresion y tomarlo en cuenta
            if i + 1 < long_exp:
                if expresion_regular[i+1] in operadores:
                    padre_actual = nuevo_nodo(indice, expresion_regular[i+1], Arbol(expresion_regular[i]), None, padre_actual)
                elif expresion_regular[i+1] == ")":
                    if i + 2 < long_exp:
                        if expresion_regular[i+2] in operadores:
                            padre_actual = nuevo_nodo(indice, expresion_regular[i+2], Arbol(expresion_regular[i]), None, padre_actual)

        # Si es un or, se analiza toda la expresion que esta despues de |, calculando donde finaliza el or.
        # Puede crear arboles temporales que luego de crearse se extraen y se insertan en el arbol principal.
        elif expresion_regular[i] == "|":
            fin_exp = i + 2 + expresiones_en_r(expresion_regular[i+1:])
            padre_actual = analizador_expresion(expresion_regular[i+1:fin_exp], len(arboles_temporales), padre_actual)
            
            # Si existe, se extrae el ultimo arbol temporal 
            if indice is None:
                arbol_temporal_i = arboles_temporales.pop()
            else:
                arbol_temporal_i = arboles_temporales.pop(indice + 1)

            # Inserta el arbol temporal en el arbol principal
            if arbol_temporal_i is not None:
                padre_actual = nuevo_nodo(indice, expresion_regular[i], Arbol(expresion_regular[i-1]), arbol_temporal_i, padre_actual)

            # Analiza si existe un operador *, +, ? para tomarlo en cuenta.
            if fin_exp < long_exp and expresion_regular[fin_exp] == ")":
                if fin_exp + 1 < long_exp:
                    if expresion_regular[fin_exp+1] in operadores:
                        padre_actual = nuevo_nodo(indice, expresion_regular[fin_exp+1], Arbol(expresion_regular[fin_exp+1]), None, padre_actual)

            i = i + fin_exp + 1
        i += 1
    return padre_actual

# Convierte la clase arbol a un arbol tipo BinaryTree
def binarytree(padre, binary_tree_parent=None):
    if binary_tree_parent is None:
        binary_tree_parent = Node(caracteres.index(padre.valor))

    if padre.izquierda is not None and padre.izquierda.valor is not None:
        binary_tree_parent.left = Node(caracteres.index(padre.izquierda.valor))
        binarytree(padre.izquierda, binary_tree_parent.left)

    if padre.derecha is not None and padre.derecha.valor is not None:
        binary_tree_parent.right = Node(caracteres.index(padre.derecha.valor))
        binarytree(padre.derecha, binary_tree_parent.right)

    return binary_tree_parent

# Hasta donde se puede ir desde un estado moviendo solo con E
def cerraduraEpsilon(estado, transiciones, estados = []):
    if estado not in estados:
        estados.append(estado)
    # /si hay transiciones con E, se recorre y para cada una vuelve a hacer la cerradura
    if (len(transiciones[estado]["E"]) > 0):
        for i in transiciones[estado]["E"]:
            if i not in estados:
                estados.append(i)
            cerraduraEpsilon(i, transiciones, estados)
    return estados

# Para un conjunto de estados a cada uno le hace la cerradura de epsilon
def cerraduraEpsilon_s(estados, transiciones):
    estados_finales = []
    # se recorre cada estado
    for i in estados:
        estado_ = []
        estado_ = cerraduraEpsilon(i, transiciones, [])
        estados_finales.append(estado_)


    estados_finales_ = []
    for j in estados_finales:
        for k in j:
            estados_finales_.append(k)

    # Se eliminan duplicados
    estados_finales_ = list(set(estados_finales_))
    estados_finales_.sort()

    return estados_finales_

# Hasta donde se puede llegar con un caracter segun un conjunto de estados
def mover(estados, caracter, transiciones):
    estados_movidos = []
    for i in estados:
        for llave, valor in transiciones.items():
            if llave == i:
                # si hay transicion para la letra, entonces agrega ese estado
                if len(valor[caracter]) > 0:
                    for st in valor[caracter]:
                        if st not in estados_movidos:
                            estados_movidos.append(st)
    return estados_movidos

def simulacion_AFN(w, transiciones, estado_final):
    estados = cerraduraEpsilon("S0", transiciones, [])
    contador = 1
    w += "·"
    inicio = w[0]
    while inicio != "·":
        estados = cerraduraEpsilon_s(mover(estados, inicio, transiciones), transiciones)
        inicio = w[contador]
        contador += 1
    if estado_final in estados:
        return True
    else:
        return False

# Si con ese nodo se puede devolver cadena vacia o no
def anulable(nodo, data):
    # or entre valor anulable izquierdo y valor anulable hijo derecho
    # si cualquiera de los hijos es anulable
    if data[str(nodo.value)]["Valor"] == "|":
        data[str(nodo.value)]["Anulable"] = data[str(nodo.left.value)]["Anulable"] or data[str(nodo.right.value)]["Anulable"]
    # and entre el anulablke, si los dos hijos son anulables
    elif data[str(nodo.value)]["Valor"] == ".":
        data[str(nodo.value)]["Anulable"] = data[str(nodo.left.value)]["Anulable"] and data[str(nodo.right.value)]["Anulable"]
    # siempre es true
    elif data[str(nodo.value)]["Valor"] == "*":
        data[str(nodo.value)]["Anulable"] = True
    # siempre es true 
    elif data[str(nodo.value)]["Valor"] == "?":
        data[str(nodo.value)]["Anulable"] = True
    # Siempre false
    elif data[str(nodo.value)]["Valor"] == "+":
        data[str(nodo.value)]["Anulable"] == False
    # Siemre es verdadero
    elif data[str(nodo.value)]["Valor"] == "E":
        data[str(nodo.value)]["Anulable"] == True
    # Una letra por default es falso.
    else:
        data[str(nodo.value)]["Anulable"] = False

def primera_posicion(nodo, data):
    # Devuelve una lista de la combinacion de la primera posicion de los hijos
    if data[str(nodo.value)]["Valor"] == "|":
        data[str(nodo.value)]["Primera posicion"] = [item for sublist in [data[str(nodo.left.value)]["Primera posicion"], data[str(nodo.right.value)]["Primera posicion"]] for item in sublist]
    # Si el hijo izquierdo es anulable, entonces se una las primeras posiciones de los hijos, de lo contrario solo es la primera posicion del hijo izquierdo
    elif data[str(nodo.value)]["Valor"] == ".":
        if data[str(nodo.left.value)]["Anulable"]:
            data[str(nodo.value)]["Primera posicion"] = [item for sublist in [data[str(nodo.left.value)]["Primera posicion"], data[str(nodo.right.value)]["Primera posicion"]] for item in sublist]
        else:
            data[str(nodo.value)]["Primera posicion"] = [item for sublist in [data[str(nodo.left.value)]["Primera posicion"]] for item in sublist]
    # Se obtiene la primera posicion de su hijo
    elif data[str(nodo.value)]["Valor"] == "*":
        data[str(nodo.value)]["Primera posicion"] = [item for sublist in [data[str(nodo.left.value)]["Primera posicion"]] for item in sublist]
    elif data[str(nodo.value)]["Valor"] == "?":
        data[str(nodo.value)]["Primera posicion"] = [item for sublist in [data[str(nodo.left.value)]["Primera posicion"], data[str(nodo.right.value)]["Primera posicion"]] for item in sublist]
    elif data[str(nodo.value)]["Valor"] == "+":
        data[str(nodo.value)]["Primera posicion"] = [item for sublist in [data[str(nodo.left.value)]["Primera posicion"]] for item in sublist]
    elif data[str(nodo.value)]["Valor"] == "E":
        data[str(nodo.value)]["Primera posicion"] = []
    # Primera posicion es la letra
    else:
        data[str(nodo.value)]["Primera posicion"] = [nodo.value]

def ultima_posicion(nodo, data):
    if data[str(nodo.value)]["Valor"] == "|":
        data[str(nodo.value)]["Ultima posicion"] = [item for sublist in [data[str(nodo.left.value)]["Ultima posicion"], data[str(nodo.right.value)]["Ultima posicion"]] for item in sublist]
    elif data[str(nodo.value)]["Valor"] == ".":
        if data[str(nodo.right.value)]["Anulable"]:
            data[str(nodo.value)]["Ultima posicion"] = [item for sublist in [data[str(nodo.left.value)]["Ultima posicion"], data[str(nodo.right.value)]["Ultima posicion"]] for item in sublist]
        else:
            data[str(nodo.value)]["Ultima posicion"] = [item for sublist in [data[str(nodo.right.value)]["Ultima posicion"]] for item in sublist]
    elif data[str(nodo.value)]["Valor"] == "*":
        data[str(nodo.value)]["Ultima posicion"] = [item for sublist in [data[str(nodo.left.value)]["Ultima posicion"]] for item in sublist]
    elif data[str(nodo.value)]["Valor"] == "?":
        data[str(nodo.value)]["Ultima posicion"] = [item for sublist in [data[str(nodo.left.value)]["Ultima posicion"], data[str(nodo.right.value)]["Ultima posicion"]] for item in sublist]
    elif data[str(nodo.value)]["Valor"] == "+":
        data[str(nodo.value)]["Ultima posicion"] = [item for sublist in [data[str(nodo.left.value)]["Ultima posicion"]] for item in sublist]
    elif data[str(nodo.value)]["Valor"] == "E":
        data[str(nodo.value)]["Ultima posicion"] = []
    else:
        data[str(nodo.value)]["Ultima posicion"] = [nodo.value]

# Solo para concatenacion y cerradura de kleene
def siguiente_posicion(nodo, data):
    # Para cada uno de las ultimas posiciones del hijo de la izquierda se pone las posiciones del hijo de la derecha 
    if data[str(nodo.value)]["Valor"] == ".":
        for up in data[str(nodo.left.value)]["Ultima posicion"]:
            for pp in data[str(nodo.right.value)]["Primera posicion"]:
                if pp not in data[str(nodo.left.value)]["Siguiente posicion"]:
                    data[str(up)]["Siguiente posicion"].append(pp)
    # Como solo es un hijo, para cada ultima posicion del hijo, se agrega TODO
    elif data[str(nodo.value)]["Valor"] == "*":
        for up in data[str(nodo.left.value)]["Ultima posicion"]:
            for pp in data[str(nodo.left.value)]["Primera posicion"]:
                if pp not in data[str(nodo.left.value)]["Siguiente posicion"]:
                    data[str(up)]["Siguiente posicion"].append(pp)

#El primer valor de la tabla es las primeras posiciones de la raiz del arbol
def transiciones_directo(transiciones, arbol, data, alfabeto):
    contador = 0
    transiciones[str(data[str(arbol.value)]["Primera posicion"])] = {
        "Estado": "S"+str(contador),
    }
    for letra in alfabeto:
        transiciones[str(data[str(arbol.value)]["Primera posicion"])][letra] = None
    contador += 1
    cont = True
    while(cont):
        initial_size = len(transiciones)
        keys = list(transiciones.keys())
        for llave in keys:
            for letra in alfabeto:
                if transiciones[llave][letra] == None:
                    new_state = []
                    estado = ast.literal_eval(llave)
                    for i in estado:
                        if data[str(i)]["Valor"] == letra:
                            new_state.append(data[str(i)]["Siguiente posicion"])
                    new_state = [item for sublist in new_state for item in sublist]
                    new_state = list(set(new_state))
                    new_state.sort()
                    if len(new_state) > 0:
                        if str(new_state) not in transiciones:
                            transiciones[str(new_state)] = {
                                "Estado": "S"+str(contador)
                            }
                            for letter in alfabeto:
                                transiciones[str(new_state)][letter] = None
                            contador +=1
                            transiciones[llave][letra] = transiciones[str(new_state)]["Estado"]
                        else:
                            transiciones[llave][letra] = transiciones[str(new_state)]["Estado"]
        final_size = len(transiciones)
        if initial_size == final_size:
            cont = not all(transiciones.values())

def simulacion_sub(transiciones, w, final):
    current_state = "0"
    for i in w:
        llave = ""
        for key, v in transiciones.items():
            if v["Estado del AFD"] == current_state and v[i] != None:
                llave = key
            elif v["Estado del AFD"] == current_state and v[i] == None:
                return False
        current_state = transiciones[llave][i]
    for llave, valor in transiciones.items():
        if valor["Estado del AFD"] == current_state:
            estado = ast.literal_eval(llave)
            if final in estado:
                return True
            else:
                return False

def simulacion_AFD(transiciones, w, final):
    estado_actual = "S0"
    for i in w:
        llave = ""
        for k, v in transiciones.items():
            if v["Estado"] == estado_actual and v[i] != None:
                llave = k
            elif v["Estado"] == estado_actual and v[i] == None:
                return False
        estado_actual = transiciones[llave][i]
    for llave, v in transiciones.items():
        if v["Estado"] == estado_actual:
            estados = ast.literal_eval(llave)
            if int(final) in estados:
                return True
            else:
                return False

padre_actual = analizador_expresion(r, None, padre_actual)
print(binarytree(padre_actual))


arbol = binarytree(padre_actual)
# print(arbol.postorder)



# ------------------------------ Thompson ------------------------------
arbol_postorder = arbol.postorder
dic_estados = {}
alfabeto_exp=[]
dic_transiciones={}
contador_estados = 1

# Diccionario de estados iniciales y finales de cada nodo
for i in arbol_postorder:
    dic_estados[str(contador_estados)] = {
        "Valor": caracteres[i.value],
        "Estado Inicial": None,
        "Estado Final": None,
    }
    i.value = contador_estados
    contador_estados +=1

# Alfabeto que tiene el alfabeto_exp del arbol mas E. Letras de la expresion
for hoja in arbol.leaves:
    for letra in alfabeto:
        if letra == dic_estados[str(hoja.value)]["Valor"]:
            if letra not in alfabeto_exp:
                alfabeto_exp.append(letra)

alfabeto_exp.sort()
alfabeto_exp.append("E")


contador = 1 # S0 = 0 (Inicial)
# Se llena el diccionario con los estados iniciales y finales de cada nodo
for j in arbol_postorder:
    # El or crea dos estados mas, dos nodos
    if dic_estados[str(j.value)]["Valor"] == "|":
        dic_estados[str(j.value)]["Estado Inicial"] = "S"+str(contador)
        contador += 1
        dic_estados[str(j.value)]["Estado Final"] = "S"+str(contador)
        contador += 1
    # Concatenación el final del hijo de la izquierda es el inicial del nodo de la derecha; el inicial de la derecha es el final de la izquierda
    elif dic_estados[str(j.value)]["Valor"] == ".":
        dic_estados[str(j.right.value)]["Estado Inicial"] = dic_estados[str(j.left.value)]["Estado Final"] 
        dic_estados[str(j.value)]["Estado Inicial"] = dic_estados[str(j.left.value)]["Estado Inicial"]
        dic_estados[str(j.value)]["Estado Final"] = dic_estados[str(j.right.value)]["Estado Final"]
    # Se crean dos estados nuevos como or
    elif dic_estados[str(j.value)]["Valor"] == "*":
        dic_estados[str(j.value)]["Estado Inicial"] = "S"+str(contador)
        contador += 1
        dic_estados[str(j.value)]["Estado Final"] = "S"+str(contador)
        contador += 1
    else:
        dic_estados[str(j.value)]["Estado Inicial"] = "S"+str(contador)
        contador += 1
        dic_estados[str(j.value)]["Estado Final"] = "S"+str(contador)
        contador += 1

# Estado inicial siempre es S0 pero al que se conecta no siempre es S1 pero si por defecto para luego actualizar este valor
estado_inicial = {
    "Estado Inicial": "S0",
    "Estado Final": "S1"
}
dot = graphviz.Digraph(comment='AFN')
dot.attr(rankdir='LR', size='15')
dot.attr(label="\nAFN: McNaughton-Yamada-Thompson")
dot.attr(fontsize='20')
dot.attr('node', shape='circle')

# Diccionario de transiciones, el contador tiene el maximo de estados
# Para cada estado y cada letra del alfabeto, una lista con cada una de sus transiciones
for i in range(contador):
    dic_transiciones["S"+str(i)]={}
    for letra in alfabeto_exp:
        dic_transiciones["S"+str(i)][letra] = []

for k in arbol_postorder:
    # Si es or, se conecta el inicial del or con el inicial de los dos hijos. El final de los hijos se conecta con el final del or
    # Poner estado inicial del or hacia el estado inicial de los hijos. El estado final de los hijos hacie el estado final del or
    if dic_estados[str(k.value)]["Valor"] == "|":
        # El final estate de s0 es el inical del or
        if dic_estados[str(k.left.value)]["Estado Inicial"] == estado_inicial["Estado Final"]:
            estado_inicial["Estado Final"] = dic_estados[str(k.value)]["Estado Inicial"]
        dot.node(str(dic_estados[str(k.value)]["Estado Inicial"]), str(dic_estados[str(k.value)]["Estado Inicial"]).translate(SUB))
        dot.node(str(dic_estados[str(k.left.value)]["Estado Inicial"]), str(dic_estados[str(k.left.value)]["Estado Inicial"]).translate(SUB))
        dot.node(str(dic_estados[str(k.right.value)]["Estado Inicial"]), str(dic_estados[str(k.right.value)]["Estado Inicial"]).translate(SUB))
        dot.edge(dic_estados[str(k.value)]["Estado Inicial"], dic_estados[str(k.left.value)]["Estado Inicial"], label="ε")
        # se guarda la transicion en la tabla de transiciones
        dic_transiciones[dic_estados[str(k.value)]["Estado Inicial"]]["E"].append(dic_estados[str(k.left.value)]["Estado Inicial"])

        dot.edge(dic_estados[str(k.value)]["Estado Inicial"], dic_estados[str(k.right.value)]["Estado Inicial"], label="ε")
        # se guarda la transicion en la tabla de transiciones
        dic_transiciones[dic_estados[str(k.value)]["Estado Inicial"]]["E"].append(dic_estados[str(k.right.value)]["Estado Inicial"])

        if dic_estados[str(k.value)]["Estado Final"] == "S"+str(contador-1):
            dot.node(str(dic_estados[str(k.value)]["Estado Final"]), str(dic_estados[str(k.value)]["Estado Final"]).translate(SUB), shape='doublecircle')
        else:
            dot.node(str(dic_estados[str(k.value)]["Estado Final"]), str(dic_estados[str(k.value)]["Estado Final"]).translate(SUB))
        dot.node(str(dic_estados[str(k.left.value)]["Estado Final"]), str(dic_estados[str(k.left.value)]["Estado Final"]).translate(SUB))
        dot.node(str(dic_estados[str(k.right.value)]["Estado Final"]), str(dic_estados[str(k.right.value)]["Estado Final"]).translate(SUB))
        dot.edge(dic_estados[str(k.left.value)]["Estado Final"], dic_estados[str(k.value)]["Estado Final"], label="ε")
        dic_transiciones[dic_estados[str(k.left.value)]["Estado Final"]]["E"].append(dic_estados[str(k.value)]["Estado Final"])

        dot.edge(dic_estados[str(k.right.value)]["Estado Final"], dic_estados[str(k.value)]["Estado Final"], label="ε")
        dic_transiciones[dic_estados[str(k.right.value)]["Estado Final"]]["E"].append(dic_estados[str(k.value)]["Estado Final"])

    # El inicial del kleene con el inicial del hijo, el final del hijo con el final de Kleene
    elif dic_estados[str(k.value)]["Valor"] == "*":
        if dic_estados[str(k.left.value)]["Estado Inicial"] == estado_inicial["Estado Final"]:
            estado_inicial["Estado Final"] = dic_estados[str(k.value)]["Estado Inicial"]
        dot.node(str(dic_estados[str(k.value)]["Estado Inicial"]), str(dic_estados[str(k.value)]["Estado Inicial"]).translate(SUB))
        dot.node(str(dic_estados[str(k.left.value)]["Estado Inicial"]), str(dic_estados[str(k.left.value)]["Estado Inicial"]).translate(SUB))
        dot.edge(dic_estados[str(k.value)]["Estado Inicial"], dic_estados[str(k.left.value)]["Estado Inicial"], label="ε")
        dic_transiciones[dic_estados[str(k.value)]["Estado Inicial"]]["E"].append(dic_estados[str(k.left.value)]["Estado Inicial"])

        if dic_estados[str(k.value)]["Estado Final"] == "S"+str(contador-1):
            dot.node(str(dic_estados[str(k.value)]["Estado Final"]), str(dic_estados[str(k.value)]["Estado Final"]).translate(SUB), shape='doublecircle')
        else:
            dot.node(str(dic_estados[str(k.value)]["Estado Final"]), str(dic_estados[str(k.value)]["Estado Final"]).translate(SUB))
        dot.node(str(dic_estados[str(k.left.value)]["Estado Final"]), str(dic_estados[str(k.left.value)]["Estado Final"]).translate(SUB))
        dot.edge(dic_estados[str(k.left.value)]["Estado Final"], dic_estados[str(k.value)]["Estado Final"], label="ε")
        dic_transiciones[dic_estados[str(k.left.value)]["Estado Final"]]["E"].append(dic_estados[str(k.value)]["Estado Final"])

        dot.edge(dic_estados[str(k.value)]["Estado Inicial"], dic_estados[str(k.value)]["Estado Final"], label="ε")
        dic_transiciones[dic_estados[str(k.value)]["Estado Inicial"]]["E"].append(dic_estados[str(k.value)]["Estado Final"])

        dot.edge(dic_estados[str(k.left.value)]["Estado Final"], dic_estados[str(k.left.value)]["Estado Inicial"], label="ε")
        dic_transiciones[dic_estados[str(k.left.value)]["Estado Final"]]["E"].append(dic_estados[str(k.left.value)]["Estado Inicial"])

    elif dic_estados[str(k.value)]["Valor"] == ".":
        # los hijos de la concatenacion ya tienen la concatenacion
        pass
    # si es letra, se una el estado inicial con el estado final
    else:
        dot.node(str(dic_estados[str(k.value)]["Estado Inicial"]),str(dic_estados[str(k.value)]["Estado Inicial"]).translate(SUB))
        if str(dic_estados[str(k.value)]["Estado Final"]) == "S"+str(contador-1):
            dot.node(str(dic_estados[str(k.value)]["Estado Final"]), str(dic_estados[str(k.value)]["Estado Final"]).translate(SUB), shape='doublecircle')
        else:
            dot.node(str(dic_estados[str(k.value)]["Estado Final"]), str(dic_estados[str(k.value)]["Estado Final"]).translate(SUB))
        dot.edge(str(dic_estados[str(k.value)]["Estado Inicial"]), str(dic_estados[str(k.value)]["Estado Final"]), label=dic_estados[str(k.value)]["Valor"])
        dic_transiciones[dic_estados[str(k.value)]["Estado Inicial"]][dic_estados[str(k.value)]["Valor"]].append(dic_estados[str(k.value)]["Estado Final"])

# Se hace el S0 y se conecta
dot.node(str(estado_inicial["Estado Inicial"]), str(estado_inicial["Estado Inicial"]).translate(SUB))
dot.edge(estado_inicial["Estado Inicial"], estado_inicial["Estado Final"], label="ε")
dic_transiciones[estado_inicial["Estado Inicial"]]["E"].append(estado_inicial["Estado Final"])

dot.view()
dot.render(directory='output', filename='Thompson')

simulacion_afn = simulacion_AFN(w, dic_transiciones, "S"+str(contador-1))
print("AFN: la cadena pertenece") if simulacion_afn else print("AFN: la cadena no pertenece")
    



# ------------------------------ Subconjuntos ------------------------------
sub_afd_transiciones = {}
# print(subconjuntos(dic_transiciones, sub_afd_transiciones, alfabeto_exp))

contador2 = 0
# Se quita epsilon ya que no existe transiciones con cadena vacia en AFD
alfabeto_exp.remove("E")

# Cerradura epsilon de estado inicial de afn
cerradura_epsilon = cerraduraEpsilon("S0", dic_transiciones, [])
cerradura_epsilon.sort()

# Diccionario de transiciones de AFD, la llave son los conjuntos de estados
sub_afd_transiciones[str(cerradura_epsilon)] = {
    "Estado del AFD": str(contador2),
}

# Transiciones con cada uno si existe
for i in alfabeto_exp:
    sub_afd_transiciones[str(cerradura_epsilon)][i] = None

contador2 += 1
continuar = True
while(continuar):
    sub_afd_long = len(sub_afd_transiciones)
    estados_afd = list(sub_afd_transiciones.keys())
    # Se recorre el diccionario
    for j in estados_afd:
        # Se recorre cada uno de los elementos
        for i in alfabeto_exp:
            if sub_afd_transiciones[j][i] == None:
                nuevo_estado = []
                split = ast.literal_eval(j)
                nuevo_estado = cerraduraEpsilon_s(mover(split, i, dic_transiciones), dic_transiciones)

                # Si el conjunto no es llave de diccionario, se agrega como nueva llave y se actualiza las transiciones
                if len(nuevo_estado) > 0:
                    if str(nuevo_estado) not in sub_afd_transiciones:
                        sub_afd_transiciones[str(nuevo_estado)] = {
                            "Estado del AFD": str(contador2)
                        }
                        for letter in alfabeto_exp:
                            sub_afd_transiciones[str(nuevo_estado)][letter] = None
                        contador2 +=1
                        sub_afd_transiciones[j][i] = sub_afd_transiciones[str(nuevo_estado)]["Estado del AFD"]
                    # Si ya estaba en la lista, se agrega el estado nuevo a la transicion evaluada 
                    else:
                        sub_afd_transiciones[j][i] = sub_afd_transiciones[str(nuevo_estado)]["Estado del AFD"]
    final_size = len(sub_afd_transiciones)
    if sub_afd_long == final_size:
        continuar = not all(sub_afd_transiciones.values())


# Dibujo AFD por subconjuntos 
dot_subconjuntos = graphviz.Digraph(comment="AFD")
dot_subconjuntos.attr(rankdir='LR', size='15')
dot_subconjuntos.attr(label="\nAFD: Subconjuntos")
dot_subconjuntos.attr(fontsize='20')
dot_subconjuntos.attr('node', shape='circle')

# Se dibujan los nodos de afd por subconjuntos
for i in sub_afd_transiciones.keys():
    estados = ast.literal_eval(i)
    if ("S"+str(contador-1)) in estados:
        dot_subconjuntos.node(sub_afd_transiciones[i]["Estado del AFD"], sub_afd_transiciones[i]["Estado del AFD"], shape='doublecircle')
    else:
        dot_subconjuntos.node(sub_afd_transiciones[i]["Estado del AFD"], sub_afd_transiciones[i]["Estado del AFD"])
        

for llave, valor in sub_afd_transiciones.items():
    for j in alfabeto_exp:
        if valor["Estado del AFD"] != None and valor[j] != None:
            estados = ast.literal_eval(llave)

            # Estado final
            if ("S"+str(contador-1)) in estados:
                dot_subconjuntos.node(valor["Estado del AFD"], valor["Estado del AFD"],  shape='doublecircle')
            else:
                dot_subconjuntos.node(valor["Estado del AFD"], valor["Estado del AFD"])
            dot_subconjuntos.node(valor[j], valor[j])
            dot_subconjuntos.edge(valor["Estado del AFD"], valor[j], j)

dot_subconjuntos.view()
dot.render(directory='output', filename='Subconjuntos')

simulacionSub = simulacion_sub(sub_afd_transiciones, w, str("S"+str(contador-1)))
print("AFD (subconjuntos): La cadena pertenece") if simulacionSub else print("AFD (subconjuntos): La cadena no pertenece")

# ------------------------------ AFD dada una expresion regular ------------------------------
# Se agrega el # que representa el ultimo caracter para el estado de aceptacion
r = "("+r+")#"
current_node_head2 = None
current_node_head2 = analizador_expresion(r, None, current_node_head2)
tree = binarytree(current_node_head2)

data = {}
transiciones2 = {}
alfabeto2=[]
arbol = tree
arbolito = tree
contador = 1
# Letra que representa, anulable, primera posicion, ultima posicion, siguiente posicion
for i in arbol.postorder:
    data[str(contador)] = {
        "Valor": caracteres[i.value],
        "Anulable": None,
        "Primera posicion": None,
        "Ultima posicion": None,
        "Siguiente posicion": [],
    }
    i.value = contador
    contador +=1
for hoja in arbol.leaves:
    for letra in alfabeto:
        if letra == data[str(hoja.value)]["Valor"]:
            if letra not in alfabeto2:
                alfabeto2.append(letra)
alfabeto2.sort()


for nodo in arbol.postorder:
    anulable(nodo, data)
    primera_posicion(nodo, data)
    ultima_posicion(nodo, data)
    siguiente_posicion(nodo, data)
transiciones_directo(transiciones2, arbol, data, alfabeto2)

resultadoAFD = simulacion_AFD(transiciones2, w, str(arbol.right.value))
print("AFD (Directo): La cadena pertenece") if resultadoAFD else print("AFD (Directo): La cadena no pertenece")



dot_directa = graphviz.Digraph(comment="AFD")
dot_directa.attr(rankdir='LR', size='15')
dot_directa.attr(label="\nAFD: Dada una expresión regular")
dot_directa.attr(fontsize='20')
dot_directa.attr('node', shape='circle')

for i in transiciones2.keys():
    estados = ast.literal_eval(i)
    if str(arbol.right.value) in estados:
        dot_directa.node(str(transiciones2[i]["Estado"]), str(transiciones2[i]["Estado"]).translate(SUB), shape='doublecircle')
    else:
        dot_directa.node(str(transiciones2[i]["Estado"]), str(transiciones2[i]["Estado"]).translate(SUB))
        

for llave, valor in transiciones2.items():
    for c in alfabeto2:
        if valor["Estado"] != None and valor[c] != None:
            dot_directa.edge(valor["Estado"], valor[c], c)

dot_directa.view()
dot.render(directory='output', filename='Directo')
