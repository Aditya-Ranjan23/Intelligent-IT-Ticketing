import math
import re
from collections import Counter

STOP = frozenset(
    """
    a an the is are was were be been being have has had do does did will would
    could should may might must shall can need to of in for on with at by from as
    into through during before after above below between under again further then
    once here there when where why how all each few more most other some such no
    nor not only own same so than too very just and but if or because until while
    my your our their this that these those i me we you he she it they them his
    her its please help
    """.split()
)


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[\w]+", text.lower(), flags=re.UNICODE)
    return [t for t in tokens if len(t) > 1 and t not in STOP]


def term_vector(tokens: list[str]) -> dict[str, float]:
    counts = Counter(tokens)
    return dict(counts)


def cosine_similarity(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(a.get(k, 0) * b.get(k, 0) for k in a if k in b)
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def text_similarity(a: str, b: str) -> float:
    return cosine_similarity(term_vector(tokenize(a)), term_vector(tokenize(b)))
