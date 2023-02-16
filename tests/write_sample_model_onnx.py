from onnx import TensorProto, load
from onnx.helper import make_model, make_node, make_graph, make_tensor_value_info
from onnx.checker import check_model


if __name__ == "__main__":
    # adapted from https://onnx.ai/onnx/intro/python.html

    X = make_tensor_value_info('X', TensorProto.FLOAT, [None, None])
    A = make_tensor_value_info('A', TensorProto.FLOAT, [None, None])
    B = make_tensor_value_info('B', TensorProto.FLOAT, [None, None])
    Y = make_tensor_value_info('Y', TensorProto.FLOAT, [None])
    node1 = make_node('MatMul', ['X', 'A'], ['XA'])
    node2 = make_node('Add', ['XA', 'B'], ['Y'])
    graph = make_graph([node1, node2], 'lr', [X, A, B], [Y])
    onnx_model = make_model(graph)
    check_model(onnx_model)

    with open("sample_model.onnx", "w") as f:
        f.write(onnx_model.__str__())

    with open("sample_model.onnx", "r") as f:
        onnx_model_from_file = f.read()

    assert str(onnx_model) == str(onnx_model_from_file)
