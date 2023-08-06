bl_info={
    "name" : "Physics-Based Vehicles",
    "author" : "aeugh",
    "version" : (1, 0),
    "blender" : (3, 5, 1),
    "location" : "View3D > Add > Mesh > New Object (this is not the actual location)",
    "description" : "Aims to assist the process of creating a rigidbody vehicles with destruction simulations",
    "warning" : "",
    "doc_url" : "",
    "category" : "Add Mesh",
}


import bpy
import bmesh
import math
import mathutils
from mathutils import Euler
from bpy.types import Panel, Operator, PropertyGroup, UIList
from bpy.props import EnumProperty, PointerProperty, StringProperty, FloatProperty, IntProperty, FloatVectorProperty, BoolProperty, BoolVectorProperty, CollectionProperty
from mathutils import Vector
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from bpy.utils import register_class, unregister_class

filename="D:/Documents/Code/VehicleDestructionSimulation/testlist.py"

# bpy.data.texts["testlist"].as_module()

class VDS_OT_AddRig(Operator):
    """Add a rig"""
    bl_idname = "vds.add_rig"
    bl_label = "Redraw"
    bl_description = "Remove object from scene"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bool(context.scene.vds)
                    
    def execute(self, context):
        def moveToCollection(obj, collection):
            for coll in obj.users_collection:
                coll.objects.unlink(obj)

            collection.objects.link(obj)

        def rotateObject(x, y, z, obj):
            eul = mathutils.Euler((math.radians(x), math.radians(y), math.radians(z)), 'XYZ')

            if obj.rotation_mode == "QUATERNION":
                obj.rotation_quaternion = eul.to_quaternion()
            elif obj.rotation_mode == "AXIS_ANGLE":
                q = eul.to_quaternion()
                obj.rotation_axis_angle[0]  = q.angle
                obj.rotation_axis_angle[1:] = q.axis
            else:
                obj.rotation_euler = eul if eul.order == obj.rotation_mode else(
                    eul.to_quaternion().to_euler(obj.rotation_mode))
        
        def keepTransformParent(obj, parent):
            obj.parent = parent
            obj.matrix_parent_inverse = parent.matrix_world.inverted()

        def selectObject(obj):
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

        scene = context.scene

        # Parent
        parentCollection = bpy.data.collections.new("Vehicle")
        bpy.context.scene.collection.children.link(parentCollection)
        parentCollection.color_tag = "COLOR_07"

        # Mesh
        meshCollection = bpy.data.collections.new("Mesh")
        parentCollection.children.link(meshCollection)
        meshCollection.color_tag = "COLOR_05"
        # Children
        bodyMeshCollection = bpy.data.collections.new("Body Mesh")
        meshCollection.children.link(bodyMeshCollection)
        bodyMeshCollection.color_tag = "COLOR_03"

        doorMeshCollection = bpy.data.collections.new("Door Mesh")
        meshCollection.children.link(doorMeshCollection)
        doorMeshCollection.color_tag = "COLOR_02"

        wheelMeshCollection = bpy.data.collections.new("Wheel Mesh")
        meshCollection.children.link(wheelMeshCollection)
        wheelMeshCollection.color_tag = "COLOR_01"


        # Deform
        deformCollection = bpy.data.collections.new("Deform")
        parentCollection.children.link(deformCollection)
        deformCollection.color_tag = "COLOR_05"
        deformCollection.hide_render = True
        # Children
        bodyDeformCollection = bpy.data.collections.new("Body Deform")
        deformCollection.children.link(bodyDeformCollection)
        bodyDeformCollection.color_tag = "COLOR_03"

        doorDeformCollection = bpy.data.collections.new("Door Deform")
        deformCollection.children.link(doorDeformCollection)
        doorDeformCollection.color_tag = "COLOR_02"

        # wheelDeformCollection = bpy.data.collections.new("Wheel Deform")
        # deformCollection.children.link(wheelDeformCollection)
        # wheelDeformCollection.color_tag = "COLOR_01"


        # Rigidbody
        rigidbodyCollection = bpy.data.collections.new("Rigidbody")
        parentCollection.children.link(rigidbodyCollection)
        rigidbodyCollection.color_tag = "COLOR_05"
        rigidbodyCollection.hide_render = True
        # Children
        bodyRigidbodyCollection = bpy.data.collections.new("Body Rigidbody")
        rigidbodyCollection.children.link(bodyRigidbodyCollection)
        bodyRigidbodyCollection.color_tag = "COLOR_03"

        doorRigidbodyCollection = bpy.data.collections.new("Door Rigidbody")
        rigidbodyCollection.children.link(doorRigidbodyCollection)
        doorRigidbodyCollection.color_tag = "COLOR_02"

        wheelRigidbodyCollection = bpy.data.collections.new("Wheel Rigidbody")
        rigidbodyCollection.children.link(wheelRigidbodyCollection)
        wheelRigidbodyCollection.color_tag = "COLOR_01"


        # Constraint
        constraintCollection = bpy.data.collections.new("Constraint")
        parentCollection.children.link(constraintCollection)
        constraintCollection.color_tag = "COLOR_05"
        constraintCollection.hide_render = True
        # Children
        bodyConstraintCollection = bpy.data.collections.new("Body Constraint")
        constraintCollection.children.link(bodyConstraintCollection)
        bodyConstraintCollection.color_tag = "COLOR_03"
        
        doorConstraintCollection = bpy.data.collections.new("Door Constraint")
        constraintCollection.children.link(doorConstraintCollection)
        doorConstraintCollection.color_tag = "COLOR_02"

        wheelConstraintCollection = bpy.data.collections.new("Wheel Constraint")
        constraintCollection.children.link(wheelConstraintCollection)
        wheelConstraintCollection.color_tag = "COLOR_01"


        # Body
        bpy.ops.object.select_all(action='DESELECT')
        body = scene.bodyTool.Body
        moveToCollection(body, bodyMeshCollection)

        # Rig
        bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(body.location), scale=(1, 1, 1))
        rig = bpy.context.active_object
        scaleVector = Vector((body.dimensions.x * 2, body.dimensions.y * 1.5, 0))
        rig.scale = scaleVector
        rig.display_type = 'WIRE'
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        rig.name = body.name + " Rig"
        moveToCollection(rig, parentCollection)

        # Body Rigidbody
        selectObject(body)

        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
        bodyRigidbody = bpy.context.active_object
        bodyRigidbody.name = body.name + " Rigidbody"
        bodyRigidbody.display_type = 'WIRE'
        bodyRigidbody.parent = rig
        bodyRigidbody.matrix_parent_inverse = rig.matrix_world.inverted()
        # Needs a better scaling system so that nothing ends up intersecting
        bodyRigidbody.scale = Vector((0.5, 0.5, 0.5))
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True, isolate_users=True)

        moveToCollection(bodyRigidbody, bodyRigidbodyCollection)

        # bm = bmesh.new()
        # bm.from_mesh(bodyRigidbody.data)
        # bmesh.ops.convex_hull(bm, input=bm.verts)
        # bm.to_mesh(bodyRigidbody.data)

        bpy.ops.rigidbody.object_add()
        bpy.context.object.rigid_body.mass = 1500

        selectObject(bodyRigidbody)
        bpy.ops.object.modifier_add(type='REMESH')
        bpy.context.object.modifiers["Remesh"].mode = 'SHARP'
        bpy.context.object.modifiers["Remesh"].octree_depth = 3
        bpy.ops.object.convert(target='MESH')

        keepTransformParent(body, bodyRigidbody)

        # Body Deform
        selectObject(body)

        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
        bodyDeform = bpy.context.active_object
        bodyDeform.name = body.name + " Deform"
        bodyDeform.display_type = 'WIRE'
        keepTransformParent(bodyDeform, rig)
        moveToCollection(bodyDeform, bodyDeformCollection)

        bm = bmesh.new()
        bm.from_mesh(bodyDeform.data)
        # bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=1, use_grid_fill=True)
        bmesh.ops.convex_hull(bm, input=bm.verts)
        bm.to_mesh(bodyDeform.data)

        selectObject(bodyDeform)
        bpy.ops.object.modifier_add(type='REMESH')
        bpy.context.object.modifiers["Remesh"].mode = 'VOXEL'
        bpy.context.object.modifiers["Remesh"].voxel_size = scene.bodyTool.DeformSubdivisions
        bpy.ops.object.modifier_add(type='SHRINKWRAP')
        bpy.context.object.modifiers["Shrinkwrap"].target = body
        bpy.ops.object.convert(target='MESH')
        bpy.ops.transform.resize(value=(scene.bodyTool.DeformSpacingMultiplier, scene.bodyTool.DeformSpacingMultiplier, scene.bodyTool.DeformSpacingMultiplier))

        bpy.ops.object.modifier_add(type='SMOOTH')
        bpy.context.object.modifiers["Smooth"].factor = 4
        bpy.ops.object.modifier_apply(modifier="Smooth")

        keepTransformParent(bodyDeform, bodyRigidbody)

        selectObject(body)
        # The fuck was I thinking here? This is going to add unneccessary vertices and possibly also break the mesh. Maybe it was because of my test mesh? Not sure
        # bpy.ops.object.modifier_add(type='SUBSURF')
        # bpy.context.object.modifiers["Subdivision"].subdivision_type = 'SIMPLE'
        # bpy.context.object.modifiers["Subdivision"].levels = scene.bodyTool.DeformSubdivisions
        # bpy.context.object.modifiers["Subdivision"].render_levels = scene.bodyTool.DeformSubdivisions

        bpy.ops.object.modifier_add(type='MESH_DEFORM')
        body.modifiers["MeshDeform"].object = bodyDeform
        bpy.ops.object.meshdeform_bind(modifier="MeshDeform")
        
        # body.modifiers["MeshDeform"].show_viewport = False

        selectObject(bodyDeform)
        bpy.ops.object.modifier_add(type='DYNAMIC_PAINT')
        bpy.ops.dpaint.type_toggle(type='CANVAS')
        bpy.context.object.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Surface"].surface_type = 'WEIGHT'
        bpy.ops.dpaint.output_toggle(output='A')

        cloudTexture = bpy.data.textures.new('CarDisplacement', type = 'CLOUDS')
        dispMod = bodyDeform.modifiers.new("Displace", type='DISPLACE')
        dispMod.texture = cloudTexture
        bpy.data.textures["CarDisplacement"].noise_scale = 1.5
        bpy.data.textures["CarDisplacement"].noise_depth = 2
        bpy.data.textures["CarDisplacement"].contrast = 1.5
        bodyDeform.modifiers["Displace"].strength = 1
        bodyDeform.modifiers["Displace"].mid_level = 0.85

        bpy.context.object.modifiers["Displace"].vertex_group = "dp_weight"

        bpy.ops.object.modifier_add(type='CORRECTIVE_SMOOTH')


        for wheel in scene.vds:
            # Wheel
            selectObject(wheel.obj)
        
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True, isolate_users=True)

            moveToCollection(wheel.obj, wheelMeshCollection)

            # Wheel Rigidbody
            rotatedVector = Vector((wheel.obj.dimensions.z, wheel.obj.dimensions.y, wheel.obj.dimensions.x))/2
            bpy.ops.mesh.primitive_cylinder_add(vertices=32, enter_editmode=False, align='WORLD', location=(wheel.obj.location), rotation=(0, 1.5708, 0), scale=(rotatedVector))
            wheelRigidbody = bpy.context.active_object
            wheelRigidbody.name = wheel.obj.name + " Rigidbody"
            wheelRigidbody.display_type = 'WIRE'
            keepTransformParent(wheelRigidbody, rig)
            moveToCollection(wheelRigidbody, wheelRigidbodyCollection)
            
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            keepTransformParent(wheel.obj, wheelRigidbody)

            bpy.ops.rigidbody.object_add()
            bpy.context.object.rigid_body.mass = 100
            bpy.context.object.rigid_body.friction = 1
            bpy.context.object.rigid_body.restitution = 0.2
            bpy.context.object.rigid_body.linear_damping = 0.005
            bpy.context.object.rigid_body.angular_damping = 0.001

            # Suspension Rigidbody
            if wheel.obj.location.x < body.location.x:
                bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(Vector((wheel.obj.location.x + 0.6, wheel.obj.location.y, wheel.obj.location.z + 0.1))), rotation=(0, -0.392699, 0), scale=(0.5, 0.1, 0.1))
            else:
                bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(Vector((wheel.obj.location.x - 0.6, wheel.obj.location.y, wheel.obj.location.z + 0.1))), rotation=(0, 0.392699, 0), scale=(0.5, 0.1, 0.1))

            suspensionRigidbody = bpy.context.active_object
            selectObject(suspensionRigidbody)
            keepTransformParent(suspensionRigidbody, rig)
            moveToCollection(suspensionRigidbody, wheelRigidbodyCollection)
            # Do or don't apply the rotation? I'm not sure it matters either way
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

            bpy.ops.rigidbody.object_add()
            bpy.context.object.rigid_body.mass = 15

            # Suspension Spring Constraint

            bpy.ops.object.empty_add(type='SPHERE', align='WORLD', location=(wheel.obj.location), rotation=(0, 0, 0), scale=(1, 1, 1))
            SuspensionConstraint = bpy.context.active_object
            SuspensionConstraint.name = wheel.obj.name + " Suspension Spring"
            keepTransformParent(SuspensionConstraint, rig)
            moveToCollection(SuspensionConstraint, wheelConstraintCollection)
 
            bpy.ops.rigidbody.constraint_add()
            bpy.context.object.rigid_body_constraint.type = 'GENERIC_SPRING'
            bpy.context.object.rigid_body_constraint.use_limit_ang_x = True
            bpy.context.object.rigid_body_constraint.use_limit_ang_y = True
            bpy.context.object.rigid_body_constraint.use_limit_ang_z = True
            bpy.context.object.rigid_body_constraint.use_limit_lin_x = True
            bpy.context.object.rigid_body_constraint.use_limit_lin_y = True
            bpy.context.object.rigid_body_constraint.use_limit_lin_z = True
            bpy.context.object.rigid_body_constraint.limit_ang_x_upper = 0
            bpy.context.object.rigid_body_constraint.limit_ang_y_lower = 0
            bpy.context.object.rigid_body_constraint.limit_ang_y_upper = 0
            bpy.context.object.rigid_body_constraint.limit_ang_z_lower = 0
            bpy.context.object.rigid_body_constraint.limit_ang_z_upper = 0
            bpy.context.object.rigid_body_constraint.limit_ang_x_lower = 0
            bpy.context.object.rigid_body_constraint.limit_lin_x_upper = 0
            bpy.context.object.rigid_body_constraint.limit_lin_y_lower = 0
            bpy.context.object.rigid_body_constraint.limit_lin_y_upper = 0
            bpy.context.object.rigid_body_constraint.limit_lin_x_lower = 0
            bpy.context.object.rigid_body_constraint.limit_lin_z_lower = -0.23
            bpy.context.object.rigid_body_constraint.limit_lin_z_upper = 0.2
            bpy.context.object.rigid_body_constraint.use_override_solver_iterations = True
            bpy.context.object.rigid_body_constraint.solver_iterations = 300
            bpy.context.object.rigid_body_constraint.use_spring_z = True
            bpy.context.object.rigid_body_constraint.spring_stiffness_z = 50000
            bpy.context.object.rigid_body_constraint.spring_damping_z = 1000
            bpy.context.object.rigid_body_constraint.object1 = suspensionRigidbody
            bpy.context.object.rigid_body_constraint.object2 = bodyRigidbody

            # Wheel Hinge Constraint
            bpy.ops.object.empty_add(type='SINGLE_ARROW', align='WORLD', location=(wheel.obj.location), rotation=(0, -1.5708, 0), scale=(1, 1, 1))
            hingeConstraint = bpy.context.active_object
            hingeConstraint.name = wheel.obj.name + " Hinge"
            keepTransformParent(hingeConstraint, rig)
            moveToCollection(hingeConstraint, wheelConstraintCollection)
 
            bpy.ops.rigidbody.constraint_add()
            bpy.context.object.rigid_body_constraint.type = 'HINGE'
            bpy.context.object.rigid_body_constraint.object1 = suspensionRigidbody
            bpy.context.object.rigid_body_constraint.object2 = wheelRigidbody



            # Motor Constraints
            # bpy.ops.object.empty_add(type='CONE', align='WORLD', location=(wheel.obj.location), rotation=(0, -1.5708, 0), scale=(1, 1, 1))
            # bpy.context.object.empty_display_size = 0.3
            # motorConstraint = bpy.context.active_object
            # motorConstraint.name = wheel.obj.name + " Motor"
            # rotateObject(0, 0, 90, motorConstraint)
            # keepTransformParent(motorConstraint, rig)

            # moveToCollection(motorConstraint, wheelConstraintCollection)

            # bpy.ops.rigidbody.constraint_add()
            # bpy.context.object.rigid_body_constraint.type = 'MOTOR'
            # bpy.context.object.rigid_body_constraint.object1 = bodyRigidbody
            # bpy.context.object.rigid_body_constraint.object2 = wheelRigidbody
            # bpy.context.object.rigid_body_constraint.use_motor_ang = True
            # bpy.context.object.rigid_body_constraint.motor_ang_target_velocity = 1e+08
            # bpy.context.object.rigid_body_constraint.motor_ang_max_impulse = 1e+07


        return{'FINISHED'}

class VDS_OT_actions(Operator):
    """Move items up and down, add and remove"""
    bl_idname = "vds.list_action"
    bl_label = ""
    bl_description = "Add, remove, and reorganize items"
    bl_options = {'REGISTER'}
    
    action : bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))

    def invoke(self, context, event):
        scene = context.scene
        idx = scene.wheelsIndex

        try:
            item = scene.vds[idx]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and idx < len(scene.vds) - 1:
                item_next = scene.vds[idx+1].name
                scene.vds.move(idx, idx+1)
                scene.wheelsIndex += 1
                info = 'Item "%s" moved to position %d' % (item.name, scene.wheelsIndex + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = scene.vds[idx-1].name
                scene.vds.move(idx, idx-1)
                scene.wheelsIndex -= 1
                info='Item "%s" moved to position %d' % (item.name, scene.wheelsIndex + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                info = 'Item "%s" removed from list' % (scene.vds[idx].name)
                scene.wheelsIndex -= 1
                scene.vds.remove(idx)
                self.report({'INFO'}, info)
                
        if self.action == 'ADD':
            if context.object:
                item = scene.vds.add()
                item.name = context.object.name
                item.obj = context.object
                item.suspensionheight = 15
                print(item)

                scene.wheelsIndex = len(scene.vds) - 1
                info = '"%s" added to list' % (item.name)
                self.report({'INFO'}, info)
            else:
                self.report({'INFO'}, "Nothing selected in the Viewport")
        return {"FINISHED"}

class VDS_OT_addViewportSelection(Operator):
    """Add all items currently selected in the viewport"""
    bl_idname = "vds.add_viewport_selection"
    bl_label = ""
    bl_description = "Add all items currently selected in the viewport"
    bl_options = {'REGISTER', 'UNDO'}
        
    def execute(self, context):
        scene = context.scene
        selected_objs = context.selected_objects
        if selected_objs:
            new_objs = []
            for i in selected_objs:
                item = scene.vds.add()
                item.name = i.name
                item.obj = i
                new_objs.append(item.name)
            info=', '.join(map(str, new_objs))
            self.report({'INFO'}, 'Added: "%s"' % (info))
        else:
            self.report({'INFO'}, "Nothing selected in the Viewport")
        return{'FINISHED'}

class VDS_OT_deleteObject(Operator):
    """Delete object from scene"""
    bl_idname = "vds.delete_object"
    bl_label = ""
    bl_description = "Remove object from scene"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bool(context.scene.vds)

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
            
    def execute(self, context):
        scene = context.scene
        selected_objs = context.selected_objects
        idx = scene.wheelsIndex
        try:
            item = scene.vds[idx]
            print(item)
        except IndexError:
            pass
        else:
            ob = scene.objects.get(item.obj.name)
            print(ob)
            if not ob:
                self.report({'INFO'}, "No object of that name found in scene")
                return {"CANCELLED"}
            else:
                bpy.ops.object.select_all(action='DESELECT')
                ob.select_set(True)
                bpy.ops.object.delete()
                    
            info = ' Item "%s" removed from Scene' % (len(selected_objs))
            scene.wheelsIndex -= 1
            scene.vds.remove(idx)
            self.report({'INFO'}, info)
        return{'FINISHED'}

# class VDS_OT_testDraw(Operator):
#     """Delete object from scene"""
#     bl_idname = "vds.test_draw"
#     bl_label = "Redraw"
#     bl_description = "Remove object from scene"
#     bl_options = {'REGISTER', 'UNDO'}

#     @classmethod
#     def poll(cls, context):
#         return bool(context.scene.vds)
                
#     def execute(self, context):
#         scene = context.scene
#         selected_objs = context.selected_objects
#         index = scene.wheelsIndex
#         # try:
#         item = scene.vds[index]
#         print(item)
#         # except IndexError:
#         #     pass
#         # else:
#         # ob = scene.objects.get(item.obj.name)
#         # print(ob)
                    
#         info = ' Item "%s" removed from Scene' % (len(selected_objs))

#         print(scene.wheelsIndex)
#         # scene.wheelsIndex -= 1
#         # scene.vds.remove(index)
#         self.report({'INFO'}, info)

#         return{'FINISHED'}

# -------------------------------------------------------------------
#   Drawing
# -------------------------------------------------------------------

# CONTROL MENU
# Panel that will display the cusomizable options for the rig
class VDS_PG_ControlsProperties(PropertyGroup):
    Steering : bpy.props.FloatProperty(
        description = "Control for the vehicle's steering",
        default = 0,
        min = -1,
        max = 1,
        step = 10,
        options = {'ANIMATABLE'}
    )
    Motor : bpy.props.FloatProperty(
        description = "Control for the vehicle's motor",
        default = 0,
        min = -1,
        max = 1,
        step = 10,
        options = {'ANIMATABLE'}
    )

class VDS_PT_Controls(Panel):
    """The Controls Panel"""
    bl_label = "Controls"
    bl_idname = "OBJECT_PT_controls"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Vehicles Sim'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene

        controlsTool = scene.controlsTool

        layout.label(text = "The controls that you drive with")

        layout.prop(controlsTool, "Steering")
        layout.prop(controlsTool, "Motor")

# RIG MENU
# class VDS_UL_bodys(UIList):
#     def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
#         obj = item.obj
#         vds_icon = "OUTLINER_OB_%s" % obj.type
#         split = layout.split(factor=0.1)
#         split.label(text="%d" % (index))
#         split.prop(obj, "name", text="", emboss=False, translate=False, icon=vds_icon)
                
#     def invoke(self, context, event):
#         pass

# class VDS_UL_doors(UIList):
#     def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
#         obj = item.obj
#         vds_icon = "OUTLINER_OB_%s" % obj.type
#         split = layout.split(factor=0.1)
#         split.label(text="%d" % (index))
#         split.prop(obj, "name", text="", emboss=False, translate=False, icon=vds_icon)
                        
#     def invoke(self, context, event):
#         pass

# UI List of all rigs in the scene
class VDS_UL_rigs(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        obj = item.obj
        vds_icon = "OUTLINER_OB_%s" % obj.type
        split = layout.split(factor=0.1)
        split.label(text="%d" % (index))
        split.prop(obj, "name", text="", emboss=False, translate=False, icon=vds_icon)
                
    def invoke(self, context, event):
        pass 

# Properties for the Rig panel
class VDS_PG_RigProperties(PropertyGroup):
    Body1 : bpy.props.PointerProperty(
        name = 'Body',
        description = '',
        type = bpy.types.Object
    )

# Panel that will display the rig menu
class VDS_PT_Rig(Panel):
    """The Rig Panel"""
    bl_label = "Rig"
    bl_idname = "OBJECT_PT_rig"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = 'Vehicles Sim'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        rigTool = scene.rigTool

        # layout.label(text="Click do add a rig for the car wow")
      
        layout.label(text="Rig List")
        rows = 4
        row = layout.row()
        row.template_list("VDS_UL_rigs", "", scene, "vds", scene, "rigsIndex", rows=rows)

        # Buttons that control the list
        col = row.column(align=True)
        col.operator("vds.list_action", icon='ADD', text="").action = 'ADD'
        col.operator("vds.list_action", icon='REMOVE', text="").action = 'REMOVE'
        col.separator()
        col.operator("vds.list_action", icon='TRIA_UP', text="").action = 'UP'
        col.operator("vds.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'
        col.separator()
        col.operator("vds.add_viewport_selection", icon="HAND") #LINENUMBERS_OFF, ANIM

        # New Rig button
        layout.operator("vds.add_rig", text="New Rig", icon='AUTO')

        # # Test Draw button
        # layout.label(text="Click to refresh draw the things wowza")
        # layout.operator("vds.test_draw", text="Refresh", icon='SPHERE')

        # Bodys
            # layout.label(text="Body List")
            # rows = 2
            # row = layout.row()
            # row.template_list("VDS_UL_bodys", "", scene, "vds", scene, "wheelsIndex", rows=rows)
        # Doors
            # layout.label(text="Door List")
            # rows = 2
            # row = layout.row()
            # row.template_list("VDS_UL_doors", "", scene, "vds", scene, "doorsIndex", rows=rows)
        # Wheels

        # col.operator("vds.delete_object", icon="X") #LINENUMBERS_OFF, ANIM

# Properties for the Body panel
class VDS_PG_BodyProperties(PropertyGroup):
    Body : bpy.props.PointerProperty(
        name = 'Body',
        description = '',
        type = bpy.types.Object
    )
    Weight : bpy.props.FloatProperty(
        name = 'Weight',
        description = "Vehicle Rigidbody Weight",
        default = 1500,
        step = 100,
    )
    DeformSpacingMultiplier : bpy.props.FloatProperty(
        name = 'Deform Spacing Multiplier',
        description = "Spacing between the deform mesh and the regular mesh",
        default = 1.1,
        step = 1,
    )
    DeformSubdivisions : bpy.props.FloatProperty(
        name = 'Deform Voxel Size',
        description = "Size of the voxels used on the remesh modifier",
        default = 0.2,
        step = 10,
    )

# Panel that will display the rig menu
class VDS_PT_Body(Panel):
    """The Body Panel"""
    bl_label = "Body"
    bl_idname = "OBJECT_PT_body"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = 'Vehicles Sim'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bodyTool = scene.bodyTool

        # Generate Rig button
        # layout.label(text="Click do add a rig for the car wow")

        layout.prop(bodyTool, "Body")
        layout.prop(bodyTool, "Weight")
        layout.prop(bodyTool, "DeformSpacingMultiplier")
        layout.prop(bodyTool, "DeformSubdivisions")

# UI List of all the assigned wheels
class VDS_UL_wheels(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        obj = item.obj
        vds_icon = "OUTLINER_OB_%s" % obj.type
        split = layout.split(factor=0.1)
        split.label(text="%d" % (index))
        split.prop(obj, "name", text="", emboss=False, translate=False, icon=vds_icon)
                
    def invoke(self, context, event):
        pass   

class VDS_PT_Wheel(Panel):
    """The Wheel Panel"""
    bl_label = "Wheel"
    bl_idname = "OBJECT_PT_wheelproperties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Vehicles Sim'
    bl_context = "objectmode"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene

        wheelTool = scene.wheelTool
      
        layout.label(text="Wheel List")
        rows = 2
        row = layout.row()
        row.template_list("VDS_UL_wheels", "", scene, "vds", scene, "wheelsIndex", rows=rows)

        # Buttons that control the list
        col = row.column(align=True)
        col.operator("vds.list_action", icon='ADD', text="").action = 'ADD'
        col.operator("vds.list_action", icon='REMOVE', text="").action = 'REMOVE'
        col.separator()
        col.operator("vds.list_action", icon='TRIA_UP', text="").action = 'UP'
        col.operator("vds.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'
        col.separator()
        col.operator("vds.add_viewport_selection", icon="HAND") #LINENUMBERS_OFF, ANIM

        # Suspension
        layout.prop(wheelTool, "obj")
        layout.prop(wheelTool, "suspensionheight")
        layout.prop(wheelTool, "motorforce")
        layout.prop(wheelTool, "steerangle")

# -------------------------------------------------------------------
#   Collection
# -------------------------------------------------------------------

# class VDS_PG_bodyCollection(PropertyGroup):
# #name: StringProperty() -> Instantiated by default
#     obj : PointerProperty(
#         name = "Object",
#         type = bpy.types.Object
#     )

# class VDS_PG_doorCollection(PropertyGroup):
# #name: StringProperty() -> Instantiated by default
#     obj : PointerProperty(
#         name = "Object",
#         type = bpy.types.Object
#     )

class VDS_PG_wheelCollection(PropertyGroup):
#name: StringProperty() -> Instantiated by default
    obj : PointerProperty(
        name = "Object",
        type = bpy.types.Object
    )
    suspensionheight : bpy.props.FloatProperty(
        name = "Suspension Height",
        description = "The height of the suspension? It's pretty self explanatory",
        default = 0,
        step = 10,
    )
    motorforce : bpy.props.FloatProperty(
        name = "Motor Torque",
        description = "The amount of torque that the wheel has",
        default = 0,
        step = 10,
    )
    steerangle : bpy.props.FloatProperty(
        name = "Steer Angle",
        description = "How far the wheel turns",
        max = 360,
        min = -360,
        default = 0,
        step = 100,
    )

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    # Operators
    VDS_OT_AddRig,
    VDS_OT_actions,
    VDS_OT_addViewportSelection,
    VDS_OT_deleteObject,
    # VDS_OT_testDraw,
    # Controls
    VDS_PG_ControlsProperties,
    VDS_PT_Controls,
    # Rig
    VDS_UL_rigs,
    # VDS_UL_bodys,
    # VDS_UL_doors,
    VDS_PG_RigProperties,
    VDS_PT_Rig,
    # Body
    VDS_PG_BodyProperties,
    VDS_PT_Body,
    # Wheel
    VDS_UL_wheels,
    VDS_PG_wheelCollection,
    VDS_PT_Wheel,
    # Collection
    # VDS_PG_bodyCollection,
    # VDS_PG_doorCollection,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    # Custom scene properties
    bpy.types.Scene.vds = CollectionProperty(type=VDS_PG_wheelCollection)
    bpy.types.Scene.controlsTool = PointerProperty(type=VDS_PG_ControlsProperties)
    bpy.types.Scene.bodyTool = PointerProperty(type=VDS_PG_BodyProperties)
    bpy.types.Scene.rigTool = PointerProperty(type=VDS_PG_RigProperties)
    bpy.types.Scene.wheelsIndex = IntProperty()
    bpy.types.Scene.rigsIndex = IntProperty()

    bpy.types.Scene.wheelTool = PointerProperty(type=VDS_PG_wheelCollection)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.vds
    del bpy.types.Scene.controlsTool
    del bpy.types.Scene.bodyTool
    del bpy.types.Scene.rigTool
    del bpy.types.Scene.wheelsIndex
    del bpy.types.Scene.rigsIndex
    del bpy.types.Scene.wheelTool

if __name__ == "__main__":
    register()