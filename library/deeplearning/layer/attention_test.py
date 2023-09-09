import torch

from library.deeplearning.layer import attention


def test_vanilla_attention():
    att_layer = attention.VanillaAttention(2, 4)
    states, weights = att_layer(torch.tensor([[2.0, 2.0], [1.0, 1.0]]))

    assert states.size(dim=0) == 2
    assert weights.size(dim=0) == 2
    torch.testing.assert_close(states, torch.tensor([1.457965, 1.457965]))
    torch.testing.assert_close(weights, torch.tensor([0.457965, 0.542035]))


def test_multi_head_attention():
    att_layer = attention.MultiHeadAttention(4, 2, 0.0)
    x = torch.tensor([[2.0, 2.0, 2.0, 2.0], [1.0, 1.0, 1.0, 1.0]])
    output = att_layer(x, x, x)

    torch.testing.assert_close(
        output,
        torch.tensor(
            [
                [[-0.424107, -0.662986, -0.877358, -0.196203]],
                [[-0.158924, -0.542139, -0.403858, -0.458013]],
            ]
        ),
    )
