/*
** Jo Sega Saturn Engine
** Copyright (c) 2012-2016, Johannes Fetz (johannesfetz@gmail.com)
** All rights reserved.
**
** Redistribution and use in source and binary forms, with or without
** modification, are permitted provided that the following conditions are met:
**     * Redistributions of source code must retain the above copyright
**       notice, this list of conditions and the following disclaimer.
**     * Redistributions in binary form must reproduce the above copyright
**       notice, this list of conditions and the following disclaimer in the
**       documentation and/or other materials provided with the distribution.
**     * Neither the name of the Johannes Fetz nor the
**       names of its contributors may be used to endorse or promote products
**       derived from this software without specific prior written permission.
**
** THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
** ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
** WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
** DISCLAIMED. IN NO EVENT SHALL Johannes Fetz BE LIABLE FOR ANY
** DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
** (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
** LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
** ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
** (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
** SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

/***************************************************************************************************\
** Special Note : The 3D part on Jo Engine is still in development. So, some glitch may occur ;)
**                Btw, texture mapping for triangle base mesh (not quads) is experimental.
\***************************************************************************************************/

#include <jo/jo.h>
// The model and texture information
#include "magus_saturn.h"
#include "magus_saturn_TEX.h"

static jo_camera    cam;
static float        rx, ry;

static float spin = 0.0f;

void			    my_draw(void)
{
    jo_printf(12, 1, "*3D Model Demo*");
    jo_3d_camera_look_at(&cam);
    jo_3d_push_matrix();
    {
        jo_3d_rotate_matrix(90.0f, 0.0f, 0.0f);
        jo_3d_translate_matrix(0, 0, -80);
        jo_3d_push_matrix();
        {
            jo_3d_rotate_matrix(0.0, 0.0f, spin);
            spin += 1.0f;
            // Model draw function from magus_saturn.c
            display_Body_mesh();
            display_Cane_mesh();
            display_Face_mesh();
            display_Hair_mesh();
            display_Clothes_mesh();
        }
        jo_3d_pop_matrix();
    }
    jo_3d_pop_matrix();
}

void			my_gamepad(void)
{
    if (jo_is_pad1_key_pressed(JO_KEY_UP))
        rx -= 0.01f;
    else if (jo_is_pad1_key_pressed(JO_KEY_DOWN))
        rx += 0.01f;
    else if (jo_is_pad1_key_pressed(JO_KEY_LEFT))
        ry += 0.01f;
    else if (jo_is_pad1_key_pressed(JO_KEY_RIGHT))
        ry -= 0.01f;
}

void			jo_main(void)
{
	jo_core_init(JO_COLOR_Blue);
    Load_magus_saturn_Texture();
    jo_3d_camera_init(&cam);
    jo_core_add_callback(my_gamepad);
	jo_core_add_callback(my_draw);
	jo_core_run();
}

/*
** END OF FILE
*/
