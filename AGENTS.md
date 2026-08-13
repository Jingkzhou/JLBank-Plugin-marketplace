# AGENTS.md

本仓库是 JLBank 内网 Claude Code 插件市场，规则适用于仓库全部目录。

## 仓库定位

- marketplace 标识固定为 `jlbank-plugin-marketplace`。
- `.claude-plugin/marketplace.json` 是唯一市场入口；仓库根目录不是单个插件，不创建根级 `.claude-plugin/plugin.json`。
- 所有可安装插件必须完整落在 `plugins/` 内，并通过 `./` 相对路径引用，不能在内网安装阶段继续下载公网源码。
- Anthropic 官方 marketplace 全量镜像；skills.sh 按明确的排行榜数量镜像，当前基线为 Top 600。扩容不得删除已有来源记录。

## 上游内容

- `plugins/` 下的镜像内容属于各自上游作者，不得无记录地修改。
- 同步时固定上游提交 SHA，保存来源、路径、哈希、同步状态和失败原因。
- 不执行上游 Hook、脚本、二进制、安装器或 MCP 服务。同步只允许下载、解包、复制和静态检查。
- 风险、重复、外网依赖和许可证未知只做标记，不作为首轮收录过滤条件。
- 需要为 Claude Code 兼容性修改镜像内容时，必须在 `catalog/modifications.json` 记录原值、修改值和理由。

## 安全与许可

- 插件属于高信任代码。收录不代表 JLBank 或 Anthropic 对第三方内容背书。
- 不得提交密钥、Cookie、OIDC token 或个人配置。
- 保留上游 LICENSE、NOTICE 和版权文件；无法确定许可证时标记为 `UNKNOWN`，不得猜测。
- 含 Hook、MCP、LSP、外部二进制、网络服务或凭据要求的插件必须在报告中标记信任边界。

## 变更与验证

- 市场生成文件通过 `scripts/sync_marketplace.py` 更新，不手工批量改写。
- 交付前运行：

  ```bash
  ./scripts/validate.sh
  ```

- 若本机 Claude Code 支持，再运行：

  ```bash
  claude plugin validate .
  ```

- 提交前运行 `git diff --check` 和 `git status --short`。
- 不发布、不推送、不删除历史镜像，除非用户明确授权。
