from ... import Module, IO, Value


class Res4(Module):
    in_ = IO("Input")
    out = IO("Output")
    freq_1 = Value("Frequency (Ch. 1)")
    freq_1_cv = IO("Frequency CV (Ch. 1)")
    freq_2 = Value("Frequency (Ch. 2)")
    bw_1 = Value("Bandwidth (Ch. 1)")
    bw_2 = Value("Bandwidth (Ch. 2)")
    volume_1 = Value("Volume (Ch. 1)")
    volume_2 = Value("Volume (Ch. 2)")
