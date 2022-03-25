import random
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import statistics

def load_graph_from_file(contact_data_file, split_sign_between_data, has_header):
    edges = []
    #read edges file
    file = open(contact_data_file, 'rb')
    if has_header:
        next(file)  #skips 1st line, when there is a header
    for line in file:
        #print(line)
        splitted = line.decode().split(split_sign_between_data)
        tuple = (splitted[0], str.rstrip(splitted[1]))  #I take 1st and 2nd entry from splitted line and remove /r/n from 2nd entry
        edges.append(tuple)
    file.close()
    #control point
    #print(edges)
    #create graph with edge list
    graph = nx.Graph()
    graph.add_edges_from(edges)
    return graph

def set_initial_node_values(graph, starting_node_list): #parameters are handed in to this method from the ipynb file
    nx.set_node_attributes(graph, 'susceptible', 'compartment') #set all nodes initially to 'susceptible' compartpment
    starting_node = random.choice(starting_node_list)

    #change compartment of starting node and start the timer "time_already infected" for this node
    graph.nodes[starting_node]['compartment'] = 'infected'
    graph.nodes[starting_node]['time_infected'] = 0
    print("starting node is node number " + str(starting_node))

def simulate_day(graph, recovery_time, infection_probability_today, module_exposed, latency_time, module_quarantine,
                 day_on_which_to_quarantine, quarantine_probability):
    nodes_to_infect = set() #we need to first create a set of nodes (set, bcs we need unique values for counting) which will be infected without actually changing them yet as it would otherwise influence the iteration process

    for node in graph.nodes:

        #module quarantine - increase infected timer for quarantined nodes and move them to recovered after recovery time
        if graph.nodes[node]['compartment'] == 'quarantined':
            graph.nodes[node]['time_infected'] = graph.nodes[node]['time_infected'] + 1
            if graph.nodes[node]['time_infected'] > recovery_time:
                graph.nodes[node]['compartment'] = 'recovered'

        #normal code
        if graph.nodes[node]['compartment'] == 'infected':
            #print("I am infected! node number: " +str(node))
            #advancing the timer - letting the infected heal over time until he/she recovers at the set recovery time
            graph.nodes[node]['time_infected'] = graph.nodes[node]['time_infected'] + 1

            if module_quarantine and graph.nodes[node]['time_infected'] == day_on_which_to_quarantine:
                if random.random() < quarantine_probability: #random gives number [0,1]. Uses the custom set day_on_which_to_quarantine as a chance to quarantine
                    graph.nodes[node]['compartment'] = 'quarantined'

            #I->R: when the timer runs out, the node is recovered at the beginning of the next day
            if graph.nodes[node]['time_infected'] > recovery_time:
                graph.nodes[node]['compartment'] = 'recovered'

            #S->I? infected node maybe infecting susceptible neighbor nodes
            #print("neighbours of " + node + " are " + str(graph.neighbors(node)))
            for neighbor in graph.neighbors(node):
                if graph.nodes[neighbor]['compartment'] == 'susceptible':
                    #print("Oh no, I am node " + str(neighbor) +" and a suspectible neighbor of an infected!")
                    if random.random() < infection_probability_today: #random gives number [0,1]. Uses the custom set infection probability as a chance to infect the neighbour
                        nodes_to_infect.add(neighbor)
                        #print("A node got quarantined!")

        #module exposed - move exposed nodes to infected state after latency time
        if graph.nodes[node]['compartment'] == 'exposed':
            graph.nodes[node]['time_exposed'] = graph.nodes[node]['time_exposed'] + 1
            if graph.nodes[node]['time_exposed'] == latency_time: #here == and not as above with infected >recovery time, as on this day, no infection is happening anymore
                graph.nodes[node]['compartment'] = 'infected'
                graph.nodes[node]['time_infected'] = 0  # does not infect this round therefore 0

    #actually infecting the nodes after completely calculating which ones get infected. Change of compartment type and starting of timer
    for node in nodes_to_infect:
        infect_node(graph, node, module_exposed) #infect_node is method, see below

    return nodes_to_infect


def infect_node(graph, node, module_exposed):
    #normal code
    graph.nodes[node]['compartment'] = 'infected'
    graph.nodes[node]['time_infected'] = 0  # does not infect this round therefore 0

    #module exposed - move infected nodes to 'exposed' compartment for n days before moving them on to 'infected'. this overwirtes the code snippet above
    if module_exposed:
        graph.nodes[node]['compartment'] = 'exposed'
        graph.nodes[node]['time_exposed'] = 0

#going through graph and checking number of nodes in every compartment
def count_compartment(graph):
    count_susceptible = 0
    count_infected = 0  # if module_quarantine on, then quarantined are also included here
    count_exposed = 0  # if module_exposed is on, otherwise zero
    count_recovered = 0

    for node in graph.nodes:
        if graph.nodes[node]['compartment'] == 'susceptible':
            count_susceptible += 1
        if graph.nodes[node]['compartment'] == 'infected' or graph.nodes[node]['compartment'] == 'quarantined':
            count_infected += 1
        if graph.nodes[node]['compartment'] == 'exposed':
            count_exposed += 1
        if graph.nodes[node]['compartment'] == 'recovered':
            count_recovered += 1

    return count_susceptible, count_infected, count_exposed, count_recovered


#draw drawing
def draw_drawing(result_compartments_for_every_day_for_each_iteration, N, module_exposed, module_random_graph, module_lockdown, module_quarantine):
#unfortunately, the iterations can all end on different days, therefore a matrix cannot be used. Here, data structure is transformed to get the mean of each day
    duration_disease = []

    other_format = {
        'S': defaultdict(lambda: []), #provides a default value for the key that does not exist. lambda: if appending to a list which does not exist (yet), an empty list is given to which it can be appended. easier than manually creating 50 lists for every day:)
        'E': defaultdict(lambda: []),
        'I': defaultdict(lambda: []),
        'R': defaultdict(lambda: [])
    }

    for result_compartment in  result_compartments_for_every_day_for_each_iteration:
        for day in range(0,len(result_compartment['S'])):
            other_format['S'][day].append(result_compartment['S'][day])
            other_format['E'][day].append(result_compartment['E'][day])
            other_format['I'][day].append(result_compartment['I'][day])
            other_format['R'][day].append(result_compartment['R'][day])

        #I also want to know the average days the disease takes
        duration_disease.append(len(result_compartment['S']))

    #averages
    average_S_per_day = [statistics.mean(other_format['S'][day]) for day in other_format['S'].keys()] #day is the key. the value is a list of the nth day of all iterations.
    average_E_per_day = [statistics.mean(other_format['E'][day]) for day in other_format['E'].keys()]
    average_I_per_day = [statistics.mean(other_format['I'][day]) for day in other_format['I'].keys()]
    average_R_per_day = [statistics.mean(other_format['R'][day]) for day in other_format['R'].keys()]

    #fractions of population
    s = [value/N for value in average_S_per_day]
    e = [value/N for value in average_E_per_day]
    i = [value/N for value in average_I_per_day]
    r = [value/N for value in average_R_per_day]

    #average duration of disease
    average_duration_disease = (sum(duration_disease)/len(duration_disease)) - 1 #Minus one, because entries from day 0 are also included.
    print("Average duration of disease is " + str(average_duration_disease))

    print("Average total number of infected is " + str(average_R_per_day[-1])) #retrieves the last entry in recovered list

    # write filename
    filename_compartments = ["S"]
    filename_modules = []

    if module_exposed:
        filename_compartments.append("E")
    filename_compartments.append("I")
    if module_quarantine:
        filename_compartments.append("Q")
    if module_random_graph:
        filename_modules.append("random_graph")
    if module_lockdown:
        filename_modules.append("lockdown")
    filename_compartments.append("R")

    #plotting
    #show all iterations in one graph
    all_iterations = plt.figure()
    ax_iterations = all_iterations.add_subplot()
    ax_iterations.set(xlabel='time', ylabel='Fraction of population',title='Network ' + "".join(filename_compartments) + " " + " ".join(filename_modules)) #for .join is separator for elements in list

    #mean
    ax_iterations.plot(s, color="blue", markersize=2)
    if module_exposed:
        ax_iterations.plot(e, color="darkorange", markersize=2)
    ax_iterations.plot(i, color="red", markersize=2)
    ax_iterations.plot(r, color="green", markersize=2)

    #all results
    for result_compartment in result_compartments_for_every_day_for_each_iteration:
        ax_iterations.plot([value/N for value in result_compartment['S']], color="royalblue", alpha=0.2)
        if module_exposed:
            ax_iterations.plot([value/N for value in result_compartment['E']], color="sandybrown", alpha=0.2)
        ax_iterations.plot([value/N for value in result_compartment['I']], color="tomato", alpha=0.2)
        ax_iterations.plot([value/N for value in result_compartment['R']], color="mediumseagreen", alpha=0.2)

    plt.legend(('S', 'I', 'R'), loc='upper right')
    if module_exposed:
        plt.legend(('S', 'E', 'I', 'R'), loc='upper right')

    #save files
    if module_exposed:
        all_iterations.savefig("result_dynamic_" + "".join(filename_compartments) + "_" + "_".join(filename_modules) + ".png")
    all_iterations.show()

def use_random_graph(number_of_nodes, number_of_edges):
    graph = nx.gnm_random_graph(number_of_nodes, number_of_edges)
    nx.set_node_attributes(graph, 'susceptible', 'compartment')  # set all nodes initially to 'susceptible' compartment
    print(graph.nodes)
    starting_node_list = get_starting_node_list(graph)
    starting_node = int(random.choice(starting_node_list))
    print("starting node list is: " + str(starting_node_list))
    print("starting node is node number " + str(starting_node))

    # change compartment of starting node and start the timer "time_already infected" for this node
    graph.nodes[starting_node]['compartment'] = 'infected'
    graph.nodes[starting_node]['time_infected'] = 0
    return graph

def get_starting_node_list(graph):

    starting_node_list = []
    # get all degrees of nodes and calculate average degree
    degrees = []
    # print("node_degrees " + str(graph.degree))
    degree = graph.degree
    for tuple in degree:
        degrees.append(tuple[1])
    average_degree = sum(degrees) / len(degrees)
    rounded_average_degree = round(average_degree)
    #find nodes with same degree as average degree
    for node_tuple in degree:
        if node_tuple[1] == rounded_average_degree:
            starting_node_list.append(str(node_tuple[0]))
    return starting_node_list


