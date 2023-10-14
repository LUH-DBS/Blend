from src.utils import Logger


logger = Logger(logging_path="logs", clear_logs=False)
choices = list(logger.logging_path.glob('*.csv'))
choices.sort(key=lambda x: x.parts[-1][::-1])
print('Available logs:')
for i, choice in enumerate(choices):
    print(f'{i}: {choice.name}')
while inp := input("Enter log id: "):
    inp = int(inp)
    logger = Logger(logging_path="logs", clear_logs=False)
    print(f"Reading {choices[inp]}")
    logger.describe_log(choices[inp].stem.removesuffix(".csv"))



