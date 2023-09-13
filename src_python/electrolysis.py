import numpy as np


# https://nelhydrogen.com/wp-content/uploads/2020/03/Electrolysers-Brochure-Rev-D.pdf 
# large scale PEM and ALK electrolysis systems

# about 17 kWh per day demand for families with children in AUS

# X amount of stacks which each can act in a range min% -> 100% of capacity
# with varying efficiency e_min -> e_max depending on capacity

# represents an electrolysis stack with a certain number of cells
# returns the 
def electrolysis_PEM(input, min_capacity, max_capacity, min_efficiency, max_efficiency):
    """
    Parameters
    ----------
    input : float -> input power in kW
    min_capacity : float -> minimum capacity of the stack in kW
    max_capacity : float -> maximum capacity of the stack in kW
    min_efficiency : float -> minimum efficiency of the stack in kWh/kg
    max_efficiency : float -> maximum efficiency of the stack in kWh/kg

    Returns
    -------
    output : float -> output hydrogen in kg/h at the stack
    """
    if input < min_capacity:
        print("input is less than minimum capacity")
        return 0
    if input > max_capacity:
        print("input is greater than maximum capacity")
        return 0
    
    efficiency = interpolate(input, min_capacity, max_capacity, min_efficiency, max_efficiency)
    output = input/efficiency # kg/h 
    return output

# electrolysis decreases in efficiency as capacity increases so we need to interpolate -> assuming linear relationship (may have to change)
def interpolate(x, x1, x2, y1, y2):
    """
    Parameters
    ----------
    x : float -> input value
    x1 : float -> x value of first point
    x2 : float -> x value of second point
    y1 : float -> y value of first point
    y2 : float -> y value of second point

    Returns
    -------
    y : float -> output value
    """
    y = y1 + (x-x1)*(y2-y1)/(x2-x1)
    return y


if __name__ == "__main__":
    print("This is a module, not a script. Please import it into another python file.")
    print("testing...")
    print(interpolate(10, 13, 5, 0,1))

    # some default values (non-variable efficiency) for a "large scale" PEM electrolysis system
    mass_conversion = 0.0889 # kg / Nm3
    max_efficiency = 4.5/mass_conversion # kWh/kg
    min_efficiency = 5/mass_conversion # kWh/kg
    max_capacity =  10618/24*min_efficiency # kW
    min_capacity = max_capacity*0.1 # kW

    print(f"efficiency: {min_efficiency:.2f} kWh/kg")
    print(f"max capacity: {max_capacity:.2f} kW")

    h2_production_rate = electrolysis_PEM(10000, min_capacity, max_capacity, min_efficiency, max_efficiency)
    print(f"hydrogen production rate: {h2_production_rate:.2f} kg/h")

    exit(1)
