# 3D Asset Agent Playbook

AI Agent 通过 MCP 操作 3D 软件制作模型时的通用思路。不绑定软件（Blender、Maya、3ds Max、Houdini、C4D、UE 编辑器……），不绑定风格（写实、风格化、低多边形、硬表面……），也不绑定交付平台。

这里写的是目标、判断标准和踩过的坑，不是固定步骤。**文档是默认值，不是上限**：Agent 有更好的方案时应坚持自己的判断，说清楚理由，然后去做。

## 给 Agent 的入口

> 先读 [docs/principles.md](docs/principles.md)。按 [docs/workflow](docs/workflow/) 的阶段推进，每个阶段对照“做对了的标准”自查并看图验证。具体软件的用法与坑看 [tools/](tools/)，风格看 [styles/](styles/)，交付规格看 [targets/](targets/)。与用户偏好冲突时以用户为准；与文档冲突而你有更好的方案时，说明理由后按更好的做。

## 目录

- [核心原则](docs/principles.md)
- 制作阶段
  1. [需求与参考](docs/workflow/01-brief.md)
  2. [大形与比例](docs/workflow/02-blockout.md)
  3. [建模与细节](docs/workflow/03-modeling.md)
  4. [材质与贴图](docs/workflow/04-materials.md)
  5. [UV 与烘焙](docs/workflow/05-uv-bake.md)
  6. [交付与导出](docs/workflow/06-delivery.md)
  7. [验收](docs/workflow/07-review.md)
- 风格档案：[Supercell 风格化](styles/supercell-stylized.md) · [写实 PBR](styles/realistic-pbr.md) · [新建模板](styles/_template.md)
- 软件与工具：[Blender](tools/blender/README.md) · [AI 生成贴图：小云雀（首选，多模型）](tools/image-gen/xiaoyunque.md) · [即梦 dreamina（备用）](tools/image-gen/dreamina.md) · [接入新软件模板](tools/_template.md)
- 交付目标：[Unreal Engine](targets/unreal.md) · [新建模板](targets/_template.md)
- 案例：[2026-10-24 带金属边的木门](cases/2026-10-24-wooden-door.md)
- 接入：[Claude Skill](integrations/claude-skill/SKILL.md) · [Codex / 其他 Agent 的 AGENTS.md 片段](integrations/AGENTS.snippet.md)

## 相关仓库

- [ue-ai-bridge-protocol](https://github.com/dadaozei01/ue-ai-bridge-protocol)：连接与操作 UE 的规范。资产导入 UE 之后的操作以它为准。

## 验证范围

- 2026-10-24，macOS Apple Silicon（M1 Max），Blender 5.2.2 + MCP for Blender：完整走通从参考图到 PBR 烘焙、合并导出 FBX 的流程（见案例）。FBX 尚未在 UE 中实测导入。
- 其他软件的 tools/ 文档为空白模板，首次接入时按实测补充，不按经验推定兼容。

维护检查：`python3 -m unittest discover -s tests -v`（需要 numpy）。只验证与软件无关的贴图处理函数，不证明实时连接或视觉效果。

阅读本仓库不会赋予任何软件或账号的操作权限。生成贴图、调用付费接口、覆盖用户文件前仍需按各自规则确认。
