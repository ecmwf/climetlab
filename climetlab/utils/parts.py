from collections import defaultdict
from collections.abc import Iterable


class Parts:
    def __init__(self, list_or_dict):
        """
        list_or_dict must be either:
        - A list as [(loc, offset, length), ...]
        - A dict as {loc: [(offset, length), ...] , ... ]

        Not supported:
        - A list as [(loc, (offset, length)), ...]
        """

        if isinstance(list_or_dict, Iterable):
            list_or_dict = list(list_or_dict)

        if isinstance(list_or_dict, (list, tuple)):
            if list_or_dict:
                assert not isinstance(list_or_dict[0][1], (tuple, list)), list_or_dict[
                    0
                ]
            self._list = list_or_dict
            return

        if isinstance(list_or_dict, dict):
            self._dict = list_or_dict
            return

        raise Exception(str(type(list_or_dict)))

    @property
    def as_dict(self):
        if not hasattr(self, "_dict"):
            self._dict = defaultdict(list)
            for loc, offset, length in self._list:
                self._dict[loc].append = (offset, length)

        return self._dict

    @property
    def as_list(self):
        if not hasattr(self, "_list"):
            self._list = []
            for loc, parts in self._dict.items():
                for offset, length in parts:
                    self._list.append((loc, offset, length))

        return self._list

    def __len__(self):
        return len(self.as_list)
