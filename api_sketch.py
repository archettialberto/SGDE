"""
Programming interface for the AI-SPRINT tool 'SGDE'.

Authors:
    Eugenio Lomurno (eugenio.lomurno@polimi.it)
    Alberto Archetti (alberto.archetti@polito.it)

Last revision: 9 May 2022
"""

import numpy as np
import pandas as pd


def get_tasks() -> pd.DataFrame:
    """
    Returns the list of pre-defined tasks from the AI-SPRINT database.

    Returns:
        tasks (pd.DataFrame): Pandas dataframe of available tasks
    """


# noinspection PyUnusedLocal
def get_generators(task_id: str = None) -> pd.DataFrame:
    """
    Returns the list of available data generators for a specific task. If None, returns the list of generators for all
    available tasks.

    Args:
        task_id (str): string identifier of a task (default is None)

    Returns:
        generators (ps.Dataframe): complete list of available generators for a specific task
    """


# noinspection PyUnusedLocal
def train_generator(task_id: str, input_data: np.nditer, batch_size: int, privacy_level: str, distribute: bool = False,
                    push: bool = True,
                    latent_dim: tuple[int] = (),
                    latent_dist: str = "normal",
                    readme: str,
                    ) -> (str, str):
    """
    Returns a data generator given a set of user samples for a specific task.

    Args:
        task_id (str): string identifier of a task
        input_data (np.nditer): numpy iterator over user samples
        batch_size (int): number of samples of a mini-batch
        privacy_level (str): 'high', 'medium', 'low', 'none'
        distribute (bool): distribute training on the computing continuum (default is False)
        push (bool): push generator on AI-SPRINT database (default is True)

    Returns:
        generator_id (str): string identifier of the trained generator
        generator (str): ONNX model in string format
    """


# noinspection PyUnusedLocal
def pull_generator(generator_id: str) -> str:
    """
    Downloads a generator from the AI-SPRINT database.

    Args:
        generator_id (str): string identifier of a specific generator

    Returns:
        generator (str): ONNX model in string format
    """


# noinspection PyUnusedLocal
def generate_data(generator: str, num_samples: int = 1, remote: bool = False) -> np.nditer:
    """
    Generates some samples from a generator.

    Args:
        generator (str): ONNX model in string format
        num_samples (int): number of samples to be generated (default is 1)

    Returns:
        data (np.nditer): numpy iterator over generated samples
    """
