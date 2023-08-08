from src.Plan import Plan
from src.Operators import Terminal, Input
from src.Operators.Seekers import MultiColumnOverlap



def MultiColumnJoinSearch(query_dataset, k=10):
    plan = Plan()
    input_element = Input(query_dataset)
    plan.add('input', input_element, [])
    element = MultiColumnOverlap(query_dataset, k)
    plan.add('query', element, ['input'])
    plan.add('terminal', Terminal(), ['query'])
    return plan
