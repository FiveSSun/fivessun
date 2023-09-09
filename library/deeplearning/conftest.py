import pytest
import torch


@pytest.fixture(autouse=True)
def torch_setting_fixture():
    """Set torch setting for test."""
    torch.manual_seed(0)
    torch.set_printoptions(6)
