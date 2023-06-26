import bpy

from bpy.props import (IntProperty,
                       BoolProperty,
                       StringProperty,
                       CollectionProperty,
                       PointerProperty)

from bpy.types import (Operator,
                       Panel,
                       PropertyGroup,
                       UIList)

# -------------------------------------------------------------------
#   Operators
# -------------------------------------------------------------------

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
    

class VDS_OT_addViewportSelection(Operator):
    """Add all items currently selected in the viewport"""
    bl_idname = "vds.add_viewport_selection"
    bl_label = "Add Viewport Selection to List"
    bl_description = "Add all items currently selected in the viewport"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scn = context.scene
        selected_objs = context.selected_objects
        if selected_objs:
            new_objs = []
            for i in selected_objs:
                item = scn.vds.add()
                item.name = i.name
                item.obj = i
                new_objs.append(item.name)
            info = ', '.join(map(str, new_objs))
            self.report({'INFO'}, 'Added: "%s"' % (info))
        else:
            self.report({'INFO'}, "Nothing selected in the Viewport")
        return{'FINISHED'}

    

# -------------------------------------------------------------------
#   Drawing
# -------------------------------------------------------------------

class VDS_UL_items(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        obj = item.obj
        vds_icon = "OUTLINER_OB_%s" % obj.type
        split = layout.split(factor=0.3)
        split.label(text="Index: %d" % (index))
        split.prop(obj, "name", text="", emboss=False, translate=False, icon=vds_icon)
            
    def invoke(self, context, event):
        pass   

class VDS_PT_objectList(Panel):
    """Adds a vds panel to the VIEW_3D"""
    bl_idname = 'TEXT_PT_my_panel'
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Custom Object List Demo"

    def draw(self, context):
        layout = self.layout
        scn = bpy.context.scene

        rows = 2
        row = layout.row()
        row.template_list("VDS_UL_items", "", scn, "vds", scn, "vds_index", rows=rows)

        col = row.column(align=True)
        col.operator("vds.list_action", icon='ADD', text="").action = 'ADD'
        col.operator("vds.list_action", icon='REMOVE', text="").action = 'REMOVE'
        col.separator()
        col.operator("vds.list_action", icon='TRIA_UP', text="").action = 'UP'
        col.operator("vds.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'
        
        row = layout.row()
        col = row.column(align=True)
        row = col.row(align=True)
        row.operator("vds.add_viewport_selection", icon="HAND") #LINENUMBERS_OFF, ANIM



# -------------------------------------------------------------------
#   Collection
# -------------------------------------------------------------------

class VDS_PG_objectCollection(PropertyGroup):
    #name: StringProperty() -> Instantiated by default
    obj: PointerProperty(
        name="Object",
        type=bpy.types.Object)
    

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    VDS_OT_actions,
    # VDS_OT_addViewportSelection,
    VDS_UL_items,
    VDS_PT_objectList,
    VDS_PG_objectCollection,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    
    # Custom scene properties
    bpy.types.Scene.vds = CollectionProperty(type=VDS_PG_objectCollection)
    bpy.types.Scene.vds_index = IntProperty()
    

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
    del bpy.types.Scene.vds
    del bpy.types.Scene.vds_index


if __name__ == "__main__":
    register()