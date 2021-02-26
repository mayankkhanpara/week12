from collections import deque 
from numpy import random
import simpy
from simpy.util import start_delayed


class Struct(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


random.seed([1, 2, 3])

end_time = 200.0
arrival_rate = 0.2
t_interarrival_mean = 1.0 / arrival_rate
t_green = 30.0
t_red = 40.0
t_depart_left = 1.6
t_depart_mode = 2.0
t_depart_right = 2.4

queue = deque()

arrival_count = departure_count = 0

Q_stats = Struct(count=0, cars_waiting=0)
W_stats = Struct(count=0, waiting_time=0.0)


def arrival():

    global arrival_count, env, light, queue

    while True:
        arrival_count += 1

        if light == 'red' or len(queue):

            queue.append((arrival_count, env.now))
            print("Car #%d arrived and joined the queue at position %d at time "
                  "%.3f." % (arrival_count, len(queue), env.now))

        else:

            print("Car #%d arrived to a green light with no cars waiting at time "
                  "%.3f." % (arrival_count, env.now))

            W_stats.count += 1

        yield env.timeout(random.exponential(t_interarrival_mean))


def departure():
    
    global env, queue

    while True:

        car_number, t_arrival = queue.popleft()
        print("Car #%d departed at time %.3f, leaving %d cars in the queue."
              % (car_number, env.now, len(queue)))

        W_stats.count += 1
        W_stats.waiting_time += env.now - t_arrival

        if light == 'red' or len(queue) == 0:
            return


        delay = random.triangular(left=t_depart_left, mode=t_depart_mode,
                                  right=t_depart_right)

        yield env.timeout(delay)


def light():
    
    global env, light

    while True:


        light = 'green'
        print("\nThe light turned green at time %.3f." % env.now)

        if len(queue):
            
            delay = random.triangular(left=t_depart_left, mode=t_depart_mode,
                                      right=t_depart_right)

            start_delayed(env, departure(), delay=delay)

        yield env.timeout(t_green)

        light = 'red'
        print("\nThe light turned red at time %.3f." % env.now)

        yield env.timeout(t_red)


def monitor():
    
    global env, Q_stats

    while True:
        Q_stats.count += 1
        Q_stats.cars_waiting += len(queue)
        yield env.timeout(1.0)


print("\nSimulation of Cars Arriving at Intersection Controlled by a Traffic "
      "Light\n\n")

env = simpy.Environment()

env.process(light())

t_first_arrival = random.exponential(t_interarrival_mean)
start_delayed(env, arrival(), delay=t_first_arrival)

env.process(monitor())

env.run(until=end_time)


print("\n\n      *** Statistics ***\n\n")

print("Mean number of cars waiting: %.3f" % (Q_stats.cars_waiting / float(Q_stats.count)))

print("Mean waiting time (seconds): %.3f" % (W_stats.waiting_time / float(W_stats.count)))

