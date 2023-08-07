from src.Plan import Plan
from src.Operators import Terminal, Input, Combiners, Seekers


def AugmentationByExample(examples, queries, K=10):
    plan = Plan()
    inputs = Input([examples, queries])
    plan.add('input', inputs)
    examples_seeker = Seekers.MC([inputs.examples], K)
    plan.add('example', examples_seeker, ['input'])
    query_seeker = Seekers.SC(inputs.queries, K)
    plan.add('query', query_seeker, ['input'])
    plan.add('combiner', Combiners.Intersection(K), ['example', 'query'])
    plan.add('terminal', Terminal(), ['combiner'])
    return plan