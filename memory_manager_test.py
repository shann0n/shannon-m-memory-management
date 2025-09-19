import threading
from memory_manager import MemoryManager

def test_basic_alloc_free():
    mm = MemoryManager(5)
    h1 = mm.Alloc(2)
    h2 = mm.Alloc(3)
    assert h1 is not None and h2 is not None
    mm.Free(h1)
    assert len(mm.free_list) == 1  # coalescing
    mm.Free(h2)
    assert mm.free_list == [(0, 5)]

def test_fragmentation_and_compaction():
    mm = MemoryManager(5)
    handles = [mm.Alloc(1) for _ in range(5)]
    mm.Free(handles[1])
    mm.Free(handles[3])
    handle_new = mm.Alloc(2)
    assert handle_new is not None
    starts = sorted([start for start, size in mm.allocations.values()])
    assert starts == list(range(len(starts)))

def test_over_allocation():
    mm = MemoryManager(5)
    h1 = mm.Alloc(5)
    h2 = mm.Alloc(1)
    assert h2 is None
    mm.Free(h1)
    h3 = mm.Alloc(5)
    assert h3 is not None

def test_thread_safety():
    mm = MemoryManager(100)
    handles = []

    def allocate_blocks():
        for _ in range(10):
            h = mm.Alloc(5)
            if h:
                handles.append(h)

    threads = [threading.Thread(target=allocate_blocks) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Ensure no overlapping allocations
    allocated_indices = []
    for start, size in mm.allocations.values():
        allocated_indices.extend(range(start, start+size))
    assert len(allocated_indices) == len(set(allocated_indices))  # no duplicates
