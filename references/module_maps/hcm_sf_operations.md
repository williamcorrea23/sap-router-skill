# HCM SuccessFactors Operations

## Overview
SuccessFactors operations are executed via SuccessFactors OData APIs through the `sf-mcp` (Model Context Protocol) server.

## Actions Reference

### `SF_READ_EMPLOYEE`
- **Purpose**: Get user profile data.
- **Endpoint**: `/odata/v2/User`
- **Params**:
  - `$filter`: User ID or username filter
  - `$select`: Specific fields to select

### `SF_READ_ORG`
- **Purpose**: Read departments organization structure.
- **Endpoint**: `/odata/v2/FODepartment`

### `SF_READ_EMPLOYMENT`
- **Purpose**: Read active employment details.
- **Endpoint**: `/odata/v2/EmpEmployment`

### `SF_READ_COMP`
- **Purpose**: Read compensation information.
- **Endpoint**: `/odata/v2/EmpCompensation`

### `SF_READ_TIMEOFF`
- **Purpose**: Read employee time off entries.
- **Endpoint**: `/odata/v2/EmployeeTime`
