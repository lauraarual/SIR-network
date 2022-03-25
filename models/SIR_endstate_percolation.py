import networkx as nx
import matplotlib.pyplot as plt
import math
import random
import importlib
import get_values_of_graph as graph_values #Load functions from our own functions.py file
import SIR_dynamic_functions as functions #Load functions from own functions.py file
###########################################
###########################################
#testing_data
# contact_data_file = "../data/test.txt"
# split_sign_between_data = ";"
# has_header = True
# iterations = 5
# infection_probability = 0.07
# recovery_time = 5
#####################
#SET PARAMETERS
contact_data_file = "../data/2008_Mossong_POLYMOD_contact_common.csv" #edge file; 2 columns of connected nodes; see test.txt file as reference; It doesnt matter if more colums are present.
#for POLYMOD it is "\t"
split_sign_between_data = "\t" #for example ";" ,"\t", " "
has_header = True

iterations = 100

infection_probability = 0.02 #percent as decimal eg. 7% = 0.07
recovery_time = 12.5 #in days; contagious days (therefore, without latency)
#####################
#module_random graph; use the boolean underneath to switch the module on and off  - set modul-specific parameters
module_random_graph = False
#test data
# number_of_nodes = 18
# number_of_edges = 21

##same edges and nodes as network you compare with. #get from running percolation script or ger_values_of_graph script
number_of_nodes = 7256
number_of_edges = 59534
############################################
############################################
if module_random_graph:
    print("module_random_graph is switched on")

list_of_results = []
starting_node_list = []
percolated_graph_number_of_edges = []

#leaving in place each edge with pb=1–e^(–β ̃*τ)
#transmission_probability = 0.5 #for testing
transmission_probability = 1 - math.exp(-infection_probability*recovery_time)

if module_random_graph:
    pass
else:
    starting_node_list.extend(graph_values.get_values_of_graph(contact_data_file, has_header, split_sign_between_data)) #needs time, therefore extra before loop

print()
print("transmission_probability is "+str(transmission_probability))

#iteration
for index in range(0,iterations):
    edges = []
    # percolation: read edges file and only take those edges which pass the "probability test"
    if module_random_graph:
        graph = nx.gnm_random_graph(number_of_nodes, number_of_edges)
        starting_node_list = functions.get_starting_node_list(graph) #getting starting node list and rounded average degree; needed for R0 and also below
        #print("starting node list: " +str(starting_node_list))
        for line in nx.generate_edgelist(graph):
            if random.random() < transmission_probability: #occupation probability
                splitted = line.split(" ")
                tuple = (splitted[0],str.rstrip(splitted[1]))  #taking 1st and 2nd entry from splitted line
                edges.append(tuple)

    else:
        file = open(contact_data_file,  "rb")
        if has_header:
            next(file) #skips 1st line, when there is a header
        for line in file:
            if random.random() < transmission_probability: #occupation probability
                splitted = line.decode().split(split_sign_between_data)
                tuple = (splitted[0],str.rstrip(splitted[1]))  #taking 1st and 2nd entry from splitted line
                edges.append(tuple)
        file.close()

    #control point
    #print(edges)
    percolated_graph_number_of_edges.append(len(edges))

    #create percolated graph with edge list
    percolated_graph = nx.Graph()
    percolated_graph.add_edges_from(edges)

    #draw graph
    #nx.draw(percolated_graph, with_labels=True, font_weight='bold')
    #plt.show()

    #get size of disease outbreak
    # getting random starting node with average degree
    starting_node = random.choice(starting_node_list)
    print("iteration " + str(index) + "; starting node is node number " + str(starting_node))

    if starting_node in percolated_graph:
        infected_component = nx.node_connected_component(percolated_graph, starting_node)
        #print("infected component: "+ str(infected_component))
        number_of_infected = len(infected_component)
        list_of_results.append(number_of_infected)

        print("total_number_of_infected is " + str(number_of_infected))

    else:
        print("infected person did not pass on disease")
        list_of_results.append(1)


print("Number of infected for each run: " + str(list_of_results))
average_result = sum(list_of_results)/len(list_of_results)
print("Average number of infected individuals after " + str(iterations) + " iterations: "+ str(average_result))
percolated_graph_average_number_of_edges = sum(percolated_graph_number_of_edges)/len(percolated_graph_number_of_edges)
print("Average number of edges is "+ str(percolated_graph_average_number_of_edges))
