# JLBank Plugin Marketplace

JLBank 内网 Claude Code 插件市场。仓库将公开插件和 Agent Skills 的完整文件固定到本地目录，整体转入内网后即可发现和安装，不需要在安装阶段访问公网源码仓库。

当前收录口径：

- Anthropic 官方 `claude-plugins-official` marketplace：全部插件。
- skills.sh：公开 all-time 排行榜 Top 50；不按安全、质量、重复或许可证筛除，风险仅做标记。

## 目录结构

```text
JLBank-Plugin-marketplace/
├── .claude-plugin/
│   └── marketplace.json
├── catalog/
│   ├── anthropic-upstream.json
│   ├── skills-sh-top-50.json
│   ├── skills-sh-metadata.json
│   ├── anthropic-description-zh.json
│   ├── plugin-description-localization.json
│   ├── provenance.json
│   ├── sync-report.json
│   ├── license-report.json
│   ├── trust-boundaries.json
│   └── modifications.json
├── plugins/
│   ├── anthropic/<plugin>/...
│   └── skills-sh/<source>/...
├── scripts/
│   ├── sync_marketplace.py
│   └── validate.sh
├── AGENTS.md
└── README.md
```

## 内网使用

将本仓库推送到内网 Git 服务后，在 Claude Code 中执行：

```text
/plugin marketplace add <内网 Git 仓库地址>
/plugin
```

也可以直接安装：

```text
/plugin install <plugin-name>@jlbank-plugin-marketplace
```

添加 marketplace 只注册目录；具体插件仍由用户选择安装。市场卡片统一展示中文描述；Top 50 skills.sh 技能按排行榜逐项展示中文能力类型、介绍、排名和下载次数。安装后的插件来自本仓库 `plugins/`，不会再根据上游 source 从公网拉取源码。`plugins/` 下的上游文件保持原样，中文化只作用于市场索引展示字段。

## 公网同步

同步机需要能够访问 GitHub、Anthropic 官方插件仓库和 skills.sh。同步只下载、解包和静态分析内容，不运行任何上游脚本：

```bash
python3 scripts/sync_marketplace.py --all --skills-limit 50
./scripts/validate.sh
```

同步可重复执行并复用 `.sync-cache/`。每个 GitHub 来源固定到提交 SHA，well-known 文件校验上游 digest；所有本地包记录内容 SHA-256。失败项保留在 `catalog/sync-report.json`，不能被成功数量掩盖。

仅同步某一来源：

```bash
python3 scripts/sync_marketplace.py --anthropic
python3 scripts/sync_marketplace.py --skills-sh --skills-limit 50
```

## 信任边界

这是公开生态的镜像，不是安全白名单。插件可能包含 Hook、MCP、LSP、外部进程、网络服务、凭据或 SaaS 账号要求；skills.sh 热门条目也不等于经过 JLBank 审批。`catalog/provenance.json` 记录每个包的内容哈希、许可证文件和静态信任边界。转入生产内网前，应基于这些证据进行第二阶段许可、安全、网络依赖与适用性筛选。

skills.sh 排行榜可能包含已从当前上游仓库删除或改名的条目。同步器优先复制固定 GitHub 提交或 well-known 完整文件；无法在当前仓库定位但 skills.sh 仍公开展示正文时，保存 `page-snapshot` 并在 provenance 中显式标记。页面快照只保证 `SKILL.md` 正文，可能不含历史 supporting files，不应误认为上游仓库的完整历史版本。

收录不表示 JLBank 或 Anthropic 对第三方插件背书。各插件仍受其上游许可证约束。
