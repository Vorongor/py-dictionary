from typing import Any, Iterable, Tuple

_TOMBSTONE = object()


class Dictionary:
    def __init__(self) -> None:
        """
        Initialize the dictionary with a default
        capacity and prepare internal storage.
        """
        self.size = 8
        self.current_size = 0
        self.resize_point = round(self.size * (2 / 3))
        self.bucket = [None] * self.size

    def __hash_index(self, key: Any) -> int:
        """
        Compute the hash index for a given key based on current table size.
        """
        return hash(key) % self.size

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Insert or update a key-value pair in the dictionary.
        Automatically resizes if load factor exceeds threshold.
        """
        idx = self.__hash_index(key)

        while (
            self.bucket[idx] is not None
            and self.bucket[idx] is not _TOMBSTONE
            and self.bucket[idx][0] != key
        ):
            idx = (idx + 1) % self.size

        if self.bucket[idx] is None or self.bucket[idx] is _TOMBSTONE:
            self.current_size += 1

        self.bucket[idx] = (key, value)

        if self.current_size > self.resize_point:
            self.__resize()

    def __getitem__(self, key: Any) -> Any:
        """
        Retrieve the value associated with a given key.
        Raises KeyError if the key is not found.
        """
        idx = self.__hash_index(key)

        while self.bucket[idx] is not None:
            if (self.bucket[idx] is not _TOMBSTONE
                    and self.bucket[idx][0] == key):
                return self.bucket[idx][1]
            idx = (idx + 1) % self.size

        raise KeyError(key)

    def __delitem__(self, key: Any) -> None:
        """
        Remove a key-value pair from the dictionary.
        Uses tombstone to preserve probing chain.
        """
        idx = self.__hash_index(key)

        while self.bucket[idx] is not None:
            if (self.bucket[idx] is not _TOMBSTONE
                    and self.bucket[idx][0] == key):
                self.bucket[idx] = _TOMBSTONE
                self.current_size -= 1
                return
            idx = (idx + 1) % self.size

        raise KeyError(key)

    def __len__(self) -> int:
        """
        Return the number of active key-value pairs in the dictionary.
        """
        return self.current_size

    def __iter__(self) -> Any:
        """
        Iterate over all keys in the dictionary.
        """
        for entry in self.bucket:
            if entry and entry is not _TOMBSTONE:
                yield entry[0]

    def items(self) -> Any:
        """
        Iterate over all key-value pairs in the dictionary.
        """
        for entry in self.bucket:
            if entry and entry is not _TOMBSTONE:
                yield entry

    def values(self) -> Any:
        """
        Iterate over all values in the dictionary.
        """
        for entry in self.bucket:
            if entry and entry is not _TOMBSTONE:
                yield entry[1]

    def __resize(self) -> None:
        """
        Double the capacity of the dictionary and rehash all existing entries.
        """
        old_bucket = self.bucket

        self.size *= 2
        self.bucket = [None] * self.size
        self.current_size = 0
        self.resize_point = round(self.size * (2 / 3))

        for entry in old_bucket:
            if entry and entry is not _TOMBSTONE:
                self.__setitem__(entry[0], entry[1])

    def clear(self) -> None:
        """
        Remove all entries from the dictionary and reset its state.
        """
        self.__init__()

    def get(self, name: Any, default: None = None) -> Any:
        """
        Return the value for a key if it exists, otherwise return the default.
        """
        try:
            return self.__getitem__(name)
        except KeyError:
            return default

    def pop(self, index: int | None = None) -> Any:
        """
        Remove and return a key-value pair
        by logical index or last inserted item.
        """
        if self.current_size == 0:
            raise KeyError("Dictionary is empty")

        if index is not None:
            keys = list(self.__iter__())
            if index >= len(keys) or index < 0:
                raise IndexError("Invalid index")
            key = keys[index]
        else:
            keys = list(self.__iter__())
            key = keys[-1]

        value = self[key]
        self.__delitem__(key)
        return key, value

    def update(self,
               updates: Iterable[Tuple[Any, Any]] | dict | tuple) -> None:
        """
        Update the dictionary with key-value pairs
        from another iterable, dict, or tuple.
        """
        if isinstance(updates, dict):
            updates = updates.items()

        if (isinstance(updates, tuple) and len(updates) == 2
                and not isinstance(updates[0], tuple)):
            updates = [updates]

        for key, value in updates:
            self.__setitem__(key, value)
