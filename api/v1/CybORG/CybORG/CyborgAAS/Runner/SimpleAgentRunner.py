import argparse
import inspect
import sys
import time
from statistics import mean, stdev
from pprint import pprint
from dataclasses import dataclass

from CybORG import CybORG, CYBORG_VERSION

from CybORG.Agents import BaseAgent
from CybORG.Agents import B_lineAgent, BlueReactRestoreAgent, BlueReactRemoveAgent, \
    RandomAgent, RedMeanderAgent, SleepAgent

from CybORG.Agents.Wrappers.ChallengeWrapper import ChallengeWrapper
from CybORG.Agents.Wrappers import EnumActionWrapper
from CybORG.Agents.Wrappers.FixedFlatWrapper import FixedFlatWrapper
from CybORG.Agents.Wrappers.IntListToAction import IntListToActionWrapper
from CybORG.Agents.Wrappers.OpenAIGymWrapper import OpenAIGymWrapper
from CybORG.Simulator.Scenarios.FileReaderScenarioGenerator import FileReaderScenarioGenerator

from CybORG.GameVisualizer.GameStateCollector import GameStateCollector

import os
import json
import redis

import logging
from pathlib import Path

# Configure logging to output to console only
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class RedAgentFactory:
    """Class for keeping building agents."""
    
    def create(self, type: str) -> BaseAgent:
        if type == "B_lineAgent":
            return B_lineAgent()  
        elif type == "RedMeanderAgent":
            return RedMeanderAgent()  
        else:
            return RandomAgent()  

@dataclass
class BlueAgentFactory:
    """Class for keeping building agents."""
    
    def create(self, type: str) -> BaseAgent:
        if type == "CardiffUni":
            return BlueReactRemoveAgent()  
        elif type == "CASTLEgym":
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
        self.wrapper_type = wrapper_type
        self.running = True
        
        self.red_agent_type = red_agent_type
        self.blue_agent_type = blue_agent_type

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
        self.blue_agent = self.blue_agent_factory.create(type=self.blue_agent_type)
        self.cyborg = self.cyborg_factory.create(type=self.wrapper_type, red_agent=self.red_agent)
        self.game_state_manager.set_environment(
            cyborg=self.cyborg,
            red_agent_name=self.red_agent_type,
            blue_agent_name=self.blue_agent_type,
            num_steps=self.max_steps
        )
        logger.info("Environment configured.")

    def run_next_step(self):
        if self.current_step >= self.max_steps:
            logger.info("Maximum steps reached.")
            return None
            
        if not self.cyborg:
            self.configure()
        
        blue_action_space = self.cyborg.get_action_space('Blue')
        blue_obs = self.cyborg.get_observation('Blue')
        blue_action = self.blue_agent.get_action(blue_obs, blue_action_space)
        result = self.cyborg.step('Blue', blue_action, skip_valid_action_check=False)

        actions = {
            "Red": str(self.cyborg.get_last_action('Red')),
            "Blue": str(self.cyborg.get_last_action('Blue'))
        }
        observations = {
            "Red": self.cyborg.get_observation('Red'),
            "Blue": self.cyborg.get_observation('Blue')
        }
        
        state_snapshot = self.game_state_manager.create_state_snapshot(actions, observations)
        self.game_state_manager.store_state(state_snapshot, self.current_step, self.max_steps)

        self.current_step += 1
        logger.info(f"Completed step {self.current_step}.")
        return state_snapshot

def parse_args():
    parser = argparse.ArgumentParser(description='Run a simple agent.')
    parser.add_argument('--game_id', type=str, default='1', help='Game ID.')
    parser.add_argument('--num_steps', type=int, default=10, help='Number of steps to run.')
    parser.add_argument('--wrapper_type', type=str, default='simple', help='Type of wrapper to use.')
    parser.add_argument('--red_agent_type', type=str, default='RedMeanderAgent', help='Type of red agent to use.')
    parser.add_argument('--blue_agent_type', type=str, default='BlueReactRemoveAgent', help='Type of blue agent to use.')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    logger.info(f"Starting SimpleAgentRunner with game_id: {args.game_id}")

    # Connect to redis server
    redis_server = os.getenv('REDIS_SERVER', 'localhost')
    try:
        redis_client = redis.Redis(host=redis_server, port=6379, db=0) 
        # Test connection
        redis_client.ping()
        logger.info(f"Connected to Redis server at {redis_server}.")
    except redis.ConnectionError:
        logger.error(f'Error connecting to Redis server at {redis_server}.')
        sys.exit(1)
    
    pubsub = redis_client.pubsub()
    try:
        pubsub.subscribe(f'game_{args.game_id}_main')
        logger.info(f"Subscribed to Redis channel 'game_{args.game_id}_main'.")
    except redis.RedisError as e:
        logger.error(f"Failed to subscribe to channel: {e}")
        sys.exit(1)
    
    # Create an instance of SimpleAgentRunner
    runner = SimpleAgentRunner(
        num_steps=args.num_steps,
        wrapper_type=args.wrapper_type,
        red_agent_type=args.red_agent_type,
        blue_agent_type=args.blue_agent_type
    )
    runner.configure()
    
    try:
        while runner.current_step < runner.max_steps:
            # logger.info("Waiting for message on Redis channel...")
            message = pubsub.get_message(timeout=1.0)
            if message and message.get('type') == 'message':
                logger.info(f"Received message: {message}")
                state_snapshot = runner.run_next_step()
                data = { 
                    'state_snapshot': state_snapshot,
                    'current_step': runner.current_step
                }
                # Push the state_snapshot onto a Redis list
                redis_client.rpush(f'game:{args.game_id}:states', json.dumps(data))
                logger.info("Pushed state snapshot to Redis list.")
                time.sleep(1)
            else:
                logger.debug("No message received.")
    except KeyboardInterrupt:
        logger.info("Interrupted by user. Exiting...")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        pubsub.close()
        logger.info("Redis pubsub connection closed.")
