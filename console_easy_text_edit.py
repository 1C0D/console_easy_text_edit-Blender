"""
move cursor under mouse clic and selection
add ctrl x: cut
add ctrl Q: quick favorite

"""

import bpy

bl_info = {
    "name": "console easy text edit",
    "description": "Add text editing options to console",
    "author": "1C0D",
    "version": (1, 1, 0),
    "blender": (2, 80, 0),
    "location": "Console",
    "category": "Console"
}


class CONSOLE_OT_MoveCursor(bpy.types.Operator):
    """select_set_cursor"""
    bl_idname = "console.set_cursor"
    bl_label = "select_set_cursor"

    @classmethod
    def poll(cls, context):
        return context.area.type == 'CONSOLE'

    def execute(self, context):

        bpy.ops.console.select_set('INVOKE_DEFAULT')
        sc = context.space_data
        bpy.ops.console.move(type='LINE_END')
        for _ in range(sc.select_end):
            bpy.ops.console.move(type='PREVIOUS_CHARACTER')

        return {'FINISHED'}


class CONSOLE_OT_Cut(bpy.types.Operator):
    '''cut selection in console'''
    bl_idname = "console.cut"
    bl_label = "console cut"

    @classmethod
    def poll(cls, context):
        return context.area.type == 'CONSOLE'

    def execute(self, context):

        bpy.ops.console.copy()  # for the cut
        sc = context.space_data
        st, se = (sc.select_start, sc.select_end)
        for _ in range(se-st):
            bpy.ops.console.move(type='LINE_END')
            for _ in range(st):
                bpy.ops.console.move(type='PREVIOUS_CHARACTER')
            bpy.ops.console.delete(type='PREVIOUS_CHARACTER')
        sc.select_start = st
        sc.select_end = st

        return {'FINISHED'}


class CONSOLE_OT_Back_Space(bpy.types.Operator):
    '''normal backspace behaviour in console'''
    bl_idname = "console.back_space"
    bl_label = "console back space"

    @classmethod
    def poll(cls, context):
        return context.area.type == 'CONSOLE'

    def execute(self, context):

        sc = context.space_data
        st, se = (sc.select_start, sc.select_end)
        if st == se:
            bpy.ops.console.delete(type='PREVIOUS_CHARACTER')
        for _ in range(se-st):
            bpy.ops.console.move(type='LINE_END')
            for _ in range(st):
                bpy.ops.console.move(type='PREVIOUS_CHARACTER')
            bpy.ops.console.delete(type='PREVIOUS_CHARACTER')
        sc.select_start = st
        sc.select_end = st

        return {'FINISHED'}


class CONSOLE_OT_Suppr(bpy.types.Operator):
    '''normal suppr behaviour in console'''
    bl_idname = "console.suppr"
    bl_label = "console suppr"

    @classmethod
    def poll(cls, context):
        return context.area.type == 'CONSOLE'

    def execute(self, context):

        sc = context.space_data
        st, se = (sc.select_start, sc.select_end)
        if st == se:
            bpy.ops.console.delete(type='NEXT_CHARACTER')
        for _ in range(se-st):
            bpy.ops.console.move(type='LINE_END')
            for _ in range(st):
                bpy.ops.console.move(type='PREVIOUS_CHARACTER')
            bpy.ops.console.delete(type='PREVIOUS_CHARACTER')
        sc.select_start = st
        sc.select_end = st

        return {'FINISHED'}


class CONSOLE_OT_Select_Line(bpy.types.Operator):
    """select line"""
    bl_idname = "console.select_line"
    bl_label = "select whole line"

    @classmethod
    def poll(cls, context):
        return context.area.type == 'CONSOLE'

    def execute(self, context):

        sc = context.space_data
        line_object = sc.history[-1]
        if line_object:
            line = line_object.body
            lenght = len(line)
            st = sc.select_start = 0
            se = sc.select_end = lenght

        return {'FINISHED'}


addon_keymaps = []


def register():
    bpy.utils.register_class(CONSOLE_OT_MoveCursor)
    bpy.utils.register_class(CONSOLE_OT_Cut)
    bpy.utils.register_class(CONSOLE_OT_Back_Space)
    bpy.utils.register_class(CONSOLE_OT_Suppr)
    bpy.utils.register_class(CONSOLE_OT_Select_Line)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is not None:
        km = kc.keymaps.new(name='Console', space_type='CONSOLE')
        kmi = km.keymap_items.new("console.set_cursor", "LEFTMOUSE", "PRESS")
        kmi = km.keymap_items.new("console.cut", "X", "PRESS", ctrl=True)
        kmi = km.keymap_items.new("console.back_space", "BACK_SPACE", "PRESS")
        kmi = km.keymap_items.new("console.suppr", "DEL", "PRESS")
        kmi = km.keymap_items.new(
            "console.select_line", "A", "PRESS", ctrl=True)

        # quick favorite
        kmi = km.keymap_items.new("wm.call_menu", "Q", "PRESS", ctrl=True)
        kmi.properties.name = "SCREEN_MT_user_menu"
        addon_keymaps.append((km, kmi))


def unregister():
    bpy.utils.unregister_class(CONSOLE_OT_MoveCursor)
    bpy.utils.unregister_class(CONSOLE_OT_Cut)
    bpy.utils.unregister_class(CONSOLE_OT_Back_Space)
    bpy.utils.unregister_class(CONSOLE_OT_Suppr)
    bpy.utils.unregister_class(CONSOLE_OT_Select_Line)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is not None:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)


if __name__ == "__main__":
    register()

    # test call
#    bpy.ops.object.simpl_operator()
