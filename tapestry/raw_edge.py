import numpy as np

from tapestry.expression_graph import (
    BlockOperation,
    ExternalTensor,
    TapestryGraph,
    TensorResult,
    TensorValue,
)
from tapestry.zspace import ZRange, ZRangeMap


def f(
    x: TensorValue,
    w: TensorValue,
) -> TensorResult:
    graph = x.assert_graph()
    assert w.graph == graph

    assert x.shape[-1] == w.shape[0]

    y_shape = np.append(x.shape[:-1], w.shape[1])

    y = graph.add_node(
        TensorResult(
            name="Y",
            shape=y_shape,
            dtype="torch.float16",
        )
    )

    op = graph.add_node(
        BlockOperation(
            name="Linear",
            index_space=ZRange(y_shape),
        )
    )

    graph.add_node(
        BlockOperation.Input(
            source_node_id=op.node_id,
            target_node_id=x.node_id,
            selector=ZRangeMap.identity_map(shape=[1, 2]),
            name="x",
        )
    )

    graph.add_node(
        BlockOperation.Input(
            source_node_id=op.node_id,
            target_node_id=w.node_id,
            selector=ZRangeMap.constant_map(2, shape=w.shape),
            name="w",
        )
    )

    graph.add_node(
        BlockOperation.Result(
            source_node_id=y.node_id,
            target_node_id=op.node_id,
            selector=ZRangeMap.identity_map(y.shape),
            name="y",
        ),
    )

    return y


def raw():
    g = TapestryGraph()

    x = g.add_node(
        ExternalTensor(
            name="X",
            shape=[100, 2],
            dtype="torch.float16",
            storage="store:x",
        )
    )

    w = g.add_node(
        ExternalTensor(
            name="W",
            shape=[2, 3],
            dtype="torch.float16",
            storage="store:w",
        )
    )

    y = f(x, w)

    print(g.pretty())


if __name__ == "__main__":
    raw()
