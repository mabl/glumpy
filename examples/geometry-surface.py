#! /usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------
import numpy as np
from glumpy import data, shaders
from glumpy import app, gl, glm, gloo, data
from glumpy.geometry import primitives
from glumpy.transforms import Trackball

vertex = """
    uniform float height;
    uniform sampler2D data;
    uniform vec2 data_shape;
    attribute vec3 position;
    attribute vec2 texcoord;

    varying vec3 v_position;
    varying vec2 v_texcoord;
    void main()
    {
        float z = height*Bicubic(data, data_shape, texcoord).r;
        gl_Position = <transform>;
        v_texcoord = texcoord;
        v_position = vec3(position.xy, z);
    }
"""

fragment = """
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform mat4 normal;
uniform sampler2D texture;
uniform float height;
uniform vec4 color;

uniform sampler2D data;
uniform vec2 data_shape;
uniform vec3 light_color[3];
uniform vec3 light_position[3];

varying vec3 v_position;
varying vec2 v_texcoord;

float lighting(vec3 v_normal, vec3 light_position)
{
    // Calculate normal in world coordinates
    vec3 n = normalize(normal * vec4(v_normal,1.0)).xyz;

    // Calculate the location of this fragment (pixel) in world coordinates
    vec3 position = vec3(view * model * vec4(v_position, 1));

    // Calculate the vector from this pixels surface to the light source
    vec3 surface_to_light = light_position - position;

    // Calculate the cosine of the angle of incidence (brightness)
    float brightness = dot(n, surface_to_light) /
                      (length(surface_to_light) * length(n));
    brightness = max(min(brightness,1.0),0.0);
    return brightness;
}

void main()
{
    // Extract data value
    float value = Bicubic(data, data_shape, v_texcoord).r;

    // Compute surface normal using neighbour values
    float hx0 = height*Bicubic(data, data_shape, v_texcoord+vec2(+1,0)/data_shape).r;
    float hx1 = height*Bicubic(data, data_shape, v_texcoord+vec2(-1,0)/data_shape).r;
    float hy0 = height*Bicubic(data, data_shape, v_texcoord+vec2(0,+1)/data_shape).r;
    float hy1 = height*Bicubic(data, data_shape, v_texcoord+vec2(0,-1)/data_shape).r;
    vec3 dx = vec3(2.0/data_shape.x,0.0,hx0-hx1);
    vec3 dy = vec3(0.0,2.0/data_shape.y,hy0-hy1);
    vec3 v_normal = normalize(cross(dx,dy));

    // Map value to rgb color
    vec4 c = 0.6+0.4*texture2D(texture, v_texcoord);

    vec4 l1 = vec4(light_color[0] * lighting(v_normal, light_position[0]), 1);
    vec4 l2 = vec4(light_color[1] * lighting(v_normal, light_position[1]), 1);
    vec4 l3 = vec4(light_color[2] * lighting(v_normal, light_position[2]), 1);

    gl_FragColor = color * c * (0.5 + 0.5*(l1+l2+l3));
} """



window = app.Window(1200, 800, color = (1,1,1,1))



@window.event
def on_draw(dt):
    global phi, theta, duration

    window.clear()

    gl.glDisable(gl.GL_BLEND)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_POLYGON_OFFSET_FILL)
    surface["color"] = 1,1,1,1
    surface.draw(gl.GL_TRIANGLES, s_indices)

    gl.glDisable(gl.GL_POLYGON_OFFSET_FILL)
    gl.glEnable(gl.GL_BLEND)
    gl.glDepthMask(gl.GL_FALSE)
    surface["color"] = 0,0,0,1
    surface.draw(gl.GL_LINE_LOOP, b_indices)
    gl.glDepthMask(gl.GL_TRUE)

    model = surface['model'].reshape(4,4)
    view = surface['view'].reshape(4,4)
    surface['normal'] = np.array(np.matrix(np.dot(view, model)).I.T)

@window.event
def on_init():
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    gl.glPolygonOffset(1, 1)
    gl.glEnable(gl.GL_LINE_SMOOTH)
    gl.glLineWidth(2.5)


n = 64
surface = gloo.Program(shaders.get_code('spatial-filters.frag') + vertex,
                       shaders.get_code('spatial-filters.frag') + fragment)
vertices, s_indices = primitives.plane(2.0, n=n)
surface.bind(vertices)

I = []
for i in xrange(n): I.append(i)
for i in xrange(1,n): I.append(n-1+i*n)
for i in xrange(n-1): I.append(n*n-1-i)
for i in xrange(n-1): I.append(n*(n-1) - i*n)
b_indices = np.array(I, dtype=np.uint32).view(gloo.IndexBuffer)


def func3(x,y):
    return (1-x/2+x**5+y**3)*np.exp(-x**2-y**2)
x = np.linspace(-2.0, 2.0, 32).astype(np.float32)
y = np.linspace(-2.0, 2.0, 32).astype(np.float32)
X,Y = np.meshgrid(x, y)
Z = func3(X,Y)

surface['data'] = (Z-Z.min())/(Z.max() - Z.min())
surface['data'].interpolation = gl.GL_NEAREST
surface['data_shape'] = Z.shape[1], Z.shape[0]
surface['u_kernel'] = data.get("spatial-filters.npy")
surface['texture'] = data.checkerboard(32,24)

transform = Trackball("vec4(position.xy, z, 1.0)")
surface['transform'] = transform
window.attach(transform)

surface['height'] = 0.75
surface["light_position[0]"] = 3, 0, 0+5
surface["light_position[1]"] = 0, 3, 0+5
surface["light_position[2]"] = -3, -3, +5
surface["light_color[0]"]    = 1, 0, 0
surface["light_color[1]"]    = 0, 1, 0
surface["light_color[2]"]    = 0, 0, 1
phi, theta = -45, 0
app.run()
