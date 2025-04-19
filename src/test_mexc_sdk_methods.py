from mexc_sdk import Spot
import inspect

spot = Spot()
print('Spot methods:', dir(spot))
print('\nnew_order signature:')
print(inspect.getfullargspec(spot.new_order))
print('\ndocstring:')
print(spot.new_order.__doc__)
