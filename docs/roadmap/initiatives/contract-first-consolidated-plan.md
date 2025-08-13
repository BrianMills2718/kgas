# Contract-First Implementation: Consolidated Plan

**Date**: 2025-08-05  
**Status**: Ready for Implementation  
**Consolidates**: Original Action Plan + Revised Plan + Next Steps

## Executive Summary

The KGAS codebase has two competing tool interface designs that need unification:
1. **Current Reality**: Tools use `Tool` protocol expected by orchestrator
2. **Target Architecture**: Contract-first `KGASTool` design from ADR-001

## Implementation Approaches

### Option A: Conservative (Original Action Plan)
**Duration**: 7 phases over 6 weeks  
**Approach**: Backwards compatibility with bridge pattern  
**Best for**: Production systems with multiple users

### Option B: Aggressive (Revised Plan) 
**Duration**: 4 weeks direct migration  
**Approach**: No backwards compatibility needed  
**Best for**: Single user, development phase (current situation)

**RECOMMENDATION**: Use Option B (Aggressive) since we're in single-user development phase.

## Aggressive 4-Week Plan (RECOMMENDED)

### Week 1: Foundation & Orchestrator Update
1. **Fix validation attribute** in tool_contract.py
2. **Update orchestrator** directly to use ToolRequest/ToolResult
3. **Update service APIs** to match tool expectations
4. **Test with one tool** (T03TextLoader)

### Week 2: Migrate Simple Tools
- All Category A tools (T01-T14 loaders)
- Establish migration patterns

### Week 3: Process & Neo4j Tools  
- Category B (processing) and C (Neo4j) tools
- Handle service integration complexity

### Week 4: Advanced Tools & Cleanup
- Categories D (analysis) and E (extraction) tools
- Remove legacy code and bridges

## Conservative 7-Phase Plan (FALLBACK)

### Phase 1: Quick Fixes (Day 1)
- Fix validation attribute mismatch
- Add service adapter methods  
- Create minimal test

### Phase 2: Documentation Update (Day 2)
- Update architecture documentation
- Create migration guide

### Phase 3: Orchestrator Bridge (Day 3-4)
- Create bridge pattern
- Test bridge with multiple tools

### Phase 4: Pilot Migration (Week 2)
- Migrate Category A tools (simple loaders)
- Parallel testing of old/new versions

### Phase 5: Service Integration (Week 3)
- Standardize service interfaces
- Remove field adapters

### Phase 6: Full Migration (Week 4-6)
- Migrate all remaining categories
- Complex tools with theory support

### Phase 7: Cleanup (Week 7)
- Remove legacy code
- Update documentation
- Archive migration history

## Implementation Details

### Key Interface Incompatibilities
1. **Validation Result Attributes**: Orchestrator expects `validation_errors`, KGASTool has `errors`
2. **Execute Method Signatures**: Different input/output patterns
3. **Service Dependencies**: Tools expect methods that may not exist

### Migration Categories
- **Category A**: Simple Loaders (15 tools) - Low complexity
- **Category B**: Processing Tools (10 tools) - Medium complexity  
- **Category C**: Neo4j Tools (8 tools) - High complexity
- **Category D**: Analysis Tools (20+ tools) - Varied complexity
- **Category E**: Extraction Tools (5 tools) - High complexity

### Risk Mitigation
- Parallel running during migration
- Git tags at each phase
- Quick revert procedures
- Comprehensive testing strategy

## Success Metrics
- Zero production incidents during migration
- Performance within 5% of current
- All tests passing
- Documentation up to date
- Interface compliance: 100% tools using KGASTool

## Next Actions

**Immediate (Choose Approach)**:
1. Confirm aggressive vs conservative approach
2. Start Week 1 tasks for chosen approach
3. Set up testing framework for migration validation

**References**:
- Interface analysis: `docs/architecture/systems/tool-interface-migration.md`
- Service APIs: `docs/api/service-apis.md`
- Tool categories and migration complexity documented in interface mapping