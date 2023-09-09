import torch

from library.deeplearning.layer import rnn


def test_rnn_layer():
    rnn_layer = rnn.BasicRNN(3, 4, 2)
    output, hidden = rnn_layer(torch.tensor([[1.0, 2.0, 3.0]]), torch.zeros([1, 4]))

    assert output.shape == torch.Size([1, 2])
    assert hidden.shape == torch.Size([1, 4])
    assert torch.sum(output) == torch.tensor(1)
