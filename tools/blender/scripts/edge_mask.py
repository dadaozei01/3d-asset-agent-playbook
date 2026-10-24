"""Object-space edge mask for box-like parts (EEVEE and Cycles).

Each part stores its half extents in obj.color (Object Info > Color); the Attribute
node could not read custom-property arrays in EEVEE (Blender 5.2). The group outputs
~1 within `Width` metres of an edge where two faces meet, 0 on flat areas.
Multiply it with a noise ramp to break it into worn chips or soft highlights.
"""
import bpy


def store_half_extents(obj):
    """Write the mesh's local half extents (before modifiers) into obj.color."""
    vs = obj.data.vertices
    hx = max(abs(v.co.x) for v in vs)
    hy = max(abs(v.co.y) for v in vs)
    hz = max(abs(v.co.z) for v in vs)
    obj.color = (hx, hy, hz, 1.0)


def build_edge_mask_group(name="EdgeMask"):
    g = bpy.data.node_groups.get(name) or bpy.data.node_groups.new(name, "ShaderNodeTree")
    g.nodes.clear()
    g.interface.clear()
    g.interface.new_socket("Width", in_out="INPUT", socket_type="NodeSocketFloat").default_value = 0.02
    g.interface.new_socket("Edge", in_out="OUTPUT", socket_type="NodeSocketFloat")
    N, L = g.nodes, g.links
    gi, go = N.new("NodeGroupInput"), N.new("NodeGroupOutput")
    tc, oi = N.new("ShaderNodeTexCoord"), N.new("ShaderNodeObjectInfo")
    ab = N.new("ShaderNodeVectorMath"); ab.operation = "ABSOLUTE"
    sub = N.new("ShaderNodeVectorMath"); sub.operation = "SUBTRACT"
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Object"], ab.inputs[0])
    L.new(oi.outputs["Color"], sub.inputs[0])
    L.new(ab.outputs[0], sub.inputs[1])
    L.new(sub.outputs[0], sep.inputs[0])

    def math(op, a=None, b=None, clamp=False):
        m = N.new("ShaderNodeMath"); m.operation = op; m.use_clamp = clamp
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                m.inputs[i].default_value = v
            else:
                L.new(v, m.inputs[i])
        return m.outputs[0]

    near = []
    for axis in "XYZ":
        d = math("DIVIDE", sep.outputs[axis], gi.outputs["Width"], clamp=True)
        near.append(math("SUBTRACT", 1.0, d))
    pair = lambda a, b: math("MULTIPLY", a, b)
    edge = math("MAXIMUM", math("MAXIMUM", pair(near[0], near[1]), pair(near[1], near[2])), pair(near[0], near[2]))
    L.new(edge, go.inputs["Edge"])
    return g
