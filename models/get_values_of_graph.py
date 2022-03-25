import matplotlib.ticker
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import time
#######################
#set parameter here for direct use

#two lines underneath concern the test data
# contact_data_file = "../data/test.txt"
# split_sign_between_data = ";"

contact_data_file = "../data/2008_Mossong_POLYMOD_contact_common.csv"
split_sign_between_data = "\t" #for example ";" ,"\t", " "
has_header = True
#######################

def get_values_of_graph(contact_data_file, has_header, split_sign_between_data):

    start_time = time.perf_counter()
    edges = []

    file = open(contact_data_file, "rb")
    if has_header:
        next(file)  # skips 1st line, when there is a header
    for line in file:
        splitted = line.decode().split(split_sign_between_data)
        tuple = (splitted[0], str.rstrip(splitted[1]))  #I take 1st and 2nd entry from splitted line and remove /r/n from 2nd entry
        edges.append(tuple)
    file.close()

    # create graph
    graph = nx.Graph()
    graph.add_edges_from(edges)

    # draw graph
    # nx.draw(graph, with_labels=True, font_weight='bold') #takes (realativley) a lot of time with larger datasets and then you also do not see anything
    # plt.show()

    #get number of nodes/edges
    number_of_nodes = nx.number_of_nodes(graph)
    number_of_edges = nx.number_of_edges(graph)



    #get all degrees of nodes and calculate average degree
    degrees = []
    #print("node_degrees " + str(graph.degree))
    degree = graph.degree
    for tuple in degree:
        degrees.append(tuple[1])
    average_degree = sum(degrees)/len(degrees)
    rounded_average_degree = round(average_degree)

    #get list of nodes with same degree as average degree - needed for percolation
    list_of_nodes_same_as_average_degree = []
    for node_tuple in degree:
        if node_tuple[1] == rounded_average_degree:
            list_of_nodes_same_as_average_degree.append(node_tuple[0])

    #components
    components = nx.connected_components(graph)
    sorted_component_list_descending = sorted(components, key=len, reverse=True)
    largest_component = sorted_component_list_descending[0]

    #plot log-log graph
    degree_histogramm = nx.degree_histogram(graph)
    print("degree_histogram " + str(degree_histogramm))
    plt.figure()
    plt.scatter(range(len(degree_histogramm)), [value / number_of_nodes for value in degree_histogramm])#x-axes number of found degrees; y-values distribution, making into fraction of N;
    #print("rangelength bla " + str(range(len(degree_histogramm))))
    #print("valuebla " +str([value / number_of_nodes for value in degree_histogramm]))
    plt.yscale('log')
    plt.yticks([10**0, 10**(-1), 10**(-2), 10**(-3), 10**(-4), 10**(-5)]) #y-axis plotting range
    plt.xscale('log')
    plt.xticks([10 ** 0, 10 ** (1), 10 ** (2), 10 ** (3), 10 ** (4)]) #x-axis plotting range
    plt.xlabel('Degree')
    plt.ylabel('Degree distribution')
    plt.title("Degree distribution")
    plt.savefig("Degree distribution network.png")
    plt.show()

    #plot bar histogramm
    degree_sequence = sorted([degree_of_node for node, degree_of_node in degree], reverse=True) #degree as defined aboth gives back tuple (node,degree_of_node); sorted big to small
    #print("degrees " + str(degree))
    #print("degree sequence " + str(degree_sequence))
    fig = plt.figure("Degree of a random graph", figsize=(7, 7))
    ax2 = fig.add_subplot()
    ax2.bar(*np.unique(degree_sequence, return_counts=True)) #unique sorts small to big and 1. takes unique values for points on x-axis 2. return_counts for the y-axis; * makes that returns are used for 1.&2. parameter
    ax2.set_title("Degree histogram")
    ax2.set_xlabel("Degree")
    ax2.set_ylabel("Number of Nodes")
    fig.tight_layout()
    plt.show()

    #print values
    print("Graph values:")
    print("Number of nodes " + str(number_of_nodes))
    print("Number of edges " + str(number_of_edges))
    print("average degree " + str(average_degree))
    print("rounded average degree " + str(rounded_average_degree))
    print("starting node list " + str(list_of_nodes_same_as_average_degree))
    # print("degree histogramm " + str(degree_histogramm))
    # print("degree distribution " + str(degree_distribution))
    print("Number of components " + str(len(sorted_component_list_descending)))
    print("Largest component size " + str(len(largest_component)))

    try:
        print("2nd Largest component size " + str(len(sorted_component_list_descending[1])))
    except:
        print ("There is only one component.")

    #end time
    end_time = time.perf_counter()
    print("script took " + str(end_time - start_time) + " seconds to complete")

    return list_of_nodes_same_as_average_degree

#this snippet checks if the script is used directly or is called by another script. Only by direct use is the method below executed.
def main():
    get_values_of_graph(contact_data_file, has_header, split_sign_between_data)
if __name__ == "__main__":
    main()
