"""
Fixed PQ injection on a bus
"""

from andes.core import ModelData, IdxParam, NumParam, Model, Algeb, ExtAlgeb

class PQinjData(ModelData):
    def __init__(self):
        ModelData.__init__(self)

        self.bus = IdxParam(
            model="Bus",
            info="Bus idx",
            mandatory=True,
        )
        self.Pin = NumParam(
            default=0.001,
            info="Active power injection",
            unit="p.u.",
            tex_name="P_{in}",
        )
        self.Qin = NumParam(
            default=0.001,
            info="Reactive power injection",
            unit="p.u.",
            tex_name="Q_{in}",
        )


class PQinjModel(Model):
    def __init__(self, system, config):
        Model.__init__(self, system, config)
        self.group = "Experimental"
        self.flags.update({"tds": True})

        self.a = ExtAlgeb(
            model="Bus",
            src="a",
            indexer=self.bus,
            tex_name=r"\theta",
            e_str="-Pout",
            ename="P",
            tex_ename="P",
        )
        self.v = ExtAlgeb(
            model="Bus",
            src="v",
            indexer=self.bus,
            tex_name=r"V",
            e_str="-Qout",
            ename="Q",
            tex_ename="Q",
        )
        self.Pout = Algeb(
            name="Pout",
            tex_name="P_{out}",
            e_str="Pin - Pout",
            v_str="Pin",
        )
        self.Qout = Algeb(
            name="Qout",
            tex_name="Q_{out}",
            e_str="Qin - Qout",
            v_str="Qin",
        )

class PQinj(PQinjData, PQinjModel):
    def __init__(self, system, config):
        PQinjData.__init__(self)
        PQinjModel.__init__(self, system, config)
