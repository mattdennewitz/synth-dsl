from modular_dsl import Surface
from modular_dsl.modules.makenoise import Telharmonic
from modular_dsl.modules.cwejman import Res4
from modular_dsl.modules.intellijel import QuadVCA
from modular_dsl.modules.doepfer import SampleAndHold
from modular_dsl.modules.verbos import VerbosRandom

patch = Surface()

verbos_random = VerbosRandom()
telharmonic = Telharmonic().centroid(50).flux(80)
res4 = Res4().freq_1("10k").bw_1(0.04)
quad_vca = QuadVCA()
sh = SampleAndHold().slew_amount("2%")

telharmonic.phase >> res4.in_
verbos_random.white_noise >> sh.sh_in
verbos_random.trigger_ch_1 >> sh.trigger_in
sh.out >> res4.freq_1_cv
res4.out >> quad_vca.in_1

patch << sh << telharmonic << res4 << quad_vca << verbos_random

patch.render()
