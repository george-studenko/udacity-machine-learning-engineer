import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        
        # TODO: Initialize any additional variables here
        self.state = None
        
        # q uses tuples of action and state for identifying a reward, e.g. {(state, action): reward}
        self.q = {}
        
        # learning rate [0 = "Doh!" (Homer Simpson) up to 1 = "New is always better!" (Barney Stinson)]
        self.alpha = 0.5
        
        # discount factor [0 = "I want it all, I want it now" (Queen) vs. 1 = "Someday Never Comes" (Creedence Clearwater Revival)]
        self.gamma = 0.5
        
        # exploration rate [0 = average Hobbit up to 1 = Kirk]
        self.epsilon = 0.25
        
        # show parameters
        print 'alpha: {:.2f}, gamma: {:.2f}, epsilon: {:.2f}'.format(self.alpha, self.gamma, self.epsilon)
        
    def reset(self, destination=None):
        self.planner.route_to(destination)
        
        # TODO: Prepare for a new trip; reset any variables here, if required

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state   
        self.state = self.build_state(inputs, self.next_waypoint)
        
        # TODO: Select action according to your policy
        action = self.compute_next_action(self.state)

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        self.q_learn(self.state, action, reward, self.build_state(self.env.sense(self), self.planner.next_waypoint()))        

        #print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]       

    # build state tuple from relevant variables
    def build_state(self, inputs, waypoint):
        return (inputs['light'], inputs['oncoming'], inputs['left'], inputs['right'], self.next_waypoint)

    # compute next action depending on daring
    def compute_next_action(self, state):
        return self.compute_random_action() if random.random() < self.epsilon else self.compute_best_action(state)     

    # compute a random action
    def compute_random_action(self):
        return random.choice(Environment.valid_actions)

    # compute best action based on previous rewards
    def compute_best_action(self, state):
        candidates = [self.q.get((state, a)) for a in Environment.valid_actions]
        index = candidates.index(max(candidates))
        return Environment.valid_actions[index]        

    # q-learning if not in uncharted territory
    def q_learn(self, state, action, reward, next_state):
        old_q = self.q.get((state, action))
        self.q[(state, action)] = reward if (old_q is None) else self.compute_bellman(old_q, state, action, reward, next_state)

    # compute the bellman equation
    # cmp. https://classroom.udacity.com/nanodegrees/nd009/parts/0091345409/modules/e64f9a65-fdb5-4e60-81a9-72813beebb7e/lessons/5446820041/concepts/6348990570923
    def compute_bellman(self, old_q, state, action, reward, next_state):
        max_q = max([self.q.get((next_state, a), 0.0) for a in Environment.valid_actions])
        estimate_q = reward + self.gamma * max_q
        return (1 - self.alpha) * old_q + self.alpha * estimate_q

def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.0, display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()