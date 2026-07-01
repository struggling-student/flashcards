# HPC Part 2 Flashcards

## What is the central performance problem in modern multi-GPU HPC systems?
Data movement is one of the main bottlenecks. Performance depends not only on FLOPs, but also on moving data efficiently within a node, between GPUs, between CPU and GPU, and across scale-out networks.

## Why can HPCG performance be much lower than HPL performance?
HPL is dense linear algebra and reaches high FLOP rates. HPCG stresses sparse computation and data movement, so performance can be much lower because memory access, communication, and irregularity dominate.

## What are the main strategies for improving HPC system efficiency?
- Improve data movement within the node.
- Use non-traditional architectures for data reuse.
- Use reduced precision when acceptable.
- Improve data movement between nodes through scale-out and scale-up networks.
- Use programming models and APIs that expose communication efficiently.

## Why are GPUs well suited for machine learning workloads?
- ML is data intensive and GPUs provide high memory bandwidth.
- ML uses many matrix multiplications and convolutions.
- Matrix operations expose massive parallelism.
- Specialized GPU units, such as tensor cores, accelerate common ML kernels.

## What is the von Neumann bottleneck?
It is the cost caused by separating processing from memory. Instructions operate on data in registers, but data must be fetched from memory and written back through an interconnect whose bandwidth and latency limit performance.

## Why do accelerators trade programmability for efficiency?
General-purpose CPUs are easier to program but less energy efficient for specialized workloads. GPUs, FPGAs, ASICs, tensor cores, and TPUs become more efficient by specializing hardware around common patterns, but they usually require more specialized programming.

## What are tensor cores?
Tensor cores are GPU hardware units optimized for matrix-matrix operations. They exploit data reuse and perform many fused multiply-add operations with less global memory traffic than a traditional scalar/vector implementation.

## Where does the performance gain of tensor cores come from?
The gain comes from both parallel execution of multiple operations and, more importantly, avoiding repeated global memory loads and stores by streaming data directly through the matrix-multiply hardware.

## What is a systolic array?
A systolic array is a spatial/dataflow architecture where processing elements pass data rhythmically to neighbors. It is useful for matrix operations because data can be reused locally while computation flows through the array.

## What is a TPU?
A Tensor Processing Unit is a domain-specific accelerator introduced by Google for tensor operations. Its key unit is a matrix multiplication unit based on dataflow/systolic-array ideas rather than a standard von Neumann execution model.

## What is a spatial or dataflow architecture?
It is an architecture where computation is mapped spatially onto many processing elements and data moves between them. The focus is on local data movement and cooperation between cores rather than repeatedly fetching operands from a central memory hierarchy.

## Why is reduced precision attractive but controversial in HPC?
Reduced precision increases throughput and lowers memory traffic, which is valuable for AI. Traditional HPC applications may require high numerical accuracy, so FP16, BF16, FP8, or INT formats are not always acceptable.

## What is a scale-out network?
A scale-out network connects compute nodes across a cluster. Examples include InfiniBand, RoCE, Slingshot, OmniPath, and future Ultra Ethernet systems.

## What is a scale-up network?
A scale-up network connects accelerators and processors inside a tightly coupled system or node. Examples include NVIDIA NVLink, AMD Infinity Fabric, Scale-Up Ethernet, and UALink.

## Why does GPU placement matter inside a node?
Not all GPU pairs have the same bandwidth or path. Some pairs may have more NVLink connections or a shorter path, so mapping ranks and communication patterns to hardware topology affects performance.

## What is the difference between scale-up and scale-out communication?
- **Scale-up**: communication inside a node or tightly coupled GPU system, usually higher bandwidth and lower latency.
- **Scale-out**: communication between nodes through the cluster network, usually longer paths and higher latency.

## Why are modern interconnects a major cost and power concern?
As systems scale, networking can become a large fraction of system power and cost. Slides note that network power/cost can now be around 30% or more, while optical networks may improve range and power at higher cable cost.

## What is the role of MPI in the multi-GPU software stack?
MPI is the standard message-passing interface for communication between processes. In multi-GPU programs, it often coordinates one process per GPU and performs point-to-point or collective communication.

## What are GPU collective communication libraries?
GPU collective communication libraries, such as NCCL or RCCL, provide GPU-centric communication primitives optimized for GPU buffers, topology, and collective operations.

## Why can NCCL be simpler or faster than MPI for GPU communication?
NCCL avoids many general MPI features such as tags, wildcards, and custom datatypes, and focuses on GPU buffers, streams, and topology-aware collectives. This specialization can improve efficiency.

## What are the main advantages of MPI over NCCL-like libraries?
- MPI is a standard.
- MPI is portable across vendors and systems.
- MPI is mature and reliable at large scale.
- NCCL is NVIDIA-specific, while equivalent libraries differ across vendors.

## What is GPUSHMEM?
GPUSHMEM refers to PGAS-style GPU libraries implementing OpenSHMEM-like models. GPUs access a partitioned global address space through one-sided put/get operations and may use host-side or device-side APIs.

## What is the difference between MPI and PGAS communication?
MPI is message passing between processes. PGAS exposes a partitioned global address space where each process or GPU owns a partition, but remote memory can be accessed with one-sided operations.

## Why would you use MPI in the multi-GPU assignment?
Use MPI for the standard distributed-programming layer:
- launching and identifying ranks;
- one process per GPU;
- mapping ranks to local GPUs;
- exchanging control information;
- interoperability with cluster job launchers;
- reductions or scalar collectives where CPU-side MPI is cheap and portable.

MPI is the safest portable baseline, especially when the communication pattern is simple or when vendor-specific GPU communication is not required.

## Why would you use CUDA-aware MPI instead of regular MPI?
CUDA-aware MPI lets MPI send and receive GPU memory pointers directly. This avoids explicit `cudaMemcpy` staging through host buffers and can use GPUDirect P2P or GPUDirect RDMA when supported.

The key benefit is simpler code and fewer data copies; the limitation is that MPI communication is usually still issued by the CPU and is not naturally ordered inside CUDA streams.

## Why would you use NCCL in the multi-GPU assignment?
Use NCCL when communication is between NVIDIA GPU buffers and benefits from GPU-centric, topology-aware, stream-aware communication. In the Jacobi assignment this fits halo exchange with `ncclSend`/`ncclRecv`, and possibly reductions with `ncclAllReduce`.

NCCL is attractive because communication is enqueued on CUDA streams, can overlap with kernels, and uses optimized algorithms for NVLink, PCIe, NICs, and multi-GPU topology.

## Why would you use NVSHMEM in the multi-GPU assignment?
Use NVSHMEM when a one-sided PGAS model makes communication easier or more GPU-centric. In Jacobi, each GPU can directly put boundary rows into the neighbor's symmetric halo memory instead of matching sends and receives.

NVSHMEM is especially interesting when communication can be stream-ordered or device-initiated from GPU kernels, reducing CPU synchronization and offload overhead.

## How should you choose between MPI, NCCL, and NVSHMEM?
- **MPI**: best baseline for portability, rank management, CPU-side control, and standard collectives.
- **CUDA-aware MPI**: good when you want MPI semantics but direct GPU buffers.
- **NCCL**: best for NVIDIA GPU-buffer collectives or stream-aware GPU send/receive.
- **NVSHMEM**: best for one-sided puts/gets, PGAS-style algorithms, and GPU-initiated communication.

The choice depends on communication pattern, portability needs, synchronization cost, overlap opportunities, and whether communication should be CPU-initiated or GPU-initiated.

## Why is MPI still useful when NCCL or NVSHMEM handles GPU communication?
MPI is still useful for launching and organizing the distributed program: ranks, communicators, node-local rank discovery, job-launcher integration, configuration exchange, and portable scalar collectives.

In many good solutions, MPI is the control plane while NCCL or NVSHMEM is the GPU communication plane.

## What are the main communication-strategy arguments in a multi-GPU program?
When choosing a communication strategy, argue from:
- **communication pattern**: nearest-neighbor halo, allreduce, alltoall, irregular exchange;
- **message size and granularity**: large contiguous messages versus many small updates;
- **data location**: CPU buffers or GPU buffers;
- **synchronization**: global barriers, stream ordering, per-peer flags, or device-side waits;
- **topology**: same node, NVLink, PCIe, inter-node network;
- **overlap**: whether communication can run while useful computation continues;
- **portability**: standard MPI versus vendor-specific GPU libraries.

Good oral answers should connect the API choice to these constraints.

## Why might you choose NCCL instead of NVSHMEM for Jacobi halo exchange?
Choose NCCL when the halo exchange is regular, paired, and GPU-buffer based. Top and bottom rows are contiguous messages, so `ncclSend`/`ncclRecv` express the exchange clearly, are ordered on CUDA streams, and avoid explicit host synchronization when used with events and high-priority streams.

This gives a simpler argument than NVSHMEM if you do not need one-sided access or device-side communication inside the kernel.

## Why might you choose NVSHMEM instead of NCCL for Jacobi halo exchange?
Choose NVSHMEM when the algorithm is naturally one-sided: each GPU computes a boundary row and directly writes it into the neighbor's symmetric halo buffer. This avoids receive matching and can move communication closer to GPU execution.

NVSHMEM becomes especially attractive if you want stream-ordered puts, GPU-initiated communication, per-peer flags/counters, or finer-grained overlap inside kernels.

## When is MPI the wrong communication strategy?
MPI is less attractive when communication is on the critical path between GPU kernels and requires frequent host synchronization. Even CUDA-aware MPI can know that a pointer is a GPU pointer, but the communication call is usually CPU-initiated and not naturally part of CUDA stream dependency graphs.

In those cases, NCCL or NVSHMEM may reduce synchronization and improve overlap.

## When is NCCL the wrong communication strategy?
NCCL is less attractive when portability across GPU vendors is required, when the communication is CPU/control-heavy, when the message is extremely tiny and a CPU-side MPI collective is cheaper, or when the algorithm is naturally one-sided and irregular.

NCCL is strongest for NVIDIA GPU buffers, stream-aware send/receive, and optimized collectives.

## When is NVSHMEM the wrong communication strategy?
NVSHMEM can be a poor fit if symmetric-memory constraints are awkward, if the code needs standard portability, if synchronization becomes too complex, or if the algorithm is a simple collective already optimized by NCCL/MPI.

It shines when the algorithm maps naturally to one-sided remote memory access or GPU-initiated communication.

## What communication strategy should you use for Jacobi halo exchange?
Compute boundary rows early, communicate them while the inner domain is computed, and use stream/event dependencies to avoid races.

A good strategy is:
1. Reset convergence/norm data.
2. Compute top and bottom boundary rows in high-priority streams.
3. Start halo exchange as soon as boundary rows are ready.
4. Compute the inner domain in a separate stream.
5. Synchronize only where data dependencies require it.

This reduces idle GPU time and hides communication behind useful computation.

## What is CUDA-aware MPI?
CUDA-aware MPI allows MPI calls to use GPU memory pointers directly as send or receive buffers. The application does not need to manually copy data through host buffers.

## Why is CUDA-aware MPI useful?
It simplifies code and can avoid extra host-device copies. With GPUDirect, it can transfer data directly between GPU memory and the network or another GPU.

## What is the common process mapping for MPI plus CUDA?
The common practice is one MPI process per GPU. Each rank selects its local GPU, often using an MPI communicator split by shared-memory node to compute a local rank.

## How can MPI ranks select GPUs on a node?
Use `MPI_Comm_split_type` with `MPI_COMM_TYPE_SHARED` to create a local communicator, get the local rank, query device count, and call `cudaSetDevice(local_rank % num_devs)`.

## What problem does CUDA Unified Virtual Addressing solve?
UVA gives CPU and GPU memory a unified virtual address space. Libraries can inspect a pointer and determine whether it points to host or GPU memory, simplifying APIs such as CUDA-aware MPI.

## What is GPUDirect P2P?
GPUDirect peer-to-peer allows GPUs in the same system to communicate directly when hardware topology supports it, avoiding unnecessary staging through host memory.

## What is GPUDirect RDMA?
GPUDirect RDMA lets a network adapter access GPU memory directly for inter-node communication, reducing CPU involvement and avoiding host staging copies.

## What happens with regular non-CUDA-aware MPI?
The application copies data from GPU to host, sends host buffers through MPI, receives into host buffers, and copies data back to GPU. These extra copies increase latency and reduce bandwidth.

## What is the Jacobi solver used for in the multi-GPU examples?
It solves a 2D Laplace equation iteratively. The domain is decomposed across GPUs, and each iteration updates grid points using neighboring values, requiring halo or boundary exchange.

## What is domain decomposition?
Domain decomposition splits the simulation grid across processes or GPUs. Each process computes its local subdomain and exchanges boundary data with neighbors.

## What is the tradeoff in choosing a domain decomposition?
- Minimizing neighbor count reduces latency-sensitive communication.
- Minimizing surface-to-volume ratio reduces total communicated data.
- Contiguous boundaries are easier and cheaper to transfer than non-contiguous ones.

## Why are top and bottom Jacobi boundaries easier to exchange than left and right boundaries?
Top and bottom rows are contiguous in row-major memory, so they can be sent directly. Left and right columns are non-contiguous, so they often require packing and unpacking or derived datatypes.

## Why does a Jacobi solver need halo exchange?
Each subdomain update depends on neighboring grid values. Boundary rows or columns must be exchanged so each GPU has the latest neighbor data for the next iteration.

## Why is waiting for the whole Jacobi tile inefficient?
If communication starts only after the whole domain is computed, the GPU can sit idle waiting for boundary data. Computing boundary rows first lets communication begin while the inner domain is still being computed.

## What is communication-computation overlap?
It is the technique of performing communication for boundary data at the same time as independent computation, such as computing the inner domain while top and bottom halo exchanges progress.

## What are CUDA streams?
CUDA streams are FIFO command queues. Operations in the same stream execute in order; operations in different streams may execute concurrently.

## Why are streams useful for overlap?
Streams let independent kernels and memory copies be enqueued separately, so GPU execution, host-to-device copies, device-to-host copies, and communication can overlap when hardware supports it.

## What is required to overlap memory copies and GPU execution?
Use asynchronous copies such as `cudaMemcpyAsync`, multiple streams, and pinned host memory. Pinned memory avoids pageable-memory overhead and enables efficient DMA.

## Why should stream pipeline segments be moderately sized?
Very small segments increase launch and DMA setup overhead and may underutilize the GPU. Very large segments reduce overlap. Good segment size balances pipeline fill/drain overhead and GPU utilization.

## What are CUDA events?
CUDA events mark points in stream execution. They can be used for timing, host synchronization, non-blocking queries, and cross-stream dependencies with `cudaStreamWaitEvent`.

## Why is `cudaStreamWaitEvent` important?
It creates a dependency between streams without blocking the host. Work submitted to one stream waits until an event recorded in another stream has occurred.

## What race condition appears with multiple streams in the Jacobi example?
If `l2_norm_d` is reset asynchronously on one stream, boundary kernels on other streams might start before the reset completes. Events are needed so those streams wait before updating the norm.

## Why can high-priority streams improve communication overlap?
Small boundary kernels may be delayed if a large compute kernel consumes GPU resources first. High-priority streams allow boundary work to preempt or run before lower-priority work, enabling communication to start earlier.

## What is NCCL?
NCCL is NVIDIA's Collective Communication Library. It provides optimized GPU communication for GPU buffers, including collectives and send/receive operations, and runs communication as GPU work on CUDA streams.

Internally, NCCL detects the hardware topology, chooses algorithms such as rings, trees, or CollNet, and launches CUDA kernels that perform communication and reductions with minimal CPU involvement.

## How does NCCL work at a high level?
NCCL creates a communicator across ranks/GPUs, discovers topology, chooses communication paths and algorithms, then enqueues communication work on CUDA streams.

For a collective such as allreduce, NCCL may use ring, tree, or CollNet algorithms. For point-to-point exchange, it can enqueue send/receive operations. The host call returns after the work is enqueued; actual progress follows CUDA stream semantics.

## Why is NCCL considered stream-aware?
NCCL communication calls take a CUDA stream. The call returns when the operation is enqueued, and completion follows normal CUDA stream semantics through events or stream synchronization.

## Why is stream-aware communication better than only CUDA-aware MPI?
CUDA-aware MPI knows about GPU buffers, but often requires explicit host synchronization between GPU kernels and CPU communication calls. Stream-aware communication can be ordered directly with GPU work in streams.

## What are the benefits of NCCL with respect to CUDA-aware MPI?
- NCCL is stream-aware, so communication can be ordered with kernels without blocking the host.
- NCCL is GPU-centric and works directly on GPU buffers.
- NCCL uses topology-aware algorithms for GPU interconnects and networks.
- NCCL collectives are heavily optimized for common GPU workloads.
- NCCL can reduce CPU synchronization in communication/computation overlap patterns.

CUDA-aware MPI is more portable and standard; NCCL is more specialized and often faster for NVIDIA GPU communication.

## How is an NCCL communicator initialized with MPI?
One rank creates a unique NCCL ID, broadcasts it with MPI, and each rank calls `ncclCommInitRank` with the world size, unique ID, and its rank.

## Why should multiple NCCL send/receive calls be grouped?
`ncclGroupStart` and `ncclGroupEnd` fuse related calls. Grouping avoids deadlocks when calls must progress together and reduces communication kernel launch overhead.

## What does `ncclGroupEnd` guarantee?
It guarantees that the grouped communication has been enqueued to the stream, not that the communication has completed.

Completion is still asynchronous and must be checked with normal CUDA stream/event synchronization if later work depends on the communicated data.

## What is a common NCCL use in the Jacobi solver?
Use NCCL send/receive to exchange top and bottom halo rows and optionally use NCCL collectives such as allreduce for the global norm.

## Why are the first NCCL operations in a program often slow?
The first NCCL operations may trigger lazy initialization work:
- communicator setup;
- topology discovery;
- graph/path search for rings, trees, or CollNet;
- kernel/module loading;
- memory registration or buffer setup;
- algorithm/protocol tuning.

For benchmarking, run warmup iterations before measuring steady-state communication time.

## Why might MPI allreduce be faster than NCCL allreduce for one scalar?
Launching a GPU communication kernel for a single norm value can cost more than copying the scalar to the host and using MPI. NCCL is strongest when enough data or GPU-side ordering justifies the overhead.

## What is the difference between staging and zero-copy communication in NCCL?
- **Staging**: data moves through an intermediate communication buffer.
- **Zero-copy**: communication reads directly from the source buffer and writes directly to the destination buffer.

## What is required for NCCL zero-copy communication?
The buffer must be allocated and registered appropriately, for example using NCCL memory allocation and communicator registration APIs.

The purpose is to let NCCL communicate directly from the user buffer instead of staging through an intermediate communication buffer.

## What is an NCCL ring algorithm?
A ring algorithm passes data around GPUs in steps so each GPU sends to and receives from neighbors. It often provides good bandwidth and avoids the contention of naive all-to-all sending.

## Why can a ring allgather outperform a naive allgather even with the same cost model?
Simple alpha-beta models do not fully capture network contention. A naive algorithm may overload switches or links, while a ring spreads traffic more uniformly.

## How does NCCL use topology detection?
NCCL builds a topology graph of GPUs, NICs, CPUs, PCI switches, NVLink, and NVSwitch, then searches for good rings, trees, or chains and tunes algorithms to the hardware.

## What are the tradeoffs between ring, tree, and CollNet algorithms?
- **Ring**: linear latency, excellent bandwidth, uniform traffic, few flows.
- **Tree**: logarithmic latency, good bandwidth, more imbalanced traffic.
- **CollNet**: can use in-network collectives for low latency and high bandwidth, but depends on hardware support.

## What is UCC?
Unified Collective Communication is a layer that can route collective operations to libraries such as NCCL while letting user code stay closer to MPI-style collectives.

## What is NVSHMEM?
NVSHMEM is an OpenSHMEM-style PGAS library for NVIDIA GPU clusters. It supports one-sided put/get, symmetric memory, GPU-centric communication, stream-aware operations, and device-side APIs.

The key idea is that each processing element owns a partition of a global symmetric memory space, and other PEs can access that memory with one-sided operations.

## How does NVSHMEM work at a high level?
NVSHMEM starts a set of processing elements, often aligned with MPI ranks. Each PE allocates symmetric memory with the same size/layout. A PE can then issue one-sided puts, gets, atomics, barriers, and waits involving symmetric objects on remote PEs.

Operations can be host-initiated, stream-ordered, or device-initiated inside kernels. This makes it possible to express communication as direct remote memory access instead of matched send/receive calls.

## What is the NVSHMEM symmetric memory model?
Each processing element allocates symmetric objects collectively with the same size on all PEs. The symmetric heap forms the partitioned global address space used for remote access.

## Why must NVSHMEM symmetric allocations have the same size on all PEs?
Symmetric memory assumes corresponding objects exist at each PE in a consistent layout. Different sizes can lead to undefined behavior.

## How does NVSHMEM interoperate with MPI?
An MPI communicator can be passed during NVSHMEM initialization. Then MPI rank/size and NVSHMEM PE identity can be aligned in the same program.

## What does an NVSHMEM put do?
An NVSHMEM put copies data from a local symmetric object to a symmetric object on another PE. It is one-sided: the target PE does not explicitly receive the message.

## Why must NVSHMEM put operations be synchronized?
Put calls are asynchronous. When the call returns, the remote write may not yet be visible. Barriers, quiet operations, stream ordering, or other synchronization are needed before consuming data.

## What is `nvshmemx_put_on_stream` used for?
It enqueues a put operation on a CUDA stream, allowing communication to be ordered with GPU kernels in the same stream.

## What is `nvshmemx_barrier_all_on_stream` used for?
It enqueues a barrier on a stream so all prior communication in that stream is completed before later stream work proceeds.

## How does NVSHMEM simplify Jacobi halo exchange?
Each PE can directly write halo rows into the neighbor's symmetric memory using put operations, instead of matching sends and receives.

## Why is NVSHMEM a good fit for halo exchange?
Halo exchange is naturally one-sided: a GPU knows which boundary row it produced and where that row belongs in the neighbor's halo. With NVSHMEM, it can directly put that row into the neighbor's symmetric memory, then use a barrier, quiet, or finer-grained synchronization before the neighbor consumes it.

This removes explicit receive matching and can move communication closer to the GPU computation.

## Why is high priority still useful with NVSHMEM?
Boundary computation and communication should start early. A high-priority communication or push stream helps boundary work progress while larger compute kernels run.

## How would you implement an AllToAllv using NVSHMEM?
AllToAllv means each PE sends a variable amount of data to every other PE. With NVSHMEM, a practical design is:
1. Allocate symmetric receive buffers, receive counts, and receive offsets on all PEs.
2. Exchange or compute `sendcounts` so every PE knows where each incoming message should land.
3. Compute prefix sums to build per-peer receive offsets.
4. For each destination PE, issue `nvshmem_put` or `nvshmemx_put_on_stream` from the local send slice into the destination's symmetric receive buffer at the correct offset.
5. Use `nvshmem_quiet`, barriers, counters, or per-peer flags to ensure remote writes are complete before reading.
6. If done on GPU, use block/warp-level puts for larger contiguous chunks rather than one tiny put per element.

The main challenge is metadata: every PE must agree on counts, offsets, and synchronization so variable-size messages do not overwrite each other.

## What synchronization is needed for an NVSHMEM AllToAllv?
You need synchronization for both metadata and payload:
- counts/offsets must be known before puts start;
- remote puts must complete before receivers consume data;
- completion can be enforced with `nvshmem_quiet`, `nvshmem_barrier_all`, stream barriers, or per-peer flags/counters;
- for GPU-initiated variants, waits or atomics can signal that a peer's data has arrived.

The synchronization strategy should avoid a global barrier if the algorithm can safely use finer-grained per-peer completion.

## What is CPU-initiated communication?
The GPU computes, then the CPU launches or coordinates communication through MPI, NCCL, or host-side APIs. This often adds synchronization and offload latency in the critical path.

## What is GPU-initiated communication?
GPU kernels issue communication directly, for example through device-side NVSHMEM operations. This can eliminate host offload latency and express communication inline with computation.

## Why can GPU-initiated communication improve strong scaling?
As per-GPU work becomes smaller, host launch and synchronization overheads matter more. GPU-initiated communication can reduce those overheads and overlap communication at finer granularity.

## What is thread-level communication in NVSHMEM?
Individual GPU threads issue remote operations, for example boundary threads writing halo elements to neighboring PEs. This enables fine-grained overlap but may produce inefficient small transfers.

## What is thread-group communication in NVSHMEM?
A warp or block cooperates to issue a larger remote operation. This can be more efficient for network transfers while still allowing overlap between computation and communication.

## What is in-kernel synchronization with NVSHMEM?
Kernels can use NVSHMEM operations such as quiet, atomic updates, and wait-until conditions to coordinate across PEs without returning to the CPU between steps.

## Why can in-kernel synchronization be risky?
Synchronization costs can be high, and progress may require careful launch constraints. The best strategy depends on workload size, communication granularity, and hardware.

## Why does NVSHMEM provide collective kernel launch?
Device-side inter-GPU synchronization may require producer and consumer blocks to be resident concurrently. Collective launch helps guarantee progress using cooperative launch constraints.

## What are CUDA Graphs?
CUDA Graphs describe a task graph of GPU operations and dependencies. The graph can be defined once, instantiated, and launched repeatedly with less CPU launch overhead.

## What limitation of streams do CUDA Graphs address?
With streams, the runtime sees operations as they are launched and may not know the full future task graph. Graphs expose the whole dependency structure and reduce repeated launch overhead.

## What are the three stages of CUDA Graph execution?
1. **Define** a graph template.
2. **Instantiate** an executable graph and initialize execution structures.
3. **Execute** the graph repeatedly in CUDA streams.

## What node types can CUDA Graphs contain?
Graphs can contain kernel nodes, memory copies, memsets, host function calls, event record/wait nodes, empty nodes, conditional nodes, and child graphs.

## How can a CUDA Graph be created?
- **Stream capture**: run normal stream code in capture mode, then convert it to a graph.
- **Graph API**: explicitly create nodes and dependencies.

## Why is graph instantiation separated from graph launch?
Instantiation can be expensive because it sets up executable GPU structures. Doing it once and launching many times amortizes that overhead.

## Why might the Jacobi graph need multiple graph instances?
Different iterations can read from different buffers and write to different buffers. Some iterations compute the norm while others do not. Separate graphs handle these different dependency patterns.

## What remains inefficient if communication still happens on the CPU?
Even with CUDA Graphs, each iteration may still need host-side communication calls and synchronization. This is especially expensive for short kernels.

## Why combine CUDA Graphs with device-side NVSHMEM?
Graphs reduce repeated launch overhead, and device-side NVSHMEM can avoid returning to the CPU for communication. Together they reduce launch/sync overhead and enable tighter compute-communication overlap.

## What is CUDA Dynamic Parallelism?
CUDA Dynamic Parallelism lets GPU threads launch new kernels from device code. It enables nested parallelism when work is discovered dynamically.

## When is dynamic parallelism useful?
It helps when nested work is irregular, unknown, or recursive, such as graph algorithms, adaptive mesh refinement, tree traversal, Bezier curves, or divide-and-conquer algorithms.

## What is the main risk of dynamic parallelism?
Launching many tiny child grids can underutilize the GPU and add significant launch metadata overhead. If every thread launches a child grid, overhead can explode.

## What are good practices for dynamic parallelism?
- Launch child grids with enough work.
- Use thresholds and serialize small tasks.
- Aggregate work, for example one launch per block rather than one per thread.
- Be aware of pending launch metadata limits and memory overhead.

## What is ROCm?
ROCm is AMD's software stack for GPU programming. It provides libraries and tools for developing applications on AMD GPUs.

## What is HIP?
HIP is a C++ dialect/API for writing portable GPU code that can target AMD GPUs and, often, NVIDIA GPUs. CUDA-like calls can often be converted to HIP, and HIPify automates part of the conversion.

## What is OpenACC?
OpenACC is a directive-based accelerator programming standard for C, C++, and Fortran. Programmers annotate sequential code with pragmas and let the compiler generate accelerator code.

## What are the advantages and limits of OpenACC?
OpenACC can improve portability and lets programmers start from sequential code. Its limits are reduced control, compiler-dependent performance, and possible correctness/performance differences when pragmas are ignored.

## What is the main conclusion of the Part 2 material?
Multi-GPU systems are necessary for modern performance and efficiency, but high performance requires careful data movement optimization, overlap, asynchronous execution, streams, graphs, and sometimes device-side communication. This power comes with more complex code.
