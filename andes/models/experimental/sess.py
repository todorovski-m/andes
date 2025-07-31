"""
Simplified model of the Energy Storage System (SESS) based on Fig. 12.4 (p. 425) from:
F. Milano, "Advances in Power System Modelling, Control and Stability Analysis", 2nd Edition, IET, 2022.
"""

from andes.core import ModelData, IdxParam, NumParam, Model, Algeb, ExtAlgeb, ConstService
from andes.core.block import Lag, LeadLag, LagAntiWindup, DeadBand
from andes.core.service import DeviceFinder


class SESSData(ModelData):
    def __init__(self):
        ModelData.__init__(self)

        self.bus = IdxParam(
            model="Bus",
            info="Bus idx",
            mandatory=True,
        )
        self.busf = IdxParam(
            model="BusFreq",
            info="BusFreq measurement device idx",
            default=None,
        )
        self.dbf = NumParam(
            default=0.000033, # 0.02/60
            info="Deadband on frequency",
            unit="p.u.",
            tex_name="\Delta_f",
        )
        self.Tf = NumParam(
            default=0.02,
            info="Input LAG block time const",
            unit="sec",
            tex_name="T_f",
        )
        self.T1 = NumParam(
            info="First time constant of the lead-lag block",
            tex_name="T_1",
            default=1.0,
        )
        self.T2 = NumParam(
            info="Second time constant of the lead-lag block",
            tex_name="T_2",
            default=3.0,
        )
        self.K = NumParam(
            info="Gain of the lead-lag block",
            tex_name="K",
            default=1.0,
        )
        self.T = NumParam(
            default=0.025,
            info="Time constant of the anti-windup limiter",
            unit="sec",
            tex_name="T",
        )
        self.Pmax = NumParam(
            default=0.2,
            info="Maximal output power",
            unit="p.u.",
            tex_name="P_{max}",
        )
        self.Pmin = NumParam(
            default=-0.2,
            info="Minimal output power",
            unit="p.u.",
            tex_name="P_{min}",
        )


class SESSModel(Model):
    def __init__(self, system, config):
        Model.__init__(self, system, config)
        self.group = "Experimental"
        self.flags.update({"tds": True})

        self.busfreq = DeviceFinder(
            self.busf,
            link=self.bus,
            idx_name="bus",
            default_model="BusFreq",
        )
        self.f = ExtAlgeb(
            model="BusFreq",
            src="f",
            indexer=self.busfreq,
            info="Bus frequency",
            unit="p.u.",
        )
        self.a = ExtAlgeb(
            model="Bus",
            src="a",
            indexer=self.bus,
            tex_name=r"\theta",
            e_str="+Pout",
            ename="P",
            tex_ename="P",
        )
        self.dbc = ConstService(
            v_str='1.0',
            info="Center value in deadband on frequency",
        )
        self.dbl = ConstService(
            v_str='1.0 - dbf',
            info="Lower value in deadband on frequency",
        )
        self.dbu = ConstService(
            v_str='1.0 + dbf',
            info="Upper value in deadband on frequency",
        )
        self.db = DeadBand(
            u=self.f,
            center=self.dbc,
            lower=self.dbl,
            upper=self.dbu,
        )
        self.f1 = Algeb(
            e_str="f * (1 - db_zi) + (dbc * db_zi) - f1",
            v_str="1.0",
            tex_name="f^{\prime}",
            info="Bus frequency after the deadband",
        )
        self.L1 = Lag(
            u='f1 - 1',
            T=self.Tf,
            K=1,
            info="Digital filter",
        )
        self.LL = LeadLag(
            u=self.L1_y,
            T1=self.T1,
            T2=self.T2,
            K=self.K,
        )
        self.L2 = LagAntiWindup(
            u=self.LL_y,
            T=self.T,
            K=1.0,
            lower=self.Pmin,
            upper=self.Pmax,
            tex_name="LAG",
            info="Lag block with an anti-windup limiter",
        )
        self.Pout = Algeb(
            name="Pout",
            tex_name="P_{out}",
            e_str="u * L2_y - Pout",
            v_str="u * L2_y",
        )

class SESS(SESSData, SESSModel):
    def __init__(self, system, config):
        SESSData.__init__(self)
        SESSModel.__init__(self, system, config)
