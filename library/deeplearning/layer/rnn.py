import torch
from torch import nn


class BasicRNN(nn.Module):
    """RNN layer.

    h_t = tanh(W_xh * x_t + W_hh * h_t-1)
    y_t = tanh(W_xy * x_t + W_hy * h_t-1)
    """

    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        super(BasicRNN, self).__init__()

        self.hidden_size = hidden_size

        # i2h: W_xh + W_hh
        # i2o: W_xy + W_hy
        self.i2h = nn.Linear(input_size + hidden_size, hidden_size)
        self.i2o = nn.Linear(input_size + hidden_size, output_size)
        self.activation_ftn = torch.tanh
        self.softmax = nn.LogSoftmax(dim=1)

    def forward(
        self,
        x: torch.Tensor,
        h: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """RNN forward.
        :arg:
            shape of x (x_t)   : (batch_size, input_size)
            shape of h (h_t-1) : (batch_size, hidden_size)

        :return:
            shape of y (y_t)   : (batch_size, output_size)
            shape of h (h_t)   : (batch_size, hidden_size)
        """
        # Combine input and hidden state.
        combined = torch.cat((x, h), 1)

        # It is possible to use one layer by combining i2h and i2o.
        # With only one layer, not necessarily use activation function.
        # h = self.activation_ftn(self.i2h(combined))
        # y = self.activation_ftn(self.i2o(combined))
        h = self.i2h(combined)
        y = self.i2o(combined)
        y = self.softmax(y)  # probability distribution
        return y, h
