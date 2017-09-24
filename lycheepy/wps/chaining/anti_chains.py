from networkx import antichains


class AntiChainsBuilder(object):
    def __init__(self, graph):
        self.graph = graph

    def build(self):
        anti_chain = [a[0] if len(a) == 1 else a for a in list(antichains(self.graph))]
        anti_chain.pop(0)
        return list(
            reversed(
                [
                    a for a in anti_chain
                    if a not in [
                        c for b in anti_chain
                        if type(b) is list
                        for c in b
                    ]
                ]
            )
        )
