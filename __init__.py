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
        body = scene.rigTool.Body
        moveToCollection(body, bodyMeshCollection)

        # Body Rigidbody
        bpy.ops.object.select_all(action='DESELECT')
        body.select_set(True)
        bpy.context.view_layer.objects.active = body

        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
        bodyRigidbody = bpy.context.active_object
        bodyRigidbody.name = body.name + " Rigidbody"
        bodyRigidbody.display_type = 'WIRE'
        moveToCollection(bodyRigidbody, bodyRigidbodyCollection)

        bm = bmesh.new()
        bm.from_mesh(bodyRigidbody.data)
        bmesh.ops.convex_hull(bm, input=bm.verts)
        bm.to_mesh(bodyRigidbody.data)

        bpy.ops.rigidbody.object_add()
        bpy.context.object.rigid_body.mass = 1500

        # Body Deform
        bpy.ops.object.select_all(action='DESELECT')
        body.select_set(True)
        bpy.context.view_layer.objects.active = body

        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
        bodyDeform = bpy.context.active_object
        bodyDeform.name = body.name + " Deform"
        bodyDeform.display_type = 'WIRE'
        # moveToCollection(bodyDeform, bodyDeformCollection)

        bm = bmesh.new()
        bm.from_mesh(bodyDeform.data)
        # bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=1, use_grid_fill=True)
        bmesh.ops.convex_hull(bm, input=bm.verts)
        bm.to_mesh(bodyDeform.data)

        bpy.ops.object.modifier_add(type='REMESH')
        bpy.context.object.modifiers["Remesh"].mode = 'VOXEL'
        bpy.context.object.modifiers["Remesh"].voxel_size = 0.2
        bpy.ops.object.modifier_add(type='SHRINKWRAP')
        bpy.context.object.modifiers["Shrinkwrap"].target = body
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.modifier_add(type='CLOTH')


        for wheel in scene.vds:
            # print(wheel.obj.location)
            # Wheel
            moveToCollection(wheel.obj, wheelMeshCollection)

            # Wheel Rigidbody
            rotatedVector = Vector((wheel.obj.dimensions.z, wheel.obj.dimensions.y, wheel.obj.dimensions.x))/2
            bpy.ops.mesh.primitive_cylinder_add(vertices=16, enter_editmode=False, align='WORLD', location=(wheel.obj.location), rotation=(0, 1.5708, 0), scale=(rotatedVector))
            wheelRigidbody = bpy.context.active_object
            wheelRigidbody.name = wheel.obj.name + " Rigidbody"
            wheelRigidbody.display_type = 'WIRE'
            moveToCollection(wheelRigidbody, wheelRigidbodyCollection)
            wheel.parent = wheelRigidbody

            bpy.ops.rigidbody.object_add()
            bpy.context.object.rigid_body.mass = 100


            # Hinge Constraints
            bpy.ops.object.empty_add(type='SINGLE_ARROW', align='WORLD', location=(wheel.obj.location), rotation=(0, -1.5708, 0), scale=(1, 1, 1))
            hingeConstraint = bpy.context.active_object
            hingeConstraint.name = wheel.obj.name + " Hinge"
            moveToCollection(hingeConstraint, wheelConstraintCollection)

            bpy.ops.rigidbody.constraint_add()
            bpy.context.object.rigid_body_constraint.type = 'HINGE'
            bpy.context.object.rigid_body_constraint.object1 = bodyRigidbody
            bpy.context.object.rigid_body_constraint.object2 = wheelRigidbody


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

# Properties for the Rig panel
class VDS_PG_RigProperties(PropertyGroup):
    Body : bpy.props.PointerProperty(
        name = 'FL Wheel',
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
    bl_category = 'Vehicles Sim'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        rigTool = scene.rigTool

        # Generate Rig button
        layout.label(text="Click do add a rig for the car wow")
        layout.operator("vds.add_rig", text="Generate Rig", icon='AUTO')

        layout.prop(rigTool, "Body")

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
        # col.operator("vds.delete_object", icon="X") #LINENUMBERS_OFF, ANIM


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
      
        # Suspension
        # layout.prop(wheelTool, "obj")
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
    VDS_UL_wheels,
    # VDS_UL_bodys,
    # VDS_UL_doors,
    VDS_PG_RigProperties,
    VDS_PT_Rig,
    # Wheel
    VDS_PT_Wheel,
    # Collection
    # VDS_PG_bodyCollection,
    # VDS_PG_doorCollection,
    VDS_PG_wheelCollection,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    # Custom scene properties
    bpy.types.Scene.vds = CollectionProperty(type=VDS_PG_wheelCollection)
    bpy.types.Scene.wheelTool = PointerProperty(type=VDS_PG_wheelCollection)
    bpy.types.Scene.wheelsIndex = IntProperty()
    bpy.types.Scene.rigTool = PointerProperty(type=VDS_PG_RigProperties)
    bpy.types.Scene.controlsTool = PointerProperty(type=VDS_PG_ControlsProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.vds
    del bpy.types.Scene.wheelsIndex
    del bpy.types.Scene.rigTool
    del bpy.types.Scene.controlsTool

if __name__ == "__main__":
    register()