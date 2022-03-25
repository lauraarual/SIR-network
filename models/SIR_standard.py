import matplotlib.pyplot as plt
##########################################
##########################################
#testing_data
#days = 20
#N= 18
#I = [1]
#################
#SET PARAMETERS
days = 160
N= 7256 #The whole population is N = S+I+R. when comparing with network, take number of nodes
I = [1] #number of initial infected

infection_probability = 0.02 #percent as decimal eg. 7% = 0.07; infection rate is computed below
average_degree = 16
recovery_time = 12.5 #in n days; contagious days (therefore, without latency); recovery rate is computed below and has the form 1/n
############################################
############################################
R = [0]
S = [N - I[0]]
beta = infection_probability*average_degree #infection rate per time step and infected person
gamma = 1/recovery_time

#control point
R0 = infection_probability*average_degree*recovery_time
print("check R0, is it more or less plausible? R0 = " + str(R0))

#update lists
#with using the index, at each time step you access the last element of the list
for index in range(0, days):
    #variables and code structure here reflect the mathematical equations and are not optimal code-wise,
    #normally you would not duplicate code fragments and use clearer variabel names
    dSdt = - beta * S[index] * I[index] / N #this are the three differential equations
    dIdt = beta * S[index] * I[index] / N - (gamma * I[index]) #here we need /N to get i
    dRdt = gamma * I[index]

    S.append(S[index]+dSdt)
    I.append(I[index]+dIdt)
    R.append(R[index]+dRdt)

print("Numer of total infected is " +str(R[-1])) #retrieving last element of list


#fractions of population
s = [value/N for value in S]
i = [value/N for value in I]
r = [value/N for value in R]

#print(S[0])
#print(s[0])

# plotting
fig = plt.figure()

ax2 = fig.add_subplot()
ax2.plot(s, color="blue")
ax2.plot(i, color="red")
ax2.plot(r, color="green")
ax2.set(xlabel='time', ylabel='Fraction of population',title='Standard SIR', )
plt.legend(('S', 'I', 'R'), loc='upper right')

plt.savefig("../output/result_SIR_standard.png")
plt.show()