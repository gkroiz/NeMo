# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# To suppress BF16 compile related issue in the CI runs with turing/V100
import torch._dynamo
import torch.multiprocessing as mp
from omegaconf.omegaconf import OmegaConf, open_dict

from nemo.collections.nlp.models.language_modeling.megatron_gpt_model import MegatronGPTModel
from nemo.collections.nlp.parts.megatron_trainer_builder import MegatronTrainerBuilder
from nemo.core.config import hydra_runner
from nemo.utils import logging
from nemo.utils.exp_manager import exp_manager
from omegaconf.omegaconf import OmegaConf, open_dict
from pytorch_lightning import Trainer
from pytorch_lightning.plugins.environments import TorchElasticEnvironment
from pytorch_lightning.trainer.connectors.checkpoint_connector import CheckpointConnector
import torch.autograd.profiler
import torch.multiprocessing as mp

torch._dynamo.config.suppress_errors = True

mp.set_start_method("spawn", force=True)


@hydra_runner(config_path='conf', config_name='megatron_gpt_config')
def main(cfg) -> None:
    logging.info('\n\n************** Experiment configuration ***********')
    logging.info(f'\n{OmegaConf.to_yaml(cfg)}')

    with torch.autograd.profiler.emit_nvtx():
        trainer = MegatronTrainerBuilder(cfg).create_trainer()
        exp_manager(trainer, cfg.exp_manager)

        model = MegatronGPTModel(cfg.model, trainer)

        import time

        s = time.time()
        trainer.fit(model)
        e = time.time()
        print(f'Train time: {(e-s):.2f}')


if __name__ == '__main__':
  main()
