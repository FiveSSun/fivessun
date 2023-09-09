import torch

from library.deeplearning.layer import cross


def test_cross():
    c_layer = cross.Cross(2, 3)
    output = c_layer(torch.tensor([1.0, 2.0]))
    assert output.size(dim=0) == 2
