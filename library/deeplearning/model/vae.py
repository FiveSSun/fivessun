"""Variational Autoencoders for Collaborative Filtering

Paper: https://arxiv.org/pdf/1802.05814.pdf
This code is based on the author's implementation:
https://github.com/dawenl/vae_cf
"""
from typing import Union

from data.ml.recsys.models import model_base
import torch
from torch import nn
from torch.nn import functional as F


def _get_annealing_steps(
    total_anneal_steps: Union[float, int], total_training_steps: int
) -> int:
    if not total_training_steps:
        return 0

    if isinstance(total_anneal_steps, float):
        return int(total_training_steps * total_anneal_steps)

    return total_anneal_steps


class VAE(model_base.RecsysModelBase):
    def __init__(
        self,
        encoder_dims: list[int],
        decoder_dims: list[int],
        dropout: float = 0.5,
        anneal_cap: float = 0.2,
        total_anneal_steps: Union[float, int] = 0.2,
        **kwargs,
    ):
        """Constructs Variational Auto-Encoder.

        For the details of KL annealing, please refer to https://aclanthology.org/K16-1002.pdf.

        Args:
            encoder_dims: A list of latent dims.
            decoder_dims: A list of latent dims.
            dropout: Dropout rate.
            anneal_cap: The maximum annealing ratio.
            total_anneal_steps: The total number of gradient updates for annealing.
                If float, annealing will be done for `total_training_steps * total_anneal_steps` steps.
                If int, annealing will be done for `total_training_steps` steps.
        """
        super().__init__(**kwargs)

        encoder_dims = [self._item_size] + encoder_dims
        decoder_dims = decoder_dims + [self._item_size]

        assert (
            encoder_dims[-1] == decoder_dims[0]
        ), "Latent dimension for encoder and decoder mismatches."

        self._encoder_dims = encoder_dims
        self._decoder_dims = decoder_dims

        self._encoder = self._make_encoder_layers()
        self._decoder = self._make_decoder_layers()
        self._dropout = nn.Dropout(dropout)

        # Annealing params.
        self._global_steps = 0
        self._anneal_cap = anneal_cap
        self._total_anneal_steps = total_anneal_steps

        self.param = kwargs

        self._init_weights()

    def _make_encoder_layers(self) -> nn.ModuleList:
        # Last dim is for mean and variance.
        return nn.ModuleList(
            [
                nn.Linear(dim_in, dim_out)
                for dim_in, dim_out in zip(
                    self._encoder_dims[:-2], self._encoder_dims[1:-1]
                )
            ]
            + [nn.Linear(self._encoder_dims[-2], self._encoder_dims[-1] * 2)]
        )

    def _make_decoder_layers(self) -> nn.ModuleList:
        return nn.ModuleList(
            [
                nn.Linear(dim_in, dim_out)
                for dim_in, dim_out in zip(
                    self._decoder_dims[:-1], self._decoder_dims[1:]
                )
            ]
        )

    def _init_weights(self):
        for layer in self._encoder:
            nn.init.xavier_normal_(layer.weight)
        for layer in self._decoder:
            nn.init.xavier_normal_(layer.weight)

    def forward(
        self, data: torch.Tensor, **kwargs
    ) -> tuple[
        torch.Tensor, torch.Tensor, torch.Tensor
    ]:  # pylint: disable=arguments-differ
        mean, logvar = self._encode(data)
        z = self._reparameterize(mean, logvar)
        return self._decode(z), mean, logvar

    def _encode(self, data: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        h = F.normalize(data)  # L2-normalization
        h = self._dropout(h)

        for layer in self._encoder[:-1]:
            h = layer(h)
            h = torch.tanh(h)

        h = self._encoder[-1](h)
        mean = h[:, : self._encoder_dims[-1]]
        logvar = h[:, self._encoder_dims[-1] :]
        return mean, logvar

    def _decode(self, data: torch.Tensor) -> torch.Tensor:
        h = data
        for layer in self._decoder[:-1]:
            h = layer(h)
            h = torch.tanh(h)
        h = self._decoder[-1](h)
        return h

    def _reparameterize(self, mean: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        if self.training:
            std = torch.exp(0.5 * logvar)
            eps = torch.randn_like(std)
            return eps.mul(std).add_(mean)

        return mean

    def configure_optimizers(self):
        if "weight_decay" in self.param:
            return torch.optim.Adam(
                self.parameters(), lr=1e-4, weight_decay=self.param["weight_decay"]
            )
        return torch.optim.Adam(self.parameters(), lr=1e-4)

    def loss(
        self,
        recon_x: torch.Tensor,
        x: torch.Tensor,
        mu: torch.Tensor,
        logvar: torch.Tensor,
    ) -> torch.Tensor:
        # pylint: disable=invalid-name
        anneal_steps = _get_annealing_steps(
            self._total_anneal_steps, self._total_training_steps
        )

        if anneal_steps > 0:
            anneal = min(self._anneal_cap, 1.0 * self._global_steps / anneal_steps)
        else:
            anneal = self._anneal_cap

        BCE = -torch.mean(torch.sum(F.log_softmax(recon_x, 1) * x, -1))
        KLD = -0.5 * torch.mean(torch.sum(1 + logvar - mu.pow(2) - logvar.exp(), dim=1))

        return BCE + anneal * KLD

    def training_step(
        self, batch_data: dict[str, torch.Tensor], batch_idx: int
    ):  # pylint: disable=arguments-differ
        batch = batch_data["inputs"]
        recon_batch, mu, logvar = self(batch)
        loss = self.loss(recon_batch, batch_data["targets"], mu, logvar)
        self.log("loss/train", loss, on_step=False, on_epoch=True, sync_dist=True)
        self._global_steps += 1

        return loss
