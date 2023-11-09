# SGDE API

The Secure Generative Data Exchange (SGDE) Client library is a set of helper Python functions that
allow users to interact with the SGDE API.
It allows to train generative models locally from
user data and generate synthetic samples from downloaded generative models.

For more information about SGDE, please refer to the [SGDE Paper](https://arxiv.org/abs/2109.12062).

## ⚙️ Installation

The Dockerfile collecting the recipe to install the
minimum [requirements](https://github.com/archettialberto/SGDE/blob/main/sgde_client/docker/requirements.txt?ref_type=heads)
of the client component is
available [here](https://github.com/archettialberto/SGDE/blob/main/sgde_client/docker/Dockerfile?ref_type=heads)
.

## 🛠️ Environment variables

Before running the client functions, you need to set the following environment variables:

| Name             | Description                | Default value |
|------------------|----------------------------|---------------|
| `API_IP`         | IP address of the SGDE API | `127.0.0.1`   |
| `API_PORT`       | Port of the SGDE API       | `8000`        |

You can add these variables to a `.client.env` file in the root folder of the project.

## 📖 Documentation

### Authentication Functions

`sgde_client.auth.register`: Registers a new user to the API. User data is required via command line.

_Returns_: A `User` Pydantic object

---

`sgde_client.auth.login`: Creates a new user session, setting a session token as a new environment variable. User data is required via command line.

_Returns_: `None`

---

`sgde_client.auth.whoami`: Checks is there exists an active session.

_Returns_: A `User` Pydantic object

---

`sgde_client.auth.get_users`: Returns the users currently registered to the API.

_Returns_: A Pandas dataframe of user data

---

`sgde_client.auth.get_user`: Returns the data of a specific user registered to the API.

_Parameters_: 
* `username` (`str`): username of the user to search

_Returns_: A `User` Pydantic object

### Exchange Functions

`sgde_client.exchange.get_generators`: Returns the list of available generators on the server.

_Returns_: A Pandas dataframe with generator data

---

`sgde_client.exchange.get_generator_metadata`: Returns the metadata related to a specific generator.

_Parameters_:
* `generator_name` (`str`): name of the generator to be searched

_Returns_: A `Generator` Pydantic object

---

`sgde_client.exchange.download_generator`: Downloads the ONNX file of the generator alongside its metadata.

_Parameters_:
* `generator_name` (`str`): name of the generator to be searched

_Returns_: A tuple composed of a metadata dictionary, the path of the ONNX generator file, and an optional path of the OXXN classifier file

---

`sgde_client.exchange.upload_generator`: Uploads a trained generator to the SGDE API.

_Parameters_:
* `metadata` (`dict`): dictionary containing the training metadata of the generator
* `gen_path` (`str`): path of the generator’s ONNX file
* `cls_path` (`str`, optional): path of the optional classifier’s ONNX file

### Generator Functions

`sgde_client.models.training.train_generator`: Trains a new data generator with local user data.

_Parameters_:
* `X` (`np.array`): input data
* `y` (`np.array`): data labels
* `gan_epochs` (`int`): number of epochs for GAN training
* `model_epochs` (`int`): number of epochs for classifier training
* `sleep_epochs` (`int`): number of epochs where the GAN is not trained, to obtain a well-performing auxiliary model
* `batch_size` (`int`): number of samples per training batch
* `data_name` (`str`): name of the training dataset
* `data_description` (`str`): description of the training dataset
* `data_structure` (`str`): "image" or "tabular"
* `task` (`str`): "classification" or "regression"

_Returns_: A metadata dictionary containing the generator training information

---

`sgde_client.models.inference.generate_samples_onnx`: Generates synthetic samples from a generator.

_Parameters_:
* `num_samples` (`int`): number of synthetic samples to be created
* `metadata` (`dict`): metadata of the generator model to be used for data generation
* `filter_model` (`bool`): if true, data generation includes the auxiliary model in the loop

_Returns_: A Numpy array containing synthetic data

## 📚 References

- [SGDE Paper](https://arxiv.org/abs/2109.12062)
- [FastAPI](https://fastapi.tiangolo.com/)
- [TensorFlow](https://www.tensorflow.org/)

## ✏️ How to Cite

```
@inproceedings{lomurno2023sgde,
  author = {Lomurno, Eugenio and Archetti, Alberto and Cazzella, Lorenzo and Samele, Stefano and Di Perna, Leonardo and Matteucci, Matteo},
  title = {SGDE: Secure Generative Data Exchange for Cross-Silo Federated Learning},
  year = {2023},
  isbn = {9781450396899},
  publisher = {Association for Computing Machinery},
  address = {New York, NY, USA},
  url = {https://doi.org/10.1145/3573942.3573974},
  doi = {10.1145/3573942.3573974},
  booktitle = {Proceedings of the 2022 5th International Conference on Artificial Intelligence and Pattern Recognition},
  pages = {205–214},
  numpages = {10},
  keywords = {Gradient leakage, Generative deep learning, Privacy, Differential privacy, Deep learning, Federated learning},
  location = {Xiamen, China},
  series = {AIPR '22}
}
```
