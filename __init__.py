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

class VDP_OT_actions(Operator):
    """Move items up and down, add and remove"""
    bl_idname = "vdp.list_action"
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
        idx = scn.vdp_index

        try:
            item = scn.vdp[idx]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and idx < len(scn.vdp) - 1:
                item_next = scn.vdp[idx+1].name
                scn.vdp.move(idx, idx+1)
                scn.vdp_index += 1
                info = 'Item "%s" moved to position %d' % (item.name, scn.vdp_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = scn.vdp[idx-1].name
                scn.vdp.move(idx, idx-1)
                scn.vdp_index -= 1
                info = 'Item "%s" moved to position %d' % (item.name, scn.vdp_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                info = 'Item "%s" removed from list' % (scn.vdp[idx].name)
                scn.vdp_index -= 1
                scn.vdp.remove(idx)
                self.report({'INFO'}, info)

        if self.action == 'ADD':
            if context.object:
                item = scn.vdp.add()
                item.name = context.object.name
                item.obj_type = context.object.type
                item.obj_id = len(scn.vdp)
                scn.vdp_index = len(scn.vdp)-1
                info = '"%s" added to list' % (item.name)
                self.report({'INFO'}, info)
            else:
                self.report({'INFO'}, "Nothing selected in the Viewport")
        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        return bool(context.scene.vdp)

    def execute(self, context):
        scn = context.scene
        removed_items = []
        # Reverse the list before removing the items
        for i in self.find_duplicates(context)[::-1]:
            scn.vdp.remove(i)
            removed_items.append(i)
        if removed_items:
            scn.vdp_index = len(scn.vdp)-1
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

class VDP_UL_wheels(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(factor=0.3)
        split.label(text="Index: %d" % (index))
        vdp_icon = "OUTLINER_OB_%s" % item.obj_type
        #split.prop(item, "name", text="", emboss=False, translate=False, icon=vdp_icon)
        split.label(text=item.name, icon=vdp_icon) # avoids renaming the item by accident

    def invoke(self, context, event):
        pass   

class VDP_PT_AddRig(Panel):
    """Adds a vdp panel to the TEXT_EDITOR"""
    bl_label = "Rig Options"
    bl_idname = "OBJECT_PT_addRig"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Physics Vehicles'

    def draw(self, context):
        layout = self.layout
        scn = bpy.context.scene

        layout.label(text="Click do add a rig for the car wow")

        # The list of object
        rows = 2
        row = layout.row()
        row.template_list("VDP_UL_wheels", "", scn, "vdp", scn, "vdp_index", rows=rows)

        # The buttons that allow control over the list
        col = row.column(align=True)
        col.operator("vdp.list_action", icon='ZOOM_IN', text="").action = 'ADD'
        col.operator("vdp.list_action", icon='ZOOM_OUT', text="").action = 'REMOVE'
        col.separator()
        col.operator("vdp.list_action", icon='TRIA_UP', text="").action = 'UP'
        col.operator("vdp.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'


# Panel that will display the rig menu
class RigOptionsProperties(PropertyGroup):
    FLWheel : bpy.props.PointerProperty(
        name  ='FL Wheel',
        description = '',
        type = bpy.types.Object
    )


class RigOptions(Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Rig Options"
    bl_idname = "OBJECT_PT_rigOptions"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Physics Vehicles'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object

        # rigOptionsPropertiesReference = scene.rigOptionsPropertiesReference_

        # row.operator("object.add_list_item", text="Add List Item")

        layout.label(text="Set the number of axles")


        
#        row = layout.row()
#        row.template_list("UI_UL_list", "", TestList, "reference_list", TestList, "active_index")

# Panel that will display the vdpizable options for the rig
class Controls(Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Controls"
    bl_idname = "OBJECT_PT_options"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Physics Vehicles'

    def draw(self, context):
        layout = self.layout
        obj = context.object

        # layout.operator(AddListItemOperator.bl_idname, text="gamer? ong?", icon='SPHERE')

# -------------------------------------------------------------------
#   Collection
# -------------------------------------------------------------------

class VDP_objectCollection(PropertyGroup):
    #name: StringProperty() -> Instantiated by default
    obj_type: StringProperty()
    obj_id: IntProperty()


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    VDP_OT_actions,
    VDP_UL_wheels,
    VDP_PT_AddRig,
    VDP_objectCollection,
    RigOptionsProperties,
    RigOptions
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    # Custom scene properties
    bpy.types.Scene.vdp = CollectionProperty(type=VDP_objectCollection)
    bpy.types.Scene.vdp_index = IntProperty()
    bpy.types.Scene.rigOptionsPropertiesReference_ = PointerProperty(type=RigOptionsProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.vdp
    del bpy.types.Scene.vdp_index
    del bpy.types.Scene.rigOptionsPropertiesReference_


if __name__ == "__main__":
    register()



# import bpy
# from bpy.types import Panel, Operator, PropertyGroup, UIList
# from bpy.props import EnumProperty, PointerProperty, StringProperty, FloatProperty, IntProperty, FloatVectorProperty, BoolProperty, BoolVectorProperty
# from mathutils import Vector
# from bpy_extras.object_utils import AddObjectHelper, object_data_add
# from bpy.utils import register_class, unregister_class

# class VDP_OT_actions(Operator):
#     """Move items up and down, add and remove"""
#     bl_idname = "vdp.list_action"
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
#         idx = scn.vdp_index

#         try:
#             item = scn.vdp[idx]
#         except IndexError:
#             pass
#         else:
#             if self.action == 'DOWN' and idx < len(scn.vdp) - 1:
#                 item_next = scn.vdp[idx+1].name
#                 scn.vdp.move(idx, idx+1)
#                 scn.vdp_index += 1
#                 info = 'Item "%s" moved to position %d' % (item.name, scn.vdp_index + 1)
#                 self.report({'INFO'}, info)

#             elif self.action == 'UP' and idx >= 1:
#                 item_prev = scn.vdp[idx-1].name
#                 scn.vdp.move(idx, idx-1)
#                 scn.vdp_index -= 1
#                 info = 'Item "%s" moved to position %d' % (item.name, scn.vdp_index + 1)
#                 self.report({'INFO'}, info)

#             elif self.action == 'REMOVE':
#                 info = 'Item "%s" removed from list' % (scn.vdp[idx].name)
#                 scn.vdp_index -= 1
#                 scn.vdp.remove(idx)
#                 self.report({'INFO'}, info)

#         if self.action == 'ADD':
#             if context.object:
#                 item = scn.vdp.add()
#                 item.name = context.object.name
#                 item.obj_type = context.object.type
#                 item.obj_id = len(scn.vdp)
#                 scn.vdp_index = len(scn.vdp)-1
#                 info = '"%s" added to list' % (item.name)
#                 self.report({'INFO'}, info)
#             else:
#                 self.report({'INFO'}, "Nothing selected in the Viewport")
#         return {"FINISHED"}


# class VDP_UL_wheels(UIList):
#     def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
#         split = layout.split(factor=0.3)
#         split.label(text="Index: %d" % (index))
#         vdp_icon = "OUTLINER_OB_%s" % item.obj_type
#         #split.prop(item, "name", text="", emboss=False, translate=False, icon=vdp_icon)
#         split.label(text=item.name, icon=vdp_icon) # avoids renaming the item by accident

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
#     VDP_OT_actions,
#     VDP_UL_wheels,
#     RigOptionsProperties,
#     RigOptions,
#     Controls
# ]