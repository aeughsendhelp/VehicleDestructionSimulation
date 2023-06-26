# ORGANIZATION

# Operators

# DRAWING
# Rig
# Options

# 
# 

bl_info = {
    "name": "Physics-Based Vehicles",
    "author": "aeugh",
    "version": (1, 0),
    "blender": (3, 5, 1),
    "location": "View3D > Add > Mesh > New Object (this is not the actual location)",
    "description": "Aims to assist the process of creating a rigidbody vehicles with destruction simulations",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}

import bpy
from bpy.types import Panel, Operator, PropertyGroup, UIList
from bpy.props import EnumProperty, PointerProperty, StringProperty, FloatProperty, IntProperty, FloatVectorProperty, BoolProperty, BoolVectorProperty, CollectionProperty
from mathutils import Vector
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from bpy.utils import register_class, unregister_class

class VDS_OT_actions(Operator):
    """Move items up and down, add and remove"""
    bl_idname = "vds.list_action"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}
        
    action: bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))

    def invoke(self, context, event):
        scn = context.scene
        idx = scn.vds_index

        try:
            item = scn.vds[idx]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and idx < len(scn.vds) - 1:
                item_next = scn.vds[idx+1].name
                scn.vds.move(idx, idx+1)
                scn.vds_index += 1
                info = 'Item "%s" moved to position %d' % (item.name, scn.vds_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = scn.vds[idx-1].name
                scn.vds.move(idx, idx-1)
                scn.vds_index -= 1
                info = 'Item "%s" moved to position %d' % (item.name, scn.vds_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                info = 'Item "%s" removed from list' % (scn.vds[idx].name)
                scn.vds_index -= 1
                scn.vds.remove(idx)
                self.report({'INFO'}, info)
                    
        if self.action == 'ADD':
            if context.object:
                item = scn.vds.add()
                item.name = context.object.name
                item.obj = context.object
                scn.vds_index = len(scn.vds)-1
                info = '"%s" added to list' % (item.name)
                self.report({'INFO'}, info)
            else:
                self.report({'INFO'}, "Nothing selected in the Viewport")
        return {"FINISHED"}

# class VDS_OT_actions(Operator):
#     """Move items up and down, add and remove"""
#     bl_idname = "vds.list_action"
#     bl_label = "List Actions"
#     bl_description = "Move items up and down, add and remove"
#     bl_options = {'REGISTER'}

#     action: bpy.props.EnumProperty(
#         items=(
#             ('UP', "Up", ""),
#             ('DOWN', "Down", ""),
#             ('REMOVE', "Remove", ""),
#             ('ADD', "Add", "")))

#     def invoke(self, context, event):
#         scn = context.scene
#         idx = scn.vds_index

#         try:
#             item = scn.vds[idx]
#         except IndexError:
#             pass
#         else:
#             if self.action == 'DOWN' and idx < len(scn.vds) - 1:
#                 item_next = scn.vds[idx+1].name
#                 scn.vds.move(idx, idx+1)
#                 scn.vds_index += 1
#                 info = 'Item "%s" moved to position %d' % (item.name, scn.vds_index + 1)
#                 self.report({'INFO'}, info)

#             elif self.action == 'UP' and idx >= 1:
#                 item_prev = scn.vds[idx-1].name
#                 scn.vds.move(idx, idx-1)
#                 scn.vds_index -= 1
#                 info = 'Item "%s" moved to position %d' % (item.name, scn.vds_index + 1)
#                 self.report({'INFO'}, info)

#             elif self.action == 'REMOVE':
#                 info = 'Item "%s" removed from list' % (scn.vds[idx].name)
#                 scn.vds_index -= 1
#                 scn.vds.remove(idx)
#                 self.report({'INFO'}, info)

#         if self.action == 'ADD':
#             if context.object:
#                 item = scn.vds.add()
#                 item.name = context.object.name
#                 item.obj_type = context.object.type
#                 item.obj_id = len(scn.vds)
#                 scn.vds_index = len(scn.vds)-1
#                 info = '"%s" added to list' % (item.name)
#                 self.report({'INFO'}, info)
#             else:
#                 self.report({'INFO'}, "Nothing selected in the Viewport")
#         return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        return bool(context.scene.vds)

    def execute(self, context):
        scn = context.scene
        removed_items = []
        # Reverse the list before removing the items
        for i in self.find_duplicates(context)[::-1]:
            scn.vds.remove(i)
            removed_items.append(i)
        if removed_items:
            scn.vds_index = len(scn.vds)-1
            info = ', '.join(map(str, removed_items))
            self.report({'INFO'}, "Removed indices: %s" % (info))
        else:
            self.report({'INFO'}, "No duplicates")
        return{'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


# -------------------------------------------------------------------
#   Drawing
# -------------------------------------------------------------------


# RIG MENU
# UI List of all the assigned wheels
class VDS_UL_wheels(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(factor=0.3)
        split.label(text="Index: %d" % (index))
        vds_icon = "OUTLINER_OB_%s" % item.obj_type
        #split.prop(item, "name", text="", emboss=False, translate=False, icon=vds_icon)
        split.label(text=item.name, icon=vds_icon) # avoids renaming the item by accident

    def invoke(self, context, event):
        pass   

# Panel that will display the rig menu
class VDS_PT_RigOptions(Panel):
    """Adds a vds panel to the TEXT_EDITOR"""
    bl_label = "Rig Options"
    bl_idname = "OBJECT_PT_addRig"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Vehicles Sim'

    def draw(self, context):
        layout = self.layout
        scn = bpy.context.scene

        layout.label(text="Click do add a rig for the car wow")

        # The list of object
        rows = 2
        row = layout.row()
        row.template_list("VDS_UL_wheels", "", scn, "vds", scn, "vds_index", rows=rows)

        # The buttons that allow control over the list
        col = row.column(align=True)
        col.operator("vds.list_action", icon='ZOOM_IN', text="").action = 'ADD'
        col.operator("vds.list_action", icon='ZOOM_OUT', text="").action = 'REMOVE'
        col.separator()
        col.operator("vds.list_action", icon='TRIA_UP', text="").action = 'UP'
        col.operator("vds.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'


class VDS_PG_RigOptionsProperties(PropertyGroup):
    FLWheel : bpy.props.PointerProperty(
        name  ='FL Wheel',
        description = '',
        type = bpy.types.Object
    )



# Panel that will display the cusomizable options for the rig
class VDS_PT_Controls(Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Controls"
    bl_idname = "OBJECT_PT_controls"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Vehicles Sim'

    def draw(self, context):
        layout = self.layout
        obj = context.object

        layout.label(text="Here will be the controls that'll allow")
        layout.label(text="you to drive the car")

        # layout.operator(AddListItemOperator.bl_idname, text="gamer? ong?", icon='SPHERE')

# -------------------------------------------------------------------
#   Collection
# -------------------------------------------------------------------

class VDS_objectCollection(PropertyGroup):
    #name: StringProperty() -> Instantiated by default
    obj_type: StringProperty()
    obj_id: IntProperty()


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    VDS_OT_actions,

    # Rig
    VDS_UL_wheels,
    VDS_PT_RigOptions,
    VDS_PG_RigOptionsProperties,
    # Controls
    VDS_PT_Controls,
    # COLLECTION
    VDS_objectCollection,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    # Custom scene properties
    bpy.types.Scene.vds = CollectionProperty(type=VDS_objectCollection)
    bpy.types.Scene.vds_index = IntProperty()
    bpy.types.Scene.rigOptionsPropertiesReference_ = PointerProperty(type=VDS_PG_RigOptionsProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.vds
    del bpy.types.Scene.vds_index
    del bpy.types.Scene.rigOptionsPropertiesReference_


if __name__ == "__main__":
    register()



# import bpy
# from bpy.types import Panel, Operator, PropertyGroup, UIList
# from bpy.props import EnumProperty, PointerProperty, StringProperty, FloatProperty, IntProperty, FloatVectorProperty, BoolProperty, BoolVectorProperty
# from mathutils import Vector
# from bpy_extras.object_utils import AddObjectHelper, object_data_add
# from bpy.utils import register_class, unregister_class

# class VDS_OT_actions(Operator):
#     """Move items up and down, add and remove"""
#     bl_idname = "vds.list_action"
#     bl_label = "List Actions"
#     bl_description = "Move items up and down, add and remove"
#     bl_options = {'REGISTER'}

#     action: bpy.props.EnumProperty(
#         items=(
#             ('UP', "Up", ""),
#             ('DOWN', "Down", ""),
#             ('REMOVE', "Remove", ""),
#             ('ADD', "Add", "")))

#     def invoke(self, context, event):
#         scn = context.scene
#         idx = scn.vds_index

#         try:
#             item = scn.vds[idx]
#         except IndexError:
#             pass
#         else:
#             if self.action == 'DOWN' and idx < len(scn.vds) - 1:
#                 item_next = scn.vds[idx+1].name
#                 scn.vds.move(idx, idx+1)
#                 scn.vds_index += 1
#                 info = 'Item "%s" moved to position %d' % (item.name, scn.vds_index + 1)
#                 self.report({'INFO'}, info)

#             elif self.action == 'UP' and idx >= 1:
#                 item_prev = scn.vds[idx-1].name
#                 scn.vds.move(idx, idx-1)
#                 scn.vds_index -= 1
#                 info = 'Item "%s" moved to position %d' % (item.name, scn.vds_index + 1)
#                 self.report({'INFO'}, info)

#             elif self.action == 'REMOVE':
#                 info = 'Item "%s" removed from list' % (scn.vds[idx].name)
#                 scn.vds_index -= 1
#                 scn.vds.remove(idx)
#                 self.report({'INFO'}, info)

#         if self.action == 'ADD':
#             if context.object:
#                 item = scn.vds.add()
#                 item.name = context.object.name
#                 item.obj_type = context.object.type
#                 item.obj_id = len(scn.vds)
#                 scn.vds_index = len(scn.vds)-1
#                 info = '"%s" added to list' % (item.name)
#                 self.report({'INFO'}, info)
#             else:
#                 self.report({'INFO'}, "Nothing selected in the Viewport")
#         return {"FINISHED"}


# class VDS_UL_wheels(UIList):
#     def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
#         split = layout.split(factor=0.3)
#         split.label(text="Index: %d" % (index))
#         vds_icon = "OUTLINER_OB_%s" % item.obj_type
#         #split.prop(item, "name", text="", emboss=False, translate=False, icon=vds_icon)
#         split.label(text=item.name, icon=vds_icon) # avoids renaming the item by accident

#     def invoke(self, context, event):
#         pass


# class RigOptionsProperties(PropertyGroup):
#     FLWheel : bpy.props.PointerProperty(
#         name  ='FL Wheel',
#         description = '',
#         type = bpy.types.Object
#     )

        
# #        row = layout.row()
# #        row.template_list("UI_UL_list", "", TestList, "reference_list", TestList, "active_index")



# # Declare the classes to be registered, then register and unregister said classes
# classes = [
#     VDS_OT_actions,
#     VDS_UL_wheels,
#     RigOptionsProperties,
#     RigOptions,
#     Controls
# ]