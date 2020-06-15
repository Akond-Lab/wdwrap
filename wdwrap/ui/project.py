#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
from traitlets import List, Instance, HasTraits, Int

from .wdtraits import WdParamTraitCollection
from ..bundle import Bundle
from .curves import VelocCurve, LightCurve
from ..param import ParFlag


class Project(HasTraits):
    light_curves = List()
    veloc_curves = List()
    light_curves_len = Int(default_value=0)
    veloc_curves_len = Int(default_value=0)

    parameters = Instance(WdParamTraitCollection, kw={'flags_any': ParFlag.lc})
    # model_parameters   = Instance(WdParamTraitCollection,
    #                               kw={'flags_not': ParFlag.curvedep|ParFlag.controlling})

    def __init__(self) -> None:
        super().__init__()
        self.bundle: Bundle = Bundle.default_binary()
        self.light_curves = [LightCurve(bundle=self.bundle, fit=True)]
        self.veloc_curves = [VelocCurve(bundle=self.bundle, fit=True)]
        self.light_curves_len = 1
        self.veloc_curves_len = 1
        self.read_bundle()  # (light_curves=True, veloc_curves=True)

    def read_bundle(self, bundle=None, light_curves=False, veloc_curves=False):
        """Copies boundle parameters to trait parameters

        If `light_curves` (or `control_curves`) is:
            * `True` : all curves will be updated
            * `False`: no curve will be updated
            * `int` : only curve on specific index will be updated
            * `list` of `int`: curve on specific indexes will be updated
        """
        if bundle is None:
            bundle = self.bundle
        for parset in [self.parameters] + self.select_curves(light_curves, veloc_curves):
            parset.read_bundle(bundle)


    def write_bundle(self, bundle=None, light_curves=False, veloc_curves=False):
        """trait parameters to boundle

        If `light_curves` (or `control_curves`) is:
            * `True` : all curves will be updated
            * `False`: no curve will be updated
            * `int` : only curve on specific index will be updated
            * `list` of `int`: curve on specific indexes will be updated
        """
        if bundle is None:
            bundle = self.bundle
        for parset in [self.parameters] + self.select_curves(light_curves, veloc_curves):
            parset.write_bundle(bundle)

    def select_curves(self, light_curves=False, veloc_curves=False):
        """Returns curves subset

            If `light_curves` (or `veloc_curves`) is:
            * `True` : all curves will be returned
            * `False`: no curve will be returned
            * `int` : only curve on specific index will be returned
            * `list` of `int`: curve on specific indexes will be returned
        """
        return self.select_elements(self.light_curves, light_curves) \
               + self.select_elements(self.veloc_curves, veloc_curves)

    @staticmethod
    def select_elements(lst, selection):
        """Selects list elements

            If `selection` is:
            * `True` : all elements will be returned
            * `False`: no elements will be returned
            * `int` : only elements on specific index will be returned
            * `list` of `int`: elements on specific indexes will be returned
        """
        if isinstance(selection, bool):
            if selection == True:
                return lst
            elif selection == False:
                return []
        elif isinstance(selection, int):
            selection = [selection]
        return [lst[i] for i in selection]

    def new_curve(self, rv: bool):
        print(f'New curve expected: rv={rv}')
        if rv:
            clist = self.veloc_curves
            cclass = VelocCurve
        else:
            clist = self.light_curves
            cclass = LightCurve

        new = cclass(bundle=self.bundle, fit=True)
        clist.append(new)
        if rv:
            self.veloc_curves_len += 1
        else:
            self.light_curves_len += 1
        return new

    def delete_curve(self, curve):
        try :
            self.veloc_curves.remove(curve)
            self.veloc_curves_len -= 1
        except ValueError:
            self.light_curves.remove(curve)
            self.light_curves_len -= 1

