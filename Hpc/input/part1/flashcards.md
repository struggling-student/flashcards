# HPC Part 1 Flashcards

## What is the main goal of single-node HPC?
- Improve the performance of an application running on one compute node.
- The usual loop is:
  1. Measure actual performance.
  2. Understand the hardware architecture.
  3. Identify the bottleneck.
  4. Remove or reduce the bottleneck.
  5. Measure again.

## Why is simulation considered the "third pillar" of science?
Simulation complements theory and experiments when real experiments are too difficult, expensive, slow, or dangerous. HPC makes it possible to model phenomena such as climate, materials, galaxies, fluids, and drug interactions using known physical laws and numerical methods.

## Why did HPC shift from faster single cores to parallelism?
- Moore's law kept increasing transistor density, but Dennard scaling ended.
- Voltage and frequency could no longer keep rising safely.
- Single-thread performance improved more slowly.
- Performance growth moved toward multicore CPUs, vector units, accelerators, and distributed systems.

## What are the main components of an HPC system?
- **Processors**: CPUs, GPUs, and other accelerators.
- **Memory**: active data storage close to computation.
- **Interconnects**: high-speed links between CPUs, GPUs, nodes, and racks.
- **Storage**: fast and capacity tiers for large datasets.
- **Software**: OS, schedulers, compilers, profilers, and parallel programming tools.

## What makes modern HPC systems heterogeneous?
Modern systems combine different compute and communication resources: multicore CPUs, GPUs, TPUs or NPUs, FPGAs, in-network computation, high-bandwidth memory, and specialized interconnects. The programmer must choose where each part of the workload should run.

## Why is communication expensive in HPC?
Communication moves data through memory hierarchies, PCIe/CXL links, inter-node networks, or storage. These movements are often much slower and more energy-expensive than arithmetic, so a program can have many available FLOPs and still be limited by data movement.

## What is the difference between HPL and HPCG as performance signals?
- **HPL** measures dense linear algebra performance and is used by TOP500.
- **HPCG** stresses sparse matrix and memory-access behavior closer to many simulations.
- A system can have huge HPL performance but a small fraction of peak on HPCG because real workloads often move sparse data irregularly.

## What does xFLOP/s measure?
xFLOP/s is a rate of floating-point operations per second. In these slides it usually refers to 64-bit floating-point additions and multiplications.

## What is theoretical peak performance?
Theoretical peak is a paper upper bound computed from hardware capabilities, such as number of cores, clock frequency, vector width, instructions per cycle, and whether FMA counts as two floating-point operations.

## Why does software not usually reach "good enough" performance by default?
Default code may use slow algorithms, poor memory locality, scalar instructions, too little parallelism, branchy control flow, or unnecessary data movement. Performance engineering can often produce orders-of-magnitude speedups.

## What are the three broad ways to write faster single-node HPC code?
1. **Optimize algorithms and data structures** to reduce work.
2. **Optimize memory access** to improve locality and data reuse.
3. **Exploit hardware parallelism** through SIMD, threads, and accelerators.

## What is operational intensity?
Operational intensity is the ratio:

`flops / bytes transferred`

It tells whether an application does many operations per byte moved. Low operational intensity usually points to memory bandwidth limits; high operational intensity is more likely to be compute limited.

## Why can an algorithmic change beat low-level optimization?
An algorithmic change can reduce the amount of work or data movement asymptotically. For example, counting sort can beat quicksort when integer keys have a limited range because the algorithm matches the data properties.

## What is the Instruction Set Architecture?
The ISA is the contract between software and hardware. It defines available instructions, registers, memory behavior, and extensions such as floating point, SIMD, tensor instructions, and AI-oriented numeric formats.

## How do load-store and register-memory ISAs differ?
- **Load-store ISAs** such as ARM or RISC-V access memory mainly through explicit load and store instructions.
- **Register-memory ISAs** such as x86 can perform some operations directly with memory operands.

## What is CPU pipelining?
Pipelining overlaps the execution of multiple instructions by splitting execution into stages. It improves throughput, but each individual instruction still has a latency through the whole pipeline.

## What is the difference between pipeline throughput and latency?
- **Throughput**: how many instructions complete per unit time.
- **Latency**: how long one instruction takes from start to finish.
- A pipeline can improve throughput without reducing the latency of a single instruction.

## What are the main pipeline hazards?
- **Structural hazards**: hardware resource conflicts.
- **Data hazards**: dependencies between instructions.
- **Control hazards**: branches or jumps change the instruction stream.

## What is a RAW dependency?
Read-after-write is a true dependency: an instruction needs a value produced by an earlier instruction. It can sometimes be helped with forwarding, but it cannot be eliminated by renaming.

## What are WAR and WAW hazards?
- **WAR**: write-after-read, a later instruction writes a register before an earlier instruction reads the old value.
- **WAW**: write-after-write, two instructions write the same register and order matters.
- These are false dependencies and can be eliminated with register renaming.

## What is out-of-order execution?
Out-of-order execution lets independent instructions execute when their operands and resources are ready, even if earlier instructions are stalled. Correctness is preserved by retiring instructions in program order.

## What is in-order retire?
In-order retire means instruction results become visible in the architectural state in original program order. This is what lets CPUs execute speculatively or out of order while preserving the program's observable behavior.

## What is a superscalar CPU?
A superscalar CPU can issue more than one instruction per cycle. Its issue width is the maximum number of instructions it can issue in the same cycle.

## What is the role of the Reorder Buffer?
The ROB tracks in-flight instructions, supports register renaming, records speculative state, allows out-of-order execution, and ensures instructions retire in program order.

## What is the role of the Reservation Station?
The Reservation Station holds micro-ops waiting for operands and execution resources. Once a micro-op is ready, it can be dispatched to a suitable execution port.

## Why do dependency chains limit IPC?
A dependency chain forces later instructions to wait for earlier results. Even on a wide superscalar CPU, the chain behaves sequentially and prevents the CPU from filling execution slots with independent work.

## What is speculative execution?
The CPU predicts a branch direction or target and executes instructions from that path before knowing whether the prediction is correct. Correct predictions save cycles; wrong predictions are squashed and cause a misprediction penalty.

## What is a branch misprediction?
A branch misprediction happens when the branch predictor guesses the wrong direction or target for a control-flow instruction. The CPU may already have fetched, decoded, and speculatively executed instructions from the wrong path, so those instructions must be discarded.

## How does the hardware recover from a branch misprediction?
The CPU detects the real branch outcome when the branch executes. If the prediction was wrong:
1. The Reorder Buffer prevents wrong-path instructions from retiring.
2. Speculative results from the wrong path are squashed.
3. The register-renaming state is restored to the correct checkpoint.
4. The frontend is redirected to fetch from the correct target.
5. The pipeline refills with correct-path instructions.

The lost cycles are the branch misprediction penalty. Deeper pipelines and wider speculation usually make this penalty more expensive.

## What structures are used by branch prediction?
- **BTB**: caches branch target addresses.
- **PHT**: stores past branch behavior, often with 2-bit counters.
- **RAS**: predicts return addresses for function calls.

## Why are 2-bit branch predictors more stable than 1-bit predictors?
A 1-bit predictor flips after one wrong outcome, so loop exits can cause two mispredictions. A 2-bit predictor changes direction only after two successive mispredictions, making it more robust for loops.

## What is simultaneous multithreading?
SMT runs multiple hardware threads on the same physical core. It duplicates architectural state such as registers and program counters, while sharing resources such as caches and execution units.

## What is the main performance risk of SMT?
SMT threads compete for shared resources, especially L1/L2 cache space, execution units, and bandwidth. This can make performance harder to predict and sometimes slower than running alone.

## What is a hybrid CPU architecture?
A hybrid CPU combines different core types, typically performance cores and efficiency cores. Scheduling must account for task priority, IPC, power, and whether a task should run on a fast core or a small efficient core.

## What is the principle of locality?
Programs tend to access a small part of their address space at a time:
- **Temporal locality**: recently used data is likely to be reused.
- **Spatial locality**: nearby data is likely to be accessed soon.

## What is a cache hit and a cache miss?
- A **hit** occurs when requested data is found in the current cache level.
- A **miss** occurs when it must be fetched from a lower, slower level.
- The miss penalty is the time needed to fetch the missing cache line.

## What is AMAT?
Average Memory Access Time is:

`AMAT = hit time + miss rate * miss penalty`

It shows why both cache hit latency and miss behavior matter for performance.

## How does direct-mapped cache placement work?
A memory block maps to exactly one cache location:

`cache index = block address modulo number of cache blocks`

This is simple and fast, but conflict misses can be frequent.

## How do fully associative and set-associative caches differ?
- **Fully associative**: a block can go anywhere, but searching all entries is expensive.
- **Set-associative**: a block maps to one set and can occupy any way inside that set, balancing flexibility and hardware cost.

## What are compulsory, capacity, and conflict cache misses?
- **Compulsory**: first access to a block.
- **Capacity**: working set is larger than the cache.
- **Conflict**: multiple active blocks compete for the same cache set.

## Why can larger cache blocks both help and hurt?
Larger blocks exploit spatial locality and can reduce misses. In a fixed-size cache, they also reduce the number of cache lines, increase pollution, and increase miss penalty.

## What is cache coherence?
Cache coherence ensures that multiple cores sharing memory see consistent values when they cache the same memory block. Protocols use mechanisms such as snooping or directories to track ownership and sharing.

## What is false sharing?
False sharing happens when different cores update different variables that reside on the same cache line. Coherence invalidates the whole line, so independent data causes unnecessary cache traffic.

## Why can memory bandwidth stop multicore scaling?
Adding cores increases demand on shared memory channels, last-level cache, and interconnects. Once memory bandwidth is saturated, more cores spend time waiting instead of doing useful work.

## What is memory interleaving?
Memory interleaving spreads adjacent addresses across multiple memory channels or devices. Fine-grained interleaving helps streaming bandwidth; coarse-grained interleaving can help NUMA-aware locality.

## What does virtual memory provide?
- Sharing physical memory among processes.
- Protection between processes.
- Relocation, so programs can run without knowing physical addresses.
- Paging, with page tables translating virtual addresses to physical addresses.

## What is a TLB?
The Translation Lookaside Buffer caches recent virtual-to-physical address translations. TLB misses require page-table walks and can become costly for large or random memory accesses.

## Why do huge pages reduce TLB pressure?
Huge pages cover more memory per translation, so fewer TLB entries are needed for the same working set. This increases TLB hit probability, but can increase fragmentation and allocation latency.

## What is NUMA?
Non-Uniform Memory Access means a processor can access memory attached to its own socket faster than memory attached to another socket. Placement and thread pinning matter because remote memory access is slower.

## What is the uncore?
The uncore includes CPU components outside individual cores, such as last-level cache, memory controllers, interconnects, PCIe/I/O controllers, and power-control logic. Memory-heavy workloads often stress the uncore.

## What is the Performance Monitoring Unit?
The PMU is the CPU hardware block used for performance analysis. It exposes:
- **Performance Monitoring Counters**: registers that count events such as cycles, retired instructions, cache misses, branch misses, stalls, or SIMD/FLOP events.
- **Event selection logic**: configures which microarchitectural event each counter counts.
- **Overflow interrupts**: trigger sampling when a counter reaches a threshold.
- **Extra tracing features** such as LBR, PEBS, and Processor Trace on Intel CPUs.

Profilers such as `perf`, VTune, and LIKWID program the PMU, run the workload, then read and interpret the collected counters.

## What are Performance Monitoring Counters?
PMCs are model-specific hardware registers that count selected CPU events. A tool configures an event, starts the program, lets the counter increment while the event occurs, then reads the final value.

Important details:
- There are only a few counters, but many possible events.
- If more events are requested than counters are available, tools multiplex events and scale the results.
- Counters can be used for aggregate counts (`perf stat`) or overflow-based sampling (`perf record`).
- Raw counts usually need to be converted into metrics such as IPC, MPKI, branch-miss rate, or TMA buckets.

## How does the PMU support sampling?
The profiler programs a counter with an event and a threshold. When the counter overflows, the PMU raises a Performance Monitoring Interrupt. The profiler records the instruction pointer, and sometimes call stack or precise-event information, then resets the counter and continues.

This is why sampling can answer: "Where in the code do most cycles, cache misses, or branch misses happen?"

## What is SIMD?
SIMD means Single Instruction Multiple Data: one instruction applies the same operation to multiple data elements packed in a vector register.

## Why does vector width matter?
Wider vector registers process more elements per instruction. For example, AVX-512 can operate on 512-bit registers, which can hold 8 double-precision values or 16 single-precision values.

## What are SIMD intrinsics?
Intrinsics are compiler-provided functions that map closely to SIMD instructions. They give low-level control while letting code remain in C/C++ rather than assembly.

## How are x86 SIMD intrinsic names structured?
They usually encode:
- register width, such as `_mm`, `_mm256`, or `_mm512`;
- operation, such as `add`, `mul`, or `cvt`;
- data type suffix, such as `ps`, `pd`, `epi32`, or `epu64`;
- optional modifiers, such as scalar or unaligned access.

## What are GCC/Clang extended vector types?
They are compiler extensions that let programmers define vector-sized types and write arithmetic directly on them. The compiler then emits SIMD operations for expressions such as `c = a + b`.

## Why does vector code need aligned memory?
Vector loads and stores operate on wide blocks. Proper alignment avoids penalties or faults for instructions that require aligned addresses, especially when using vector types or aligned load intrinsics.

## What are the three phases of compiler vectorization?
1. **Legality check**: prove the loop can be transformed safely.
2. **Profitability check**: estimate whether vectorization is faster.
3. **Transformation**: generate vector code plus scalar remainder and guards when needed.

## Why can autovectorization fail?
- Loop-carried dependencies.
- Pointer aliasing or memory overlap.
- Non-associative floating-point reductions.
- Non-contiguous or irregular memory access.
- Operations without efficient vector support.
- Compiler cost model decides vectorization is not profitable.

## How can programmers help vectorization?
- Use `__restrict__` when pointers do not alias.
- Use contiguous and aligned memory.
- Prefer SoA layouts for vector access.
- Avoid unnecessary branches, exceptions, and function calls in hot loops.
- Inspect compiler vectorization reports.

## Why can floating-point reductions block vectorization?
Floating-point addition is not strictly associative because rounding changes results. Reordering operations for SIMD can change numerical results unless the compiler is allowed to relax rules, for example with fast-math options.

## What does `-ffast-math` actually do?
`-ffast-math` lets the compiler relax strict IEEE floating-point semantics so it can apply more aggressive optimizations. It may assume, for example, that:
- operations can be reassociated, so `(a + b) + c` may become `a + (b + c)`;
- NaNs and infinities do not need full strict handling;
- signed zero distinctions are not important;
- floating-point exceptions and exact rounding behavior are not observable;
- reciprocal or approximate math transformations are acceptable.

This can enable vectorization and faster reductions, but results may differ numerically from strict IEEE execution.

## Why can `-ffast-math` help vectorize a floating-point sum?
A scalar floating-point sum has an order-dependent rounding behavior. SIMD reduction changes the order of additions. With strict math, the compiler may refuse that transformation; with `-ffast-math`, it can reassociate operations and use vector reductions.

## What is the risk of using `-ffast-math` in scientific code?
It can change numerical results, hide NaNs/Infs assumptions, remove strict exception behavior, and break algorithms that depend on exact IEEE semantics. It is useful only when the application tolerates small numerical differences and has been validated.

## What is the main vectorization lesson from the N-body lab?
Vectorization often requires changing data layout and dependencies, not just adding flags. The lab moves toward SoA layout and removes dependent memory updates so the compiler can use SIMD more effectively.

## What is LIKWID used for in the labs?
LIKWID accesses hardware counters and provides event groups such as `FLOPS_DP`, `MEM_DP`, cache, and energy metrics. It helps determine whether code is compute-bound, memory-bound, vectorized, or bandwidth limited.

## What are "speeds" and "feeds" in performance analysis?
- **Speeds**: how fast operations can execute, such as add, multiply, division, FMA, SIMD, and core throughput.
- **Feeds**: how fast data can be supplied through memory, caches, network, or disk.

## What is the Roofline model?
The Roofline model relates attainable performance to operational intensity. It shows whether a kernel is limited by memory bandwidth or compute peak, and whether optimization should move the point upward or to the right.

## How do optimizations move a point on a Roofline plot?
- Vectorization and threading can move the point upward by increasing compute throughput.
- Better locality and reuse increase operational intensity, moving the point to the right.
- Reducing data movement can improve both position and performance.

## Why are theoretical FLOPs and bandwidth rarely reached?
Theoretical values assume perfect alignment, full vectorization, no stalls, no cache misses, no synchronization, no OS interruptions, no thermal throttling, and ideal instruction mix. Real programs almost never satisfy all of these.

## What is IPC?
Instructions per cycle measures how many instructions retire per core cycle:

`IPC = retired instructions / core cycles`

Low IPC often suggests stalls; high IPC suggests good pipeline utilization, though it does not guarantee useful work.

## What is CPI?
Cycles per instruction is the inverse of IPC:

`CPI = cycles / retired instructions`

Higher CPI usually means more cycles are spent waiting or stalled per instruction.

## Why is IPC alone not enough to judge performance?
IPC does not say whether instructions are useful, vectorized, or doing enough work. A program can retire many cheap instructions in a spin loop or scalar code and still deliver poor application performance.

## What is L1MPKI?
L1 Misses Per Kilo Instructions measures L1 cache misses per 1000 instructions. High L1MPKI indicates poor locality and potential memory stalls.

## What is event-based sampling?
Event-based sampling uses hardware counters to trigger interrupts after a selected event count overflows. It helps locate hotspots for cycles, cache misses, branch misses, or TMA-related events.

## What is instrumentation-based profiling?
Instrumentation profiling inserts measurement code into the program. The inserted code marks regions, records timestamps, or reads counters at region boundaries.

Examples:
- LIKWID marker API around a hot function.
- VTune or uProf task markers.
- Manual timers around a code region.

It gives precise region-level measurements, but changes the program slightly and adds overhead.

## What is the difference between instrumentation and sampling?
- **Instrumentation** measures selected code regions explicitly. It is precise for those regions, but requires code changes or compiler/tool insertion and adds overhead.
- **Sampling** interrupts execution periodically or on PMU counter overflow. It needs fewer code changes and has lower overhead, but gives statistical results and may need enough samples to be reliable.

Use instrumentation when you already know the region of interest; use sampling to discover hotspots.

## How should you start profiling an unknown HPC program?
1. Measure wall-clock time and identify the workload/input.
2. Use a broad model such as Roofline to ask whether the kernel is memory-bandwidth-bound or compute-bound.
3. Use TMA or PMU metrics to classify the bottleneck: Frontend, Backend, Bad Speculation, or Retiring.
4. Use sampling (`perf record`, VTune, LIKWID, etc.) to localize the bottleneck to functions, lines, or instructions.
5. Apply an optimization that matches the bottleneck.
6. Re-run the same measurement to check whether the bottleneck moved or performance improved.

## When should you use Roofline instead of TMA?
Use **Roofline** to reason at the kernel/application level about arithmetic intensity, memory bandwidth, and compute peak. Use **TMA** to reason at the CPU pipeline level about why cycles are lost. They are complementary: Roofline tells "memory vs compute"; TMA tells "which microarchitectural resource is blocking progress."

## Why collect call stacks during profiling?
If a hot function is called from multiple places, call stacks reveal which caller paths are responsible. This helps optimize the right context instead of only the hot callee.

## What is Top-down Microarchitecture Analysis?
TMA is a hierarchy of event-based metrics that classifies CPU pipeline slot usage. It identifies whether execution is mainly Retiring, Frontend Bound, Backend Bound, or Bad Speculation.

## What do the four top-level TMA categories mean?
- **Retiring**: useful instructions are completing.
- **Frontend Bound**: the CPU cannot fetch/decode enough work.
- **Backend Bound**: execution or memory resources are overloaded.
- **Bad Speculation**: work was done on the wrong path and discarded.

## What is Level 1 in TMA?
Level 1 is the first coarse classification of pipeline slots into four buckets:
- **Frontend Bound**
- **Backend Bound**
- **Bad Speculation**
- **Retiring**

It answers: "Which major part of the CPU pipeline is limiting this workload?"

## What is Level 2 in TMA?
Level 2 drills into the dominant Level 1 bucket. For example:
- Frontend Bound can split into frontend latency and frontend bandwidth.
- Backend Bound can split into **Memory Bound** and **Core Bound**.
- Bad Speculation can split into branch mispredictions and machine clears.

It answers: "What kind of frontend, backend, or speculation problem is this?"

## What is Level 3 in TMA?
Level 3 drills into a Level 2 category to find a more specific cause. For example, Memory Bound can split into L1 Bound, L2 Bound, L3 Bound, DRAM Bound, and Store Bound; Core Bound can split into Divider and Port Utilization.

It answers: "Which concrete resource or memory level is responsible?"

## How are TMA Level 1 and Level 2 metrics usually expressed?
The top two TMA levels are usually expressed as a percentage of all pipeline slots. This makes the major buckets comparable and shows how the CPU pipeline is being used overall.

## How are deeper TMA levels such as Level 3 often expressed?
Starting from Level 3, metrics may be expressed in clocks or stall cycles instead of pipeline-slot percentages. At that point the goal is to analyze a specific bottleneck, not necessarily compare every bucket against every other bucket.

## Why does TMA use a "drill down" hierarchy?
The high-level buckets tell where to look first, but not the exact fix. The workflow is to identify the dominant Level 1 bottleneck, drill into Level 2 and Level 3 metrics, then sample on a related event to locate the problematic code.

## What does high Frontend Bound usually indicate?
High Frontend Bound means the backend could execute more work, but the frontend is not supplying decoded micro-ops fast enough. Causes include poor code layout, instruction-cache or uop-cache issues, frequent branching, code duplication, and unnecessary work.

## How can Frontend Bound problems be reduced?
- Improve code layout and locality, especially by co-locating hot code.
- Reduce branchy code.
- Reduce code size when possible.
- Use profile-guided optimization when available.
- Remove unnecessary work from hot paths.

## What does high Backend Bound usually indicate?
High Backend Bound means the frontend can supply work, but execution is stalled because backend resources are overloaded. It should be split into **Memory Bound** and **Core Bound** before deciding what to optimize.

## What should you do when Backend Bound is mostly Memory Bound?
Focus on moving data closer to the core and reducing memory stalls:
- improve locality and data layout;
- reduce random/scattered accesses;
- use blocking/tiling;
- avoid false sharing;
- consider prefetching or huge pages when appropriate.

## What should you do when Backend Bound is mostly Core Bound?
Look for execution-resource pressure:
- long dependency chains;
- divisions or special functions;
- port contention;
- limited floating-point/vector resources.

Possible fixes include breaking dependency chains, replacing expensive operations, vectorizing, or changing the algorithm.

## What does high Bad Speculation mean in TMA?
High Bad Speculation means the CPU executed work that did not retire, usually because it followed a wrong control-flow path. Typical causes are branch mispredictions and machine clears.

## How can Bad Speculation be reduced?
- Use profile-guided optimization.
- Avoid unpredictable indirect branches when possible.
- Simplify branch-heavy hot paths.
- Remove error conditions or memory-ordering situations that cause machine clears.

Fixing Bad Speculation can also reduce Frontend Bound because fewer wrong-path instructions must be fetched and decoded.

## What does high Retiring mean in TMA?
High Retiring means many pipeline slots are producing instructions that retire. This is usually good, but it only says instructions are retiring, not that they are doing useful high-level work efficiently.

In an oral exam, the important nuance is: high Retiring means the CPU is not mostly stalled, but the code may still be inefficient at the algorithmic level.

## Why can high Retiring still hide a performance problem?
A program can retire many instructions while doing low-value work, such as spinning on a lock, executing scalar code that should be vectorized, or using microcoded operations. If Retiring is high but performance is poor, inspect whether the hot loop is doing useful vectorized work.

## What practical situation can cause high Frontend Bound?
A large branch-heavy parser, interpreter, virtual-dispatch-heavy OOP code, or code with poor instruction-cache locality can be Frontend Bound. The backend could execute more, but the frontend cannot fetch, predict, decode, or deliver enough useful uops.

Example symptoms:
- many small functions;
- indirect calls or virtual calls;
- unpredictable branches;
- large hot code footprint.

## What practical situation can cause high Backend Bound?
A stencil, graph traversal, sparse matrix-vector multiply, or random hash-table lookup can be Backend Bound because the core waits for memory. A tight floating-point loop with many divisions can also be Backend Bound, but as **Core Bound** rather than Memory Bound.

Example interpretation:
- random accesses missing all caches -> Memory Bound / DRAM Bound;
- many divisions in a hot loop -> Core Bound / Divider;
- many independent operations fighting for the same execution ports -> Core Bound / Port Utilization.

## What should you do if both Frontend Bound and Backend Bound are high?
Treat the program as having multiple relevant bottlenecks. Start with the larger bucket, drill down, and fix the most actionable cause. Then measure again, because removing one bottleneck can expose the other more clearly.

## What happens if TMA shows high Frontend Bound and high Core Bound?
The CPU is both undersupplied by the frontend and limited by execution resources when work reaches the backend. Typical actions are to reduce branch/code-layout problems for the frontend and inspect hot loops for divisions, dependency chains, vectorization failure, or port contention.

## What is the difference between bottleneck identification and bottleneck localization in TMA?
- **Identification**: use TMA metrics to classify the bottleneck, such as Backend Bound -> Memory Bound -> DRAM Bound.
- **Localization**: sample on a related event, such as an L3-miss precise event, to find the function, source line, or assembly instruction causing it.

## In the TMA cache-miss case study, how does the analysis drill down?
The example starts with high Level 1 Backend Bound, then Level 2 shows Memory Bound, then Level 3 shows DRAM Bound. This means many loads miss all cache levels and reach main memory.

## Why does a DRAM Bound result suggest prefetching in the TMA case study?
The problematic access is random and misses cache, but the code has independent dummy work between computing the address and loading it. Issuing a prefetch before that work gives memory more time to arrive before the load is used.

## What is Store Bound in TMA?
Store Bound is a Memory Bound subcategory related to store pipeline pressure or dependencies involving stores. It can indicate cases where loads depend on earlier stores or where store resources are limiting progress.

## What do the Divider and Port Utilization metrics tell you?
- **Divider** indicates cycles where divider hardware is heavily used.
- **Port Utilization** indicates competition for execution ports or specific execution units.

Both are Core Bound signals rather than memory hierarchy signals.

## What is the standard TMA workflow?
1. Identify the bottleneck category with top-level metrics.
2. Drill down into more specific metrics.
3. Sample on a bottleneck-related event to locate code.
4. Change the code.
5. Measure again.

## What does DRAM Bound mean in TMA?
DRAM Bound means many memory accesses miss in cache and go to main memory, causing stalls while the CPU waits for data. Optimizations should improve locality, prefetching, blocking, or data layout.

## What is a precise event?
A precise event identifies the instruction that caused a sampled hardware event. Intel PEBS can provide precise instruction pointers for some events, reducing the ambiguity of interrupt-based sampling.

## Why can prefetching fix a DRAM-bound bottleneck?
Prefetching starts the memory request earlier. If enough independent work happens before the load is needed, cache-miss latency can be hidden.

## What does Core Bound mean in TMA?
Core Bound means execution resources are the bottleneck, not memory. Common causes include divider pressure, special functions, port contention, and long data dependencies.

## Why did replacing division/square root with `rsqrt` help the N-body example?
The N-body kernel was core-bound due to expensive floating-point division/square-root operations. Approximate reciprocal square root uses vector hardware more efficiently and reduces divider pressure, with refinement if more precision is needed.

## What is data-oriented design?
Data-oriented design focuses on data layout and data movement. It prioritizes arrays, cache lines, contiguous memory, and operations on data already in cache rather than object-centered call structure.

## Why can object-oriented layout hurt HPC performance?
OOP-style code can create deep call stacks, heap allocation, indirect virtual calls, poor cache locality, and branch mispredictions. These costs matter when processing large collections of objects.

## What is the difference between AoS and SoA?
- **AoS**: Array of Structures, where each object stores all fields together.
- **SoA**: Structure of Arrays, where each field has its own contiguous array.
- SoA is often better for SIMD and cache locality when loops process one field across many elements.

## What are the cache effects of AoS versus SoA?
With **AoS**, each cache line contains several fields of a few objects. If a loop needs only one field, it still loads the other fields, wasting bandwidth and cache capacity. Padding inside structures can waste even more cache space.

With **SoA**, the same field for many elements is contiguous. A cache line contains mostly useful values for that loop, hardware prefetching works better, and SIMD loads are simpler.

AoS can still be good when each loop uses most fields of each object together; SoA is usually better when one operation scans one or a few fields across many objects.

## Why does SoA often vectorize better than AoS?
SoA places same-field values contiguously, so vector loads can fetch consecutive values. AoS may require gather/scatter operations or load unused fields, wasting bandwidth and vector lanes.

## What is the difference between low-level and high-level loop optimizations?
- **Low-level optimizations** usually transform a single loop and are often done by the compiler.
- **High-level optimizations** change the structure of nested loops and often require manual reasoning about legality and performance.

## Why are loop optimizations important in HPC?
Hot loops dominate many high-performance programs. Small changes to dependency chains, memory access order, vectorization, or cache reuse can strongly affect runtime.

## What are examples of low-level loop optimizations?
- Loop Invariant Code Motion.
- Loop Unrolling.
- Loop Strength Reduction.

These usually modify the body or induction logic of one loop.

## What is Loop Invariant Code Motion?
Loop Invariant Code Motion moves computations that do not change across iterations outside the loop, avoiding repeated work.

Example: if `scale * dt` is the same for every iteration, compute it once before the loop instead of recomputing it for every array element.

## What is Loop Strength Reduction?
Loop Strength Reduction replaces expensive operations with cheaper ones, often by using induction variables. For example, replacing repeated `i * 10` address arithmetic with a variable that increments by `10`.

## Why can loop unrolling improve performance?
Loop unrolling performs multiple iterations per loop body. It reduces branch overhead and can create independent accumulators or operations, increasing instruction-level parallelism and helping hide latency.

## When can loop unrolling hurt performance?
Too much unrolling can increase register pressure, code size, and instruction-cache pressure. If registers spill to memory, the loop can become slower.

## What are examples of high-level loop optimizations?
- Loop Interchange.
- Loop Blocking or Tiling.
- Loop Fusion.
- Loop Distribution or Fission.
- Loop Unroll and Jam.

These often restructure nested loops and affect memory locality.

## Why are high-level loop optimizations harder for compilers?
The compiler must prove that changing loop order or structure preserves program semantics and is profitable. Dependencies, imperfect loop nests, aliasing, and complex memory access patterns make this difficult.

## What is loop interchange?
Loop interchange swaps nested loop order to improve memory access order, usually making accesses sequential in memory. It requires legal dependencies and often works best with perfectly nested loops.

## When is loop interchange useful?
It is useful when changing loop order makes multidimensional array accesses sequential in memory. This improves spatial locality and can reduce memory latency and bandwidth bottlenecks.

## Why do imperfect loop nests make loop interchange harder?
Interchange is easiest when loops are perfectly nested. Statements before, between, or after inner loops may need to be split, moved, or promoted to temporary arrays before the transformation is legal.

## What is loop blocking or tiling?
Tiling splits a multidimensional iteration space into smaller blocks that fit in cache. Instead of sweeping an entire large matrix or grid at once, the program works on a tile, reuses its data while it is still in cache, then moves to the next tile.

The goal is to reduce memory traffic by increasing temporal locality.

## When is loop blocking or tiling useful?
Tiling is useful when a loop repeatedly accesses a working set larger than cache. By operating on blocks that fit in private caches, it improves temporal locality and reduces memory traffic.

## How does tiling work in practice?
Suppose a loop repeatedly combines rows and columns of large matrices. Without tiling, data may be loaded, used once, evicted, and later loaded again. With tiling:
1. Choose a block size that fits the target cache.
2. Iterate over outer tile coordinates.
3. For each tile, run the original computation on only that block.
4. Reuse loaded values many times before leaving the tile.

If the tile is too large, it does not fit in cache; if too small, loop overhead and poor vector utilization can dominate.

## What is loop fusion?
Loop fusion combines loops over the same range when dependencies allow it. It can reduce loop overhead and improve temporal locality by reusing data while it is still hot.

## When is loop fusion useful?
Fusion is useful when separate loops traverse the same arrays and can reuse data if executed together. It reduces loop overhead and can keep data hot in cache.

## What is loop fission?
Loop fission splits one loop into multiple loops. It can reduce register pressure, cache contention, and instruction-cache pressure, and may let the compiler optimize each smaller loop separately.

## When is loop fission useful?
Fission is useful when a loop body does too much independent work at once. Splitting it can reduce register pressure, improve instruction-cache behavior, reduce cache contention, or allow different loops to be vectorized separately.

## What is loop unrolling?
Loop unrolling performs multiple iterations per loop body. It can increase instruction-level parallelism, reduce branch overhead, and break some dependency chains by using multiple accumulators.

## What is loop unroll and jam?
Loop unroll and jam unrolls an outer loop, then fuses the resulting inner loop bodies. It can increase data reuse and instruction-level parallelism in nested loops, but it must respect dependencies and register pressure.

## How can you discover loop optimization opportunities?
- Read compiler optimization reports.
- Inspect generated machine code.
- Use TMA to identify memory latency, memory bandwidth, or compute limits.
- Use Roofline analysis to see whether the loop is memory-bound or compute-bound.
- Apply the transformation that matches the measured bottleneck.

## Which loop optimizations are suggested by memory latency or bandwidth bottlenecks?
Use transformations that improve locality and reduce data movement, such as loop interchange, tiling, fusion when it improves reuse, SoA data layout, prefetching, and reducing non-contiguous accesses.

## Which loop optimizations are suggested by compute or dependency-chain bottlenecks?
Use transformations that increase independent work or reduce expensive operations, such as unrolling with multiple accumulators, vectorization, strength reduction, replacing division/special functions, or changing the algorithm.

## What is the shortcut problem in the lab?
Given a complete directed graph with edge costs `d[i][j]`, compute the cheapest path from each `i` to each `j` using at most two edges:

`r[i][j] = min_k(d[i][k] + d[k][j])`

## What optimization sequence was used for the shortcut problem?
1. Parallelize the outer loop with OpenMP.
2. Improve memory access by transposing data for linear reads.
3. Break dependency chains and expose ILP.
4. Use SIMD vectorization.
5. Reuse data in registers through tiling.

## Why did transposing the matrix help the shortcut problem?
The baseline reads one matrix dimension linearly and the other by columns. Transposing allows both streams to be read linearly, which matches cache lines and hardware prefetching.

## Why did tiling improve the shortcut problem?
Tiling computes multiple output elements together, reusing loaded rows and columns in registers. This reduces memory traffic and increases operational intensity.

## What is sparsity?
Sparsity means many values are zero or absent. Exploiting sparsity avoids storing and computing on zero values, often reducing work and memory footprint dramatically.

## What arrays define Compressed Sparse Row format?
- `values[]`: all nonzero values.
- `col_index[]`: column index for each nonzero value.
- `row_ptr[]`: prefix sums that mark where each row starts and ends.

## Why is CSR useful for sparse matrix-vector multiplication?
CSR stores only nonzero values and row boundaries. Each row can be processed independently, and the FLOP count is proportional to the number of nonzeros: roughly `2 * nnz`.

## What are Explicit Huge Pages?
Explicit Huge Pages are reserved huge pages exposed through `hugetlbfs` or `mmap` with huge-page flags. They avoid fragmentation at runtime and reduce TLB pressure, but statically consume memory.

## What are Transparent Huge Pages?
Transparent Huge Pages let Linux try to promote normal pages into huge pages automatically. They are convenient, but system-wide THP can affect other processes and allocation latency can be nondeterministic.

## When is software prefetching useful?
Software prefetching is useful when access patterns are too irregular for hardware prefetchers but the program can know future addresses early enough. The prefetch distance must be far enough to hide latency but not so far that it pollutes cache.

## What path does a received packet normally take inside an end host?
A received packet normally follows this path:
1. The NIC receives the packet from the wire and stores it in NIC memory.
2. The NIC fetches a descriptor from its RX queue to know which host packet buffer to use.
3. The NIC performs DMA over PCIe to copy packet data into host memory.
4. The NIC signals completion, often through an interrupt or polling-visible descriptor update.
5. The driver reads the descriptor ring and creates or attaches an `sk_buff`.
6. The packet goes through kernel processing such as GRO, Netfilter, and TCP/IP.
7. In-order data is appended to the socket receive queue.
8. The application reads from the socket, copying payload data from kernel buffers to a user-space buffer.

## What is DMA in end-host networking?
Direct Memory Access lets the NIC move packet data into host memory over PCIe without CPU copying. The NIC uses descriptors from RX queues to know where packet buffers are located.

## What mechanism does the NIC use to write a received packet into kernel memory?
The NIC uses **DMA** plus **descriptor rings**:
1. The kernel allocates packet buffers in host memory.
2. The driver writes descriptors into the NIC RX queue. Each descriptor points to an available buffer.
3. When a packet arrives, the NIC takes a descriptor and DMA-writes the packet into that buffer over PCIe.
4. The NIC marks the descriptor as completed and notifies the driver via interrupt or polling.
5. The driver wraps the buffer in an `sk_buff` and passes it to the kernel network stack.

## Why are descriptor rings important for NIC receive paths?
Descriptor rings contain pointers to available packet buffers. The driver fills RX queues with descriptors, the NIC consumes them for DMA, and the driver later recycles descriptors after packets are processed.

## What are interrupt mitigation strategies?
NICs can reduce interrupt overhead by batching packets or delaying interrupts. This lowers CPU overhead but can increase packet latency.

## What is Receive-Side Scaling?
RSS spreads packet processing across multiple RX queues and CPU cores, usually by hashing packet headers. It helps scale network receive processing while keeping packets from the same flow on the same core.

## What is Data Direct I/O?
Data Direct I/O allows device DMA traffic to target CPU cache rather than only main memory. This can reduce memory traffic and latency for packet processing.

## Why does PCIe packetization matter for networking performance?
PCIe transfers are packetized into transaction layer packets with headers and overhead. Larger transfers make protocol overhead less painful, which is why offloads such as TSO, UFO, GRO, and LRO can help.

## What is CXL and why is it relevant?
CXL is a PCIe-compatible interconnect standard that targets lower latency and cache-coherent access between CPUs and devices. It includes protocols for I/O, device access to host cache/memory, and host access to device memory.

## What is `sk_buff`?
`sk_buff` is the Linux kernel packet data structure. It stores pointers to packet data, header positions, metadata, device information, timestamps, and fields used by the network stack.

## Why does `sk_buff` use headroom and tailroom?
Headroom and tailroom let the kernel add or remove headers by moving pointers within the buffer, avoiding unnecessary allocation and copying.

## What is GRO?
Generic Receive Offload merges related incoming packets into fewer socket buffers early in the receive path. Later stack stages process fewer `sk_buff` objects, reducing overhead.

## What does Netfilter provide?
Netfilter is the kernel framework for packet filtering, NAT, port translation, and connection tracking. Tools such as iptables use it to implement firewall policies.

## Why does the kernel copy packet payloads to user space?
The kernel copies payloads from socket buffers to user-space buffers to protect kernel memory and preserve isolation. Inside the kernel, much processing uses metadata and pointer manipulation instead of payload copies.

## Why are `sk_buff` allocation and processing expensive?
`sk_buff` is a rich metadata structure used by many kernel networking layers. Allocating it, initializing fields, moving it through GRO, Netfilter, TCP/IP, queues, and socket logic adds per-packet overhead. This is why batching/offloads such as GRO/LRO/TSO and jumbo frames can help: fewer packet objects need to be processed.

## What is DPDK?
DPDK is a set of user-space libraries and drivers that bypass the Linux kernel network stack. It lets the NIC DMA packets directly into user-space memory and uses poll-mode drivers.

## What is the main tradeoff of DPDK?
DPDK is fast, but bypassing the kernel gives up normal kernel services such as TCP/IP stack processing, firewalling, `tcpdump`, `ping`, and standard interface management. It can also dedicate a NIC port to one application.

## What is RDMA?
Remote Direct Memory Access lets one machine access memory on another machine without normal kernel-stack involvement in the data path. It provides high throughput, low latency, low CPU use, and zero-copy transfers.

## What are one-sided and two-sided RDMA operations?
- **One-sided**: RDMA read, write, or atomic. The initiator specifies the remote memory address and the receiver CPU is passive.
- **Two-sided**: send/receive. The receiver posts receive buffers, similar to a message API.

## How does an RDMA write work?
In an RDMA write, the sender is active and the receiver is passive:
1. The receiver has registered a memory region and shared the remote address and key.
2. The sender posts a work request describing the local buffer, remote address, size, and permissions.
3. The sender NIC reads local memory and sends data over the RDMA transport.
4. The receiver NIC writes the data directly into the registered remote memory.
5. The receiver CPU does not execute a receive operation and may not be notified unless the protocol/application adds notification.
6. The sender gets a completion when the operation is acknowledged.

## How does an RDMA read work?
In an RDMA read, the initiator pulls data from remote memory:
1. The remote side registers memory and shares address/key information.
2. The initiator posts an RDMA read work request.
3. The initiator NIC asks the remote NIC for the specified remote memory range.
4. The remote NIC reads its local registered memory and sends the data back.
5. The initiator NIC writes the data into the initiator's local buffer.
6. The initiator receives a completion; the remote CPU is not involved in the data movement.

## What happens when an application registers RDMA memory?
The application pins memory so it cannot be swapped, gives the NIC address-translation information, and sets permissions. The NIC can then safely DMA to or from that memory region.

## What RDMA queues are used for communication?
RDMA uses send queues, receive queues, and completion queues. Work Request Elements describe operations, and Completion Queue Elements notify the application when work is done.

## What is a SmartNIC?
A SmartNIC is a programmable NIC that can offload more than packet movement, such as transport processing, filtering, crypto, compression, or custom packet-processing logic.

## How do FPGA and SoC SmartNICs differ?
- **FPGA SmartNICs** are highly reconfigurable and can approach ASIC-like performance, but are harder to program and can be expensive.
- **SoC SmartNICs** combine fixed-function accelerators with general-purpose cores, making programming easier at some performance or flexibility tradeoff.

## What problem does eBPF solve?
eBPF lets programs extend kernel behavior at runtime without recompiling the kernel or maintaining custom kernel modules. It supports safe, event-driven kernel programmability.

## What are the key features of eBPF?
- Runtime bytecode injection.
- Safety through verification and sandboxing.
- Efficient execution in kernel space.
- Event hooks for networking, tracing, observability, scheduling, and other kernel events.

## What is an eBPF hook point?
A hook point is a kernel event where an eBPF program can run. Networking examples include XDP, Traffic Control, and SK_SKB.

## Why is XDP a high-performance eBPF hook?
XDP runs at the driver level before `sk_buff` allocation. It can drop, redirect, or pass packets very early, avoiding expensive kernel processing for packets that do not need it.

## Why is XDP better suited to stateless protocols than arbitrary TCP manipulation?
XDP runs before much of the TCP/IP stack. Dropping or modifying TCP packets there can corrupt connection state, while stateless protocols such as UDP are easier to handle safely.

## What is AF_XDP?
AF_XDP sockets let XDP redirect selected frames to a user-space memory buffer. This provides a Linux kernel-bypass path while still allowing other traffic to continue through the normal kernel stack.

## How does AF_XDP differ from DPDK conceptually?
DPDK sends all owned-port traffic directly to user space. AF_XDP can split traffic: some packets bypass the kernel to user space, while others continue through normal kernel processing.

## What are eBPF maps?
Maps are typed key-value data structures used by eBPF programs. They can share data between kernel and user space, store configuration, export statistics, or share state between eBPF programs.

## What is the eBPF toolchain?
Restricted C or another supported language is compiled by Clang/LLVM into eBPF bytecode. The kernel verifier checks safety, then the bytecode runs through an interpreter or JIT at the chosen hook point.
