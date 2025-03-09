def calculate_ev(odds, win_probability):
    if odds > 0:
        potential_profit = odds / 100
        potential_loss = 1
    else:
        potential_profit = 1
        potential_loss = abs(odds) / 100
    
    ev = (win_probability * potential_profit) - ((1 - win_probability) * potential_loss)
    return ev
