from collections import defaultdict

from climetlab.utils import download_and_cache


class Part:
    def __init__(self, path, offset, length):
        assert path is not None
        self.path = path
        self.offset = offset
        self.length = length

    def __eq__(self, other):
        return (
            self.path == other.path
            and self.offset == other.offset
            and self.length == other.length
        )

    @classmethod
    def resolve(cls, parts):
        paths = defaultdict(list)
        for i, part in enumerate(parts):
            paths[part.path].append(part)

        for path, bits in paths.items():
            if (
                path.startswith("http://")
                or path.startswith("https://")
                or path.startswith("ftp://")
            ):
                newpath = download_and_cache(
                    path, parts=[(p.offset, p.length) for p in bits]
                )
                newoffset = 0
                for p in bits:
                    p.path = newpath
                    p.offset = newoffset
                    newoffset += p.length

        return parts

    def __repr__(self):
        return f"Part[{self.path},{self.offset},{self.length}]"
