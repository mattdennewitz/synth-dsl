from ... import Module, IO, Value


class Telharmonic(Module):
    phase = IO()
    harmonic = IO()
    noise = IO()
    centroid = Value()
    flux = Value()


class QPAS(Module):
    in_left = IO()
