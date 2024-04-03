v_supply = 5.0


def brakePressure(adcValue: int):
    v_output = (v_supply * adcValue) / 4095

    # TODO double check math
    return ((v_output - 0.5) * 10) + 5

def linearPotentiometer(adcValue: int):
    return 0.014 * adcValue - 2.772
    
