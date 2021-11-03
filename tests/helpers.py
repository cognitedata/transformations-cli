from typing import List


def from_table(table: str) -> List[List[str]]:
    rows = table.replace("=", "").split("\n")
    res = []
    for row in rows:
        tmp = row.split(" ")
        tmp = [r for r in tmp if r != ""]
        if tmp:
            res.append(tmp)
    return res
