from PIL import Image
from hypergan.samplers.base_sampler import BaseSampler
from hypergan.viewer import GlobalViewer
import numpy as np
import torch
import torch.nn as nn
import time

class BatchWalkSampler(BaseSampler):
    def __init__(self, gan, samples_per_row=4, session=None):
        BaseSampler.__init__(self, gan, samples_per_row)
        self.step = 0
        self.step_count = 30
        self.latent1 = self.gan.latent.next()
        self.latent2 = self.gan.latent.next()
        direction = self.gan.latent.next()
        self.direction = direction / torch.norm(direction, p=2, dim=1, keepdim=True).expand_as(direction)
        self.velocity = 10.0
        self.hardtanh = nn.Hardtanh()

    def compatible_with(gan):
        if hasattr(gan, 'latent'):
            return True
        return False

    def _sample(self):
        gan = self.gan
        self.step+=1
        if self.step > self.step_count:
            self.latent1 = self.latent2
            direction = self.gan.latent.next()
            self.direction = direction / torch.norm(direction, p=2, dim=1, keepdim=True).expand_as(direction)
            self.velocity = 10.0
            self.step = 0

        latent = self.direction * self.step / self.step_count * self.velocity + self.latent1
        latent = self.hardtanh(latent)
        self.latent2 = latent

        g = gan.generator.forward(latent)
        #    gs.append(g)
        return [
            ('generator', g)
        ]
