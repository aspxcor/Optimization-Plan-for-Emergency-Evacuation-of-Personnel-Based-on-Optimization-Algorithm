# coding: utf-8
# # Step1. TSP Solving
# Here comes 10 cities, we can easily show them below
# - 1： (41, 94)；
# - 2： (37, 84)；
# - 3： (54, 67)；
# - 4： (25, 62)；
# - 5： (7, 64)；
# - 6： (2, 99)；
# - 7： (68, 58)；
# - 8： (71, 44)；
# - 9： (54, 62)；
# - 10： (83, 69)

import numpy as np
import  random
import matplotlib.pyplot as plt

# Hyperparameter
# N_CITIES = 10  # DNA size
# POP_SIZE = 500
CROSS_RATE = 0.65    #Crossover rate
MUTATE_RATE = 0.25  #Mutation rate
N_GENERATIONS = 500 #epochs
LOCS = [(41, 94),(37, 84),(54, 67),(25, 62),(7, 64),(2, 99),(68, 58),(71, 44),(54, 62),(83, 69)]

# # Section1.Get adjoining matrix

# [Function name] CacDistance
# [Function Usage] Calculate the distance between two points
# [Parameter] Coordinates of two input points
# [Return value] Returns the distance between two points
# [Developer and date] Zhi DING 2020/11/24
# [Change Record] None

def CacDistance(a,b):
    a = np.array(a)
    b = np.array(b)
    c = a-b
    distance = np.sqrt(np.sum(c*c))
    return distance
    
# [Function name] CityDistance
# [Function Usage] Calculate the distance between cities and return the adjacent matrix representing the distance
# [Parameter] None
# [Return value] Returns the adjacent matrix representing the distance
# [Developer and date] Zhi DING 2020/11/24
# [Change Record] None

def CityDistance():
    n = len(LOCS)
    dis_mat = np.zeros([10,10])
    for i in range(n-1):
        for j in range(i+1,n):
            dist = CacDistance(LOCS[i],LOCS[j])
            dis_mat[i,j] = dist

    for i in range(n):
        dis_mat[:,i] = dis_mat[i,:]

    return dis_mat

# # Section2.Genetic algorithm
# ## Section2.1 Cross

# [Function name] Cross
# [Function Usage] Crossover between two sets of genes
# [Parameter] Two sets of genes for crossover
# [Return value] Return the two sets of genes after crossover
# [Developer and date] Zhi DING 2020/11/24
# [Change Record] None

def Cross(p1,p2):
    a = np.array(p1).copy()
    b = np.array(p2).copy()

    # Randomly generate two integers between 0-9 as the starting point and ending point of the mapping
    begin = random.randint(0,9)
    end = random.randint(0,9)
    # Make `begin` less than `end`
    if begin > end:
        temp = begin
        begin = end
        end = temp
        
    #print begin,end        #Used for debugging
    
    # Establish a mapping relationship
    cross_map = {}
    is_exist = False
    # Preliminary mapping
    for i in range(begin,end+1):
        if a[i] not in cross_map.keys():
            cross_map[a[i]] = []
        if b[i] not in cross_map.keys():
            cross_map[b[i]] = []

        cross_map[a[i]].append(b[i])
        cross_map[b[i]].append(a[i])

    # Processing transfer mapping such as 1:[6],6:[3,1]-->1:[6,3,1],6:[3,1]
    # Count the number of occurrences of the element in the substring, the number is 2, then the element is the intermediate node passed, such as 1:[6],6:[3,1], the number of occurrences of ‘6’ is 2.
    
    appear_times = {}
    for i in range(begin,end+1):
        if a[i] not in appear_times.keys():
            appear_times[a[i]] = 0
        if b[i] not in appear_times.keys():
            appear_times[b[i]] = 0

        appear_times[a[i]] += 1
        appear_times[b[i]] += 1

        if a[i] == b[i]:
            appear_times[a[i]] -= 1

    for k,v in appear_times.items():
        if v == 2:
            values = cross_map[k]
            for key in values:
                cross_map[key].extend(values)
                cross_map[key].append(k)
                cross_map[key].remove(key)
                cross_map[key] = list(set(cross_map[key]))

    # Use mapping cross
    # First map the selected substring
    temp = a[begin:end+1].copy()
    a[begin:end+1] = b[begin:end+1]
    b[begin:end+1] = temp

    # Map the remaining substrings according to the mapping rules
    
    seg_a = a[begin:end+1]
    seg_b = b[begin:end+1]

    remain = list(range(begin))
    remain.extend(range(end+1,len(a)))

    for i in remain:
        keys = cross_map.keys()
        if a[i] in keys:
            for fi in cross_map[a[i]]:
                if fi not in seg_a:
                    a[i] = fi
                    break

        if b[i] in keys:
            for fi in cross_map[b[i]]:
                if fi not in seg_b:
                    b[i] = fi
                    break

    return a,b            

# ## Section2.2 Variation
# [Function name] Variation
# [Function Usage] Variation between two sets of genes
# [Parameter] Two sets of genes for variation
# [Return value] Return the two sets of genes after Variation
# [Developer and date] Zhi DING 2020/11/24
# [Change Record] None

def Variation(s):
    c = range(10)
    index1,index2 = random.sample(c,2)
    temp = s[index1]
    s[index1] = s[index2]
    s[index2] = temp
    return s

# ## Section2.3 Calculate the fitness
# [Function name] cost
# [Function Usage] Calculate the fitness
# [Parameter] the set of genes for Calculating the fitness
# [Return value] Return the fitness. Since we require the minimum distance to be calculated, we should calculate the fitness value with negative
# [Developer and date] Zhi DING 2020/11/24
# [Change Record] None

def cost(s):
    dis = CityDistance()
    n = len(s)
    cost = 0
    for i in range(n):
        cost += dis[s[i],s[(i+1)%n]]
    return -cost

# ## Section2.4 The key part of genetic algorithm
# [Function name] TakeThird
# [Function Usage] The parameter is a list to be sorted
# [Parameter] the set of genes for Calculating the fitness
# [Return value] Return the third element of the list
# [Developer and date] Zhi DING 2020/11/24
# [Change Record] None

def TakeThird(elem):
    return elem[2]
    
# [Function name] CacAdap
# [Function Usage] Calculate the fitness of each individual and select the probability
# [Parameter] Population used to calculate fitness
# [Return value] Return the fitness of each individual
# [Developer and date] Zhi DING 2020/11/24
# [Change Record] None

def CacAdap(population):
    adap = []   # adap n*4,n is the number of rows, each row includes: individual index, fitness, selection probability, cumulative probability
    psum = 0
    # Calculate fitness
    i = 0
    for p in population:
        icost = np.exp(cost(p))
        psum += icost
        # Add individual subscripts
        adap.append([i])
        # Add fitness
        adap[i].append(icost)
        i += 1
    # Calculate the probability of selection
    for p in adap:
        # Add selection probability and cumulative probability, here cumulative probability is temporarily equal to selection probability, and the assignment will be recalculated later
        p.append(p[1]/psum)
        p.append(p[2])

    # Sort according to fitness
    adap.sort(key=TakeThird,reverse=True)
    #print adap     #Used for debugging
    # Calculate cumulative probability
    n = len(adap)
    for i in range(1,n):
        p = adap[i][3] + adap[i-1][3]
        adap[i][3] = p
    
    return adap

# [Function name] Chose
# [Function Usage] Take turns to choose according to the adap
# [Parameter] the fitness of each individual
# [Return value] Return the list of this turns chosen
# [Developer and date] Zhi DING 2020/11/24
# [Change Record] None

def Chose(adap):

    chose = []
    # Number of choices
    epochs = N_GENERATIONS//2           # max(len(adap)//2,N_GENERATIONS//2)    #20
    '''
    #while(len(set(chose)) <2):
    #print 'chosing...length %d'%len(set(chose))
    '''
    n = len(adap)
    for a in range(epochs):
        p = random.random()
        if adap[0][3] >= p:
            chose.append(adap[0][0])
        else:
            for i in range(1,n):
                if adap[i][3] >= p and adap[i-1][3] < p:
                    chose.append(adap[i][0])
                    break

    chose = list((chose))
    return chose

# [Function name] Cross_Variation
# [Function Usage] Gene crossover and mutation
# [Parameter] Population and cross mutation selection results for mutation
# [Return value] Return the Population after cross mutation
# [Developer and date] Zhi DING 2020/11/24
# [Change Record] None

def Cross_Variation(chose,population):
    # Cross mutation
    chose_num = len(chose)
    sample_times = chose_num//2
    for i in range(sample_times):
        index1,index2 = random.sample(chose,2)
        #print index1,index2        #Used for debugging
        # Parent node participating in crossover
        parent1 = population[index1]
        parent2 = population[index2]
        # These two parent nodes have crossed, so don’t participate later, so remove them from the sample
        chose.remove(index1)
        chose.remove(index2)
        
        p = random.random()
        if CROSS_RATE >= p:
            child1,child2 = Cross(parent1,parent2)
            #print child1,child2        #Used for debugging
            p1 = random.random()
            p2 = random.random()
            if MUTATE_RATE > p1:
                child1 = Variation(child1)
            if MUTATE_RATE > p2:
                child2 = Variation(child2)
            population.append(list(child1))
            population.append(list(child2))
    return population

# [Function name] GA
# [Function Usage] Describes a complete genetic process
# [Parameter] the population in the genetic process
# [Return value] Return the Population after genetic variation
# [Developer and date] Zhi DING 2020/11/24
# [Change Record] None

def GA(population):  
    adap = CacAdap(population)
    chose = Chose(adap)     #Select the fragments to be cross-mutated
    population = Cross_Variation(chose,population)      #Cross mutation
    return population

# ## Section2.5 Call the genetic algorithm repeatedly until the termination condition is reached
# [Function name] find_min
# [Function Usage] Using genetic algorithm to find the minimum total distance
# [Parameter] The initial population used to find the shortest total distance
# [Return value] None
# [Developer and date] Zhi DING 2020/11/24
# [Change Record] None

def find_min(population):
    loss = []
    #epochs = 51     #Genetic frequency
    i = 0
    while i < N_GENERATIONS:
        adap = []
        # Calculate fitness
        for p in population:
            icost = cost(p)
            adap.append(icost)
        
        # Update population using genetic algorithm
        population = GA(population)
        
        min_cost = max(adap)
        print('epoch %d: loss=%.2f'%(i,-min_cost))
        loss.append([i,-min_cost])
        i += 1
        if i == N_GENERATIONS:
            # Output optimal solution
            p_len = len(population)
            for index in range(p_len):
                if adap[index] == min_cost:
                    print('Optimal path:')
                    print(population[index])
                    print('Optimal cost:')
                    print(-min_cost)
                    break
    # Make a schematic diagram of the loss function and output
    loss = np.array(loss)
    plt.plot(loss[:,0],loss[:,1])
    plt.title('GA')
    plt.show()

# Initialize the original population
s1 = [1,2,3,4,5,6,7,8,9,0]
s2 = [5,4,6,9,2,1,7,8,3,0]
s3 = [0,1,2,3,7,8,9,4,5,6]
s4 = [2,4,3,1,5,7,6,8,9,0]
population = [s1,s2,s3,s4]
# According to genetic algorithm, find the best route
find_min(population)
