from ... import Module, IO, Value


class SampleAndHold(Module):
    sh_in = IO("S&H In")
    trigger_in = IO("Trigger In")
    out = IO("S&H Out")
    slew_amount = Value("Slew Amount")
