// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
#version 120

float marker(vec2 P, float size)
{
   const float SQRT_2 = 1.4142135623730951;
   float x = SQRT_2/2 * (P.x - P.y);
   float y = SQRT_2/2 * (P.x + P.y);

    float r1 = max(abs(x - size/3), abs(x + size/3));
    float r2 = max(abs(y - size/3), abs(y + size/3));
    float r3 = max(abs(x), abs(y));
    float r = max(min(r1,r2),r3);
    r -= size/2;
    return r;
}
