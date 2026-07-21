# SF Workbook Updater

SAP SuccessFactors Workbook 更新助手 - Claude Code Skill

## 功能概述

将会议记录、录音转写或需求描述自动提取并更新到 SAP SuccessFactors Workbook 中。

### 核心能力

| 功能 | 说明 |
|------|------|
| 录音转写 | 支持 audio.m4a 等格式转成会议记录 |
| 需求提取 | 从会议记录提取结构化需求 |
| 字段映射 | 自动匹配 Workbook 标准字段 |
| 用户确认 | 展示需求确认表，等待用户确认 |
| Workbook 更新 | 创建带时间戳的副本，保留原始文件 |
| 高亮标记 | 红色高亮更新内容，黄色高亮关注行 |
| 实现建议 | 提供 SAP SuccessFactors 专业实现建议 |
| 版本追踪 | 自动更新版本历史 |

## 安装

```bash
# 克隆仓库
git clone https://github.com/linglong06/sf-workbook-updater.git

# 复制到 Claude Code skills 目录
cp -r sf-workbook-updater ~/.claude/skills/
```

## 使用方式

### 触发场景

- 用户提供录音文件需要转写成会议记录
- 用户提供会议记录文本需要提取需求
- 用户提供 Workbook 草稿需要对齐标准格式
- 用户需要根据会议内容更新 Workbook
- 用户提到 "更新 workbook"、"会议纪要转workbook"、"需求提取"

### 示例用法

```
用户: 根据这条会议记录更新 workbook：
      个人信息的性别要根据身份证号自动判断

处理流程:
1. 提取需求并映射到 Workbook 字段
2. 展示确认表等待用户确认
3. 确认后创建带时间戳的 Workbook 副本
4. 红色高亮更新内容
5. 提供 SAP SuccessFactors Business Rules 实现建议
```

## 工作流程

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  输入材料    │ -> │  需求提取    │ -> │  用户确认    │ -> │ 更新Workbook │
│             │    │             │    │             │    │             │
│ • 录音文件   │    │ • 结构化需求  │    │ • 确认表展示  │    │ • 创建副本   │
│ • 会议记录   │    │ • 字段映射   │    │ • 补充信息   │    │ • 红色高亮   │
│ • 需求描述   │    │ • 实现建议   │    │ • 状态标记   │    │ • 版本历史   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## 输出文件

| 文件 | 说明 |
|------|------|
| `WorkBook_xxx_YYYYMMDD_HHMMSS.xlsx` | 带时间戳的 Workbook 副本 |
| `requirements-xxx.yaml` | 结构化需求文件 |
| `workbook-diff.md` | 更新差异报告 |

## 目录结构

```
sf-workbook-updater/
├── SKILL.md                          # 主技能文件
├── README.md                         # 说明文档
├── scripts/
│   └── update_workbook.py            # Workbook 更新脚本
└── references/
    ├── sf-implementation.md          # SAP SuccessFactors 实现建议参考
    └── workbook-structure.md         # 标准 Workbook 结构说明
```

## SAP SuccessFactors 实现建议

Skill 会针对不同类型的需求提供专业的实现建议：

| 需求类型 | 实现方式 |
|---------|---------|
| 字段配置 | Element Configuration, Country-Specific Fields |
| 下拉选项 | Picklist 配置 |
| 业务规则 | Business Rules (if-then-else) |
| 工作流 | Workflow Configuration |
| 权限 | Role-Based Permissions (RBP) |
| 集成 | Integration Center, OData API |

## 依赖

- Python 3.8+
- openpyxl (Excel 处理)
- PyYAML (YAML 处理)

```bash
pip install openpyxl pyyaml
```

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-03-10 | 初始版本，支持会议记录转 Workbook |

## License

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request。

---

**Created for SAP SuccessFactors Implementation Consultants**
