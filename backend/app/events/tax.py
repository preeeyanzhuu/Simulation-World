DEFAULT_TAX_HIKE_DURATION_TICKS = 20
DEFAULT_TAX_HIKE_MULTIPLIER = 0.7 

class TaxState:
    def __init__(self):
        self.active = False
        self.ticks_remaining = 0
        self.multiplier = 1.0

    def trigger_hike(self, duration_ticks=DEFAULT_TAX_HIKE_DURATION_TICKS,
                      multiplier=DEFAULT_TAX_HIKE_MULTIPLIER):
        self.active = True
        self.ticks_remaining = duration_ticks
        self.multiplier = multiplier

    def update(self):
        if self.ticks_remaining > 0:
            self.ticks_remaining -= 1
            if self.ticks_remaining == 0:
                self.active = False
                self.multiplier = 1.0
        return self.active


def trigger_tax_hike(tax_state, duration_ticks=DEFAULT_TAX_HIKE_DURATION_TICKS,
                      multiplier=DEFAULT_TAX_HIKE_MULTIPLIER):
    tax_state.trigger_hike(duration_ticks=duration_ticks, multiplier=multiplier)
    return tax_state.active
