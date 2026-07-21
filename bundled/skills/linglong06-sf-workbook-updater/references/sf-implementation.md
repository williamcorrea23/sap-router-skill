# SAP SuccessFactors 实现建议参考

本文档提供常见需求的 SAP SuccessFactors 实现方式建议，供更新 Workbook 时参考。

## 一、字段自动计算类需求

### 1. 性别根据身份证自动判断

**实现方式**: Business Rules

**配置步骤**:
1. 创建 Business Rule: `Calculate Gender from National ID`
2. 触发条件: `onSave` 事件，当 `national-id` 字段变更时
3. 规则逻辑:
   ```
   IF country = "CHN" AND cardType = "ResidentIdCard" THEN
     gender = IF(MID(nationalId, 17, 1) % 2 = 1, "M", "F")
   ```
4. 目标字段: `personalInfo.gender`

**注意事项**:
- 中国身份证第17位：奇数=男，偶数=女
- 需配置错误处理：身份证格式不符时如何处理
- 历史数据是否需要回填

---

### 2. 年龄根据出生日期自动计算

**实现方式**: Business Rules 或 Expression

**配置**:
```
age = DATEDIFF(TODAY(), dateOfBirth, "YEARS")
```

---

### 3. 工龄根据入职日期自动计算

**实现方式**: 系统字段 + Business Rules

**相关字段**:
- `jobInfo.timeInPosition` - 在岗时间（系统自动计算）
- 自定义工龄字段可通过 Business Rule 计算

---

## 二、权限控制类需求

### 1. 字段只读

**实现方式**: Permission Role Configuration

**配置步骤**:
1. 确定角色：员工、经理、HR
2. 在字段权限设置中调整
3. 将对应角色的权限设为 `View Only` 或 `Hide`

**示例**:
```
员工对自己的性别字段: View Current (只读)
HR 管理者: Correct Data (可修改)
```

---

### 2. 字段隐藏

**实现方式**: Permission Settings

**场景**:
- 敏感字段隐藏（薪资、身份证）
- 特定条件下隐藏

---

### 3. 条件性权限

**实现方式**: Role-Based Permissions + Business Rules

**示例**:
```
IF employee.country = "CHN" THEN
  SHOW nationalId CHN field
ELSE
  HIDE nationalId CHN field
```

---

## 三、数据联动类需求

### 1. 字段间联动

**实现方式**: Business Rules

**常见场景**:
- 选择部门后自动填充成本中心
- 选择职位后自动填充职级
- 国家变更后重置区域字段

**配置示例**:
```
TRIGGER: jobInfo.department onChange
ACTION: SET jobInfo.costCenter = department.costCenter
```

---

### 2. 跨模块联动

**实现方式**: Business Rules + Integration

**示例**: 员工信息变更同步到其他系统
- 使用 Integration Center 配置出站集成
- 或使用 SF API 触发外部系统更新

---

## 四、审批流程类需求

### 1. 字段变更审批

**实现方式**: Workflow Configuration

**配置步骤**:
1. 定义 Workflow 规则
2. 设置触发条件
3. 配置审批链

**示例**:
```
TRIGGER: jobInfo.position onChange
WORKFLOW: Position Change Approval
APPROVERS: Manager → HRBP
```

---

### 2. 条件审批

**实现方式**: Dynamic Workflow

**示例**:
```
IF jobInfo.payGrade >= "M3" THEN
  approvers = [Manager, HRBP, VP HR]
ELSE
  approvers = [Manager, HRBP]
```

---

## 五、数据校验类需求

### 1. 格式校验

**实现方式**: Field Validation Rules

**常见校验**:
- 邮箱格式
- 手机号格式
- 身份证格式（中国18位）

---

### 2. 业务规则校验

**实现方式**: Business Rules

**示例**:
```
VALIDATE:
  IF nationality = "CHN" AND nationalId IS NOT EMPTY THEN
    LENGTH(nationalId) = 18
    AND ISDIGIT(LEFT(nationalId, 17))
```

---

## 六、多国家本地化需求

### 1. 国家特定字段

**实现方式**: Country-Specific Portlets

**配置**:
1. 在 Country-Specific 配置中启用字段
2. 按国家设置字段可见性和必填性

---

### 2. 多语言标签

**实现方式**: Label Translation

**配置**:
1. 配置自定义标签
2. 为每种语言设置翻译

---

## 七、常见实现方式速查表

| 需求类型 | 推荐实现方式 | 配置位置 |
|---------|-------------|---------|
| 字段自动计算 | Business Rules | Rules Engine |
| 字段权限控制 | Permission Settings | Role-Based Permissions |
| 字段联动 | Business Rules | Rules Engine |
| 审批流程 | Workflow | Workflow Configuration |
| 数据校验 | Validation Rules / Business Rules | 字段配置 / Rules Engine |
| 跨系统集成 | Integration Center | Integration Center |
| 报表输出 | Ad Hoc Reports / Stories | Reporting |
| 定时任务 | Scheduled Jobs | Admin Center |

---

## 八、实现建议模板

当用户提出需求时，建议按以下格式提供实现建议：

```markdown
### 实现建议

**实现方式**: [Business Rules / Workflow / Permission / 等]

**配置位置**: [具体配置路径]

**触发条件**: [onSave / onChange / 定时 / 等]

**规则逻辑**:
```
[伪代码或配置逻辑]
```

**前置条件**:
- [需要的配置或数据]

**注意事项**:
- [边界情况]
- [历史数据处理]
- [性能影响]
```
