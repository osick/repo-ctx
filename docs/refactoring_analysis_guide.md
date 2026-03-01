# Refactoring Analysis Guide

This document describes the graph analysis capabilities in repo-ctx that support
code refactoring and modernization projects. It explains which analyses are most
valuable, how to interpret results, and how to use them for refactoring decisions.

## Table of Contents

1. [Refactoring Workflow](#refactoring-workflow)
2. [Analysis Levels](#analysis-levels)
3. [Graph Types](#graph-types)
4. [Coupling Metrics](#coupling-metrics)
5. [Cycle Detection](#cycle-detection)
6. [Practical Recommendations](#practical-recommendations)
7. [Implementation Status](#implementation-status)

---

## Refactoring Workflow

A typical refactoring/modernization project follows these phases, each requiring
specific information:

| Phase | Question to Answer | Required Analysis |
|-------|-------------------|-------------------|
| **1. Assessment** | "What's the current state?" | Architecture overview, dependency graphs |
| **2. Identification** | "What needs to change?" | Coupling hotspots, code smells, cycles |
| **3. Prioritization** | "What's risky vs. safe?" | Coupling metrics, stability analysis |
| **4. Planning** | "How to structure the target?" | Natural boundaries, cohesion groups |
| **5. Execution** | "If I change X, what breaks?" | Reverse dependencies, impact analysis |

---

## Analysis Levels

Dependency analysis can be performed at different granularity levels. Each level
serves different purposes in the refactoring process.

### Level Comparison

| Level | Granularity | Unit of Analysis | Best For |
|-------|-------------|------------------|----------|
| **Package/Module** | Coarsest | Directory/namespace | High-level architecture, module extraction |
| **File** | Medium | Source file | Small projects, import analysis |
| **Class** | Fine | Class/Interface | OOP refactoring, coupling analysis |
| **Function/Method** | Finest | Callable | Call graph, impact analysis |

### Recommended Level by Project Size

| Project Size | Primary Level | Secondary Level |
|--------------|---------------|-----------------|
| Small (<50 files) | File | Function |
| Medium (50-500 files) | Class | Package |
| Large (>500 files) | Package | Class |

### Why Class-Level is Most Valuable for Refactoring

1. **Classes are the unit of change**: Most refactoring patterns (Extract Class,
   Move Method, Extract Interface) operate at class level
2. **Classes have semantic meaning**: Unlike files, classes represent concepts
3. **Classes define responsibilities**: Coupling between classes reveals
   responsibility boundaries
4. **OOP design principles apply**: SOLID principles are class-level concerns

---

## Graph Types

### 1. Dependency Graph

Shows directed dependencies between components.

**File-Level** (current implementation):
```
main.py ──imports──> services.py ──imports──> utils.py
```

**Class-Level** (high value for refactoring):
```
UserController ──uses──> UserService ──uses──> UserRepository
       │                      │
       └──uses──> AuthService─┘
```

**Dependency Types:**
- `imports`: Module/file import
- `extends`: Inheritance relationship
- `implements`: Interface implementation
- `uses`: Field type, parameter, return type
- `calls`: Method invocation
- `creates`: Object instantiation

### 2. Inheritance Tree

Shows class hierarchy relationships.

```
BaseEntity
├── User
│   ├── AdminUser
│   └── GuestUser
└── Product
    ├── PhysicalProduct
    └── DigitalProduct
```

**Refactoring Signals:**
- Depth > 4 levels: Consider flattening with composition
- Width > 10 children: Missing abstraction layer
- Empty subclasses: Unnecessary inheritance
- Diamond patterns: Complexity smell

### 3. Call Graph

Shows function/method invocation relationships.

```
main()
├── initialize()
│   ├── loadConfig()
│   └── connectDB()
└── processRequest()
    ├── validateInput()
    ├── executeLogic()
    │   └── queryDatabase()
    └── formatResponse()
```

**Refactoring Signals:**
- High fan-in (many callers): Core function, change carefully
- High fan-out (many callees): God function, consider splitting
- No callers: Potentially dead code
- Recursive cycles: Usually intentional

### 4. Package/Module Graph

Shows dependencies between packages/directories.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   api/      │────>│  services/  │────>│   models/   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           v
                    ┌─────────────┐
                    │   utils/    │
                    └─────────────┘
```

**Refactoring Signals:**
- Cycles between packages: Architectural problem
- Many cross-package dependencies: Poor modularization
- Utils depending on business logic: Inverted dependency

---

## Coupling Metrics

Coupling metrics quantify how connected components are, helping prioritize
refactoring efforts.

### Core Metrics

| Metric | Formula | Meaning |
|--------|---------|---------|
| **Ca** (Afferent Coupling) | Count of incoming dependencies | How many depend ON this |
| **Ce** (Efferent Coupling) | Count of outgoing dependencies | How many does this DEPEND on |
| **Instability** | Ce / (Ca + Ce) | 0.0 = stable, 1.0 = unstable |
| **Abstractness** | Abstract types / Total types | Ratio of abstract classes |
| **Distance from Main Sequence** | \|A + I - 1\| | 0.0 = ideal balance |

### Interpreting Instability

```
Instability = Ce / (Ca + Ce)

         0.0                    0.5                    1.0
          │                      │                      │
   ┌──────┴──────┐        ┌──────┴──────┐        ┌──────┴──────┐
   │   STABLE    │        │  BALANCED   │        │  UNSTABLE   │
   │             │        │             │        │             │
   │ Many depend │        │ Moderate    │        │ Few depend  │
   │ on this     │        │ coupling    │        │ on this     │
   │             │        │             │        │             │
   │ HARD to     │        │             │        │ EASY to     │
   │ change      │        │             │        │ change      │
   └─────────────┘        └─────────────┘        └─────────────┘
```

### Refactoring Decision Matrix

| Instability | Abstractness | Zone | Meaning | Action |
|-------------|--------------|------|---------|--------|
| Low (0.0-0.3) | High (0.7-1.0) | Ideal | Stable abstraction | Leave alone |
| Low | Low | Zone of Pain | Rigid, hard to change | Add interfaces |
| High (0.7-1.0) | Low | Normal | Volatile implementation | OK if intentional |
| High | High | Zone of Uselessness | Over-abstracted | Simplify |

### Practical Thresholds

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Ca (Afferent) | < 10 | 10-20 | > 20 |
| Ce (Efferent) | < 10 | 10-15 | > 15 |
| Class size (methods) | < 20 | 20-30 | > 30 |
| Method parameters | < 4 | 4-6 | > 6 |

---

## Cycle Detection

Cycles in dependencies are architectural smells that should be eliminated.

### Cycle Severity by Level

| Level | Severity | Example | Impact |
|-------|----------|---------|--------|
| **Package** | CRITICAL | `api/` ↔ `services/` | Cannot deploy independently |
| **Class** | HIGH | `UserService` ↔ `OrderService` | Tight coupling, hard to test |
| **Function** | LOW | Mutual recursion | Often intentional |

### Cycle Types

**Direct Cycle (2 nodes):**
```
A ──> B
^     │
└─────┘
```

**Transitive Cycle (3+ nodes):**
```
A ──> B ──> C
^           │
└───────────┘
```

**Self-Loop:**
```
A ──┐
^   │
└───┘
```

### Breaking Cycles

**Strategy 1: Extract Interface**
```
Before:  ServiceA ←→ ServiceB

After:   ServiceA ──> IServiceB <── ServiceB
```

**Strategy 2: Dependency Injection**
```
Before:  ServiceA creates ServiceB, ServiceB creates ServiceA

After:   Container creates both, injects dependencies
```

**Strategy 3: Extract Shared Module**
```
Before:  ModuleA ←→ ModuleB (share types)

After:   ModuleA ──> SharedTypes <── ModuleB
```

**Strategy 4: Event-Based Decoupling**
```
Before:  ServiceA calls ServiceB, ServiceB calls ServiceA

After:   ServiceA ──> EventBus <── ServiceB
```

---

## Practical Recommendations

### High-Priority Refactoring Targets

1. **God Classes** (Ca > 20, Ce > 15)
   - Many depend on it, it depends on many
   - Split by responsibility

2. **Unstable Core** (Instability > 0.7, Ca > 10)
   - Volatile but many dependents
   - Stabilize with interfaces

3. **Package Cycles**
   - Any cycle at package level
   - Break immediately

4. **Deep Hierarchies** (depth > 4)
   - Hard to understand and modify
   - Flatten with composition

5. **Bidirectional Dependencies**
   - Two classes depending on each other
   - Extract interface or mediator

### Output Format for Refactoring Reports

```markdown
## Refactoring Recommendations

### Critical Issues
1. **Package cycle detected**: `services` ↔ `models` ↔ `utils`
   - Impact: Cannot deploy independently
   - Suggestion: Extract shared types to `common` package

### High-Priority Targets
1. **God class**: `UserManager` (Ca=23, Ce=15)
   - 23 classes depend on it, touches 15 others
   - Suggestion: Split by responsibility

2. **Unstable core**: `DatabaseConnection` (Instability=0.8, Ca=45)
   - 45 dependents but high instability
   - Suggestion: Add interface, reduce direct dependencies

### Improvement Opportunities
1. **Deep hierarchy**: `BaseWidget` → 6 levels deep
   - Suggestion: Flatten using composition

2. **Tight coupling**: `OrderService` ↔ `PaymentService`
   - Bidirectional dependency
   - Suggestion: Extract `OrderPaymentMediator`
```

---

## Implementation Status

### Currently Implemented

| Feature | Level | Status |
|---------|-------|--------|
| Dependency Graph | File | ✅ Implemented |
| Cycle Detection | File | ✅ Implemented |
| Layer Detection | File | ✅ Implemented |
| DSM (Design Structure Matrix) | File | ✅ Implemented |
| Mermaid Diagrams | File | ✅ Implemented |

### Planned Implementation

| Feature | Level | Priority |
|---------|-------|----------|
| Dependency Graph | Class | P1 - Essential |
| Coupling Metrics (Ca/Ce) | Class | P1 - Essential |
| Cycle Detection | Class, Package | P1 - Essential |
| Inheritance Tree | Class | P2 - Important |
| Call Graph | Function | P2 - Important |
| Dependency Graph | Package | P2 - Important |
| Cohesion Analysis | Class | P3 - Nice to have |

---

## References

- Martin, R. (2003). *Agile Software Development: Principles, Patterns, and Practices*
- Lakos, J. (1996). *Large-Scale C++ Software Design*
- Fowler, M. (2018). *Refactoring: Improving the Design of Existing Code*
- Bass, L., Clements, P., Kazman, R. (2012). *Software Architecture in Practice*
