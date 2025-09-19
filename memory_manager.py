import threading

class MemoryManager:
    def __init__(self, num_bytes: int):
        """Initialize the memory manager with a contiguous buffer of size num_bytes."""
        self.buffer = bytearray(num_bytes)
        self.size = num_bytes
        self.free_list = [(0, num_bytes)]  # list of (start_index, size)
        self.allocations = {}              # handle -> (start_index, size)
        self.next_handle = 1               # incrementing handle counter
        self.lock = threading.Lock()       # lock for thread safety

    def Alloc(self, size: int) -> int | None:
        """
        Allocate a block of memory of given size.
        Returns a handle (integer ID) or None if allocation fails.
        Implements first-fit allocation.
        Thread-safe.
        """
        with self.lock:
            # First-fit allocation
            for i, (start, length) in enumerate(self.free_list):
                if length >= size:
                    alloc_start = start
                    alloc_end = start + size

                    # Update free list
                    if length == size:
                        self.free_list.pop(i)
                    else:
                        self.free_list[i] = (alloc_end, length - size)

                    # Record allocation
                    handle = self.next_handle
                    self.next_handle += 1
                    self.allocations[handle] = (alloc_start, size)
                    return handle

            # Try compaction if allocation failed
            self._compact()
            for i, (start, length) in enumerate(self.free_list):
                if length >= size:
                    alloc_start = start
                    alloc_end = start + size
                    if length == size:
                        self.free_list.pop(i)
                    else:
                        self.free_list[i] = (alloc_end, length - size)
                    handle = self.next_handle
                    self.next_handle += 1
                    self.allocations[handle] = (alloc_start, size)
                    return handle

            return None  # allocation failed

    def Free(self, handle: int):
        """
        Free a previously allocated block by handle.
        Thread-safe.
        """
        with self.lock:
            if handle not in self.allocations:
                raise ValueError(f"Invalid free: handle {handle} not allocated")

            start, size = self.allocations.pop(handle)
            self.free_list.append((start, size))
            self._coalesce()

    def _coalesce(self):
        """Merge adjacent free blocks to reduce fragmentation."""
        self.free_list.sort()
        merged = []
        for start, size in self.free_list:
            if merged and merged[-1][0] + merged[-1][1] == start:
                last_start, last_size = merged[-1]
                merged[-1] = (last_start, last_size + size)
            else:
                merged.append((start, size))
        self.free_list = merged

    def _compact(self):
        """
        Move allocated blocks to remove fragmentation.
        Updates allocation handles to reflect new positions.
        """
        allocated_blocks = sorted(self.allocations.items(), key=lambda x: x[1][0])
        new_start = 0
        for handle, (old_start, size) in allocated_blocks:
            if old_start != new_start:
                # Move memory
                self.buffer[new_start:new_start+size] = self.buffer[old_start:old_start+size]
                self.allocations[handle] = (new_start, size)
            new_start += size
        self.free_list = [(new_start, self.size - new_start)]
