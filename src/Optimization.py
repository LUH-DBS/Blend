import types
import random


def changeOptimizationOrder(*seekers):
    for i, seeker in enumerate(seekers):
        seeker.cost = types.MethodType(lambda self, v=i: v, seeker)

def giveSameType(*seekers):
    rnd = random.randint(0, 100000)
    for seeker in seekers:
        seeker.cost = types.MethodType(lambda self: rnd, seeker)
        

