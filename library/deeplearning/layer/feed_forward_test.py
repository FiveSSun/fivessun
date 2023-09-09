import torch

from library.deeplearning.layer import feed_forward


def test_feed_forward():
    ff_layer = feed_forward.FeedForward(2, 4, dropout1=0, dropout2=0)
    output = ff_layer(torch.tensor([[2.0, 2.0], [1.0, 1.0]]))

    torch.testing.assert_close(
        output, torch.tensor([[-0.128069, 0.342875], [0.040470, 0.387964]])
    )
