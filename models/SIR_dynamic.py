import time
import networkx as nx
import matplotlib.pyplot as plt
import threading
import math
import random
import importlib
from multiprocessing import Pool
import SIR_dynamic_functions as functions #Load functions from own functions.py file
#################################################################
#################################################################
#testing_data (you can comment a whole block in and out with 1. select block 2. str+shift+c)
# contact_data_file = "../data/test.txt"
# has_header = True
# split_sign_between_data = ';'
# iterations = 3
# recovery_time = 6
# infection_probability = 0.8
# number_of_threads = 8
##################
#SET PARAMETERS
contact_data_file = "../data/2008_Mossong_POLYMOD_contact_common.csv" #edge file; 2 columns of connected nodes; see test.txt file as reference; It doesnt matter if more colums are present.
has_header = True
split_sign_between_data = '\t' #for example ";" ,"\t", " "

iterations = 100 #number of simulations

recovery_time = 12.5 #in days; contagious days (therefore, without latency); can infect others on n days; recovered at the beginning of the (n+1)th day.
infection_probability = 0.02 #percent as decimal eg. 7% = 0.07
#make sure that the ratio between recovery time and infection_probability corresponds to your chosen R0!

number_of_threads = 8 #number of (virtual) cpu cores. is needed to run the process faster. if you dont know how many cpu cores your computer has, just put it to 2
###################
#module_lockdown; use the boolean underneath to switch the module on and off - set modul-specific parameters
module_lockdown = True
day_lockdown_implemented = 8 #in days; Chosen in a way that - for POLYMOD data - 5% are already infected. If you want to have 5% with other data also, run the script without lockdown first, and then roughly estimate with drawn graph
infection_probability_lockdown = 0.013
###################
#module_exposed;  use the boolean underneath to switch the module on and off - set modul-specific parameters
module_exposed = True
latency_time = 4 #in days, they start to infect on the (n+1)th day
###################
#module_quarantine; use the boolean underneath to switch the module on and off  - set modul-specific parameters
module_quarantine = True
quarantine_probability = 2/3 #percentage of people going into quarantine; as fraction or decimal

#concerns nodes in compartment "infected". on day_on_which_to_quarantine nodes are immeditely quarantined and cannot infect someone on that day
#from this day onward, node is in quarantine and cannot infect anymore
day_on_which_to_quarantine = 3
##################
#module_random graph; use the boolean underneath to switch the module on and off  - set modul-specific parameters
module_random_graph = True
#test data
# number_of_nodes = 18
# number_of_edges = 21

##same edges and nodes as network you compare with. #get from running percolation script or ger_values_of_graph script
number_of_nodes = 7256
number_of_edges = 59534
###############################################################
###############################################################

if module_exposed:
    print("module_exposed is switched on")
if module_lockdown:
    print("module_lockdown is switched on")
if module_quarantine:
    print("module_quarantine is switched on")
if module_random_graph:
    print("module_random_graph is switched on")

start_time = time.perf_counter() #Measuring script runtime

starting_node_list = []

#get starting node list
if module_random_graph:
    pass
else:
    graph = functions.load_graph_from_file(contact_data_file, split_sign_between_data, has_header)
    #get number of nodes
    number_of_nodes = nx.number_of_nodes(graph)
    starting_node_list.extend(functions.get_starting_node_list(graph)) #extend gives a list of values to a existing list

#method which runs a single iteration
def run_iteration(iteration):
    #load graph
    if module_random_graph:
        graph = functions.use_random_graph(number_of_nodes, number_of_edges)  # gives all nodes compartment "susceptible" and infects starting node
    else:
        graph = functions.load_graph_from_file(contact_data_file, split_sign_between_data, has_header)
        print("starting_node_list " + str(starting_node_list))
        # give all nodes compartment "susceptible" and infect starting node
        functions.set_initial_node_values(graph, starting_node_list)

    # draw graph
    # functions.nx.draw(graph, with_labels=True, font_weight='bold') #this takes a lot of time! remove when having a lot of iterations!!!!!
    # plt.show()
    # show list of nodes
    # print("original graph " + str(graph.nodes(data=True)))
    print()

    #state at time step 0 in all compartments
    E = [0]
    I = [1]  # quarantined are part of infected, if present
    S = [number_of_nodes - I[0]]
    R = [0]
    continue_running_simulation = True
    day = 1
    while continue_running_simulation:  # boolean; true is implied
        infection_probability_today = infection_probability
        if module_lockdown and day >= day_lockdown_implemented: #change infection probability on set day
            infection_probability_today = infection_probability_lockdown

        nodes_to_infect = functions.simulate_day(graph, recovery_time, infection_probability_today, module_exposed, #simulate one day; see SIR_dynamic functions file
                                                 latency_time, module_quarantine,  day_on_which_to_quarantine, quarantine_probability)
        print(
            "interation " + str(iteration) + ", day " + str(day) + "; number_of_nodes_which_got_infected_today: " + str(
                len(nodes_to_infect)))
        count_susceptible, count_infected, count_exposed, count_recovered = functions.count_compartment(graph)
        if count_exposed == 0 and count_infected == 0:
            continue_running_simulation = False  #when no infected (or quarantined or exposed) are present at the end of the day, the model stops

        #total in departments per day
        S.append(count_susceptible)
        E.append(count_exposed)
        I.append(count_infected)
        R.append(count_recovered)

        day += 1
    result = {
        "iteration": iteration,
        "S": S,  #S, E, I, R are lists
        "E": E,
        "I": I,
        "R": R
    }
    return result

if __name__ == "__main__": #in this case needed for pool library
    pool = Pool(number_of_threads)
    #list which stores the results of departmnets from every iteration;
    result_departments_for_every_day_for_each_iteration = pool.map(run_iteration, range(0, iterations)) #mapping threads to iteration
    pool.close()

    print()
    print("All results: " + str(result_departments_for_every_day_for_each_iteration)) #note1: count is done in the "evening". Therefore, on day 1 there can already be 3 nodes in compartment "I", however, only the first seed node did spread on this day.
    #note2: the same goes for "exposed".

    functions.draw_drawing(result_departments_for_every_day_for_each_iteration, number_of_nodes, module_exposed, module_random_graph, module_lockdown, module_quarantine)

    print("completed in " + str(time.perf_counter() - start_time) + " seconds")