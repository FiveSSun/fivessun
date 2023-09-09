import torch

from library.deeplearning.layer import mlp


def test_mlp():
    mlp_layer = mlp.MLP([2, 4])
    output = mlp_layer(torch.tensor([1.0, 2.0]))
    assert output.size(dim=0) == 4
