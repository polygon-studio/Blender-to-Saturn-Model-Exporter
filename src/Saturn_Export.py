#!BPY
import bpy
import mathutils
import math
import os
from collections import defaultdict

###===================================================================================================
### CREATE MDL FILE
###===================================================================================================

dir = os.path.dirname( bpy.data.filepath )
name = bpy.path.basename( bpy.context.blend_data.filepath )
name = name.split( ".blend" )[0]
filepath = os.path.join ( dir, name + ".mdl" )
ngons = False

###===================================================================================================
### TEXNO DEFINITION
###===================================================================================================
texdef = str().join( name.split() ).upper() + "_TEXNO"

###===================================================================================================
### POPULATE MDL FILE WITH MODEL DATA
###===================================================================================================
with open ( filepath, 'w' ) as file:
    file.write( "/* Model Name: " + name + " */\n" )
    file.write( "/* Total Objects: " + str( len( bpy.data.objects ) ) + " */\n" )
    file.write( "/*\n" )
    for ob in bpy.data.objects:
        file.write("    -" + ob.name + "\n");
    file.write( "*/\n" )
    file.write( "\n" )
    
    file.write( "#include \"TEXTURES%s%s_DEF.ini\"\n" % (  '/', name ) )
    file.write( "#define GRaddr 0xe000\n\n" )
    tex_id = 0
    
    ###===============================================================================================
    ### GET DATA FROM EACH OBJECT IN THE SCENE
    ###===============================================================================================
    for ob in bpy.data.objects:
        
        if ob.type == "MESH":
            ###=======================================================================================
            ### VERTICES
            ###=======================================================================================
            file.write( "POINT point_" + ob.name + "[%d] = {\n" % ( len( ob.data.vertices ) ) )
            for v in ob.data.vertices:
                x, y, z = v.co
                file.write( "   POStoFIXED(%9.6f, %9.6f, %9.6f),\n" % ( x, y, z ) );
            file.write( "};\n\n" )
            
            ###=======================================================================================
            ### FACES AND NORMALS
            ###=======================================================================================
            file.write( "POLYGON polygon_" + ob.name + "[%d] = {\n" % ( len( ob.data.polygons ) ) )
            for p in ob.data.polygons:
                if len( p.vertices ) == 4:
                    file.write( "   NORMAL(%9.6f, %9.6f, %9.6f), VERTICES(%3d, %3d, %3d, %3d),\n" % (
                        p.normal.x,
                        p.normal.y,
                        p.normal.z,
                        p.vertices[0],
                        p.vertices[1],
                        p.vertices[2],
                        p.vertices[3]
                    ) )
                elif len( p.vertices ) == 3:
                    file.write( "   NORMAL(%9.6f, %9.6f, %9.6f), VERTICES(%3d, %3d, %3d, %3d),\n" % (
                        p.normal.x,
                        p.normal.y,
                        p.normal.z,
                        p.vertices[0],
                        p.vertices[1],
                        p.vertices[2],
                        p.vertices[0]
                    ) )
                else:
                    file.write( "//CANNOT CONVERT THIS FACE!\n" )
                    ngons = True
                    p.select = True
                    
            file.write( "};\n\n" )
            
            ###=======================================================================================
            ### ATTRIBUTES
            ###=======================================================================================
            file.write("ATTR attribute_"+ ob.name + "[%d] = {\n" % ( len( ob.data.polygons ) ) )
            for p in ob.data.polygons:
                ###===================================================================================
                ### FACE COLORS
                ###===================================================================================
                # Get the values the face's vertex colors and average tem to get the color of the face
                r = g = b = 31
                vcol = ob.data.vertex_colors.active
                if vcol:
                    for l in p.loop_indices:
                        r = vcol.data[l].color.r * 31
                        g = vcol.data[l].color.g * 31
                        b = vcol.data[l].color.b * 31
                
                ###===================================================================================
                if ob.data.uv_textures.active != None and ob.data.uv_textures.active.data[p.index].image != None:
                    texno = texdef + "+" + str( tex_id )
                    spr = "sprNoflip"
                    tex_id += 1
                    colno = "CL32KRGB|MESHoff|CL_Gouraud"
                else:
                    texno = "No_Texture"
                    spr = "sprPolygon"
                    colno = "MESHoff|CL_Gouraud"
                
                file.write( "   ATTRIBUTE(Single_Plane, SORT_CEN, %20s, C_RGB(%2d, %2d, %2d), GRaddr+%3d, %27s, %10s, UseGouraud),\n" % (
                texno,
                r,
                g,
                b,
                p.index,
                colno,
                spr
                ) )
            file.write( "};\n\n" )
            
            ###=======================================================================================
            ### POLYGON DATA
            ###=======================================================================================
            file.write( "VECTOR vector_" + ob.name + "[sizeof(point_" + ob.name + ") / sizeof(POINT)];\n\n" )
            
            file.write( "XPDATA XPD_" + ob.name + "[6] = {\n" )
            file.write( "   point_" + ob.name + ", sizeof(point_" + ob.name + ")/sizeof(POINT),\n" )
            file.write( "   polygon_" + ob.name + ", sizeof(polygon_" + ob.name + ")/sizeof(POLYGON),\n" )
            file.write( "   attribute_" + ob.name + ",\n" )
            file.write( "   vector_" + ob.name + ",\n" )
            file.write( "};\n\n" )
            
    file.close()

if ngons == True:
    raise ValueError( "This model contains ngons. They have been automatically selected for review." )
    
###==================================================================================================
### CREATE C FILE
###==================================================================================================
filepath = os.path.join ( dir, name + ".c" )

with open ( filepath, 'w' ) as file:
    
    file.write( "#include %s.mdl\n\n" % ( name ) )
    
    ###==============================================================================================
    ### MODEL STRUCTURE GENERATION
    ###==============================================================================================
    # Start with the outermost objects of the heiarchy and continue with each of its children
    for ob in bpy.data.objects:
        if ob.parent != None:
            continue
        
        c_name = str().join( ob.name.split() ).lower()
        
        file.write( "// %s model Properties\n" % ( c_name.capitalize() ) )
        file.write( "FIXED %s_pos[XYZ];\n" % ( c_name ) )
        file.write( "ANGLE %s_ang[XYZ];\n" % ( c_name ) )
        file.write( "FIXED %s_scl[XYZ];\n\n" % ( c_name ) )
        file.write( "%s_pos[X] = %s_pos[Y] = %s_pos[Z] = toFIXED(0.0);\n" % ( c_name, c_name, c_name ) )
        file.write( "%s_ang[X] = %s_ang[Y] = %s_ang[Z] = DEGtoANG(0.0);\n" % ( c_name, c_name, c_name ) )
        file.write( "%s_scl[X] = %s_scl[Y] = %s_scl[Z] = toFIXED(0.0);\n\n" % ( c_name, c_name, c_name ) )
        
        file.write( "%s_Draw( FIXED *light )\n" % ( c_name.capitalize() ) )
        file.write( "{\n" )
        file.write( "   slPushMatrix();\n" )
        file.write( "   {\n" )
        file.write( "       slTranslate( %s_pos[X], %s_pos[Y], %s_pos[Z] );\n" % ( c_name, c_name, c_name ) )
        file.write( "       slScale( %s_scl[X], %s_scl[Y], %s_scl[Z] );\n" % ( c_name, c_name, c_name ) )
        file.write( "       slRotX( %s_ang[X] );\n" % ( c_name ) )
        file.write( "       slRotY( %s_ang[Y] );\n" % ( c_name ) )
        file.write( "       slRotZ( %s_ang[Z] );\n\n" % ( c_name ) )
        file.write( "       slPutPolygonX( &XPD_%s, light );\n" % ( ob.name ) )
        file.write( "   }\n" )
        file.write( "   slPopMatrix();\n" )
        file.write( "}\n\n" )

    ###==============================================================================================
    ### ROOT STRUCTURE GENERATION
    ###==============================================================================================    
    # Create a root matrix that will contain all of our objects
    c_name = str().join( name.split() ).lower()
    
    file.write( "// ROOT MATRIX //\n" )
    file.write( "FIXED %s_pos[XYZ];\n" % ( c_name ) )
    file.write( "ANGLE %s_ang[XYZ];\n" % ( c_name ) )
    file.write( "FIXED %s_scl[XYZ];\n" % ( c_name ) )
    file.write( "%s_pos[X] = %s_pos[Y] = %s_pos[Z] = toFIXED(0.0);\n" % ( c_name, c_name, c_name ) )
    file.write( "%s_ang[X] = %s_ang[Y] = %s_ang[Z] = DEGtoANG(0.0);\n" % ( c_name, c_name, c_name ) )
    file.write( "%s_scl[X] = %s_scl[Y] = %s_scl[Z] = toFIXED(0.0);\n\n" % ( c_name, c_name, c_name ) )    
    
    file.write( "%s_Draw( FIXED *light )\n" % ( c_name.capitalize() ) )
    file.write( "{\n" )
    file.write( "   slPushMatrix();\n" )
    file.write( "   {\n" )
    file.write( "       slTranslate( %s_pos[X], %s_pos[Y], %s_pos[Z] );\n" % ( c_name, c_name, c_name ) )
    file.write( "       slScale( %s_scl[X], %s_scl[Y], %s_scl[Z] );\n" % ( c_name, c_name, c_name ) )
    file.write( "       slRotX( %s_ang[X] );\n" % ( c_name ) )
    file.write( "       slRotY( %s_ang[Y] );\n" % ( c_name ) )
    file.write( "       slRotZ( %s_ang[Z] );\n\n" % ( c_name ) )
    
    for ob in bpy.data.objects:
        draw_func = str().join( ob.name.split() ).capitalize() + "_Draw( light )\n"
        file.write( "       %s" % ( draw_func ) )
    
    file.write( "   }\n" )
    file.write( "   slPopMatrix();\n" )
    file.write( "}\n\n" )
    
    file.close()
                
###=======================================================================================
### SPRITE TEXTURE CONVERSION AND TABLE GENERATION
###=======================================================================================
dir = os.path.dirname( bpy.data.filepath ) + os.path.dirname( "/TEXTURES/" )
name = bpy.path.basename( bpy.context.blend_data.filepath )
name = name.split( ".blend" )[0]

if os.path.exists( dir ) == False:
    os.mkdir( dir )

filepath = os.path.join ( dir, name + ".txr" )

with open ( filepath, 'w' ) as file:
    
    # Create a TEXTURE and PICTURE array
    tex_id = 0
    tex_table = []
    pic_table = []
    
    # Create our Material, Texture, and Image for texture baking
    mat = bpy.data.materials.new( "_tmp" )
    sprite_image = bpy.data.images.new( "_tmp", 64, 64 )
    sprite_tex = bpy.data.textures.new( "_tmp", type="IMAGE" )
    
    for ob in bpy.data.objects:
        if ob.type == "MESH" and ob.data.uv_layers.active != None:
            ###=======================================================================================
            ### UV LAYER SETUP
            ###=======================================================================================
            # Clean our selection queue and make sure our target object is selected
            bpy.ops.object.select_all( action="DESELECT" )
            ob.select = True
            
            # Setup image and uv for sprite creation
            sprite_uv = ob.data.uv_textures.new( "_tmp" )
            
            # Unlink the original texture from our sprite uvs
            for tf in ob.data.uv_textures[sprite_uv.name].data:
                tf.image = None
            
            # Adjust our sprite uvs into squares for each face
            ob.data.uv_textures[sprite_uv.name].active = True
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all( action="SELECT" )
            bpy.ops.uv.reset()
            bpy.ops.mesh.select_all()
            bpy.ops.object.editmode_toggle()
            
            ###=======================================================================================
            ### MATERIAL BAKE PREPARATION
            ###=======================================================================================
            # Create and apply a material for baking our sprites
            if len( ob.data.materials ) > 0:
                ob.data.materials[0] = mat
            else:
                ob.data.materials.append( mat )
            
            # Setup our material for baking
            mat.diffuse_color = ( 1, 1, 1 )
            mat.diffuse_intensity = 1
            mat.use_shadeless = True
            
            # Setup our sprite texture for baking
            mat.active_texture = sprite_tex
            mat.texture_slots[0].uv_layer = ob.data.uv_layers[0].name
            
            sprite_tex.filter_type = "BOX"
            sprite_tex.filter_size = 0.1
            sprite_tex.use_interpolation = False
            sprite_tex.use_mipmap = False
            
            # Set up our render settings
            bpy.data.scenes[0].render.bake_type = "TEXTURE"
            bpy.ops.object.hide_render_clear_all()
            
            ###=======================================================================================
            ### SPRITE GENERATION
            ###=======================================================================================
            # Bake each face as a seperate sprite
            for i in range( len ( ob.data.uv_textures[0].data ) ):
                if ob.data.uv_textures[0].data[i].image != None:
                    ob.data.uv_textures[sprite_uv.name].data[i].image = sprite_image
                    sprite_tex.image = ob.data.uv_textures[0].data[i].image
                    bpy.ops.object.bake_image()
                    
                    file.write( "TEXDAT %s_tex%d[] = {\n" % ( ob.name, tex_id ) )
                    
                    #convert this newly baked image into a texture table
                    pixels = sprite_image.pixels[:]
                    for x in range( 0, len( pixels ), 4 ):
                        #( BLUE << 10) | ( GREEN << 5) | (RED) | 0x8000
                        r = int( pixels[x] * 31 )
                        g = int( pixels[x+1] * 31 )
                        b = int( pixels[x+2] * 31 )
                        color = ( b << 10 ) | ( g << 5 ) | ( r ) | 0x8000
                        
                        if x*0.25 % 8 == 0:
                            file.write( "   %s," % ( hex( color ) ) )
                        elif x*0.25 % 8 == 7:
                            file.write( "%s,\n" % ( hex( color ) ) )
                        else:
                            file.write( "%s," % ( hex( color ) ) )
                    
                    # Store information in a table array
                    tex_table.append( "   TEXDEF( %3d, %3d, CGADDRESS+%9d ),\n" % ( 
                        sprite_image.generated_width,
                        sprite_image.generated_height,
                        ( ( sprite_image.generated_width * sprite_image.generated_height ) * 2 ) * ( tex_id )
                    ) )
                        
                    pic_table.append( "   PICDEF( %s+%3d, COL_32K, %s_tex%d ),\n" % (
                        texdef,
                        tex_id,
                        ob.name,
                        tex_id,
                    ) )
                    
                    tex_id += 1    
                    
                    file.write( "};\n\n" )
                    
                    # Unlink our sprite from our face after finishing
                    ob.data.uv_textures[sprite_uv.name].data[i].image = None
        
            #Remove this material, texture, and image as it's no longer needed
            bpy.ops.mesh.uv_texture_remove()
            bpy.ops.object.select_all( action="DESELECT" )
    
    ###==============================================================================================
    ### CLEAN UP
    ###==============================================================================================
    mat.active_texture = None
    ob.active_material = None
    sprite_tex.image = None
    
    sprite_image.user_clear()
    
    bpy.data.materials.remove(mat, do_unlink=True)
    bpy.data.images.remove(sprite_image)
    bpy.data.textures.remove(sprite_tex)
    
    file.close()
    
###==================================================================================================
### TEXTURE TABLE PROTOTYPE
###==================================================================================================
filepath = os.path.join ( dir, name + "_TEX.tbl" )

with open ( filepath, 'w' ) as file:
    
    file.write( "// Number of Textures:%9d\n" % len( tex_table ) )
    if len ( tex_table ) > 0:
        #//file.write( "TEXTURE tex_%s[] = {\n" % ( ob.name ) )
        for t in tex_table:
            file.write(t)
        #//file.write( "};\n\n" )
    else:
        file.write( "// No textures to define!" )
    file.write( "// Include this in a master texture table\n" )
        
    file.close()
                
###==============================================================================================
### PICTURE TABLE PROTOTYPE
###==============================================================================================
filepath = os.path.join ( dir, name + "_PIC.tbl" )

with open ( filepath, 'w' ) as file:

    file.write( "// Number of Pictures:%9d\n" % len( pic_table ) )
    if len ( pic_table ) > 0:
        #//file.write( "PICTURE pic_%s[] = {\n" % ( ob.name ) )
        for p in pic_table:
            file.write(p)
        #//file.write( "};\n\n" )
    else:
        file.write( "// No pictures to define!" )
    file.write( "// Include this in a master picture table\n")
        
    file.close()
    
###==============================================================================================
### PICTURE TABLE PROTOTYPE
###==============================================================================================
filepath = os.path.join ( dir, name + "_DEF.ini" )

with open ( filepath, 'w' ) as file:
    
    file.write( "#define %s 0" % texdef )
    
    file.close()

