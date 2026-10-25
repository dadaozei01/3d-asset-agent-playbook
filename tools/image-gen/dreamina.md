# AI 生成贴图：即梦（Dreamina CLI）

即梦是字节的图像生成服务，`dreamina` 是它的命令行。本机已通过 Codex 的 skill 接入（`~/.codex/skills/dreamina-cli/SKILL.md`），Claude 直接调用同一个 CLI。

自 2026-10-25 起首选 [小云雀](xiaoyunque.md)（一个会员可用 Seedream 5.0 Pro 和其他多个模型）；即梦作为备用。

## 用法

```bash
dreamina user_credit
dreamina text2image -h
dreamina text2image --model_version=5.0Pro --resolution_type=2k --ratio=1:1 --generate_num=1 --poll=90 --prompt="..."
dreamina query_result --submit_id=<id> --download_dir=<dir>
```

- 以效果为准，不为省额度选免费模型。贴图默认用 5.0Pro、1:1、1 张（2026-10-25 用户确认）。
- 分辨率按用途选：平铺贴图会重复铺开，2K 通常够用；需要直接贴满整个部件或近景特写的贴图用 4K。
- 2026-10-24 的木门案例用的是 5.0（Lite），之后的贴图应以 5.0Pro 为准重新验证提示词效果。
- 提交前告诉用户模型、分辨率、比例、数量；生成会消耗额度。
- 以 `gen_status=success` 为准，不只看退出码。保存 `submit_id`。
- 下载到独立的空目录，文件名带 `submit_id`，再按用途改名。

## 写贴图提示词

- 开头说明用途：“游戏贴图、无缝四方连续平铺纹理、正面正交视角、均匀柔光、无投影”。
- 明确风格档案的描述（见 [styles/](../../styles/)）。
- 用“无 X”列出不要的元素：描边、文字、物体、边框、木节、木板缝隙……
- 一次只生成一种材质，不要在一张图里要多种材质。

## 已知局限与后处理

| 现象 | 处理 |
|---|---|
| 说了“无缝”但实际有接缝 | 逐轴错位融合（`tools/blender/scripts/seamless.py`） |
| 带不要的元素（木节、描边） | 同行取样覆盖（`paint_out.py`），或重新生成并在提示词里禁止 |
| 颜色过饱和、偏色 | 材质里用色相/饱和度节点调整，原图不动 |
| 大块深色脏斑 | 压缩低于中位数的亮度（`flatten_darks`） |
| 生成出网格状排列（如 6 条木板） | 可以利用：把每个部件的 UV 对齐其中一格 |
