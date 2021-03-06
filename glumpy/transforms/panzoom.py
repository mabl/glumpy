#! /usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import numpy as np
from . transform import Transform
from glumpy.shaders import get_code


class PanZoom(Transform):

    def __init__(self, *args, **kwargs):
        code = get_code("panzoom.glsl")
        Transform.__init__(self, code, *args, **kwargs)

        self.scale     = np.array([1.,1.])
        self.translate = np.array([0.,0.])
        self.bounds = (0.1, 10000.0)
        self.aspect = np.ones(2)


    def on_attach(self, program):
        """ A new program is attached """

        self["scale"]     = self.scale
        self["translate"] = self.translate


    def on_resize(self, width, height):
        """ Window has been resized """

        self.width = float(width)
        self.height = float(height)
        ratio = self.width/self.height
        if ratio > 1.0:
            aspect = np.array([1.0/ratio, 1.0])
        else:
            aspect = np.array([1.0, ratio/1.0])
        self.translate *= aspect / self.aspect
        self.aspect = aspect
        self["scale"] = self.scale #* self.aspect
        self["translate"] = self.translate


    def on_mouse_scroll(self, x, y, dx, dy):
        """ Mouse has been scrolled """

        x = x/(self.width/2) - 1
        y = 1 - y/(self.height/2)
        scale_min, scale_max = self.bounds
        s = np.minimum(np.maximum(self.scale*(1+dy/100.0), scale_min), scale_max)
        self.translate[0] = x - s[0] * (x - self.translate[0]) / self.scale[0]
        self.translate[1] = y - s[1] * (y - self.translate[1]) / self.scale[1]
        self.scale = s
        self["scale"] = self.scale #* self.aspect
        self["translate"] = self.translate


    def on_mouse_drag(self, x, y, dx, dy, button):
        """ Mouse has been dragged """

        self.translate += (2*dx/self.width, -2*dy/self.height)
        self["translate"] = self.translate

    def reset(self):
        """ Reset transformation """

        self.scale = np.array([1.,1.])
        self.translate = np.array([0.,0.])
        self["scale"] = self.aspect * np.array([1.,1.])
        self["translate"] = np.array([0.,0.])
