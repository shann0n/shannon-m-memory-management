# Twingate Memory Manager

## Overview
This project implements a simple memory manager in Python that simulates allocation and freeing of a contiguous block of memory. The memory manager supports:

- `Alloc(size)` — allocate memory blocks.
- `Free(handle)` — free previously allocated blocks.
- **Compaction** — moves allocated blocks to remove fragmentation, ensuring allocations succeed when total free memory is sufficient.
- **Thread-safe** — multiple threads can safely call `Alloc` and `Free` concurrently.
- Handles (integer IDs) instead of raw indices, making compaction safe.

---

## Design Choices

### 1. Buffer Representation
- Used a Python `bytearray` to simulate contiguous memory.
- Size is fixed at initialization.

### 2. Allocation Strategy
- **First-Fit**: Allocates memory from the first free block large enough to satisfy the request.
- **Rationale**: Simple, fast, and easy to implement.
- **Trade-offs**: Can leave small free holes at the start (external fragmentation), but compaction mitigates this.

### 3. Free List Management
- Maintains a list of free blocks as `(start_index, size)`.
- Coalesces adjacent free blocks on every `Free` to reduce fragmentation.

### 4. Handles vs. Indices
- `Alloc` returns a **handle (integer ID)** instead of a raw index.
- The handle maps internally to `(start_index, size)` in the buffer.
- **Benefit**: Enables compaction without breaking references.

### 5. Compaction
- Slides allocated blocks toward the beginning of the buffer to remove gaps.
- Updates allocation table to reflect new start indices.
- Ensures fragmented memory can satisfy allocation requests that would otherwise fail.

### 6. Thread Safety
- All public operations (`Alloc`, `Free`) are wrapped in a `threading.Lock()`.
- Protects shared state: `free_list`, `allocations`, and `next_handle`.
- Multiple threads can safely allocate and free memory concurrently.
- **Future Improvement**: For high-performance scenarios, fine-grained locking or lock-free structures could be explored.

---

## Unit Tests
- Included tests verify:
  - Basic allocation and freeing.
  - Fragmentation and compaction behavior.
  - Over-allocation edge cases.
  - Thread safety with concurrent allocation.
- Implemented with `pytest`.

---

## Future Improvements

1. **Alternative Allocation Strategies**
   - Best-fit or buddy allocator could further reduce fragmentation.
   - Trade-offs: slightly slower allocation or increased metadata complexity.

2. **Metadata Optimization**
   - Currently uses Python dictionaries for tracking allocations.
   - Could be made more memory-efficient for very large buffers.

3. **Performance Optimizations**
   - Compaction currently moves memory linearly.
   - Incremental or lazy compaction could reduce overhead in large memory spaces.

---

## How to Run

1. **Install pytest**
```bash
pip install pytest
```

2. Run the test suite
```bash
   pytest memory_manager_test.py
```
You should see an output:
```bash
memory_manager_test.py ....                                              [100%]

============================== 4 passed in 0.00s ===============================
```
