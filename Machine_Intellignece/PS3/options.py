# This file contains the options that you should modify to solve Question 2

def question2_1():
    # Let the discount faction to be low not to get affected by the future states,
    # Let the noise to be zero to ensure moving through the shortest path as a deterministing environment without getting to -10 states
    # Let living rewarads to be low enough to ensure that the utility sequence to the terminal state of +1 is better than that of +10
    return {
        "noise": 0.0,
        "discount_factor": 0.1,
        "living_reward": -0.2
    }

def question2_2():
    # give some noise, and let the discount factor to be low to ensure seeking long path, also 
    # make living rewarad to be less to get to the terminal state of +1 safely
    return {
        "noise": 0.1,
        "discount_factor": 0.1,
        "living_reward": -1.0
    }

def question2_3():
    # Increasy extensivly the discount factor to make sure you get to the terminal state of +10 [future state rewards]
    # and No noise not to get to dangeourous states of -10
    return {
        "noise": 0.0,
        "discount_factor": 0.9,
        "living_reward": -0.2
    }

def question2_4():
    # Let the discout factor to be high enough to reach +10 states, also some noise added and living rewards of 0
    return {
        "noise": 0.1,
        "discount_factor": 0.99,
        "living_reward": 0.0
    }

def question2_5():
    # Give a very large living reward to make sure it is going forever between states without reaching terminals
    return {
        "noise": 0.0,
        "discount_factor": 0.1,
        "living_reward": 200.0
    }

def question2_6():
    # Give a very small living reward to let him make sure that the -10 states are better options 
    # also make sure that the noise will be 0 to take the shortest path
    return {
        "noise": 0.0,
        "discount_factor": 0.1,
        "living_reward": -200.0
    }