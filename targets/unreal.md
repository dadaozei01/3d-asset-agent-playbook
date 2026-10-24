# 交付目标：Unreal Engine

> 状态：FBX 导出参数按 Blender 默认约定设置，尚未在 UE 中实测导入（2026-10-24）。实测后补充。连接与操作 UE 本身以 [ue-ai-bridge-protocol](https://github.com/dadaozei01/ue-ai-bridge-protocol) 为准。

## 模型

- 格式 FBX；一个资产一个合并网格，材质槽尽量少。
- 单位：软件里用米建模，导出时让导出器处理单位换算（Blender：`apply_unit_scale=True`，`FBX_SCALE_NONE`）。
- 原点在使用位置（门放底部中心），变换已应用。
- 平滑：按面导出平滑信息，带切线空间（Blender：`mesh_smooth_type='FACE'`，`use_tspace=True`）。
- 多个物体也可以导，UE 导入时勾选 **Combine Meshes** 合并；但交付时先在软件里合并更可控。

## 贴图

| 贴图 | UE 设置 |
|---|---|
| `_BaseColor` | sRGB 开 |
| `_Normal` | 压缩设置 Normalmap；软件导出的是 OpenGL 法线时勾选 Flip Green Channel（Blender 烘焙为 OpenGL） |
| `_ORM` | sRGB 关；压缩设置 Masks |

## 材质连法

- BaseColor → Base Color
- ORM.R → Ambient Occlusion，ORM.G → Roughness，ORM.B → Metallic
- Normal → Normal

## 命名

`SM_` 网格、`M_` 材质、`MI_` 材质实例、`T_` 贴图；后缀 `_BaseColor` / `_Normal` / `_ORM`。
