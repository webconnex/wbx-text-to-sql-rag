# 📚 Documentation Management - Agent-Driven Documentation

## Specialized Agents for Documentation

### Primary Agents
- **@doc-curator**: Documentation strategy, content organization, knowledge management
- **@test-engineer**: Test documentation, validation procedures
- **@security-guardian**: Security documentation, compliance reports  
- **@api-architect**: API documentation, endpoint specifications

## Documentation Philosophy

### Living Documentation Principle
Documentation is **code-adjacent** and **agent-maintained**. Each agent is responsible for maintaining documentation in their domain of expertise.

### Documentation Types
```
docs/
├── TESTING_REPORTS.md         # @test-engineer maintains
├── SECURITY_AUDIT.md          # @security-guardian maintains  
├── DEVELOPMENT.md             # @doc-curator + multiple agents
├── API_REFERENCE.md           # @api-architect maintains
├── ARCHITECTURE.md            # @aws-architect + @api-architect
└── PERFORMANCE_BENCHMARKS.md  # @performance-optimizer maintains
```

## Agent Documentation Responsibilities

### @doc-curator Responsibilities
- **Overall documentation strategy** and information architecture
- **Cross-agent coordination** for comprehensive documentation
- **User-facing guides** and onboarding documentation
- **Documentation quality assurance** and consistency checks
- **Knowledge gap identification** and documentation planning

### Domain-Specific Documentation
```python
documentation_matrix = {
    "@test-engineer": [
        "Test methodologies and procedures",
        "Security layer testing protocols", 
        "Performance benchmarking procedures",
        "Integration test documentation"
    ],
    "@security-guardian": [
        "7-layer security architecture",
        "Threat analysis and mitigation",
        "Compliance requirements and audits",
        "Security incident response procedures"
    ],
    "@performance-optimizer": [
        "Performance benchmarks and targets",
        "Optimization techniques and results",
        "Load testing procedures and results",
        "Monitoring and alerting setup"
    ],
    "@aws-architect": [
        "Infrastructure architecture diagrams",
        "Cost optimization strategies",
        "Deployment and scaling procedures",
        "Disaster recovery plans"
    ]
}
```

## Documentation Standards

### Markdown Structure
```markdown
# Title with Emoji Icon

## Overview
Brief description of what this document covers

## Agent Responsible
- Primary: @agent-name
- Contributing: @agent1, @agent2

## Last Updated
- Date: YYYY-MM-DD
- Updated by: @agent-name
- Next Review: YYYY-MM-DD

## Content sections...

## IMPORTANT Notes
Critical information for developers

## Related Documents
Links to related documentation
```

### Code Documentation
```python
def document_function():
    """
    Function documentation standard.
    
    Args:
        param1 (type): Description
        param2 (type): Description
        
    Returns:
        type: Description
        
    Raises:
        ExceptionType: When this exception occurs
        
    Example:
        >>> result = document_function()
        >>> print(result)
        
    Agent Responsible: @agent-name
    Last Updated: YYYY-MM-DD
    """
    pass
```

## Documentation Workflows

### Agent-Driven Updates
```bash
# Update documentation after changes
/agent:summon @doc-curator "update documentation for new RAG optimization"

# Cross-agent documentation review
/agent:collaborate @doc-curator @security-guardian "review security documentation for accuracy"

# Comprehensive documentation audit
/agent:hive-mind "conduct full documentation audit and update"
```

### Documentation Automation
```python
def auto_update_documentation():
    """Automated documentation updates triggered by code changes"""
    
    changed_files = get_git_changes()
    
    for file in changed_files:
        if 'backend/services/' in file:
            trigger_agent_update('@api-architect', 'update API documentation')
        elif 'tests/' in file:
            trigger_agent_update('@test-engineer', 'update test documentation')
        elif 'security' in file.lower():
            trigger_agent_update('@security-guardian', 'update security documentation')
```

## Quality Assurance

### Documentation Review Checklist
```markdown
## @doc-curator Review Checklist
- [ ] Content is accurate and up-to-date
- [ ] Agent responsibilities are clearly defined
- [ ] Cross-references are working and relevant
- [ ] Code examples are tested and functional
- [ ] Formatting follows documentation standards
- [ ] Technical accuracy verified by domain agents

## Domain Agent Review
- [ ] Technical content reviewed by responsible agent
- [ ] Examples and procedures validated
- [ ] Integration with related documentation verified
- [ ] Agent-specific best practices included
```

### Documentation Metrics
```python
documentation_kpis = {
    "coverage": "95% of code has documentation",
    "freshness": "Documentation updated within 7 days of code changes", 
    "accuracy": "Zero reported documentation errors",
    "completeness": "All agent domains have comprehensive documentation",
    "usability": "New developers can onboard using docs alone"
}
```

## Agent Coordination Examples

### Multi-Agent Documentation Project
```bash
# Example: Document new feature end-to-end
/agent:collaborate @doc-curator @api-architect @security-guardian @test-engineer "document new multi-tenant query feature including API specs, security implications, and testing procedures"
```

### Documentation Maintenance
```bash
# Quarterly documentation review
/agent:hive-mind "conduct quarterly documentation review and update all agent-maintained documents"

# Security documentation audit
/agent:summon @security-guardian "review all security documentation for compliance and accuracy"
```

## Documentation Templates

### New Feature Documentation Template
```markdown
# Feature Name

## Agent Responsible
- Primary: @agent-name
- Contributing: @agent1, @agent2

## Overview
Brief description of the feature

## Implementation Details
Technical implementation with code examples

## Security Considerations
Security implications and safeguards

## Testing Strategy  
How to test this feature

## Performance Impact
Performance considerations and benchmarks

## API Reference
If applicable, API endpoints and usage

## Troubleshooting
Common issues and solutions

## Related Documentation
Links to related docs
```

## IMPORTANT: Documentation Best Practices

### For All Agents
1. **Update documentation** immediately after code changes
2. **Include practical examples** that developers can copy-paste  
3. **Document the 'why'** not just the 'what'
4. **Cross-reference related documentation**
5. **Include troubleshooting sections**

### For @doc-curator Specifically
1. **Maintain information architecture** and navigation
2. **Ensure consistency** across all documentation  
3. **Identify documentation gaps** and assign to appropriate agents
4. **Coordinate major documentation initiatives**
5. **Monitor documentation usage** and improve based on feedback

### For Domain Agents
1. **Own your domain's documentation** completely
2. **Keep technical accuracy** as the highest priority
3. **Include real examples** from actual system usage
4. **Update metrics and benchmarks** regularly
5. **Coordinate with @doc-curator** for major changes

Remember: Documentation is not an afterthought - it's a critical system component that enables rapid development and effective collaboration!