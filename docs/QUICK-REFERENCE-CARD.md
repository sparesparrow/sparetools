# SpareTools Monorepo: Quick Reference Card

**Print this or bookmark it!**  
**Version:** 1.0 | **Date:** December 13, 2025

---

## 📋 The 3-Document System

```
┌─────────────────────────────────────────────────────────┐
│  EXECUTIVE-SUMMARY.md                                   │
│  WHO: Leadership, all stakeholders                       │
│  LENGTH: 10-15 min read                                 │
│  CONTENT: Vision, benefits, ROI, timeline               │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  SPARETOOLS-MONOREPO-PLAN.md                            │
│  WHO: Architects, tech leads                            │
│  LENGTH: 30-45 min read                                 │
│  CONTENT: 12-part detailed design, principles           │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  MIGRATION-CHECKLIST.md                                 │
│  WHO: Dev teams, project managers                       │
│  LENGTH: Reference document (not sequential read)       │
│  CONTENT: 5 phases × granular task breakdown            │
└─────────────────────────────────────────────────────────┘
```

---

## 🗂️ New Monorepo Structure

```
sparetools/
├── packages/
│   ├── foundation/                  # 4 packages
│   │   ├── sparetools-base
│   │   ├── sparetools-bootstrap
│   │   ├── sparetools-shared-dev-tools
│   │   └── sparetools-cpython
│   │
│   └── consumers/                   # 8+ packages in 5 domains
│       ├── openssl/
│       │   ├── sparetools-openssl
│       │   └── sparetools-openssl-tools
│       ├── mia/
│       │   ├── sparetools-mia
│       │   └── sparetools-obd-sim
│       ├── mcp/
│       │   ├── sparetools-mcp-orchestrator
│       │   ├── sparetools-tinymcp
│       │   └── sparetools-mcpserver-cpp
│       └── audio/
│           └── sparetools-rtp-midi
│
├── scripts/                         # Centralized automation
│   ├── bootstrap/                   # CPython setup
│   ├── build/                       # Build orchestration
│   ├── validation/                  # 5-tier quality gates
│   ├── ci-cd/                       # GitHub Actions matrix
│   └── utilities/                   # Generators, linkers
│
├── docs/                            # Central documentation hub
│   ├── foundation/
│   ├── consumers/
│   ├── operations/
│   ├── integration/
│   ├── security/
│   ├── development/
│   ├── api/                         # Auto-generated
│   └── examples/
│
├── workspaces/                      # 12+ VS Code workspaces
│   ├── root.code-workspace
│   ├── foundation.code-workspace
│   ├── consumers/
│   │   ├── openssl.code-workspace
│   │   ├── mia.code-workspace
│   │   ├── mcp.code-workspace
│   │   └── audio.code-workspace
│   └── development/
│
└── examples/                        # 4+ integration scenarios
```

---

## 🎯 Key Concepts in 30 Seconds

| Concept | Explanation | File/Location |
|---------|-------------|---------------|
| **Foundation Layer** | Shared packages all consumers use | `packages/foundation/` |
| **Consumer Domain** | Specific use case (openssl, mia, mcp, etc.) | `packages/consumers/<domain>/` |
| **Consumer Config** | Metadata file for each domain | `packages/consumers/<domain>/.consumer.yaml` |
| **Recipe Base Classes** | Python inheritance for consistent patterns | `scripts/recipe_base.py` |
| **Shared Scripts** | Centralized automation (bootstrap, build, validate) | `scripts/bootstrap/build/validation/` |
| **Validation Tiers** | 5-level quality gates (syntax→integration→security) | `scripts/validation/tier*.py` |
| **Workspace Gen** | Auto-generate VS Code workspaces | `scripts/utilities/workspace-generator.py` |
| **Doc Hub** | Centralized docs with auto-linking | `docs/` + `scripts/utilities/doc-linker.py` |
| **CI/CD Matrix** | Dynamic GitHub Actions matrix | `scripts/ci-cd/matrix-generator.py` |

---

## 🚀 Implementation Timeline (16 weeks)

```
Week 1-2:   Foundation Setup       [Phase 1 - Blue]
├─ Create directories
├─ Consumer configs (.consumer.yaml)
├─ Recipe base classes
└─ Doc hub structure

Week 3-4:   Foundation Packages    [Phase 2 - Green]
├─ Migrate sparetools-base
├─ Migrate sparetools-bootstrap
├─ Migrate sparetools-shared-dev-tools
└─ Migrate sparetools-cpython

Week 5-8:   Consumer Packages      [Phase 3 - Yellow]
├─ Migrate openssl consumer (2 packages)
├─ Migrate mia consumer (2 packages)
├─ Migrate mcp consumer (3 packages)
└─ Migrate audio consumer (1 package)

Week 9-12:  Automation & CI/CD     [Phase 4 - Orange]
├─ Build orchestrator
├─ Validation framework
├─ CI/CD workflows
└─ Test automation

Week 13-16: Developer Experience   [Phase 5 - Purple]
├─ Generate workspaces
├─ Auto-generate docs
├─ Create examples
└─ Training materials

TOTAL: 16 weeks to production-ready
BREAK-EVEN: Week 24 (8 weeks after)
```

---

## 💻 Common Commands (Post-Migration)

### Build Commands
```bash
# Build single consumer
python3 scripts/build/build-orchestrator.py --consumer openssl

# Build with parallel
python3 scripts/build/build-orchestrator.py --consumer mia --parallel 4

# Build all packages
python3 scripts/build/build-orchestrator.py --all
```

### Validation Commands
```bash
# Tier 1: Syntax check
python3 scripts/validation/tier1-syntax.py

# Tier 2: Dependencies
python3 scripts/validation/tier2-dependencies.py

# Tier 3: Cross-consumer compat
python3 scripts/validation/tier3-cross-consumer.py

# Tier 4: Integration tests
python3 scripts/validation/tier4-integration.py

# Tier 5: Security gates
python3 scripts/validation/tier5-security.py
```

### Workspace Commands
```bash
# Generate workspace for consumer
python3 scripts/utilities/workspace-generator.py --consumer mia

# Generate all workspaces
python3 scripts/utilities/workspace-generator.py --all

# Open workspace
code workspaces/consumers/mia.code-workspace
```

### Documentation Commands
```bash
# Regenerate docs (INDEX, API, cross-links)
python3 scripts/utilities/doc-linker.py --regenerate

# Validate all links
python3 scripts/utilities/doc-linker.py --validate

# Generate consumer guide
python3 scripts/utilities/doc-linker.py --consumer openssl
```

---

## 📊 Phase Gates (What Success Looks Like)

### Phase 1 ✅
- [ ] Directories created (0 errors)
- [ ] All .consumer.yaml valid
- [ ] Recipe base classes work
- [ ] Doc structure complete

### Phase 2 ✅
- [ ] 4 foundation packages in Conan
- [ ] All exports working
- [ ] No unresolved imports
- [ ] `conan list "sparetools-*/*"` ✅

### Phase 3 ✅
- [ ] 8+ consumer packages in Conan
- [ ] Cross-consumer deps resolve
- [ ] Cross-consumer tests pass
- [ ] No ModuleNotFoundError

### Phase 4 ✅
- [ ] All validation tiers pass
- [ ] Build matrix generates
- [ ] Workflows have no syntax errors
- [ ] Security gates pass

### Phase 5 ✅
- [ ] 12+ workspaces functional
- [ ] docs/INDEX.md generated
- [ ] 4+ examples build
- [ ] Dev guides complete

---

## 🎯 Adding a New Consumer (Fast Path)

```bash
# 1. Create structure
mkdir -p packages/consumers/my-consumer/sparetools-my-{main,tools}/{src,tests,docs}

# 2. Create .consumer.yaml
cat > packages/consumers/my-consumer/.consumer.yaml << EOF
name: my-consumer
display_name: "My Consumer"
dependencies:
  foundation: ["sparetools-base", "sparetools-cpython"]
packages:
  - sparetools-my-main
  - sparetools-my-tools
EOF

# 3. Create conanfile.py (use base class)
# (Copy template from scripts/recipe_base.py)

# 4. Generate workspace
python3 scripts/utilities/workspace-generator.py --consumer my-consumer

# 5. Validate
python3 scripts/validation/tier1-syntax.py

# Done! Integrated into monorepo.
```

---

## 🔄 Dependency Relationships

```
sparetools-base
    ↑
    └── Used by everything

sparetools-cpython
    ↑
    ├── Used by sparetools-bootstrap
    ├── Used by all consumers
    └── Provides hermetic Python 3.12.7

sparetools-bootstrap
sparetools-shared-dev-tools
    ↑
    └── Used by consumers for build automation

sparetools-openssl
    ↑
    └── Required by: sparetools-mia, sparetools-mcp (optional)

sparetools-mia
sparetools-mcp-orchestrator
    ↑
    └── Can work together for IoT + AI orchestration

All → sparetools-base (foundation)
```

---

## 📈 Expected Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Build time (full)** | 30 min | 6 min | 5x faster |
| **Build time (single)** | 8 min | 2 min | 4x faster |
| **Documentation quality** | Scattered | Unified + auto-linked | Excellent |
| **New consumer setup** | Hours | 15 minutes | 20x faster |
| **Onboarding time** | Days | 2 hours | 95% reduction |
| **Test pass rate** | 95% | >99% | Better quality |
| **Workspace setup** | Manual | Automated | 100% consistency |

---

## ⚡ TL;DR (2-Minute Version)

**What:** Reorganize SpareTools into a scalable monorepo  
**Why:** Support multiple consumers (OpenSSL, MIA, MCP, Audio) with shared foundation  
**How:** 16-week phased migration with 5 layers + automation  
**When:** Weeks 1-2 start, week 17 production ready  
**Who:** Architects (plan), Dev teams (execute), Leadership (approve)  
**Impact:** 5x faster builds, 20x faster consumer setup, excellent DX

**Key Files:**
- `EXECUTIVE-SUMMARY.md` - Read first (15 min)
- `SPARETOOLS-MONOREPO-PLAN.md` - Full design (45 min)
- `MIGRATION-CHECKLIST.md` - Task list (reference during execution)

---

## 🆘 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| "Script not found" | Ensure `scripts/` on PATH or use `python3 scripts/...` |
| "Consumer not recognized" | Check `.consumer.yaml` exists and is valid YAML |
| "Conan package not found" | Run `conan list "sparetools-*/*"` to verify in cache |
| "Workspace won't open" | Regenerate with `workspace-generator.py` |
| "Docs have broken links" | Run `doc-linker.py --validate` to check |
| "Build fails" | Run validation tiers in order (tier1 → tier5) |

---

## 📞 Support Resources

| Need | Reference |
|------|-----------|
| **Big picture** | EXECUTIVE-SUMMARY.md |
| **Architecture details** | SPARETOOLS-MONOREPO-PLAN.md (Parts 1-8) |
| **Task checklist** | MIGRATION-CHECKLIST.md |
| **Building scripts** | scripts/build/README.md |
| **Validation** | scripts/validation/README.md |
| **CI/CD** | .github/workflows/README.md (post-migration) |

---

## ✅ Pre-Migration Checklist

- [ ] Read EXECUTIVE-SUMMARY.md (everyone)
- [ ] Review SPARETOOLS-MONOREPO-PLAN.md (architects)
- [ ] Understand MIGRATION-CHECKLIST.md (dev leads)
- [ ] Get buy-in from stakeholders
- [ ] Assign phase owners
- [ ] Create project tracking (Jira/GitHub Projects)
- [ ] Schedule weekly sync meetings
- [ ] Prepare test environments
- [ ] Backup current repos
- [ ] Ready for Phase 1 kickoff!

---

## 🎬 Next Steps

1. **This week:** Review the 3 documents
2. **Next week:** Stakeholder review + approval
3. **Following week:** Phase 1 kickoff
4. **16 weeks:** Production-ready monorepo
5. **Week 24+:** Recouping investment with efficiency gains

---

**Quick Reference Version:** 1.0  
**Status:** Ready to Print/Share  
**Last Updated:** December 13, 2025

*Keep this card handy during migration!*
