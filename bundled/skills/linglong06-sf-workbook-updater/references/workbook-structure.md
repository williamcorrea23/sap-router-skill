# SAP SuccessFactors Workbook 结构参考

本文档描述标准 SAP SuccessFactors Workbook 的结构，用于字段定位和需求映射。

## 一、Workbook 整体结构

### Sheet 分类

| 类型 | Sheet 名称示例 | 说明 |
|------|---------------|------|
| 系统信息 | 封面、版本历史、目录 | 元数据，一般不更新业务需求 |
| 员工数据 | 员工档案、个人信息、职务信息 | 核心业务需求所在 |
| 国家特定 | CSF_* 系列 | 国家/地区特定字段配置 |
| 配置数据 | Picklists、MDF | 下拉值、基础对象配置 |

### 常见业务 Sheet

```
员工档案Employ Profile      - 员工基本信息
出生信息BiographicInfo      - 出生日期、出生地
个人信息PersonalInfo        - 个人详细信息
CSF个人信息Global Info      - 全球个人信息
身份证信息NationalID        - 身份证件
电子邮件信息emailInfo       - 邮箱
电话信息phoneInfo          - 电话
地址homeAddress            - 地址
支付信息paymentInfo         - 支付方式
证件&执照workpermit        - 工作证件
紧急联系人emergencyContact  - 紧急联系人
亲属信息dependents          - 家属
雇佣详细信息Employment      - 雇佣信息
职务信息jobInfo            - 职务信息（核心）
工作关系JobRelationships   - 汇报关系
薪酬信息Compensation       - 薪酬
全球委派GlobalAssignment   - 全球派遣
背景信息Background Info    - 背景调查
```

---

## 二、字段定位规则

### 标准 Sheet 结构

```
行 1-3: 标题和说明区域
行 4: 表头行（关键字段：系统字段id、英文标签、类型、是否必填、自定义标签...Comments）
行 5+: 数据行（每个字段一行）
```

### 关键列位置

| 列号 | 列名（中文） | 列名（英文） | 说明 |
|-----|------------|------------|------|
| A | - | - | 通常为空或导航链接 |
| B | - | - | 通常为迭代变更标记 |
| C | 系统字段id | Field ID | **关键字段定位标识** |
| D | 英文标签 | Label | 字段显示名称 |
| E | 类型 | Type | string/date/number/user 等 |
| F | 最大长度 | Max Length | 字符串最大长度 |
| G | 是否必填 | Required | Yes/No |
| H | 自定义标签 | Custom Label | 中文标签 |
| I | 选项列表 | Picklist | 下拉值来源 |
| ... | ... | ... | 权限设置列 |
| 最后一列 | Comments | - | **业务规则写入位置** |

### 字段定位方法

```python
# 通过系统字段id定位
def find_field_row(sheet, field_id: str) -> int:
    for row in range(4, sheet.max_row + 1):  # 从第4行开始（跳过表头）
        cell_value = sheet.cell(row=row, column=3).value  # C列
        if cell_value and str(cell_value).strip().lower() == field_id.lower():
            return row
    return -1  # 未找到

# 通过自定义标签定位
def find_field_by_label(sheet, label: str) -> int:
    for row in range(4, sheet.max_row + 1):
        cell_value = sheet.cell(row=row, column=8).value  # H列
        if cell_value and label in str(cell_value):
            return row
    return -1
```

---

## 三、字段属性说明

### 字段类型

| 类型 | 说明 | 示例字段 |
|-----|------|---------|
| STRING | 字符串 | userId, firstName |
| DATE | 日期 | dateOfBirth, hireDate |
| NUMBER | 数字 | standardHours, fte |
| USER | 用户引用 | managerId, hrId |
| COUNTRY | 国家代码 | nationality, country |
| PICKLIST | 下拉选择 | gender, employmentType |
| FOUNDATION OBJECT | 基础对象 | company, position, jobCode |
| GENERIC OBJECT | 通用对象 | 自定义 MDF 对象 |

### 权限设置列

| 角色列 | 说明 |
|-------|------|
| 员工对他人的权限 | Employee View Others |
| 员工对自己的权限 | Employee View Self |
| 经理 | Manager |
| 二级经理 | Second Level Manager |
| HR 经理 | HR Manager |
| HR 管理者 | HR Admin |
| 系统管理者 | System Admin |
| Global Mobility | 全球派遣 |

### 权限值

| 值 | 说明 |
|---|------|
| Hide | 隐藏 |
| View Current | 查看当前 |
| View Current & History | 查看当前和历史 |
| Add Data | 添加数据 |
| Correct Data | 修正数据（可修改历史） |
| View | 只读 |
| Edit | 可编辑 |

---

## 四、常用字段速查表

### 员工档案 (Employ Profile)

| 系统字段id | 英文标签 | 中文标签 | 说明 |
|-----------|---------|---------|------|
| userId | User ID | 用户标识 | 登录账号 |
| empId | Employee ID | 工号 | 员工编号 |
| username | User Name | 用户名 | 显示名称 |
| status | Status | 状态 | 激活/非激活 |
| email | Email | 邮箱 | 主要邮箱 |
| firstName | First Name | 名 | - |
| lastName | Last Name | 姓 | - |
| managerId | Manager | 直线经理 | 汇报对象 |

### 个人信息 (Personal Info)

| 系统字段id | 英文标签 | 中文标签 | 说明 |
|-----------|---------|---------|------|
| gender | Gender | 性别 | M/F/Unknown |
| nationality | Nationality | 国籍 | 国家代码 |
| maritalStatus | Marital Status | 婚姻状况 | - |
| salutation | Salutation | 称呼 | Mr./Ms.等 |

### 身份证信息 (National ID)

| 系统字段id | 英文标签 | 中文标签 | 说明 |
|-----------|---------|---------|------|
| country | Country | 国家 | 证件所属国家 |
| card-Type | Card Type | 证件类型 | ResidentIdCard 等 |
| national-id | National ID | 身份证号 | 证件号码 |
| isPrimary | Is Primary | 主要证件 | 是否主要证件 |

### 职务信息 (Job Info)

| 系统字段id | 英文标签 | 中文标签 | 说明 |
|-----------|---------|---------|------|
| position | Position | 职位 | 岗位 |
| company | Company | 法人实体 | 公司/法律实体 |
| jobCode | Job Code | 职位代码 | 职务编码 |
| department | Department | 部门 | - |
| location | Location | 地点 | 工作地点 |
| division | Division | 分部 | - |
| costCenter | Cost Center | 成本中心 | - |
| employmentType | Employment Type | 雇佣类型 | Full-time/Part-time |
| employeeClass | Employee Class | 员工类别 | - |
| timeTypeProfile | Time Type Profile | 考勤类型 | 考勤规则 |
| standardHours | Standard Hours | 标准工时 | 每周工时 |

---

## 五、版本历史 Sheet 结构

标准版本历史 Sheet 通常包含以下列：

| 列 | 内容 |
|---|------|
| A | 序号/空 |
| B | 版本号 |
| C | 版本说明 |
| D | 修改人 |
| E | 邮箱 |
| F | 日期 |
| G | 备注 |

更新 Workbook 时应在版本历史中添加记录。

---

## 六、YAML 结构化映射

为便于 AI 处理，建议将 Workbook 转换为以下 YAML 结构：

```yaml
sections:
  - id: PI-001
    sheet_name: 个人信息PersonalInfo
    module: Employee Central
    area: Personal Info
    workbook_location: "Sheet: 个人信息PersonalInfo / Row 10"
    fields:
      - id: PI-001-gender
        field_id: gender
        label: Gender
        custom_label: 性别
        type: STRING
        required: No
        current_requirement: ""
        current_decision: ""
        status: draft
        source_meetings: []
        comments: ""
```

此结构便于：
- 需求映射
- 变更追踪
- 会议关联
