#!BPY
import bpy
import mathutils
import math
import os
from collections import defaultdict

###===================================================================================================
### CREATE FILEPATH
###===================================================================================================
dir = os.path.dirname( bpy.data.filepath )
name = bpy.path.basename( bpy.context.blend_data.filepath )
name = name.split( ".blend" )[0]
filepath = os.path.join( dir, name + ".h" )

###===================================================================================================
### GLOBALS
###===================================================================================================
tex_id = -1
img = []
img_id = 0
sprite_image = bpy.data.images.new( "_tga", 16, 16 )
    
###===================================================================================================
### TEXNO DEFINITION
###===================================================================================================
#texdef = str().join( name.split() ).upper() + "_TEXNO"

###===================================================================================================
### POPULATE WITH MODEL DATA
###===================================================================================================
def Export_Mesh( _tex_id ):
    ngons = False
    with open (filepath, 'w') as file:
        file.write( "/* Model Name: " + name.title() + " */\n" )
        file.write( "/* Total Objects : " + str( len( bpy.data.objects ) ) + " */\n" )
        file.write( "/*\n" )
        for ob in bpy.data.objects:
            file.write("    -" + ob.name + "\n")
        file.write( "*/\n" )
        file.write( "\n" )
        
        file.write( "#ifndef __3D_%s_H__\n" % ( name.upper() ) )
        file.write( "#define __3D_%s_H__\n" % ( name.upper() ) )
        file.write( "\n" )
        
        ###===========================================================================================
        ### GET DATA FROM EACH OBJECT IN THE SCENE
        ###===========================================================================================
        for ob in bpy.data.objects:
            ###=======================================================================================
            if ob.type == "MESH":
                file.write( "// %s\n" % ( ob.name.upper() ) )
                ###===================================================================================
                ### VERTICES / POINTS
                ###===================================================================================
                file.write( "static POINT point_" + ob.name + "[%d] = {\n" % ( len( ob.data.vertices ) ) )
                for v in ob.data.vertices:
                    x, y ,z = v.co * 500000 ## Convert Units to Sega Saturn 3D Space
                    file.write( "   {%9.6f, %9.6f, %9.6f},\n" % ( x, y, z ) )
                file.write( "};\n\n" )
                
                ###===================================================================================
                ### FACES AND NORMALS / POLYGONS
                ###===================================================================================
                file.write( "static POLYGON polygon_" + ob.name + "[%d] = {\n" % ( len( ob.data.polygons ) ) )
                for p in ob.data.polygons:
                    if len( p.vertices ) == 4:
                        file.write( "   {{%9.6f, %9.6f, %9.6f}, {%3d, %3d, %3d, %3d}},\n" % (
                            p.normal.x,
                            p.normal.y,
                            p.normal.z,
                            p.vertices[1],
                            p.vertices[2],
                            p.vertices[3],
                            p.vertices[0]
                        ) )
                    elif len( p.vertices ) == 3:
                        file.write( "   {{%9.6f, %9.6f, %9.6f}, {%3d, %3d, %3d, %3d}},\n" % (
                            p.normal.x,
                            p.normal.y,
                            p.normal.z,
                            p.vertices[0],
                            p.vertices[1],
                            p.vertices[2],
                            p.vertices[0]
                        ) )
                    else:
                        file.write( "// CANNOT CONVERT THIS FACE!\n" )
                        ngons = True
                        p.select = True
                        
                file.write( "};\n\n" )
                
                ###===================================================================================
                ### ATTRIBUTES
                ###===================================================================================
                file.write( "static ATTR attribute_" + ob.name + "[%d] = {\n" % ( len( ob.data.polygons ) ) )
                for p in ob.data.polygons:
                    ###===============================================================================
                    ### FACE COLORS
                    ###===============================================================================
                    # Get the values the face's vertex colors and average them to get the color of the face
                    r = g = b = 31
                    vcol = ob.data.vertex_colors.active
                    if vcol:
                        for l in p.loop_indices:
                            r = vcol.data[l].color.r * 31
                            g = vcol.data[l].color.g * 31
                            b = vcol.data[l].color.b * 31
                            
                    ###================================================================================
                    if ob.data.uv_textures.active != None and ob.data.uv_textures.active.data[p.index].image != None:
                        #texno = texdef + "+" + str( tex_id )
                        _tex_id += 1
                        colno = "CL32KRGB|No_Gouraud"
                        spr = "sprNoflip"
                    else:
                        texno = 0
                        colno = "CL32KRGB|MESHoff"
                        spr = "sprPolygon"
                        
                    file.write( "   ATTRIBUTE(Dual_Plane, SORT_CEN, %20s, C_RGB(%2d, %2d, %2d), CL32KRGB | No_Gouraud, %27s, %10s, UseLight),\n" % (
                        _tex_id,
                        r,
                        g,
                        b,
                        colno,
                        spr
                        ) )
                file.write( "};\n\n" )
                    
                ###===================================================================================
                ### MESH STRUCTURE
                ###===================================================================================
                file.write( "jo_3d_mesh     mesh_" + ob.name + " = { \n")
                file.write( "   .data =\n" )
                file.write( "   {\n")
                file.write( "       point_" + ob.name + ",\n" )
                file.write( "       %3d,\n" % ( len( ob.data.vertices ) ) )
                file.write( "       polygon_" + ob.name + ",\n" )
                file.write( "       %3d,\n" % ( len( ob.data.polygons ) ) )
                file.write( "       attribute_" + ob.name + ",\n" )
                file.write( "   }\n" )
                file.write( "};\n\n" )
                
                ###===================================================================================
                ### MESH DRAW FUNCTION
                ###===================================================================================
                file.write( "static __jo_force_inline void      display_%s_mesh(void)" % ( ob.name ) )
                file.write( "{\n" )
                file.write( "   jo_3d_mesh_draw(&mesh_%s);\n" % ( ob.name ) )
                file.write( "}\n\n" )
        
        file.write( "#endif\n" )
        file.close()
        ###===========================================================================================

    if ngons == True:
        raise ValueError( "This model contains ngons. They have been automatically selected for review." )
    ###===============================================================================================

###===================================================================================================
### SPRITE TEXTURE CONVERSION
###===================================================================================================
def Export_Textures( _dir, _img_id, _sprite_image ):
    _dir += os.path.dirname( "/TEXTURES/" )
    if os.path.exists( dir ) == False:
        os.mkdir( dir )
        
    # Convert each textured plane as a TGA image
    bpy.context.scene.render.image_settings.file_format = "TARGA_RAW"
    _sprite_image.file_format = "TARGA"

    for ob in bpy.data.objects:
        if ob.type == "MESH" and ob.data.uv_layers.active != None:
            ###=======================================================================================
            ### UV LAYER SETUP
            ###=======================================================================================
            # Clean our selection queue and make sure our target object is selected
            bpy.ops.object.select_all( action="DESELECT" )
            ob.select = True
            
            # Setup image and UV for sprite creation
            sprite_uv = ob.data.uv_textures.new( "_tmp" )
            
            # Unlink the original texture from our sprite UVs
            for tf in ob.data.uv_textures[sprite_uv.name].data:
                tf.image = None
            
            # Setup UVs to bake
            i = 0
            for p in ob.data.polygons:
                ob.data.uv_layers[sprite_uv.name].data[i].uv[0] = 0
                ob.data.uv_layers[sprite_uv.name].data[i].uv[1] = 0
                
                ob.data.uv_layers[sprite_uv.name].data[i+1].uv[0] = 0
                ob.data.uv_layers[sprite_uv.name].data[i+1].uv[1] = 1
                
                ob.data.uv_layers[sprite_uv.name].data[i+2].uv[0] = 1
                ob.data.uv_layers[sprite_uv.name].data[i+2].uv[1] = 1
                    
                if len( p.vertices ) == 4:
                    ob.data.uv_layers[sprite_uv.name].data[i+3].uv[0] = 1
                    ob.data.uv_layers[sprite_uv.name].data[i+3].uv[1] = 0
                    i += 4
                    
                elif len( p.vertices ) == 3:
                    i += 3
                    
                else:
                    raise ValueError( "This model contains ngons. Cannot wind UVs." )
            
            ''' DOESN'T WORK SINCE UV_LAYERS DOESN'T MARK TRIANGLES
            # Wind the UVs into quad shapes
            for i in range( 0, len ( ob.data.uv_layers[sprite_uv.name].data ), 4 ):
                
                ob.data.uv_layers[sprite_uv.name].data[i].uv[0] = 0
                ob.data.uv_layers[sprite_uv.name].data[i].uv[1] = 0
                
                ob.data.uv_layers[sprite_uv.name].data[i+1].uv[0] = 0
                ob.data.uv_layers[sprite_uv.name].data[i+1].uv[1] = 1
                
                ob.data.uv_layers[sprite_uv.name].data[i+2].uv[0] = 1
                ob.data.uv_layers[sprite_uv.name].data[i+2].uv[1] = 1
                
                ob.data.uv_layers[sprite_uv.name].data[i+3].uv[0] = 1
                ob.data.uv_layers[sprite_uv.name].data[i+3].uv[1] = 0
            '''
                
            ''' DOESN'T WORK BLENDER ONLY EDITS THE FIRST MESH
            # Adjust our sprite UVs into squares for each face
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all( action="SELECT" )
            bpy.ops.uv.reset()
            bpy.ops.mesh.select_all( action="DESELECT" )
            bpy.ops.object.editmode_toggle()
            '''
            
            ###=======================================================================================
            ### MATERIAL BAKE PREPARATION
            ###=======================================================================================   
            # Set up our render settings
            ob.data.uv_textures[sprite_uv.name].active = True
            bpy.data.scenes[0].render.bake_type = "TEXTURE"
            bpy.ops.object.hide_render_clear_all()
            
            ###=======================================================================================
            ### SPRITE GENERATION
            ###=======================================================================================
            # Bake each face as a separate sprite
            for i in range( len ( ob.data.uv_textures[0].data ) ):
                if ob.data.uv_textures[0].data[i].image != None:
                    
                    ob.data.uv_textures[sprite_uv.name].data[i].image = sprite_image
                    bpy.ops.object.bake_image()
                    
                    # Save our image as a new TGA file
                    # Format our file name to make it compatible with texture loading
                    filename = "%s.TGA" % ( _img_id )
                    _img_id += 1
                    filepath = os.path.join( _dir, filename )
                    sprite_image.save_render( filepath )
                    
                    # Store the name to record it in a Header file later
                    img.append( filename )
                        
                    # Unlink our sprite from our face after finishing
                    ob.data.uv_textures[sprite_uv.name].data[i].image = None
                
            # Remove this UV Map as it's not longer needed
            #bpy.ops.mesh.uv_texture_remove()
            bpy.ops.object.select_all( action = "DESELECT" )
            ob.select = False

###===================================================================================================
### TEXTURE HEADER
###===================================================================================================
def Export_TexHeader( ):
    # Create a Header file that loads all of our textures
    filepath = os.path.join( dir, name + "_TEX.h" )

    with open ( filepath, 'w' ) as file :
        file.write( "#ifndef __%s_TEX__\n" % ( name ) )
        file.write( "#define __%s_TEX__\n" % ( name ) )
        file.write( "void       Load_%s_Texture(void)\n" % ( name.replace(" ", "" ) ) )
        file.write( "{\n" )
        for i in img :
            file.write( "   jo_sprite_add_tga (JO_ROOT_DIR, \"%s\", JO_COLOR_Transparent);\n" % ( i ) )
        file.write( "}\n" )
        file.write( "#endif\n" )
        file.close()
        
###===================================================================================================
### ANIMATIONS
###===================================================================================================
def Export_Anims( ):
    return False

###===================================================================================================
### EXPORT SEQUENCE
###===================================================================================================
# Export Options
export_Mesh      = True
export_Textures  = True
export_TexHeader = True
export_Anims     = False

if export_Mesh:
    Export_Mesh( tex_id )
    
if export_Textures:
    Export_Textures( dir, img_id, sprite_image )
    
if export_TexHeader and export_Textures:
    Export_TexHeader( )

if export_Anims:
    Export_Anims( )

###===============================================================================================
### CLEAN UP
###===============================================================================================
sprite_image.user_clear()
bpy.data.images.remove( sprite_image )

###===============================================================================================