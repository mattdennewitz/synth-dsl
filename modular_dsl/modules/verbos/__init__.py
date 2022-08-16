from ... import Module, IO, Value


class VerbosRandom(Module):
    white_noise = IO("White Noise Out")
    trigger_ch_1 = IO("Random Trigger Out (Ch. 1)")
