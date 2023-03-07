import os

from onnx import TensorProto
from onnx.checker import check_model
from onnx.helper import make_tensor_value_info, make_node, make_model, make_graph

if __name__ == "__main__":
    onnx_folder = os.path.join(os.getcwd(), "test_onnx")
    os.makedirs(onnx_folder, exist_ok=True)

    X = make_tensor_value_info('X', TensorProto.FLOAT, [None, None])
    A = make_tensor_value_info('A', TensorProto.FLOAT, [None, None])
    B = make_tensor_value_info('B', TensorProto.FLOAT, [None, None])
    Y = make_tensor_value_info('Y', TensorProto.FLOAT, [None])
    node1 = make_node('MatMul', ['X', 'A'], ['XA'])
    node2 = make_node('Add', ['XA', 'B'], ['Y'])
    graph = make_graph([node1, node2], 'lr', [X, A, B], [Y])
    onnx_model = make_model(graph)
    check_model(onnx_model)

    with open(os.path.join(onnx_folder, "onnx_model.onnx"), "wb") as f:
        f.write(onnx_model.SerializeToString())

    with open(os.path.join(onnx_folder, "wrong_onnx_model.onnx"), "w") as f:
        f.write(str(onnx_model))
