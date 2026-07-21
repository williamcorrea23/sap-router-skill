# OData Service Discovery Configuration

The SAP MCP Server supports flexible configuration for OData service discovery, allowing you to control which services are exposed through the MCP interface.

## Configuration Methods

### Environment Variables

Set these environment variables to configure service discovery:

```bash
# Allow all services (overrides all patterns)
ODATA_ALLOW_ALL=true

# Service inclusion patterns (comma-separated or JSON array)
ODATA_SERVICE_PATTERNS=ZBP*,ZTRANSPORT*,ZBC_UI_PARAM_E_CDS*

# Service exclusion patterns
ODATA_EXCLUSION_PATTERNS=*_TEST*,*_TEMP*,*_DEBUG*

# Maximum number of services to discover
ODATA_MAX_SERVICES=50

# Discovery mode
ODATA_DISCOVERY_MODE=whitelist
```

### Pattern Types

The configuration supports multiple pattern types:

#### 1. Glob Patterns (default)
- `*` matches any characters
- `?` matches single character
- Case-insensitive

```bash
ODATA_SERVICE_PATTERNS=Z*,API_*,C_CUSTOMER*
```

#### 2. Regex Patterns
Enclose in forward slashes for regex:

```bash
ODATA_SERVICE_PATTERNS=/^Z(BP|TRANSPORT|BC_UI_PARAM_E_CDS).*/
```

#### 3. Exact Match
```bash
ODATA_SERVICE_PATTERNS=ZBP_EMPLOYEE_CDS,API_BUSINESS_PARTNER
```

#### 4. JSON Array (for complex configurations)
```bash
ODATA_SERVICE_PATTERNS='["Z*", "/^API_.*_SRV$/", "C_CUSTOMER_CDS"]'
```

## Configuration Examples

### 1. Allow All Services
```bash
ODATA_ALLOW_ALL=true
```

### 2. Only Custom Z Services
```bash
ODATA_SERVICE_PATTERNS=Z*
ODATA_EXCLUSION_PATTERNS=*_TEST*,*_TEMP*
```

### 3. Specific Service Types
```bash
ODATA_SERVICE_PATTERNS=ZBP_*,API_*,C_*
ODATA_MAX_SERVICES=30
```

### 4. Complex Regex Pattern
```bash
ODATA_SERVICE_PATTERNS="/^(ZBP|ZTRANSPORT|API_BUSINESS).*/"
```

### 5. Mixed Patterns with Exclusions
```bash
ODATA_SERVICE_PATTERNS='["Z*", "API_*"]'
ODATA_EXCLUSION_PATTERNS='["*_TEST*", "*_DEBUG*", "*_TEMP*"]'
```

## Runtime Configuration

### View Current Configuration
```bash
GET http://localhost:3003/config/services
```

### Test Patterns
```bash
POST http://localhost:3003/config/services/test
Content-Type: application/json

{
  "serviceNames": ["ZBP_EMPLOYEE_CDS", "API_BUSINESS_PARTNER", "TEMP_TEST_SRV"]
}
```

### Update Configuration
```bash
POST http://localhost:3003/config/services/update
Content-Type: application/json

{
  "allowAllServices": false,
  "servicePatterns": ["ZBP_*", "API_*"],
  "exclusionPatterns": ["*_TEST*"],
  "maxServices": 25
}
```

## Configuration Validation

The system validates configuration and provides warnings for:
- Invalid regex patterns
- Very high service limits (>200)
- Missing inclusion patterns
- Invalid configuration types

## Default Configuration

If no configuration is provided, the system uses these defaults:
- Service patterns: `["ZBP*", "ZTRANSPORT*", "ZBC_UI_PARAM_E_CDS*"]`
- No exclusion patterns
- Maximum 50 services
- Whitelist discovery mode

## Best Practices

1. **Use specific patterns** rather than allowing all services to improve performance
2. **Set reasonable limits** for maximum services (typically 10-50)
3. **Use exclusions** to filter out test/development services
4. **Test patterns** before deployment using the CLI tool
5. **Monitor logs** for service discovery information

## Troubleshooting

### No Services Discovered
- Check if patterns match actual service names
- Verify exclusion patterns aren't too broad
- Increase `ODATA_MAX_SERVICES` if needed
- Use `ODATA_ALLOW_ALL=true` for testing

### Performance Issues
- Reduce `ODATA_MAX_SERVICES`
- Use more specific patterns
- Add exclusion patterns for unwanted services

### Pattern Not Working
- Test patterns using the CLI tool
- Check logs for configuration validation errors
- Verify regex syntax if using regex patterns
