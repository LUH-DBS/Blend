from src.Plan import Plan
from src.Operators import Terminal, Input, Combiners, Seekers

def UnionSearch(dataset, k=10): # Changed name from UnionSearchPlan to UnionSearch
    plan = Plan("vertica", "main_tokenized_quadrants") # Added required parameters
    input_element = Input(dataset)
    plan.add('input', input_element)
    for clm_name in dataset.columns:
        element = Seekers.SC(dataset[clm_name], k)
        plan.add(clm_name, element, ['input'])
    plan.add('counter', Combiners.Counter(k), list(dataset.columns), {"k": k}) # Changed K to k, Added list() around dataset.columns
    plan.add('terminal', Terminal(), ['counter'])

    return plan