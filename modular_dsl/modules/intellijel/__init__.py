from ... import Module, IO, Value


class QuadVCA(Module):
    in_1 = IO("Input")
    volume_1 = Value("Volume (Ch. 1)")
