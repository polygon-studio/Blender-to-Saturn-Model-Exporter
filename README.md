# Blender-to-Saturn-Model-Exporter

Converts mesh and texture data to be readable by the Sega Saturn directly from Blender.

## Features
- Converts polygon data into pseudo polygons (distorted sprites) rendered by the Sega Saturn VDP1 chip
- Creates Folded polygons when a polygon face has only three points to allow for triangle meshes on VDP1
- Converts each textured face into an formated sprite
- SGL version converts textured faces into TEXDAT structures
- Jo3D version converts each textured face into a TGA compatible sprite

![Example](https://i.imgur.com/GFNggi1.png)

## Todo
- Optimize the texture conversion process to make it faster
- Identify similar looking textures to cutdown on filesize
- Recognize manually converted faces and perform a straight export without conversion to save time
- Allow for predefined and/or smart deduction of texture conversion based off textured face size relative to overall mesh
- Recognize mirrored and instanced meshes to create optimized models
- Support for animated meshes
