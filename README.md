# SGDE

The Secure Generative Data Exchange (SGDE) is a Python application that allows users to train, upload, and download generative models to and from a server.
Generative models allow the generation of synthetic data that is statistically similar to the original data, preserving individuals' privacy.
Through the SGDE Client, users can register to the SGDE API by providing a unique username, email, and password and upload their models.
Then, they can download models from the server and use them to generate synthetic data in a user-friendly way.

The SGDE API is built on top of FastAPI and uses SQLAlchemy to manage the database. Objects are exchanged using Pydantic models.
The SGDE Client relies on TensorFlow to train generative models and on the SGDE API to upload and download them.

For more information about SGDE, please refer to the [SGDE Paper](https://arxiv.org/abs/2109.12062).

SGDE is part of the [AI-SPRINT](https://www.ai-sprint-project.eu/) project, where it provides an alternative to federated learning as a framework to train ML models on edge-stored, sensitive data.

## 🚀 Demo

An example usage of SGDE can be found [here](https://github.com/archettialberto/SGDE/blob/main/sgde_demo.ipynb).

## 📖 Documentation

Detailed documentation of the SGDE API and Client can be found in the following links:
* [SGDE API Documentation](https://github.com/archettialberto/SGDE/blob/main/sgde_api/README.md)
* [SGDE Client Documentation](https://github.com/archettialberto/SGDE/blob/main/sgde_client/README.md)


## 📚 References

- [SGDE Paper](https://arxiv.org/abs/2109.12062)
- [AI-SPRINT](https://www.ai-sprint-project.eu/)

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
