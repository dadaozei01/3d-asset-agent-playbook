# 软件：Blender

实测：Blender 5.2.2 LTS，macOS Apple Silicon（M1 Max），MCP for Blender 插件（协议 14），2026-10-24。

## 连接

- MCP 服务名 `blender`。先 `get_addon_status`（版本、插件是否需要更新），再 `get_scene_info`。
- `execute_blender_code` 在用户正在运行的 Blender 里执行 Python（bpy、bmesh、mathutils、numpy）。
- `look` 看图：`mode=camera` 看相机，`mode=angles` + `views` 看指定方向（`[x,y,z]` 是从目标指向眼睛的方向，`[0,1,0.2]` 即从背面看），`shading=rendered` 看最终效果。

## 常用能力

| 能力 | 做法 | 实测 |
|---|---|---|
| 几何 | bmesh 建立盒体，倒角修改器 | ✅ |
| 材质 | 按类型查找节点（`n.type=="BSDF_PRINCIPLED"`），节点名可能被本地化 | ✅ |
| 看图 | `look`，EEVEE 实时 | ✅ |
| UV | 多物体编辑模式下 `smart_project` + `pack_islands` 共用一张贴图 | ✅ |
| 烘焙 | Cycles + Metal GPU，`bpy.ops.object.bake` | ✅ |
| 导出 | `bpy.ops.export_scene.fbx` | ✅（未在 UE 实测导入） |

## 坑

- **自定义属性读不到**：EEVEE 下 Attribute 节点（Object 类型）读不到物体的浮点数组自定义属性，结果为 0。改用 `obj.color` 存数据，节点里用 Object Info → Color 读。
- **半透明贴花在背光面消失**：带光照的 Principled 半透明片在没有直射光的一面和底下表面亮度接近，看起来就没了。脏污类贴花用两个 Transparent BSDF 混合（白色和暗色调），做成不受光照影响的乘法变暗。
- **UV 层名**：bmesh 的 `loops.layers.uv.verify()` 新建的层叫 `Float2` 而不是 `UVMap`。新增 UV 层前，把材质里的 UV Map 节点固定到具体层名。
- **长时间烘焙超时**：4K 烘焙会让 MCP 返回 “No data received”，但 Blender 仍在后台继续。不要重发，稍后查询贴图是否已生成。
- **平铺 UV 默认名**：上一条导致的连锁问题，展开烘焙 UV 后要把渲染用 UV 设回原来那层。
- **另存会生成 `.blend1`**：每次保存都会留下上一版备份。交付前删除，或在偏好设置里把保存版本设为 0。
- **烘焙时隐藏原件**：副本与原件重叠时，AO 会被重合面挡住。烘焙前把原件 `hide_render`。
- **`bpy.ops.object.join` 前确认选择**：只选要合并的物体，并检查活动物体。

## 可复用脚本

在 Blender 里 `exec(open(path).read())` 或复制函数使用。

| 脚本 | 作用 |
|---|---|
| [scripts/texture_ops.py](scripts/texture_ops.py) | 贴图无缝化、去除元素、压暗斑（纯 numpy，与软件无关）+ Blender 读写辅助 |
| [scripts/edge_mask.py](scripts/edge_mask.py) | 盒体边缘遮罩节点组，用于边角磨损 |
| [scripts/bake_pbr.py](scripts/bake_pbr.py) | 一组物体烘焙 BaseColor / Roughness / Normal / AO / Metallic / Position，合成 ORM |
| [scripts/dust_from_position.py](scripts/dust_from_position.py) | 用 Position 图把连接件周围的灰尘烘进 BaseColor 和 AO |
