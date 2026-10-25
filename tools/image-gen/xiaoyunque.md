# AI 生成贴图：小云雀（Pippit CLI）

小云雀是剪映团队（字节）的创作平台，海外版叫 Pippit。官方 CLI `pippit-tool-cli` 可以用一个会员调用多个图片模型，并支持参考图编辑。即梦 CLI 继续保留作为备用，见 [dreamina.md](dreamina.md)。

实测：2026-10-25，macOS Apple Silicon，CLI v1.0.47，会员账号。

## 安装

需要 Node.js 16+。本机没有 Homebrew 时，用 nodejs.org 的免安装包解压到 `~/.local`（核对 SHASUMS256），并把 `node` / `npm` / `npx` 链接到 `~/.local/bin`，无需管理员权限。

```bash
npm config set prefix "$HOME/.local"
PIPPIT_CLI_DISABLE_TELEMETRY=1 npx -y @pippit-dev/cli@latest install
pippit-tool-cli login
pippit-tool-cli status
```

- 安装脚本会从 GitHub Release 下载程序本体并校验 SHA256，同时把 3 个 skill（`xyq-skill`、`xyq-short-drama-skill`、`xyq-marketing-skill`）装进 `~/.agents/skills`，并链接给 Claude Code 和 Codex。
- `PIPPIT_CLI_DISABLE_TELEMETRY=1` 关闭安装统计上报。
- `login` 会打开浏览器授权，授权有效期约一年。

## 生图

```bash
pippit-tool-cli get-credit-balance
pippit-tool-cli model list --type image
pippit-tool-cli model describe "Seedream 5.0 Pro" --type image
pippit-tool-cli generate-image --model "Seedream 5.0 Pro" --prompt "..." --ratio 6 --resolution 2K
pippit-tool-cli generate-image --model "智能图片V2.5 Pro" --prompt "..." --image ./ref.png
pippit-tool-cli query-result --thread-id <id> --run-id <id>
```

- `--model` 用 `model list` 返回的完整名称，带空格要加引号。
- `--ratio` 传数字：`6` 是 1:1，`2` 是 16:9，`0` 是自适应（以 `model describe` 的 `option_labels` 为准）。
- `--image` 传参考图，可以重复多次。适合把生成的贴图喂回去，让它去掉木节、改成无缝。
- 生成是异步的：保存返回的 `thread_id`、`run_id`，用 `query-result` 取回并下载。

## 可用图片模型（2026-10-25，会员账号）

| 模型名 | 分辨率 | 说明 |
|---|---|---|
| Seedream 5.0 Pro | 1K / 1.5K / 2K / 4K | 和即梦 5.0Pro 同一模型；支持交互式编辑 |
| Seedream 5.0 Flash | — | 速度优先 |
| 智能图片V2.5 Pro | 1K / 2K / 4K，推理强度 low–max | 官方描述“image 2.5 水准”，精准生成与编辑 |
| 智能图片V2.5 Fast | — | 速度优先 |
| 智能图片V2 | — | |
| 旗舰生图模型 V2-Pro | 1K / 2K / 4K | 即 Nano Banana Pro（用户 2026-10-25 确认）；擅长图片编辑、还原复杂场景 |
| 旗舰生图模型 V2-Flash | — | |
| 美学模型 8.2 | 1K / 2K | 悠船 v8.2，适合影视、视觉概念 |
| Anycook影视版 | — | |

模型列表由服务端按账号下发，随时可能变化，用前先 `model list`。

## 选模型

- 用户已授权：以效果为准，不为省积分选便宜的模型。
- 新类型贴图第一次生成时，用同一句提示词在 Seedream 5.0 Pro、智能图片V2.5 Pro、旗舰生图模型 V2-Pro（Nano Banana Pro）上各出一张对比，选效果最好的，并把结论写进对应的风格档案。
- 小云雀 skill 规定没有用户授权时不能代选模型；本仓库的风格档案里写明的默认模型，视为用户已授权的选择。
