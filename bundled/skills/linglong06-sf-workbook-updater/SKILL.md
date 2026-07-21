---
name: sf-workbook-updater
description: SAP SuccessFactors Workbook 更新助手。处理录音转写、会议记录或 Workbook 草稿，提取需求并更新到标准 Workbook。触发场景：(1) 用户提供录音文件需要转写成会议记录 (2) 用户提供会议记录文本需要提取需求 (3) 用户提供 Workbook 草稿需要对齐标准格式 (4) 用户需要根据会议内容更新 Workbook (5) 用户提到 "更新 workbook"、"会议纪要转workbook"、"需求提取"。更新内容用红色高亮，文件名带时间戳。
---

# SAP SuccessFactors Workbook 更新助手

## 工作流程

```
输入 → 需求提取 → 用户确认 → 创建副本 → 更新Workbook → 红色高亮
```

### 输入类型处理

#### 1. 录音文件
- 使用 ppocrv5 或 Whisper 进行语音转写
- 生成 transcript.md
- 继续按会议记录流程处理

#### 2. 会议记录文本
- 解析会议内容，识别需求、决策、待确认项
- 映射到 Workbook 字段结构
- 生成 requirements.yaml 供用户确认

#### 3. Workbook 草稿
- 读取标准 Workbook 结构
- 对比草稿与标准格式差异
- 生成差异报告供用户确认

## 标准处理流程

### Step 1: 解析输入并提取需求

读取输入内容后，提取以下结构化信息：

```yaml
requirements:
  - id: R-{date}-{seq}
    module: Employee Central / Recruiting / 等
    area: Personal Info / Job Info / 等
    topic: 具体配置点
    requirement: 需求描述
    status: draft / confirmed / open
    priority: high / medium / low
    mapped_workbook_section: 对应的 Workbook section
    implementation_note: SAP SF 实现建议
```

### Step 2: 用户确认

以清晰格式展示提取的需求：

```markdown
## 需求确认

| ID | 模块 | 字段 | 需求 | 实现建议 |
|----|------|------|------|----------|
| R-001 | EC | gender | 根据身份证自动判断 | Business Rules |
```

**必须等待用户确认后才能继续更新 Workbook。**

### Step 3: 创建 Workbook 副本

- 文件名格式：`{原文件名}_updated_{YYYYMMDD_HHMMSS}.xlsx`
- 保持原始文件不变

### Step 4: 更新 Workbook

使用 `scripts/update_workbook.py` 脚本：

```bash
python scripts/update_workbook.py <workbook_path> --requirements requirements.yaml
```

更新规则：
- 定位目标字段在 Workbook 中的位置（Sheet、行号）
- 在 Comments 列添加业务规则和实现建议
- 红色背景高亮新增内容
- 黄色背景高亮整行以示关注

### Step 5: 添加 SAP SuccessFactors 实现建议

根据需求类型提供专业建议，参考 [references/sf-implementation.md](references/sf-implementation.md)。

## Workbook 结构参考

标准 Workbook 结构详见 [references/workbook-structure.md](references/workbook-structure.md)。

核心字段定位逻辑：
- 系统字段id 在第 3 列（C列）
- 自定义标签 在第 7 列（G列）
- Comments 在最后一列

## 高亮样式规范

```python
# 红色高亮 - 新增内容
red_fill = PatternFill(start_color='FF6B6B', end_color='FF6B6B', fill_type='solid')
red_font = Font(color='FFFFFF', bold=True)

# 黄色高亮 - 整行关注
yellow_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
yellow_font = Font(color='000000', bold=True)
```

## 使用示例

**示例 1：从会议记录更新**
```
用户：根据这条会议记录更新 workbook：个人信息的性别要根据身份证号自动判断

处理流程：
1. 提取需求：gender 字段自动计算
2. 定位：个人信息PersonalInfo sheet，gender 字段
3. 确认：展示需求映射
4. 更新：创建副本，添加业务规则，红色高亮
5. 建议：使用 Business Rules 实现，触发条件配置
```

**示例 2：录音文件处理**
```
用户：这是会议录音，帮我更新 workbook [audio.m4a]

处理流程：
1. 转写录音 → transcript.md
2. 提取需求列表
3. 用户确认
4. 批量更新 Workbook
```

## 输出文件

| 文件 | 说明 |
|------|------|
| `{原文件名}_updated_{timestamp}.xlsx` | 更新后的 Workbook 副本 |
| `requirements.yaml` | 提取的结构化需求 |
| `workbook-diff.md` | 更新差异报告（可选） |

## 注意事项

1. **永远不要直接修改原始文件**，始终创建副本
2. **必须等待用户确认**后才能更新 Workbook
3. **提供 SAP SuccessFactors 专业建议**，不仅仅是记录需求
4. **版本历史**：在 Workbook 的版本历史 sheet 中记录更新
