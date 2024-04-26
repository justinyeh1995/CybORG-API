import subprocess
import inspect
import time
import os
from statistics import mean, stdev
import random
import collections
from pprint import pprint
from dataclasses import dataclass

from CybORG import CybORG, CYBORG_VERSION

from CybORG.Agents import BaseAgent

from CybORG.Agents import B_lineAgent, BlueReactRestoreAgent, BlueReactRemoveAgent, \
    RandomAgent, RedMeanderAgent, SleepAgent
# from CybORG.Agents.MainAgent import MainAgent

from CybORG.Agents.Wrappers.ChallengeWrapper import ChallengeWrapper
from CybORG.Agents.Wrappers import EnumActionWrapper
from CybORG.Agents.Wrappers.FixedFlatWrapper import FixedFlatWrapper
from CybORG.Agents.Wrappers.IntListToAction import IntListToActionWrapper
from CybORG.Agents.Wrappers.OpenAIGymWrapper import OpenAIGymWrapper
from CybORG.Simulator.Scenarios.FileReaderScenarioGenerator import FileReaderScenarioGenerator

from CybORG.GameVisualizer.GameStateCollector import GameStateCollector

@dataclass
class RedAgentFactory:
    """Class for keeping building agents."""
    
    def create(self, type: str) -> BaseAgent:
        if type == "B_lineAgent":
            # return MainAgent()
            return B_lineAgent()  
        elif type == "RedMeanderAgent":
            # return MainAgent_cyborg_mm()
            return RedMeanderAgent()  
        else:
            return RandomAgent()  

@dataclass
class BlueAgentFactory:
    """Class for keeping building agents."""
    
    def create(self, type: str) -> BaseAgent:
        if type == "CardiffUni":
            # return MainAgent()
            return BlueReactRemoveAgent()  
        elif type == "CASTLEgym":
            # return MainAgent_cyborg_mm()
            return BlueReactRemoveAgent()  
        else:
            return BlueReactRemoveAgent()  

@dataclass
class CybORGFactory:
    """Class for keeping building agents."""
    type: str = "wrap"
    file_name: str = "Scenario2"
    
    def wrap(self, env):
        return ChallengeWrapper(env=env, agent_name='Blue')
    
    def create(self, type: str, red_agent) -> CybORG:
        path = str(inspect.getfile(CybORG))
        path = path[:-7] + f'/Simulator/Scenarios/scenario_files/{self.file_name}.yaml'
        sg = FileReaderScenarioGenerator(path)
        cyborg = CybORG(sg, 'sim', agents={'Red': red_agent})
        
        if type == "wrap":
            return self.wrap(cyborg)
            
        return cyborg

class SimpleAgentRunner:
    def __init__(self, num_steps: int, wrapper_type: str, red_agent_type: str, blue_agent_type: str):
        self.max_steps = num_steps
        self.MAX_EPS = 1
        self.current_step = 0
        self.wrapper_type = "simple"
        
        self.red_agent_type = "B_lineAgent" # default red_agent_type
        self.blue_agent_type = "BlueReactRemoveAgent"

        self.red_agent_factory = RedAgentFactory()
        self.red_agent = None
        
        self.blue_agent_factory = BlueAgentFactory()
        self.blue_agent = None
        
        self.cyborg_factory = CybORGFactory()
        self.cyborg = None
        
        self.game_state_manager = GameStateCollector(environment='sim')

    def set_red_type(self, red_agent_type: str):
        self.red_agent_type = red_agent_type

    def set_blue_type(self, blue_agent_type: str):
        self.blue_agent_type = blue_agent_type

    def set_wrapper_type(self, wrapper_type: str):
        self.wrapper_type = wrapper_type
    
    def configure(self):
        self.red_agent = self.red_agent_factory.create(type=self.red_agent_type)
        self.blue_agent = self.blue_agent_factory.create(type=self.blue_agent_type)  # Change this line to load your agent
        self.cyborg = self.cyborg_factory.create(type=self.wrapper_type, red_agent=self.red_agent)
        self.game_state_manager.set_environment(
            cyborg=self.cyborg,
            red_agent_name=self.red_agent_type,
            blue_agent_name=self.blue_agent_type,
            num_steps=self.max_steps
        )
            
    def run_next_step(self):
        if self.current_step > self.max_steps:
            return None
            
        if not self.cyborg:
            self.configure()
        
        blue_action_space = self.cyborg.get_action_space('Blue')
        blue_obs = self.cyborg.get_observation('Blue')  # get the newest observation
        blue_action = self.blue_agent.get_action(blue_obs, blue_action_space)
        result = self.cyborg.step('Blue', blue_action, skip_valid_action_check=False)

        actions = {"Red":str(self.cyborg.get_last_action('Red')), "Blue": str(self.cyborg.get_last_action('Blue'))}
        observations = {"Red": self.cyborg.get_observation('Red'), "Blue": self.cyborg.get_observation('Blue')}
        
        state_snapshot = self.game_state_manager.create_state_snapshot(actions, observations)
        self.game_state_manager.store_state(state_snapshot, self.current_step, self.max_steps)

        self.current_step += 1
        # Return the current state, rewards, actions, etc., as needed
        return state_snapshot

    def get_step(self, num: int):
        pass
        
    
    def run_all_steps(self):
        self.configure()
        for num_steps in [self.max_steps]:
            for red_agent in [self.red_agent_type]:

                
                self.cyborg = self.cyborg_factory.create(type=self.wrapper_type, red_agent=self.red_agent)
    
                observation = self.cyborg.reset()
                # print('observation is:',observation)
                
                # Rest set up game_state_manager
                self.game_state_manager.set_environment(cyborg=self.cyborg,
                                                   red_agent=self.red_agent_type,
                                                   blue_agent=self.blue_agent_type,
                                                   num_steps=num_steps)
                self.game_state_manager.reset()

                action_space = self.cyborg.get_action_space(agent_name)
    
                total_reward = []
                actions = []
                for i in range(self.MAX_EPS):
                    r = []
                    a = []
                    
                    # cyborg.env.env.tracker.render()
                    for j in range(num_steps):
                        blue_action_space = self.cyborg.get_action_space('Blue')
                        blue_obs = self.cyborg.get_observation('Blue') # get the newest observation
                        blue_action = self.agent.get_action(blue_obs, blue_action_space)
                        # pprint(blue_action)
                            
                        result = self.cyborg.step('Blue', blue_action, skip_valid_action_check=False)
                        
                        actions = {"Red":str(self.cyborg.get_last_action('Red')), "Blue": str(self.cyborg.get_last_action('Blue'))}
                        observations = {"Red": self.cyborg.get_observation('Red'), "Blue": self.cyborg.get_observation('Blue')}
                        
                        state_snapshot = self.game_state_manager.create_state_snapshot(actions, observations)

                        # game manager store state
                        self.game_state_manager.store_state(state_snapshot, i, j)
    
                        
                    # game manager reset
                    self.agent.end_episode()
                    total_reward.append(sum(r))
                    actions.append(a)
                    # observation = cyborg.reset().observation
                    observation = self.cyborg.reset()
                    # game state manager reset
                    self.game_state_manager.reset()
            
    
        return self.game_state_manager.get_game_state()

