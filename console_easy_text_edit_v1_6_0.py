"""
move cursor under mouse clic and selection
ctrl x, ctrl v, suppr, backspace working even on selections
undo Ctrl+Z
redo shift+ctrl+Z
ctrl A: select line
shift+right/left arrow translate selection
add ctrl Q: quick favorite

"""

import bpy

bl_info = {
    "name": "console easy text edit",
    "description": "Add text editing options to console",
    "author": "1C0D",
    "version": (1, 6, 0),
    "blender": (2, 93, 0),
    "location": "Console",
    "category": "Console"
}

line_list = []
st_list = []
se_list = []
cursor_pos_list = []
redo_line = []
redo_st = []
redo_se = []
redo_cursor_pos = []

class CONSOLE_OT_MoveCursor(bpy.types.Operator):
    """select_set_cursor"""
    bl_idname = "console.set_easy_cursor"
    bl_label = "select set cursor"

    @classmethod
    def poll(cls, context):

        return context.area.type == 'CONSOLE'

    def execute(self, context):

        bpy.ops.console.select_set('INVOKE_DEFAULT')
        sc = context.space_data
        se =  sc.select_end
        line_object = sc.history[-1]
        if line_object:
            line = line_object.body
            length = len(line)      
        if se < length+3:
            sc = context.space_data
            bpy.ops.console.move(type='LINE_END')
            for _ in range(se):
                bpy.ops.console.move(type='PREVIOUS_CHARACTER')

        return {'FINISHED'}


class CONSOLE_OT_Cut(bpy.types.Operator):
    '''cut selection in console'''
    bl_idname = "console.easy_cut"
    bl_label = "console cut"

    @classmethod
    def poll(cls, context):
        return context.area.type == 'CONSOLE'

    def execute(self, context):

        bpy.ops.console.copy()  # for the paste
        sc = context.space_data
        st, se = (sc.select_start, sc.select_end)
        # for undo
        line_object = sc.history[-1]
        if line_object:
            line = line_object.body
            current = line_object.current_character
            cursor_pos = len(line)-current

        bpy.ops.console.move(type='LINE_END')
        for _ in range(st):
            bpy.ops.console.move(type='PREVIOUS_CHARACTER')
        for _ in range(se-st):
            bpy.ops.console.delete(type='PREVIOUS_CHARACTER')
        sc.select_start = st
        sc.select_end = st
        # for undo
        line_list.append(line)
        st_list.append(st)
        se_list.append(se)
        cursor_pos_list.append(cursor_pos)

        return {'FINISHED'}


class CONSOLE_OT_Paste(bpy.types.Operator):
    '''paste selection in console over selection'''
    bl_idname = "console.easy_paste"
    bl_label = "console paste"

    @classmethod
    def poll(cls, context):
        return context.area.type == 'CONSOLE'

    def execute(self, context):

        sc = context.space_data
        st, se = (sc.select_start, sc.select_end)
        line_object = sc.history[-1]
        if line_object:
            line = line_object.body
            current = line_object.current_character
            cursor_pos = len(line)-current
        if st==se:
            bpy.ops.console.paste()
        else:
            bpy.ops.console.move(type='LINE_END')
            for _ in range(st):
                bpy.ops.console.move(type='PREVIOUS_CHARACTER')
            for _ in range(se-st):
                bpy.ops.console.delete(type='PREVIOUS_CHARACTER')
            sc.select_start = se
            sc.select_end = se
            bpy.ops.console.paste()

        line_list.append(line)
        st_list.append(st)
        se_list.append(se)
        cursor_pos_list.append(cursor_pos)

        return {'FINISHED'}


class CONSOLE_OT_Undo(bpy.types.Operator):
    """local undo"""
    bl_idname = "console.easy_undo"
    bl_label = "console undo"

    @classmethod
    def poll(cls, context):
        return context.area.type == 'CONSOLE'

    def execute(self, context):

        if not line_list:
            return {'FINISHED'}

        sc = context.space_data
        st1, se1 = (sc.select_start, sc.select_end)

        line_object = sc.history[-1]
        if line_object:
            line1 = line_object.body
            lenght = len(line1)
            st1 = sc.select_start = 0
            se1 = sc.select_end = lenght

        bpy.ops.console.move(type='LINE_END')
        for _ in range(lenght):
            bpy.ops.console.delete(type='PREVIOUS_CHARACTER')

        bpy.ops.console.insert(text=(line_list[-1]))
        sc.select_start = st_list[-1]
        sc.select_end = se_list[-1]
        for _ in range(cursor_pos_list[-1]):
            bpy.ops.console.move(type='PREVIOUS_CHARACTER')

        if line_list:
            redo_line.append(line_list[-1])
            redo_st.append(st_list[-1])
            redo_se.append(se_list[-1])
            redo_cursor_pos.append(cursor_pos_list[-1])

        line_list.pop()
        st_list.pop()
        se_list.pop()
        cursor_pos_list.pop()

        return {'FINISHED'}


class CONSOLE_OT_Redo(bpy.types.Operator):
    """local undo"""
    bl_idname = "console.easy_redo"
    bl_label = "console redo"

    @classmethod
    def poll(cls, context):
        return context.area.type == 'CONSOLE'

    def execute(self, context):

        if not redo_line:
            return {'FINISHED'}

        sc = context.space_data
        st1, se1 = (sc.select_start, sc.select_end)

        line_object = sc.history[-1]
        if line_object:
            line1 = line_object.body
            lenght = len(line1)
            st1 = sc.select_start = 0
            se1 = sc.select_end = lenght

        bpy.ops.console.move(type='LINE_END')
        for _ in range(lenght):
            bpy.ops.console.delete(type='PREVIOUS_CHARACTER')

        bpy.ops.console.insert(text=(redo_line[-1]))
        sc.select_start = redo_st[-1]
        sc.select_end = redo_se[-1]
        for _ in range(redo_cursor_pos[-1]):
            bpy.ops.console.move(type='PREVIOUS_CHARACTER')

        line_list.append(redo_line[-1])
        st_list.append(redo_st[-1])
        se_list.append(redo_se[-1])
        cursor_pos_list.append(redo_cursor_pos[-1])

        redo_line.pop()
        redo_st.pop()
        redo_se.pop()
        redo_cursor_pos.pop()

        return {'FINISHED'}


class CONSOLE_OT_Back_Space(bpy.types.Operator):
    '''normal backspace behaviour in console'''
    bl_idname = "console.back_easy_space"
    bl_label = "console back space"

    @classmethod
    def poll(cls, context):
        return context.area.type == 'CONSOLE'

    def execute(self, context):
                
        global line_list, st_list, se_list, cursor_pos_list

        sc = context.space_data
        st, se = (sc.select_start, sc.select_end)
        line_object = sc.history[-1]
        line = line_object.body
        if not line:
            return {'CANCELLED'}
        current = line_object.current_character
        length = len(line)
        cursor_pos = len(line)-current
        if se > length+3: #deselect
            st = se = current
        if st == se:
            bpy.ops.console.delete(type='PREVIOUS_CHARACTER')
        else:
            bpy.ops.console.move(type='LINE_END')
            for _ in range(st):
                bpy.ops.console.move(type='PREVIOUS_CHARACTER')
            for _ in range(se-st):
                bpy.ops.console.delete(type='PREVIOUS_CHARACTER')

        sc.select_start = st
        sc.select_end = st

        line_list.append(line)
        st_list.append(st)
        se_list.append(se)
        cursor_pos_list.append(cursor_pos)

        return {'FINISHED'}


class CONSOLE_OT_Suppr(bpy.types.Operator):
    '''normal suppr behaviour in console'''
    bl_idname = "console.easy_suppr"
    bl_label = "console suppr"

    @classmethod
    def poll(cls, context):
        return context.area.type == 'CONSOLE'

    def execute(self, context):

        sc = context.space_data
        st, se = (sc.select_start, sc.select_end)
        line_object = sc.history[-1]
        line = line_object.body
        if not line:
            return {'CANCELLED'}        
        length = len(line)
        current = line_object.current_character
        cursor_pos = len(line)-current
        if se > length+3: #deselect
            current = line_object.current_character
            st = se = current
        if st == se:
            bpy.ops.console.delete(type='NEXT_CHARACTER')
        else:
            bpy.ops.console.move(type='LINE_END')
            for _ in range(st):
                bpy.ops.console.move(type='PREVIOUS_CHARACTER')
            for _ in range(se-st):
                bpy.ops.console.delete(type='PREVIOUS_CHARACTER')

        sc.select_start = st
        sc.select_end = st

        line_list.append(line)
        st_list.append(st)
        se_list.append(se)
        cursor_pos_list.append(cursor_pos)

        return {'FINISHED'}


class CONSOLE_OT_Select_Line(bpy.types.Operator):
    """select line"""
    bl_idname = "console.easy_select_line"
    bl_label = "select whole line"

    @classmethod
    def poll(cls, context):
        return context.area.type == 'CONSOLE'

    def execute(self, context):

        sc = context.space_data
        line_object = sc.history[-1]
        if line_object:
            line = line_object.body
            length = len(line)
            st = sc.select_start = 0
            se = sc.select_end = length

        return {'FINISHED'}


class CONSOLE_OT_Insert(bpy.types.Operator):
    """insert"""
    bl_idname = "console.easy_insert"
    bl_label = "console easy insert"

    @classmethod
    def poll(cls, context):
        return context.area.type == 'CONSOLE'

    def execute(self, context):

        sc = context.space_data
        st, se = (sc.select_start, sc.select_end)
        line_object = sc.history[-1]
        if line_object:
            line = line_object.body
            current = line_object.current_character
            cursor_pos = len(line)-current

        if st == se:
            bpy.ops.console.insert('INVOKE_DEFAULT')
        else:
            bpy.ops.console.move(type='LINE_END')
            for _ in range(st):
                bpy.ops.console.move(type='PREVIOUS_CHARACTER')
            for _ in range(se-st):
                bpy.ops.console.delete(type='PREVIOUS_CHARACTER')
            sc.select_start = st
            sc.select_end = st
            bpy.ops.console.insert('INVOKE_DEFAULT')

        line_list.append(line)
        st_list.append(st)
        se_list.append(se)
        cursor_pos_list.append(cursor_pos)

        return {'PASS_THROUGH'}

# class CONSOLE_OT_Translate(bpy.types.Operator): #need to do redo
    # """insert"""
    # bl_idname = "console.easy_translate"
    # bl_label = "console easy translate"
    
    # direction:bpy.props.StringProperty(default='back')

    # @classmethod
    # def poll(cls, context):
        # return context.area.type == 'CONSOLE'

    # def execute(self, context):
        # forward
        # sc = context.space_data
        # st, se = (sc.select_start, sc.select_end)

        # bpy.ops.console.easy_cut()
        # if self.direction=='forward':
            # bpy.ops.console.move(type='NEXT_CHARACTER')
        # else:
            # bpy.ops.console.move(type='PREVIOUS_CHARACTER')
        # bpy.ops.console.easy_paste()
        # if self.direction=='forward':
            # sc.select_start = st-1
            # sc.select_end = se-1
        # else:
            # sc.select_start = st+1
            # sc.select_end = se+1

        # return {'PASS_THROUGH'}



def get_area(context, area_type):
    for window in context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type != area_type:
                continue
            for region in area.regions:
                if region.type != 'WINDOW':
                    continue
                return window, screen, area, region
                
def override(context, *param):
    override = {'window': param[0], 'screen': param[1], 'area': param[2], 'region': param[3]}
    return {
        **context.copy(),
        **override,
    }

class TEXT_OT_Paste_console_to_text_editor(bpy.types.Operator):
    """past to text editor"""
    bl_idname = "text.paste_console_to_text_editor"
    bl_label = "paste console to text editor"

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):

        sel = context.window_manager.clipboard
        
        if ("C." or "D.") in sel:
            sel = sel.replace("C.", "bpy.context.").replace("D.", "bpy.data.")
            print(sel)

        text = context.space_data.text
        if text:
            text.write(text=sel)

        return {'FINISHED'}
        

        
def easy_panel(self, context):
    self.layout.separator()
    self.layout.operator("console.easy_select_line", text="Select Line")
#    self.layout.operator("console.easy_translate", text="Translate Right").direction = "forward"
#    self.layout.operator("console.easy_translate", text="Translate Left")
    self.layout.operator("console.easy_cut", text="Cut") 

addon_keymaps = []

classes=(CONSOLE_OT_MoveCursor, CONSOLE_OT_Cut, CONSOLE_OT_Paste, 
            CONSOLE_OT_Back_Space, CONSOLE_OT_Suppr, CONSOLE_OT_Insert, 
                CONSOLE_OT_Undo, CONSOLE_OT_Select_Line, CONSOLE_OT_Redo,
                    TEXT_OT_Paste_console_to_text_editor,
#                    CONSOLE_OT_Translate
                    )

def register():
    
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.CONSOLE_MT_console.prepend(easy_panel)
    bpy.types.CONSOLE_MT_context_menu.prepend(easy_panel)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is not None:
        km = kc.keymaps.new(name='Console', space_type='CONSOLE')
        kmi = km.keymap_items.new(
            "console.set_easy_cursor", "LEFTMOUSE", "PRESS")
        addon_keymaps.append((km, kmi))
#        kmi = km.keymap_items.new(
#            "console.easy_translate", "RIGHT_ARROW", "PRESS", shift=True)
#        kmi.properties.direction = "forward"    
#        addon_keymaps.append((km, kmi))
#        kmi = km.keymap_items.new(
#            "console.easy_translate", "LEFT_ARROW", "PRESS", shift=True)
#        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("console.easy_cut", "X", "PRESS", ctrl=True)
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(
            "console.easy_paste", "V", "PRESS", ctrl=True)
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(
            "console.back_easy_space", "BACK_SPACE", "PRESS")
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("console.easy_suppr", "DEL", "PRESS")
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(
            "console.easy_select_line", "A", "PRESS", ctrl=True)
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(
            "console.easy_insert", 'TEXTINPUT', 'ANY', any=True)
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("console.easy_undo", "Z", "PRESS", ctrl=True)
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(
            "console.easy_redo", "Z", "PRESS", shift=True, ctrl=True)
        addon_keymaps.append((km, kmi))
        # quick favorite
        kmi = km.keymap_items.new("wm.call_menu", "Q", "PRESS", ctrl=True)
        kmi.properties.name = "SCREEN_MT_user_menu"
        addon_keymaps.append((km, kmi))
        # copy to text editor
        km = kc.keymaps.new(name='Text', space_type='TEXT_EDITOR')
        kmi = km.keymap_items.new(
            "text.paste_console_to_text_editor", "V", "PRESS", ctrl=True, shift=True)
        addon_keymaps.append((km, kmi))



def unregister():

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is not None:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)

    addon_keymaps.clear()
            
    bpy.types.CONSOLE_MT_console.remove(easy_panel)
    bpy.types.CONSOLE_MT_context_menu.remove(easy_panel)

    for c in classes:
        bpy.utils.unregister_class(c)
