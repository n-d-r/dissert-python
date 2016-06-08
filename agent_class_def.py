# -*- coding: utf-8 -*-

#==============================================================================
# Imports
#==============================================================================

import numpy as np
import random as rnd
import matplotlib as mpl

#==============================================================================
# Classes
#==============================================================================

class Agent:
    """
    Central agent class that represents individuals in the network
    """
    def __init__(self, name):
        self.name = name
        self.type = "individual"
        self.risk_signals = []        
        self.rs_sent = 0        
        self.rs_sent_overall = 0
        self.rs_received = 0
        
        # randomly determined rate of media consumption
        self.media_consumption = rnd.random()
                
        # covariance matrix of risk, benefit, fear
        cov_mat = np.mat([[0.6933637,-0.3912554,0.3871803],
                   [-0.3912554,0.6219291,-0.2147406],
                   [0.3871803,-0.2147406,0.7555526]])

        risk_mean = 3.143534            # mean risk score, rescaled
        benefit_mean = 2.465156         # mean benefit scores, rescaled
        techn_fear_mean = 3.025205      # mean techn. fear, rescaled
        
        # drawing from multivar. joint normal prob. distribution
        rbtf = np.random.multivariate_normal([risk_mean, benefit_mean,
                                           techn_fear_mean],
                                           cov_mat)
        
        risk = rbtf[0]
        benefit = rbtf[1]
        techn_fear = rbtf[2]
        
        # risk, benefit and techn. fear are bounded 1.0 <= rbtf <= 5.0
        if risk > 5: self.risk_perception = 5
        elif risk < 1: self.risk_perception = 1
        else: self.risk_perception = risk
        self.original_rp = self.risk_perception
        
        if benefit > 5: self.benefit_perception = 5
        elif benefit < 1: self.benefit_perception = 1
        else: self.benefit_perception = benefit
            
        if techn_fear > 5: self.technological_fear = 5
        elif techn_fear < 1: self.technological_fear = 1
        else : self.technological_fear = techn_fear
            
        # multipliers are bounded 0.1 <= mult <= 2.0
        self.benefit_multiplier = self.rescale(self.benefit_perception,
                                               1.0, 5.0, 1.0, .1)        
        
        self.techn_fear_multiplier = self.rescale(self.technological_fear,
                                                  1.0, 5.0, 2.0, 1.0)   
                    
        # to record original risk perception to reinitialize later
        self.original_rp = self.risk_perception
            
        # update color according to agent's risk perception
        self.update_color()        
               
    def re_initialise(self):
        """        
        Function to "reset" agent into original, pre-simulation state, 
        including original risk perception. Used to run several simulations
        with the same network structure and risk perception distribution
        """        
        self.risk_signals = []
        self.report_rs = False          
        self.rs_sent = 0        
        self.rs_sent_overall = 0
        self.rs_received = 0    
        self.risk_perception = self.original_rp
        self.update_color()           
               
    def rescale(self, oldvalue, oldmin, oldmax, newmax, newmin):
        """
        Function to rescale values
        """
        return (oldvalue - oldmin) / (oldmax - oldmin) * (newmax - newmin) + newmin         
               
    def update_color(self):
        """
        Updates the agent's color category based on current risk perception
        """
        if self.risk_perception < 2:
            self.color = "green"
        elif self.risk_perception < 3:
            self.color = "yellow"
        elif self.risk_perception < 4:
            self.color = "orange"
        else:
            self.color = "red"
            
    def init_neighbors(self, social_network):
        """
        Initializes and stores the neighbours of the agent in the 
        social network
        """
        self.neighbors = social_network.neighbors(self)
            
    def get_name(self):
        return self.name
            
    def get_risk_perception(self):
        return self.risk_perception
        
    def add_risk_signal(self, risk_signal):
        """
        Lets an outside institution or other agent create a risk signal
        in this agent's list of risk signals; the list records all
        outside risk signals that reach this particular agent
        """
        self.risk_signals.append(risk_signal)        
        
    def get_color(self):
        return self.color
        
    def get_neighbors(self):
        return self.neighbors   
        
    def get_rs_sent(self):
        """
        Returns the number of risk signals this agent has sent since
        the last time this function has been called (usually since the last
        time step)
        """
        self.rs_sent_overall += self.rs_sent
        tmp = self.rs_sent
        self.rs_sent = 0
        return tmp        

    def get_rs_end_state(self):
        return (self.rs_sent_overall, self.rs_received)        
    
    def tick_behaviour(self, The_Media, The_Government, The_Hazard):
        """
        Overview
        ---------------
        The tick behaviour of an agent; called every tick/time step

        Input
        ---------------
        The_Media: an instance of object type Media
        The_Government: an instance of object type Government
        The_Hazard: an instance of object type Hazard
        
        Output
        ---------------
        Does not output anything directly but alters the current state
        of the agent according to its environment and neighbours in 
        the network
        
        Abbreviations
        ---------------
        rs: risk signal(s)
        rp: risk perception
        """
        if rnd.random() < self.media_consumption:
            if rnd.random() < The_Media.get_intensity():
                if The_Media.reports:
                    rs_to_pass_on = The_Media.get_rp_multiplier() * \
                                    The_Hazard.get_rp_multiplier()
                    # risk signals above 2 or below .1 not possible
                    if rs_to_pass_on > 2:
                        rs_to_pass_on = 2
                    elif rs_to_pass_on < .1:
                        rs_to_pass_on = .1
                    self.add_risk_signal(RiskSignal("media", rs_to_pass_on))
                    The_Media.increment_rs_sent()
        
        # only execute the following if the agent received a risk signal
        if len(self.risk_signals) > 0:
            rs_magnitudes = []
            rs_neighbour_intermediate = []
            for risk_signal in self.risk_signals:
                if risk_signal.get_origin() == "neighbour":                
                    rs_neighbour_intermediate.append(risk_signal.get_magnitude())
                    self.rs_received += 1
                else:
                    rs_magnitudes.append(risk_signal.get_magnitude())
                
            if len(rs_neighbour_intermediate) > 0:
                rs_magnitudes.append(np.mean(rs_neighbour_intermediate))
            
            # adaptation of agent's risk perception according to rs received
            self.risk_perception = self.get_risk_perception() * \
                                   np.mean([np.mean(rs_magnitudes),
                                            self.benefit_multiplier,
                                            self.techn_fear_multiplier])
            
            # risk perceptions cannot be higher than 5 or lower than 1
            if self.risk_perception > 5:
                self.risk_perception = 5
            elif self.risk_perception < 1:
                self.risk_perception = 1
                        
            # the higher the agent's own risk perception, the higher
            # the chance that it will share its risk perceptions
            # with a random subset of its network neighbours
            if self.rescale(rnd.random(), 0, 1, 5, 1) <= self.risk_perception:
                rp_to_pass_on = self.rescale(self.get_risk_perception(), 
                                             1, 5, 2, 0.1) * \
                                             The_Hazard.get_rp_multiplier()
                # risk signals with magnitude above 2 or below .1 impossible
                if rp_to_pass_on > 2:
                    rp_to_pass_on = 2
                elif rp_to_pass_on < .1:
                    rp_to_pass_on = .1
                try:
                    # sending new risk signals to neighbours
                    send_signal_to = rnd.sample(self.neighbors, 
                                                rnd.randint(1, \
                                                len(self.neighbors)/2))
                    for neighbor in send_signal_to:
                        neighbor.add_risk_signal(RiskSignal("neighbour", 
                                                            rp_to_pass_on))
                        self.rs_sent += 1
                except ValueError:
                    pass

            # reset risk signal counter
            self.risk_signals = []            
            # update color again to reflect changed risk perceptions
            self.update_color()                

class Media:   
    """
    Object class to represent sum of all media organisations relevant
    to the simulation; only one instance used per simulation
    """             
    def __init__(self, name):
        self.name = name
        self.color = "purple"
        self.reports = False                
        self.multiplier = 0
        self.intensity = 0
        self.length_of_reporting = 0
        self.rs_sent = 0
            
    def rescale(self, oldvalue, oldmin, oldmax, newmax, newmin):
        return (oldvalue - oldmin) / (oldmax - oldmin) * \
               (newmax - newmin) + newmin                 
            
    def start_reporting(self, MediaMultiplier):
        """
        Initiates the media reporting with given multiplier which is a 
        simulation parameter
        """
        self.reports = True        
        self.multiplier = MediaMultiplier
        
    def get_rp_multiplier(self):
        return self.multiplier
        
    def set_intensity(self, intensity):
        self.intensity = intensity
            
    def get_intensity(self):
        return self.intensity                    
                
    def increment_rs_sent(self):
        self.rs_sent += 1                
                
    def get_rs_sent(self):
        """
        Returns number of risk signals sent and resets counter to 0
        """
        tmp = self.rs_sent
        self.rs_sent = 0
        return tmp                
            
    def tick_behaviour(self, local_avg_rp):
        """
        Overview
        ---------------
        Tick behaviour of Media object. self.intensity equals 0 in the 
        beginning but rises to MediaReportingIntensity (system parameter)
        upon starting to report on the hazard event. 
        
        Input
        ---------------
        local_avg_rp: average risk perception at a particular time step, 
        assumed to be between 1 and 5, needs to be rescaled for use 
        as a multiplier
        """
                     
        self.intensity *= self.rescale(local_avg_rp, 1, 5, 2, .1)
                         
        # self.intensity is the intensity with which the media reports on
        # a risk event. An intensity of 100% was deemed unrealistic so
        # a cap of 0.8 was introduced
        if self.intensity > .8:
            self.intensity = .8
        self.length_of_reporting += .05
                
class Government:
    """
    Object class to represent the sum of all relevant government 
    organisations; only one instance per simulation used
    """
    def __init__(self, name, risk_signal_magnitude):
        self.name = name
        self.color = "blue"
        self.communicates = False
        self.risk_signal_magnitude = risk_signal_magnitude
        
    def get_risk_signal_magnitude(self):
        return self.risk_signal_magnitude

    def send_risk_signal(self, target_group, The_Hazard):
        """
        Overview
        ---------------
        Makes Government object send out risk signals to a group of nodes
        in a network
        
        Input
        ---------------
        target_group: assumed to be a list of nodes 
        The_Hazard: assumed to be an instance of object type Hazard
        """
        for target in target_group:
            rs_to_pass_on = self.risk_signal_magnitude * \
                            The_Hazard.get_rp_multiplier()
            # risk signals above 2 or below .1 impossible
            if rs_to_pass_on > 2:
                rs_to_pass_on = 2
            elif rs_to_pass_on < .1:
                rs_to_pass_on = .1
            target.add_risk_signal(RiskSignal("government", rs_to_pass_on))
                       
class RiskSignal:
    """
    Risk signal object that is sent around by neighbours, the government,
    the media and the grid
    """
    def __init__(self, origin, magnitude):
        """
        origin indicates whether it came from the government, the media, 
        a neighbour or the grid
        """        
        self.origin = origin
        self.magnitude = magnitude
        
    def get_origin(self):
        return self.origin
        
    def get_magnitude(self):
        return self.magnitude


class Hazard:
    """
    Hazard object that saves hazard multiplier; only one used per simulation
    """
    def __init__(self, name, rp_multiplier):
        self.name = name
        self.rp_multiplier = rp_multiplier
        
    def get_name(self):
        return self.name
        
    def get_rp_multiplier(self):
        return self.rp_multiplier
        