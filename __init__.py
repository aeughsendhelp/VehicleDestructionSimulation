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
from bpy.types import Panel, Operator, PropertyGroup, UIList
from bpy.props import EnumProperty, PointerProperty, StringProperty, FloatProperty, IntProperty, FloatVectorProperty, BoolProperty, BoolVectorProperty, CollectionProperty
from mathutils import Vector
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from bpy.utils import register_class, unregister_class

filename="D:/Documents/Code/VehicleDestructionSimulation/testlist.py"

# bpy.data.texts["testlist"].as_module()

class VDS_OT_actions(Operator):
    """Move items up and down, add and remove"""
    bl_idname="vds.list_action"
    bl_label=""
    bl_description="Add, remove, and reorganize items"
    bl_options={'REGISTER'}
    
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

class VDS_OT_testDraw(Operator):
    """Delete object from scene"""
    bl_idname = "vds.test_draw"
    bl_label = "Redraw"
    bl_description = "Remove object from scene"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bool(context.scene.vds)
                
    def execute(self, context):
        scene = context.scene
        selected_objs = context.selected_objects
        index = scene.wheelsIndex
        # try:
        item = scene.vds[index]
        print(item)
        # except IndexError:
        #     pass
        # else:
        # ob = scene.objects.get(item.obj.name)
        # print(ob)
                    
        info = ' Item "%s" removed from Scene' % (len(selected_objs))

        print(scene.wheelsIndex)
        # scene.wheelsIndex -= 1
        # scene.vds.remove(index)
        self.report({'INFO'}, info)

        return{'FINISHED'}

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
# UI List of all the assigned wheels
class VDS_UL_wheels(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        obj = item.obj
        suspensionheight = item.suspensionheight
        vds_icon = "OUTLINER_OB_%s" % obj.type
        split = layout.split(factor=0.1)
        split.label(text="%d" % (index))
        split.prop(obj, "name", text="", emboss=False, translate=False, icon=vds_icon)
                
    def invoke(self, context, event):
        pass   

# Properties for the Rig panel
class VDS_PG_RigProperties(PropertyGroup):
    FLWheel : bpy.props.PointerProperty(
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

        # Add Rig button NEEDS NEW OPERATOR
        layout.label(text="Click do add a rig for the car wow")
        layout.operator("object.select_all", text="Add Rig", icon='AUTO')

        # Test Draw button
        layout.label(text="Click to refresh draw the things wowza")
        layout.operator("vds.test_draw", text="Refresh", icon='SPHERE')

        # List of wheels
        layout.label(text="The wheels for the vehicle")
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
        col.operator("vds.delete_object", icon="X") #LINENUMBERS_OFF, ANIM


class VDS_PT_Wheel(Panel):
    """The Wheel Panel"""
    bl_label = "Wheel"
    bl_idname = "OBJECT_PT_wheelproperties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Vehicles Sim'
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene

        wheelTool = scene.wheelTool
      
        # Suspension
        layout.prop(wheelTool, "obj")
        layout.prop(wheelTool, "suspensionheight")
        layout.prop(wheelTool, "motorforce")
        layout.prop(wheelTool, "steerangle")

# -------------------------------------------------------------------
#   Collection
# -------------------------------------------------------------------

objList = []
# suspensionList = []

class VDS_PG_objectCollection(PropertyGroup):
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
    VDS_OT_actions,
    VDS_OT_addViewportSelection,
    VDS_OT_deleteObject,
    VDS_OT_testDraw,
    # Controls
    VDS_PG_ControlsProperties,
    VDS_PT_Controls,
    # Rig
    VDS_UL_wheels,
    VDS_PG_RigProperties,
    VDS_PT_Rig,
    # Wheel
    VDS_PT_Wheel,
    # Collection
    VDS_PG_objectCollection,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    # Custom scene properties
    bpy.types.Scene.vds = CollectionProperty(type=VDS_PG_objectCollection)
    bpy.types.Scene.wheelTool = PointerProperty(type=VDS_PG_objectCollection)
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