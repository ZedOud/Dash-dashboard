import random, sys
import matplotlib.pyplot as plt
# replace with Dash and plottly


def read_to_list(fn):
    with open(fn) as fi:
        lines = [float(line.strip()) for line in fi]
        decimal = [round(line/100, 5) for line in lines]
        return decimal

def default_input(prompt, default=None):
    prompt(f'{prompt} [{default}]')
    response = input(prompt)
    return default if not response and default else response # possible logic error: use parenthesis


print('\nNote: Input data should be in percent, not decimal!\n')
try:
    bonds = read_to_list('blah.txt')
    stocks = None
    blend_40_50_10 = None
    blend_50_50 = None
    infl_rate =  None

except IOError as e:
    print(f'{e}. \nTerminating program.', file=sys.stderr) # change output to JS console with Dash
    sys.exit(1) # change to proper exit for Dash?

investment_type_args = {
    'bonds': bonds,
    'stocks': stocks,
    'blend_sbc': blend_40_50_10,
    'blend_sb': blend_50_50
}

print('\tstocks = SP500')
print('\tbonds = 10-yr Treasury Bond')
print('\tsb_blend = 50% SP500 w/ 50% TBond')
print('\tsbc_blend = 40% SP500 w/ 50% TBond w/ 10% Cash')
print()

print('Press ENTER to take default value show in [brackets]. \n')

invest_type = default_input('Enter investment type: (stocks, bonds, blend_sb, blend_sbc): \n', 'bonds').lower()

while invest_type not in investment_type_args:
    invest_type = input('Invalid investment. Enter investment type as listed in prompt: ').lower()

start_value = default_input('Enter starting value of investments: \n', '2000000')

while not start_value.isdigit():
    start_value = input('Invalid input! Input integer only: ')

withdrawal = default_input("Input annual pre-ta withdrawal (today's $): \n", '80000')

while not withdrawal.isdigit():
    withdrawal = input('Invalid input! Input integer only: ')

