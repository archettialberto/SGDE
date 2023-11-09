# SGDE API

The Secure Generative Data Exchange (SGDE) API is a Python API that allows users to upload and download generative models to and from a server.
Models are stored in ONNX format and can be downloaded by any SGDE user. Users can register to the API by providing a unique username, email, and password and upload their own models.

The SGDE API is built on top of FastAPI and uses SQLAlchemy to manage the database. Objects are exchanged using Pydantic models.

For more information about SGDE, please refer to the [SGDE Paper](https://arxiv.org/abs/2109.12062).

## ⚙️ Installation with docker-compose

To install the API, you can run the following command from the root folder of the project:

```bash
docker-compose build
```

## 🛠️ Environment variables

Before running the API, you need to set the following environment variables:

| Name             | Description                          | Default value                    |
|------------------|--------------------------------------|----------------------------------|
| `JWT_SECRET`     | Secret used to sign JWT tokens       | _Unspecified_                    |
| `INSTANCE_PATH`  | Path to the database instance folder | `/instance  `                    |
| `DATABASE_URL`   | Database URL                         | `sqlite:////instance/sgde_db.db` |
| `GENERATOR_PATH` | Path to the generator folder         | `/instance/generators`           |
| `PORT`           | Port to run the server on            | `8000`                           |

You can add these variables to a `.api.env` file in the root folder of the project.

## 🏎️ Running the API with docker-compose

To run the API, you can run the following command from the root folder of the project:

```bash
docker-compose up -d
```

To stop the API, you can run the following command from the root folder of the project:

```bash
docker-compose down
```

## 📖 API Documentation

Once started, the API documentation is available at the following address: [http://localhost:8000/docs](http://localhost:8000/docs).
The available endpoints are:

### Authentication Endpoints

`GET /users`: Get a list of all the users registered to SGDE.

_Returns_:
* `200 OK`: list of users

---

`GET /users/{username}`: Get a user by their username.

_Parameters_:
* `username`: username of the user to get

_Returns_:
* `200 OK`: user with the given username
* `404 Not found`: user with the given username not found

---

`POST /auth/register`: Register a new user.

_Body_:
* `username`: username of the user to register
* `email`: email of the user to register
* `password`: password of the user to register

_Returns_:
* `201 Created`: user created
* `400 Bad Request`: invalid request body
* `400 Bad Request`: username already exists
* `400 Bad Request`: email already exists

---

`POST /auth/token`: Create a new access token.

_Body_:
* `username`: username of the user to login
* `password`: password of the user to login

_Returns_:
* `201 Created`: access token created
* `400 Bad Request`: invalid request body
* `401 Unauthorized`: invalid username or password
* `404 Not Found`: user with the given username not found

---

`GET /auth/whoami`: Get the current user.

_Headers_:
* `Authorization`: access token of the user

_Returns_:
* `200 OK`: current user
* `401 Unauthorized`: invalid access token

### Generator Endpoints

`GET /generators`: Get a list of all the generators' metadata.

_Returns_:
* `200 OK`: list of generators

---

`GET /generators/{name}`: Get a generator metadata by its name.

_Parameters_:
* `name`: name of the generator to get

_Returns_:
* `200 OK`: generator with the given name
* `404 Not found`: generator with the given name not found

---

`POST /exchange/upload`: Upload a new generator to the SGDE server.

_Body_:
* `gen_onnx_file`: file containing the generator to upload
* `cls_onnx_file` (optional): file containing the classifier to validate the generator
* `json_file`: file containing the generator's metadata; the JSON file must contain only integers, floats, strings, and lists of integers, floats, and strings; required fields are
  * `name`: name of the generator to upload
  * `data_name`: name of the dataset used to train the generator
  * `data_description`: description of the dataset used to train the generator
  * `data_structure`: structure of the dataset input (currently supported: "image")
  * `data_length`: number of data samples to train the generator
  * `task`: target task for the generated data (currently supported: "classification")
  * `metric`: target metric to validate the best generator, e.g., "accuracy"
  * `best_score`: best score achieved by the classifier on synthetic data
  * `best_score_real`: best score achieved by the classifier on real data

_Returns_:
* `201 Created`: generator uploaded
* `400 Bad Request`: invalid request body
* `400 Bad Request`: generator already exists
* `400 Bad Request`: invalid ONNX file
* `401 Unauthorized`: invalid access token

---

`GET /generators/{name}/download`: Download a generator's ONNX file from the SGDE server.

_Parameters_:
* `name`: name of the generator to download

_Returns_:
* `200 OK`: generator's zip file containing the ONNX file of the generator, an optional ONNX file of a classifier, and the complete JSON metadata file
* `401 Unauthorized`: invalid access token
* `404 Not found`: generator with the given name not found

## 📚 References

- [SGDE Paper](https://arxiv.org/abs/2109.12062)
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)

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
