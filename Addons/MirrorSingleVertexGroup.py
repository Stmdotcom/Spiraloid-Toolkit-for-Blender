bl_info = {
    'name': 'Mirror A Vertex Group',
    'description': 'Mirror and replace the contents of a single vertex group with another.',
    'version': (1, 0),
    'blender': (2, 93, 0),
    'category': 'Animation',
    'location': 'Mesh > Vertex Group Menu',
}

import bpy
import datetime

def copy_mirror_weight(axis, way, left_side, right_side, tolerance):
    start = (datetime.datetime.now())
    print('Start Vertex Group Mirror')
    bpy.ops.object.mode_set(mode='OBJECT')

    ori_side = left_side
    dest_side = right_side

    obj = bpy.context.active_object
    mesh = bpy.data.objects[obj.name].data.name

    x_multiply = 1
    y_multiply = 1
    z_multiply = 1

    if axis == 'X':
        axis_num = 0
        x_multiply = -1
    if axis == 'Y':
        axis_num = 1
        y_multiply = -1
    if axis == 'Z':
        axis_num = 2
        z_multiply = -1

    ## create the dict for the groups attache the index to the name
    DictGroup = {} ##ask the index it will give you the name
    DictGroupINV = {} ## ask the name, it will give you the index
    i=0
    for group in bpy.context.active_object.vertex_groups:
        DictGroup[i] = group.name
        i += 1

    for item in DictGroup:
        DictGroupINV[DictGroup[item]] = item

    #for each vertices of the mesh
    DictVertexOri = {}
    DictVertexDest = {}
    DictMirror = {}
    for vertex in bpy.data.meshes[mesh].vertices:
        #create the dicts for the good side
        if (vertex.co[axis_num] > tolerance and way == 'normal') or (vertex.co[axis_num] < -tolerance and way == 'reverse'): #compare with the tolerance and position of the origin
            DictVertexOri[vertex.index] = vertex.co

        #create the dicts for the mirror side
        if (vertex.co[axis_num] < tolerance and way == 'normal') or (vertex.co[axis_num] > -tolerance and way == 'reverse'): #compare with the tolerance and position of the origin
            DictVertexDest[vertex.index] = vertex.co

    for vertex in DictVertexOri:
        vertexCoXOri = DictVertexOri[vertex][0]
        vertexCoYOri = DictVertexOri[vertex][1]
        vertexCoZOri = DictVertexOri[vertex][2]

        for vertexMirror in DictVertexDest: #check the coordinates of each axis, the multiply is inversing the mirror axes from -x.xxxx to x.xxxx so that the side doesn't matter
            if vertexCoXOri-tolerance<DictVertexDest[vertexMirror][0] * x_multiply<vertexCoXOri+tolerance:
                if vertexCoYOri-tolerance<DictVertexDest[vertexMirror][1] * y_multiply<vertexCoYOri+tolerance:
                    if vertexCoZOri-tolerance<DictVertexDest[vertexMirror][2] * z_multiply<vertexCoZOri+tolerance:
                        DictMirror[vertex]=vertexMirror

    for vertex in DictMirror:
        myGroupVertex = {}
        myMirrorGroupVertex = {}
        for groups in bpy.data.meshes[mesh].vertices[vertex].groups:
            myGroupVertex[groups.group] = groups.weight #create a dictionary nameGroup = weight

            for OneGroup in myGroupVertex: #create a new dictionary with the name mirror
                if obj.vertex_groups[OneGroup].name.find(ori_side) > -1:
                    mirror_normal_group_name = obj.vertex_groups[OneGroup].name.replace(ori_side,dest_side)
                    if mirror_normal_group_name in DictGroupINV:
                        myMirrorGroupVertex[DictGroupINV[mirror_normal_group_name]] = myGroupVertex[OneGroup]
                    else:
                        #if this group doesn't exist yet add it to the group and the dictionnary
                        length = len(DictGroup)
                        bpy.context.active_object.vertex_groups.new(name=mirror_normal_group_name)
                        DictGroup[length] = mirror_normal_group_name
                        DictGroupINV[mirror_normal_group_name]=length


                if obj.vertex_groups[OneGroup].name.find(dest_side) > -1:
                    mirror_normal_group_name = obj.vertex_groups[OneGroup].name.replace(dest_side,ori_side)
                    if mirror_normal_group_name in DictGroupINV:
                        myMirrorGroupVertex[DictGroupINV[mirror_normal_group_name]] = myGroupVertex[OneGroup]
                    else:
                        #if this group doesn't exist yet add it to the group and the dictionnary
                        length = len(DictGroup)
                        bpy.context.active_object.vertex_groups.new(name=mirror_normal_group_name)
                        DictGroup[length] = mirror_normal_group_name
                        DictGroupINV[mirror_normal_group_name] = length

        ## only process if there has been a match vertex group found
        if len(myMirrorGroupVertex) > 0:
            ## Preform the mirroring
            for OneGroupVertex in myMirrorGroupVertex.keys():
                obj.vertex_groups[DictGroup[OneGroupVertex]].remove([DictMirror[vertex]])
                obj.vertex_groups[DictGroup[OneGroupVertex]].add([DictMirror[vertex]], myMirrorGroupVertex[OneGroupVertex],'REPLACE')

    print('End Vertex Group Mirror')
    end = (datetime.datetime.now())
    timing = end - start
    print(timing)
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')

class BR_OT_mirror_a_vertex_group_dialog(bpy.types.Operator):
    """Mirror A Vertex group"""
    bl_idname = "object.mirror_a_vertex_group"
    bl_label = "Mirror A Vertex Group"
    bl_options = {'REGISTER', 'UNDO'}

    enum_axis: bpy.props.EnumProperty(name="Mirror Axis?", default='X',
        items = [('Z', 'Z axis', 'Mirror on Z axis'),('Y', 'Y axis', 'Mirror on Y axis'), ('X', 'X axis', 'Mirror on X axis')])

    left_side: bpy.props.StringProperty(name="Left Vertex Group", default="LEFT_GROUP_NAME")

    right_side: bpy.props.StringProperty(name="Right Vertex Group", default="RIGHT_GROUP_NAME")

    enum_way: bpy.props.EnumProperty(name="Mirror Direction?", default='normal',
        items = [('reverse', 'Right (-) to Left (+)', 'Mirror weights from right side to left side'), ('normal', 'Left (+) to Right (-)', 'Mirror weights from left side to right side')])

    tolerance: bpy.props.FloatProperty(name="Tolerance", min=0, max=100, precision=3, default=0.001)

    def execute(self, context):
        copy_mirror_weight(self.enum_axis, self.enum_way, self.left_side, self.right_side, self.tolerance)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

def menu_draw(self, context):
    self.layout.separator()
    self.layout.operator(BR_OT_mirror_a_vertex_group_dialog.bl_idname, text="Mirror a vertex group", icon='ARROW_LEFTRIGHT')

def register():
    bpy.utils.register_class(BR_OT_mirror_a_vertex_group_dialog)
    bpy.types.MESH_MT_vertex_group_context_menu.append(menu_draw)

def unregister():
    bpy.utils.unregister_class(BR_OT_mirror_a_vertex_group_dialog)
    bpy.types.MESH_MT_vertex_group_context_menu.remove(menu_draw)

if __name__ == "__main__":
    register()
