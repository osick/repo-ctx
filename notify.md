# .github/ISSUE_TEMPLATE/bug_report.md - bug_report

--- name: Bug report about: Create a report to help us improve title: '' labels: '' assignees: ''.

---

# .github/ISSUE_TEMPLATE/feature_request.md - feature_request

--- name: Feature request about: Suggest an idea for this project title: '' labels: '' assignees: ''.

---

# CONTRIBUTING.md - Contribute to **deep**doctection

We are happy to welcome you as a contributor to **deep**doctection. This document will guide you through the 
process of contributing to the project.

## Code Examples

### One possibility is to hand over the entire installation palette. This is sufficient
```python
import deepdoctection as dd

print(dd.collect_env_info())
```

### Example usage
```text
### Adding new features

Deepdoctection was designed and developed almost exclusively by Dr. Janis Meyer. 
Before you have an idea for a major adaptation or extension of the code base, it is 
advisable to get in touch with him to discuss a possible implementation. 

## Setting up the development environment


If you want to develop your own deepdoctection, the easiest way is to fork the repo. 

There is a Makefile for installation in development mode that can simplify the work. 

```bash
make install-dd-dev-pt
```

### Example usage
```bash
make install-dd-dev-pt
```

### Example usage
```text
or

```bash
make install-dd-dev-tf
```

### Example usage
```bash
make install-dd-dev-tf
```

### Example usage
```text
installs deepdoctection in editable mode together with the dependencies for testing, development and 
documentation.

## Code quality and type checking

We use Pylint for checking code quality and isort as well as black for code formatting:

```bash
make lint
```

### We use Pylint for checking code quality and isort as well as black for code formatting
```bash
make lint
```

### We use Pylint for checking code quality and isort as well as black for code formatting
```text
```bash
make format
```

### Example usage
```bash
make format
```

### Example usage
```text
We use mypy for type checking:

```bash
make analyze
```

### We use mypy for type checking
```bash
make analyze
```

### We use mypy for type checking
```text
## Testing the environment

Test cases are divided into six groups, which differ in terms of which dependency the test case is based on. 
The 
dependencies are based on the installation options as specified in setup.py.

`basic`: The basic installation without DL-Libary. Only the packages that are assigned to the dist_deps in 
setup.py are 
required.

`additional`: Extended installation without DL library. All dist_deps and additional_deps packages are 
required.

`tf_deps`: Installation with Tensorflow

`pt_deps`: Installation with PyTorch

`requires_gpu`: Test cases that run functions using the GPU

`integration`: Integration test, where a complete pipeline is tested

Test cases with bundled groups can be executed in the Makefile. The most important bundles are

```bash
make test-basic  # Runs only the basic package
make test-pt  # Runs the basic, additional, pt_deps and integration groups.
make test-tf  # Runs the basic, additional and tf_deps groups.
```

### Example usage
```bash
make test-basic  # Runs only the basic package
make test-pt  # Runs the basic, additional, pt_deps and integration groups.
make test-tf  # Runs the basic, additional and tf_deps groups.
```

### Example usage
```text
You can trigger Github Actions to run the tests by pushing your changes to your fork by adding `[force ci]` to
your 
commit message. This will run formatting checks, mypy, pylint and tests und Python 3.8 and 3.10.
```

---

# README.md - NEW

<p align="center"> <img 
src="https://github.com/deepdoctection/deepdoctection/raw/master/docs/tutorials/_imgs/dd_logo.png" alt="Deep 
Doctection Logo" width="60%"> </p>.

## Code Examples

### Example usage
```text
pip install gradio_client   # requires Python >= 3.10
```

### Example usage
```text
To process a single image:

```python
from gradio_client import Client, handle_file

if __name__ == "__main__":

    client = Client("deepdoctection/deepdoctection")
    result = client.predict(
        img=handle_file('/local_path/to/dir/file_name.jpeg'),  # accepts image files, e.g. JPEG, PNG
        pdf=None,   
        max_datapoints = 2,
        api_name = "/analyze_image"
    )
    print(result)
```

### To process a single image
```python
from gradio_client import Client, handle_file

if __name__ == "__main__":

    client = Client("deepdoctection/deepdoctection")
    result = client.predict(
        img=handle_file('/local_path/to/dir/file_name.jpeg'),  # accepts image files, e.g. JPEG, PNG
        pdf=None,   
        max_datapoints = 2,
        api_name = "/analyze_image"
    )
    print(result)
```

### Example usage
```text
To process a PDF document:

```python
from gradio_client import Client, handle_file

if __name__ == "__main__":

    client = Client("deepdoctection/deepdoctection")
    result = client.predict(
        img=None,
        pdf=handle_file("/local_path/to/dir/your_doc.pdf"),
        max_datapoints = 2, # increase to process up to 9 pages
        api_name = "/analyze_image"
    )
    print(result)
```

### To process a PDF document
```python
from gradio_client import Client, handle_file

if __name__ == "__main__":

    client = Client("deepdoctection/deepdoctection")
    result = client.predict(
        img=None,
        pdf=handle_file("/local_path/to/dir/your_doc.pdf"),
        max_datapoints = 2, # increase to process up to 9 pages
        api_name = "/analyze_image"
    )
    print(result)
```

### Example usage
```text
--------------------------------------------------------------------------------------------------------

# Example

```python
import deepdoctection as dd
from IPython.core.display import HTML
from matplotlib import pyplot as plt

analyzer = dd.get_dd_analyzer()  # instantiate the built-in analyzer similar to the Hugging Face space demo

df = analyzer.analyze(path = "/path/to/your/doc.pdf")  # setting up pipeline
df.reset_state()                 # Trigger some initialization

doc = iter(df)
page = next(doc) 

image = page.viz(show_figures=True, show_residual_layouts=True)
plt.figure(figsize = (25,17))
plt.axis('off')
plt.imshow(image)
```

### # Example
```python
import deepdoctection as dd
from IPython.core.display import HTML
from matplotlib import pyplot as plt

analyzer = dd.get_dd_analyzer()  # instantiate the built-in analyzer similar to the Hugging Face space demo

df = analyzer.analyze(path = "/path/to/your/doc.pdf")  # setting up pipeline
df.reset_state()                 # Trigger some initialization

doc = iter(df)
page = next(doc) 

image = page.viz(show_figures=True, show_residual_layouts=True)
plt.figure(figsize = (25,17))
plt.axis('off')
plt.imshow(image)
```

### Example usage
```text
<p align="center">
  <img src="https://github.com/deepdoctection/deepdoctection/raw/master/docs/tutorials/_imgs/dd_rm_sample.png"
alt="sample" width="40%">
</p>
```

### Example usage
```text
HTML(page.tables[0].html)
```

### Example usage
```text
<p align="center">
  <img src="https://github.com/deepdoctection/deepdoctection/raw/master/docs/tutorials/_imgs/dd_rm_table.png" 
alt="table" width="40%">
</p>
```

### Example usage
```text
print(page.text)
```

### Example usage
```text
<p align="center">
  <img src="https://github.com/deepdoctection/deepdoctection/raw/master/docs/tutorials/_imgs/dd_rm_text.png" 
alt="text" width="40%">
</p>


-----------------------------------------------------------------------------------------

# Requirements

![requirements](https://github.com/deepdoctection/deepdoctection/raw/master/docs/tutorials/_imgs/install_01.pn
g)

- Linux or macOS. Windows is not supported but there is a 
[Dockerfile](./docker/pytorch-cpu-jupyter/Dockerfile) available.
- Python >= 3.9
- 2.6 \<= PyTorch **or** 2.11 \<= Tensorflow < 2.16. (For lower Tensorflow versions the code will only run on 
a GPU).
  Tensorflow support will be stopped from Python 3.11 onwards.
- To fine-tune models, a GPU is recommended.

| Task | PyTorch | Torchscript | Tensorflow |
|---------------------------------------------|:-------:|----------------|:------------:|
| Layout detection via Detectron2/Tensorpack | ✅ | ✅ (CPU only) | ✅ (GPU only) |
| Table recognition via Detectron2/Tensorpack | ✅ | ✅ (CPU only) | ✅ (GPU only) |
| Table transformer via Transformers | ✅ | ❌ | ❌ |
| Deformable-Detr | ✅ | ❌ | ❌ |
| DocTr | ✅ | ❌ | ✅ |
| LayoutLM (v1, v2, v3, XLM) via Transformers | ✅ | ❌ | ❌ |

------------------------------------------------------------------------------------------

# Installation

We recommend using a virtual environment.

## Get started installation

For a simple setup which is enough to parse documents with the default setting, install the following:

**PyTorch**
```

### For a simple setup which is enough to parse documents with the default setting, install the following
```text
pip install transformers
pip install python-doctr==0.10.0 # If you use Python 3.10 or higher you can use the latest version.
pip install deepdoctection
```

### Example usage
```text
**TensorFlow**
```

### Example usage
```text
pip install tensorpack
pip install deepdoctection
pip install "numpy>=1.21,<2.0" --upgrade --force-reinstall  # because TF 2.11 does not support numpy 2.0 
pip install "python-doctr==0.9.0"
```

### Example usage
```text
Both setups are sufficient to run the [**introduction 
notebook**](https://github.com/deepdoctection/notebooks/blob/main/Get_Started.ipynb).

### Full installation

The following installation will give you ALL models available within the Deep Learning framework as well as 
all models
that are independent of Tensorflow/PyTorch.

**PyTorch**

First install **Detectron2** separately as it is not distributed via PyPi. Check the instruction
[here](https://detectron2.readthedocs.io/en/latest/tutorials/install.html) or try:
```

### [here](https://detectron2.readthedocs.io/en/latest/tutorials/install.html) or try
```text
pip install detectron2@git+https://github.com/deepdoctection/detectron2.git
```

### [here](https://detectron2.readthedocs.io/en/latest/tutorials/install.html) or try
```text
Then install **deep**doctection with all its dependencies:
```

### Then install **deep**doctection with all its dependencies
```text
pip install deepdoctection[pt]
```

### Then install **deep**doctection with all its dependencies
```text
**Tensorflow**
```

### Example usage
```text
pip install deepdoctection[tf]
```

### Example usage
```text
For further information, please consult the [**full installation 
instructions**](https://deepdoctection.readthedocs.io/en/latest/install/).


## Installation from source

Download the repository or clone via
```

### Installation from source
```text
git clone https://github.com/deepdoctection/deepdoctection.git
```

### Example usage
```text
**PyTorch**
```

### Example usage
```text
cd deepdoctection
pip install ".[pt]" # or "pip install -e .[pt]"
```

### Example usage
```text
**Tensorflow**
```

### Example usage
```text
cd deepdoctection
pip install ".[tf]" # or "pip install -e .[tf]"
```

### Example usage
```text
## Running a Docker container from Docker hub

Pre-existing Docker images can be downloaded from the [Docker 
hub](https://hub.docker.com/r/deepdoctection/deepdoctection).
```

### Running a Docker container from Docker hub
```text
docker pull deepdoctection/deepdoctection:<release_tag>
```

### Example usage
```text
Use the Docker compose file `./docker/pytorch-gpu/docker-compose.yaml`.
In the `.env` file provided, specify the host directory where **deep**doctection's cache should be stored.
Additionally, specify a working directory to mount files to be processed into the container.
```

### Example usage
```text
docker compose up -d
```

### Example usage
```text
will start the container. There is no endpoint exposed, though.

-----------------------------------------------------------------------------------------------

# Credits

We thank all libraries that provide high quality code and pre-trained models. Without, it would have been 
impossible
to develop this framework.


# If you like **deep**doctection ...

...you can easily support the project by making it more visible. Leaving a star or a recommendation will help.

# License

Distributed under the Apache 2.0 License. Check 
[LICENSE](https://github.com/deepdoctection/deepdoctection/blob/master/LICENSE) for additional information.
```

---

# docker/pytorch-cpu-jupyter/README.md - Dockerfile for Docker version (>=20.10)

This Dockerfile allows you to build an image to based on the base layer `python:3.8-slim` with torch for CPU 
and the full **deep**doctection suite installed for demonstration purposes. A Jupyter notebook for can be used
to run sample code in the container.

## Code Examples

### run sample code in the container.
```text
docker build -t dd:<your-tag> -f docker/pytorch-cpu-jupyter/Dockerfile .
```

### Example usage
```text
Then start running a container. Specify a host directory if you want to have some files mounted into the 
container
```

### Example usage
```text
docker run -d -t --name=dd-jupyter -v /host/to/dir:/home/files -p 8888:8888 dd:<your_tag>
```

### Example usage
```text
You can then access jupyter through `http://localhost:8888/tree`. You will have to enter a token you can 
access through
container logs:
```

### container logs
```text
docker logs <container id>
```

### container logs
```text

```

---

# docker/pytorch-cpu/README.md - Dockerfile for Docker version (>=20.10)

This Dockerfile allows you to build an image to based on the base layer `python:3.9-slim` with torch for CPU 
and the full **deep**doctection suite installed for demonstration purposes.

## Code Examples

### Example usage
```text
docker build -t dd:<your-tag> -f docker/pytorch-cpu/Dockerfile .
```

### Example usage
```text
Then start running a container. Specify a host directory if you want to have some files mounted into the 
container
```

### Example usage
```text
docker run -d -t --name=dd-deepdoctection-cpu -v /host/to/dir:/home/files dd:<your-tag>
```

### Example usage
```text

```

---

# docker/pytorch-gpu/README.md - Dockerfile for Docker version (>=20.10)

This Dockerfile allows you to build an image to based on the base layer 
`nvidia/cuda:11.7.1-cudnn8-devel-ubuntu22.04` with torch and GPU support for the full **deep**doctection 
suite.

## Code Examples

### Example usage
```text
docker build -t deepdoctection/deepdoctection:<your-tag> -f docker/pytorch-gpu/Dockerfile .
```

### Example usage
```text
Then start running a container. You can specify a volume for the cache, so that you do not need to download 
all weights
and configs once you re-start the container.
```

### Example usage
```text
docker run --name=dd-gpu --gpus all -v /host/to/dir:/home/files -v /path/to/cache:/root/.cache/deepdoctection 
-d -it deepdoctection/deepdoctection:<your-tag>
```

### Example usage
```text
# Getting a Docker image from the Docker hub for the last published release

With the release of version v.0.27.0, we are starting to provide Docker images for the full installation. 
This is due to the fact that the requirements and dependencies are complex and even the construction of Docker
images 
can lead to difficulties.

## Pulling images from the Docker hub:
```

### Pulling images from the Docker hub:
```text
docker pull deepdoctection/deepdoctection:<release_tag>
```

### Pulling images from the Docker hub:
```text
The container can be started with the above `docker run` command.

## Starting a container with docker compose

We provide a `docker-compose.yaml` file to start the generated image pulled from the hub. In order to use it, 
replace 
first the image argument with the tag, you want to use. Second, in the `.env` file, set the two environment 
variables:

`CACHE_HOST`: Model weights/configuration files, as well as potentially datasets, are not baked into the image
during 
the build time, but mounted into the container with volumes. For a local installation, this is 
usually `~/.cache/deepdoctection`.

`WORK_DIR`: A temporary directory where documents can be loaded and also mounted into the container.

The container can be started as usual, for example, with:
```

### The container can be started as usual, for example, with
```text
docker compose up -d
```

### The container can be started as usual, for example, with
```text
Using the interpreter of the container, you can then run something like this:

```python
import deepdoctection as dd

if __name__=="__main__":

    analyzer = dd.get_dd_analyzer()

    df = analyzer.analyze(path = "/home/files/your_doc.pdf")
    df.reset_state()

    for dp in df:
        print(dp.text)
```

### Using the interpreter of the container, you can then run something like this
```python
import deepdoctection as dd

if __name__=="__main__":

    analyzer = dd.get_dd_analyzer()

    df = analyzer.analyze(path = "/home/files/your_doc.pdf")
    df.reset_state()

    for dp in df:
        print(dp.text)
```

### for dp in df
```text

```

---

# docs/about.md - About **deep**doctection

Documents are everywhere: in business, administration, and private life. They are a foundational medium for 
storing and communicating information. Well-crafted documents combine content, structure, and visual layout to
guide the reader and highlight the most important data.

---

# docs/index.md - <p align="center">

<p align="center"> <img 
src="https://github.com/deepdoctection/deepdoctection/raw/master/docs/tutorials/_imgs/dd_logo.png" alt="Deep 
Doctection Logo" width="100%"> </p>.

---

# docs/install.md - ## Requirements

![](./tutorials/_imgs/install_01.png).

## Code Examples

### Minimal setup
```text
pip install transformers
pip install python-doctr==0.9.0
pip install deepdoctection
```

### Example usage
```text
#### Tensorflow
```

### Example usage
```text
pip install tensorpack
pip install deepdoctection
pip install "numpy>=1.21,<2.0" --upgrade --force-reinstall  # because TF 2.11 does not support numpy 2.0 
pip install "python-doctr==0.9.0"
```

### Example usage
```text
Both setups are sufficient to run the [**introduction 
notebook**](https://github.com/deepdoctection/notebooks/blob/main/Get_Started.ipynb). 

### Full setup

This will give you ALL models available within the Deep Learning framework as well as all models
that are independent of Tensorflow/PyTorch.

#### PyTorch 

First install [**Detectron2**](https://detectron2.readthedocs.io/en/latest/tutorials/install.html) separately 
as it 
is not distributed via PyPi.

You can use our fork:
```

### You can use our fork
```text
pip install detectron2@git+https://github.com/deepdoctection/detectron2.git
```

### You can use our fork
```text
Then install all remaining dependencies with:
```

### Then install all remaining dependencies with
```text
pip install deepdoctection[pt]
```

### Then install all remaining dependencies with
```text
#### Tensorflow
```

### Example usage
```text
pip install deepdoctection[tf]
```

### Example usage
```text
!!! info 

    This will install **deep**doctection with all dependencies listed in the dependency diagram above the 
**deep**doctection 
    layer. This includes:

    - **Boto3**, the AWS SDK for Python to provide an API to AWS Textract (only OCR service). This is a paid 
service and 
      requires an AWS account.
    - **Pdfplumber**, a PDF text miner based on Pdfminer.six
    - **Fasttext**, a library for efficient learning of word representations and sentence classification. Used
for language
      recognition only. The **Fasttext** is in archive mode and will be removed in a future version.
    - **Jdeskew**, a library for automatic deskewing of images.
    - **Transformers**, a library for state-of-the-art NLP models. 
    - **DocTr**, an OCR library as alternative to Tesseract
    - **Tensorpack**, if the Tensorflow setting has been installed. Tensorpack is a library for training 
models and also 
      provides many examples. We only use the object detection model.


If you want to have more control with your installation and are looking for fewer dependencies then 
install **deep**doctection with the basic setup only and add the dependencies you need manually.


### Install from source

If you want all files and latest additions etc. then download the repository or clone via
```

### Install from source
```text
git clone https://github.com/deepdoctection/deepdoctection.git
```

### Example usage
```text
Install the package in a virtual environment. Learn more about 
[`virtualenv`](https://docs.python.org/3/tutorial/venv.html). 


#### PyTorch

Again, install [**Detectron2**](https://detectron2.readthedocs.io/en/latest/tutorials/install.html) 
separately.
```

### Example usage
```text
cd deepdoctection
pip install ".[source-pt]"
```

### Example usage
```text
#### Tensorflow
```

### Example usage
```text
cd deepdoctection 
pip install ".[tf]"
```

### Example usage
```text
### Running a Docker container from Docker hub

Starting from release `v.0.27.0`, pre-existing Docker images can be downloaded from the [Docker 
hub](https://hub.docker.com/r/deepdoctection/deepdoctection).
```

### Running a Docker container from Docker hub
```text
docker pull deepdoctection/deepdoctection:<release_tag>
```

### Example usage
```text
To start the container, you can use the Docker compose file `./docker/pytorch-gpu/docker-compose.yaml`. 
In the `.env` file provided, specify the host directory where **deep**doctection's cache should be stored. 
This directory will be mounted. Additionally, specify a working directory to mount files to be processed into 
the 
container.
```

### Example usage
```text
docker compose up -d
```

### Example usage
```text
will start the container.

We provide a few more [Dockerfiles](https://github.com/deepdoctection/deepdoctection/tree/master/docker).


## Developing and testing

To make a full dev installation with an additional update of all requirements, run
```

### Example usage
```text
make install-dd-dev-pt
```

### Example usage
```text
or
```

### Example usage
```text
make install-dd-dev-tf
```

### Example usage
```text
To run the test cases use `make` and check the Makefile for the available targets.


### Formatting, linting and type checking
```

### Formatting, linting and type checking
```text
make format-and-qa
```

### Formatting, linting and type checking
```text

```

---

# docs/modules/deepdoctection.analyzer.md - deepdoctection.analyzer

::: deepdoctection.analyzer options: show_submodules: True filters: - "!config_sanity_checks".

---

# docs/modules/deepdoctection.dataflow.md - deepdoctection.dataflow

::: deepdoctection.dataflow options: show_submodules: True filters: - "!DataFlowTerminated" - 
"!DataFlowResetStateNotCalled" - "!DataFlowReentrantGuard" - "!del_weakref" - "!_MultiProcessZMQDataFlow" - 
"!_ParallelMapData".

---

# docs/modules/deepdoctection.datapoint.md - deepdoctection.datapoint

::: deepdoctection.datapoint options: show_submodules: True filters: - "!__post_init__" - "!as_dict" - 
"__getattr__" - "!ann_from_dict" - "!AnnotationMap".

---

# docs/modules/deepdoctection.datasets.md - deepdoctection.datasets

::: deepdoctection.datasets.

---

# docs/modules/deepdoctection.eval.md - deepdoctection.eval

::: deepdoctection.eval options: show_submodules: True filters: - "!sub_cats" - "!summary_sub_categories" - 
"!_MAX_DET_INDEX".

---

# docs/modules/deepdoctection.extern.md - deepdoctection.extern

::: deepdoctection.extern.

---

# docs/modules/deepdoctection.extern.tp.md - deepdoctection.extern.tp

::: deepdoctection.extern.tp.tfutils options: show_submodules: True.

---

# docs/modules/deepdoctection.mapper.md - deepdoctection.mapper

::: deepdoctection.mapper options: show_submodules: True filters: - "!__enter__" - "!__exit__".

---

# docs/modules/deepdoctection.pipe.md - deepdoctection.pipe

::: deepdoctection.pipe options: show_submodules: True filters: - "!datapoint" - "!_entry" - "!build_pipe" - 
"!clone" - "!cell" - "!_html_row" - "!_html_table" - "!_default_segment_table".

---

# docs/modules/deepdoctection.utils.md - deepdoctection.utils

::: deepdoctection.utils options: show_submodules: True filters: - "!concurrency" - "!develop" - 
"!IsDataclass" - "!PopplerNotFound" - "!TesseractNotFound" - "!_LazyModule" - "!FileExtensionError" - 
"!LoadImageFunc" - "!__getattr__" - "!__setattr__" - "!__str__" - "!PopplerError".

---

# docs/requirements.txt - # This file is autogenerated by pip-compile with Python 3.9

accelerate==0.29.1 attrs==22.2.0 boto3==1.34.102 botocore==1.34.144 catalogue==2.0.10 certifi==2022.12.7 
cffi==1.15.1 charset-normalizer==2.1.1 click==8.1.3 colorama==0.4.6 cryptography==38.0.4 filelock==3.8.2 
fsspec==2023.12.2 ghp-import==2.1.0 griffe==0.25.0 huggingface-hub==0.28.1 idna==3.4 importlib-metadata==5.2.0
jdeskew==0.2.2 jinja2==3.0.3 jmespath==1.0.1 jsonlines==3.1.0 lazy-imports==0.3.1 lxml==4.9.2 
lxml-stubs==0.5.1 markdown==3.3.7 markupsafe==2.1.1 mergedeep==1.3.4 mkdocs==1.4.2 mkdocs-autorefs==0.4.1 
mkdocs-material==8.5.11 mkdocs-material-extensions==1.1.1 mkdocstrings==0.19.1 mkdocstrings-python==0.8.2 
mock==4.0.3 mpmath==1.3.0 msgpack==1.0.4 msgpack-numpy==0.4.8 networkx==2.8.8 numpy==1.24.0 
opencv-python-headless==4.9.0.80 packaging==21.3 pdfminer-six==20231228 pdfplumber==0.11.2 pillow==10.1.0 
psutil==5.9.4 pycparser==2.21 pygments==2.13.0 pymdown-extensions==9.9 pyparsing==3.0.9 pypdf==6.0.0 
pypdfium2==4.30.0 python-dateutil==2.8.2 pyyaml==6.0.1 pyyaml-env-tag==0.1 pyzmq==24.0.1 regex==2022.10.31 
requests==2.28.1 s3transfer==0.10.2 safetensors==0.4.1 scipy==1.13.1 six==1.16.0 sympy==1.12 tabulate==0.9.0 
tensorpack==0.11 termcolor==2.1.1 tokenizers==0.21.0 torch==2.1.2 tqdm==4.64.0 transformers==4.48.3 
typing-extensions==4.4.0 urllib3==1.26.13 watchdog==2.2.0 zipp==3.11.0.

---

# docs/tutorials/Analyzer_Configuration.md - Analyzer Configuration

<p align="center"> <img 
src="https://github.com/deepdoctection/deepdoctection/raw/master/docs/tutorials/_imgs/dd_logo.png" alt="Deep 
Doctection Logo" width="60%"> <h3 align="center"> </h3> </p>.

## Code Examples

### Pass the adjustments in a list
```python
import deepdoctection as dd

config_overwrite = ["USE_TABLE_SEGMENTATION=False",
                    "USE_OCR=False",
                    "TEXT_ORDERING.BROKEN_LINE_TOLERANCE=0.01",
                    "PT.LAYOUT.FILTER=['title']"]  # (1) 

analyzer = dd.get_dd_analyzer(config_overwrite=config_overwrite)
```

### Example usage
```text
1. Ensure to include quotation marks around the string values (e.g., ['title']), as omitting them may cause 
parsing 
   errors.

### Configuration file

There is a configuration file that can be used to set the default parameters. The configuration file is 
located at 
`~/.cache/deepdoctection/configs/dd/conf_dd_one.yaml`.

!!! info "Cache directory"
    **deep**doctection creates a cache directory the first time `dd.get_dd_analyzer()` is called. This cache 
directory 
    stores all models and configurations that are used at any point in time.  The configuration file is 
located at 
    `~/.cache/deepdoctection`.

The config file will be used once we set `dd.get_dd_analyzer(load_default_config_file=True)`.  

!!! info 

    We can use the configuration file or the `config_overwrite` argument to overwrite the default setting
    Note, that `config_overwrite` has higher priority. 

## High level Configuration

The analyzer consists of various steps that can be switched on and off. 

```yaml
USE_ROTATOR: False, # (1) 
USE_LAYOUT: True, # (2)
USE_LAYOUT_NMS: True, # (3) 
USE_TABLE_SEGMENTATION: True, # (4) 
USE_TABLE_REFINEMENT: False, # (5)
USE_PDF_MINER: False, # (6)
USE_OCR: True, # (7) 
USE_LAYOUT_LINK: False, # (8)
USE_LINE_MATCHER: False, # (9)
```

### High level Configuration
```yaml
USE_ROTATOR: False, # (1) 
USE_LAYOUT: True, # (2)
USE_LAYOUT_NMS: True, # (3) 
USE_TABLE_SEGMENTATION: True, # (4) 
USE_TABLE_REFINEMENT: False, # (5)
USE_PDF_MINER: False, # (6)
USE_OCR: True, # (7) 
USE_LAYOUT_LINK: False, # (8)
USE_LINE_MATCHER: False, # (9)
```

### Example usage
```text
1. Determining the orientation of a page and rotating the page accordingly (requires Tesseract)
2. Segmenting a page into layout sections. We can choose various object detection models
3. Layout NMS by pairs of layout sections (e.g. 'table' and 'title'). Reduces significantly false positives.
4. This will determine cells and rows/column of a detected table
5. A particular component for a very specific table recognition model
6. When processing a PDF file, it will first try to extract words using pdfplumber
7. Whether to use an OCR engine
8. Whether to link layout sections, e.g. figure and caption
9. Only relevant for very specific layout models

## Layout models

Once `USE_LAYOUT=True` we can configure the layout pipeline component further.

!!! info "Layout models"

    Layout detection uses either Tensorpack's Cascade-RCNN, Deformable-Detr, Detectron2 Cascade-RCNN or 
Table-Transformer, 
    depending on which DL framework PyTorch or Tensorflow has been installed. Models have been trained on 
different datasets 
    and therefore return different layout sections. 

We can choose between `layout/d2_model_0829999_layout_inf_only.pt`, 
`microsoft/table-transformer-detection/pytorch_model.bin`, 
`Aryn/deformable-detr-DocLayNet/model.safetensors`. What works best on your use-case is up to you to check. 
For 
instance, we can switch between Pytorch models like this:

```yaml
PT:
   LAYOUT:
      FILTER:
         - figure
      PAD:
         BOTTOM: 0
         LEFT: 0
         RIGHT: 0
         TOP: 0
       PADDING: false
       WEIGHTS: layout/d2_model_0829999_layout_inf_only.pt
       WEIGHTS_TS: layout/d2_model_0829999_layout_inf_only.ts
```

### instance, we can switch between Pytorch models like this
```yaml
PT:
   LAYOUT:
      FILTER:
         - figure
      PAD:
         BOTTOM: 0
         LEFT: 0
         RIGHT: 0
         TOP: 0
       PADDING: false
       WEIGHTS: layout/d2_model_0829999_layout_inf_only.pt
       WEIGHTS_TS: layout/d2_model_0829999_layout_inf_only.ts
```

### Example usage
```text
Here, we are using the `model layout/d2_model_0829999_layout_inf_only.pt` for PyTorch. With

```yaml
FILTER:
  - figure
```

### Example usage
```yaml
FILTER:
  - figure
```

### FILTER
```text
we instruct the system to filter out all figure objects. 


!!! info "ModelCatalog"
    
    In general, the `ModelCatalog` can be used to obtain information about registered models. Each model has a
`Profile` 
    that includes information about its origin, the categories it can detect, and the framework that must be 
used to run 
    the model.

    ```python
    from dataclasses import asdict

    asdict(dd.ModelCatalog.get_profile("layout/d2_model_0829999_layout_inf_only.pt"))
```

### Example usage
```python
asdict(dd.ModelCatalog.get_profile("microsoft/table-transformer-detection/pytorch_model.bin"))
```

### Example usage
```text
!!! info "Output"

    {'name': 'microsoft/table-transformer-detection/pytorch_model.bin',
     'description': 'Table Transformer (DETR) model trained on PubTables1M. It was introduced in the paper 
PubTables-1M: Towards Comprehensive Table Extraction From Unstructured Documents by Smock et al. This model is
devoted to table detection',
     'size': [115393245],
     'tp_model': False,
     'config': 'microsoft/table-transformer-detection/config.json',
     'preprocessor_config': 'microsoft/table-transformer-detection/preprocessor_config.json',
     'hf_repo_id': 'microsoft/table-transformer-detection',
     'hf_model_name': 'pytorch_model.bin',
     'hf_config_file': ['config.json', 'preprocessor_config.json'],
     'urls': None,
     'categories': {1: <LayoutType.TABLE>, 2: <LayoutType.TABLE_ROTATED>},
     'categories_orig': None,
     'dl_library': 'PT',
     'model_wrapper': 'HFDetrDerivedDetector',
     'architecture': None,
     'padding': None}


```yaml
PT:
   LAYOUT:
      WEIGHTS: microsoft/table-transformer-detection/pytorch_model.bin
   PAD:
      TOP: 60
      RIGHT: 60
      BOTTOM: 60
      LEFT: 60
```

### Example usage
```yaml
PT:
   LAYOUT:
      WEIGHTS: microsoft/table-transformer-detection/pytorch_model.bin
   PAD:
      TOP: 60
      RIGHT: 60
      BOTTOM: 60
      LEFT: 60
```

### Example usage
```text
Table transformer requires image padding for more accurate results. The default padding provided might not be 
optimal. 
We can tweak and change it according to our needs.


### Custom model

!!! info "Custom model"

    A custom model can be added as well, but it needs to be registered. The same holds true for some special 
categories. 
    We refer to [this notebook](Analyzer_Model_Registry_And_New_Models.md) for adding your own or third party 
models.

## Layout Non-Maximum-Supression

This is relevant if `USE_LAYOUT_NMS=True`.


!!! info 
    
    Layout models often produce overlapping layout sections. These can be removed using Non-Maximum 
Suppression (NMS). 
    However, experience has shown that NMS often needs to be fine-tuned. For example, it can be useful to 
exclude tables 
    from the NMS process.

    Suppose a large and complex table is detected — it's not uncommon for a text block or a title to be 
mistakenly 
    recognized within the table as well, potentially even with a high confidence score. In such cases, you may
still want 
    to retain the table at all costs.

Using the `LAYOUT_NMS_PAIRS` configuration, we can define pairs of layout sections that should be subject to 
NMS 
once a certain overlap threshold is exceeded. Additionally, we can set a priority to specify which category 
should 
be favored when overlaps occur.

The configuration consists of three parts:

```yaml
LAYOUT_NMS_PAIRS:
  COMBINATIONS:  # Pairs of layout categories to be checked for NMS
    - - table
      - title
  PRIORITY:  # Preferred category when overlap occurs. If set to `None`, NMS uses the confidence score.
    - table
  THRESHOLDS:  # IoU overlap threshold. Pairs with lower IoU will be ignored.
    - 0.001
```

### The configuration consists of three parts
```yaml
LAYOUT_NMS_PAIRS:
  COMBINATIONS:  # Pairs of layout categories to be checked for NMS
    - - table
      - title
  PRIORITY:  # Preferred category when overlap occurs. If set to `None`, NMS uses the confidence score.
    - table
  THRESHOLDS:  # IoU overlap threshold. Pairs with lower IoU will be ignored.
    - 0.001
```

### Example usage
```text
## Table Segmentation in **deep**doctection

Table segmentation — i.e., the detection of cells, rows, columns, and multi-spanning cells — can be performed 
using two 
different approaches in **deep**doctection.


### Original deepdoctection approach

In the original method, table structure is constructed using two separate models: one for detecting cells and 
another 
for detecting rows and columns. Once these components are detected, the row and column indices of each cell 
are 
assigned based on how cells spatially overlap with the detected rows and columns.

!!! info
    
    While this description may sound straightforward, the underlying logic involves several intermediate 
steps:

        * Row and column regions must be “stretched” to fully cover the table.
        * Overlapping rows or columns that create ambiguity must be removed.
        * Specific rules for assigning cells to rows and columns must be applied, based on overlap criteria.


### Table Transformer Process

Starting from release **v0.34**, the default method for table segmentation is the **Table Transformer** 
approach. 
This model handles the detection of rows, columns, and multi-spanning cells in a single step. Moreover, the 
model is 
able to detect column header, projected row header and projected column headers. Cells are formed by 
intersecting the 
detected rows and columns. In a subsequent refinement step, simple (non-spanning) cells may be replaced with 
multi-spanning cells where appropriate.

Finally, each cell is assigned its row and column number.

!!! note
    
    Table Transformer is only available with **PyTorch**.

!!! info
    In practice, we have observed that the recognition of multi-spanning cells is **less reliable** for 
non-scientific 
    tables (e.g., tables not originating from medical articles). If multi-spanning headers are not essential, 
we 
    recommend filtering them out. The result is a table structure consisting only of simple cells, i.e., cells
    with `row_span = 1` and `column_span = 1`.


### Configuration

The segmentation configuration is extensive, and we cannot cover every setting in detail. For a comprehensive 
description of all parameters, we refer to the source code. We will focus on the parameters that have the most
significant impact on the segmentation results.

```yaml
SEGMENTATION:
  ASSIGNMENT_RULE: ioa  # (1) 
  FULL_TABLE_TILING: true  # (2) 
  REMOVE_IOU_THRESHOLD_COLS: 0.2 # (3) 
  REMOVE_IOU_THRESHOLD_ROWS: 0.2
  STRETCH_RULE: equal  # (4) 
  THRESHOLD_COLS: 0.4 # (5)
  THRESHOLD_ROWS: 0.4
```

### description of all parameters, we refer to the source code. We will focus on the parameters that have the 
most
```yaml
SEGMENTATION:
  ASSIGNMENT_RULE: ioa  # (1) 
  FULL_TABLE_TILING: true  # (2) 
  REMOVE_IOU_THRESHOLD_COLS: 0.2 # (3) 
  REMOVE_IOU_THRESHOLD_ROWS: 0.2
  STRETCH_RULE: equal  # (4) 
  THRESHOLD_COLS: 0.4 # (5)
  THRESHOLD_ROWS: 0.4
```

### Example usage
```text
1. IoU is another cell/row/column overlapping rule
2. In order to guarantee that the table is completely covered with rows and columns
3. Removes overlapping rows based on an IoU threshold. Helps prevent multiple row spans caused by overlapping 
detections.
   Note: for better alignment, SEGMENTATION.FULL_TABLE_TILING can be enabled. Using a low threshold here may 
result in 
   a very coarse grid.
4. How to stretch row/columns: left is another choice
5. Threshold for assigning a (special) cell to a row based on the chosen rule (IoU or IoA). The row assignment
is based 
   on the highest-overlapping row. Multiple overlaps can lead to increased rowspan.

!!! note

    The more accurate the underlying detectors are for your specific use case, the higher the thresholds 
(e.g., 
    `THRESHOLD_ROWS`, `THRESHOLD_COLS`) should be set to take full advantage of the predictions.

### Filtering Redundant Detections

The Table Transformer may detect redundant table structures and headers. To filter those out, apply the 
following:

```yaml
PT:
  ITEM:
    WEIGHTS: microsoft/table-transformer-structure-recognition/pytorch_model.bin
    FILTER:
      - table
      - column_header
      - projected_row_header
      - spanning
```

### The Table Transformer may detect redundant table structures and headers. To filter those out, apply the 
following
```yaml
PT:
  ITEM:
    WEIGHTS: microsoft/table-transformer-structure-recognition/pytorch_model.bin
    FILTER:
      - table
      - column_header
      - projected_row_header
      - spanning
```

### Example usage
```text
!!! note

    This ensures that only relevant cell structures are retained, improving clarity and reducing noise in the 
    segmentation output.


## Text extraction

There are four different options for text extraction.

### PDFPlumber

Extraction with pdfplumber. This requires native PDF documents where the text can be extracted from the byte 
encoding. 
If we try to pass images through this pipeline, we will run into an error.

```yaml
USE_PDF_MINER: True
```

### Example usage
```yaml
USE_PDF_MINER: True
```

### Example usage
```text
The remaining three are all OCR methods. If we want to use an OCR engine, we need to set `USE_OCR=True`.

!!! info

    It is possible to select PdfPlumber in combination with an OCR. If no text was extracted with PdfPlumber, 
the OCR 
    service will be called, otherwise it will be omitted. 

!!! info

    There is currently no option to grap everything with OCR that cannot be extracted with PdfPlumber. It is 
all or 
    nothing.  


```yaml
USE_OCR: True
OCR:
  USE_TESSERACT: False
  USE_DOCTR: True
  USE_TEXTRACT: False
```

### Example usage
```yaml
USE_OCR: True
OCR:
  USE_TESSERACT: False
  USE_DOCTR: True
  USE_TEXTRACT: False
```

### OCR
```text
### DocTr

DocTr is a powerful library that provides models for both TensorFlow and PyTorch. What makes it particularly 
valuable 
is that it includes training scripts and allows models to be trained with custom vocabularies. This makes it 
possible 
to build OCR models for highly specialized scripts where standard OCR solutions fail.

A DocTr OCR pipeline consists of two steps: spatial word detection and character recognition within the region
of 
interest.

!!! info

    For **DOCTR_WORD**, the following models are registered in the ModelCatalog:

    * For PyTorch: `doctr/db_resnet50/pt/db_resnet50-ac60cadc.pt`
    * For TensorFlow: `doctr/db_resnet50/tf/db_resnet50-adcafc63.zip`

    For **DOCTR_RECOGNITION**, you can choose from the following PyTorch models:

     * `doctr/crnn_vgg16_bn/pt/crnn_vgg16_bn-9762b0b0.pt`
     * `Felix92/doctr-torch-parseq-multilingual-v1/pytorch_model.bin`
     * `doctr/crnn_vgg16_bn/pt/master-fde31e4a.pt`

     For TensorFlow, only one model is currently registered:

     * `doctr/crnn_vgg16_bn/tf/crnn_vgg16_bn-76b7f2c6.zip`
 
To use DocTr set `OCR.USE_OCR=True` and select the model for word detection and text recognition.

```yaml
OCR:
  WEIGHTS:
    DOCTR_WORD:
      TF: doctr/db_resnet50/tf/db_resnet50-adcafc63.zip
      PT: doctr/db_resnet50/pt/db_resnet50-ac60cadc.pt
    DOCTR_RECOGNITION:
      TF: doctr/crnn_vgg16_bn/tf/crnn_vgg16_bn-76b7f2c6.zip
      PT: doctr/crnn_vgg16_bn/pt/crnn_vgg16_bn-9762b0b0.pt
```

### Example usage
```yaml
OCR:
  WEIGHTS:
    DOCTR_WORD:
      TF: doctr/db_resnet50/tf/db_resnet50-adcafc63.zip
      PT: doctr/db_resnet50/pt/db_resnet50-ac60cadc.pt
    DOCTR_RECOGNITION:
      TF: doctr/crnn_vgg16_bn/tf/crnn_vgg16_bn-76b7f2c6.zip
      PT: doctr/crnn_vgg16_bn/pt/crnn_vgg16_bn-9762b0b0.pt
```

### DOCTR_RECOGNITION
```text
### Tesseract

In addition to DocTr, Tesseract is arguably the most widely known open-source OCR solution and provides 
pre-trained 
models for a large number of languages. However, Tesseract must be installed separately. We refer to the 
official 
Tesseract documentation.

!!!info

    Tesseract comes with its own configuration file, which is located alongside other configuration files 
under 
    `~/.cache/deepdoctection/configs/dd/conf_dd_one.yaml`. 

To use Tesseract within the analyzer, configure it as follows:

```yaml
USE_OCR: True
OCR:
  USE_TESSERACT: True
  USE_DOCTR: False
  USE_TEXTRACT: False
```

### To use Tesseract within the analyzer, configure it as follows
```yaml
USE_OCR: True
OCR:
  USE_TESSERACT: True
  USE_DOCTR: False
  USE_TEXTRACT: False
```

### OCR
```text
### AWS Textract

Textract is the AWS OCR solution that can be accessed via an API. It is superior to the Open Source solutions.
This 
is a paid service and requires an AWS account. You also need to install `boto3`. We refer to the official 
documentation 
to access the service via API.

To use the API, credentials must be provided. We can either use the AWS CLI with its built-in secret 
management, or 
set the environment variables at the beginning: `AWS_ACCESS_KEY`, `AWS_SECRET_KEY`, and `AWS_REGION`.

To use Textract within the analyzer, configure as follows:

```yaml
USE_OCR: True
OCR:
  USE_TESSERACT: False
  USE_DOCTR: False
  USE_TEXTRACT: True
```

### To use Textract within the analyzer, configure as follows
```yaml
USE_OCR: True
OCR:
  USE_TESSERACT: False
  USE_DOCTR: False
  USE_TEXTRACT: True
```

### OCR
```text
The following two pipeline configuration will automatically be effective once you set `USE_OCR=True` or 
`USE_PDF_MINER=True`.


## Word matching


Word matching serves to merge the results of layout analysis (including table structure) with those of OCR. Up
to this 
point, all layout segments and words are independent elements of a page, with no established relationships 
between them. 
Word matching creates a link between each word and the appropriate layout segment.

!!! info

    The most effective way to establish this link is by evaluating the spatial overlap between a word and 
layout 
    segments. 
    It must be clearly defined which layout segments are eligible for such associations — not all segments are
    suitable. 
    For example, words that are part of a table should not be linked to the table's outer frame, but rather to
the 
    individual cell identified during table segmentation.

    The configuration below defines the layout segments that can be directly linked to words. Using the `RULE`
    parameter — 
    either *intersection-over-area* (`ioa`) or *intersection-over-union* (`iou`) — you can specify the logic 
for 
    determining 
    whether a relationship should be established. If the overlap exceeds the given `THRESHOLD`, a connection 
is made.

It is also possible for a word to overlap with multiple layout segments. In such cases, setting 
`MAX_PARENT_ONLY = True` 
ensures that the word is only assigned to the segment with the highest overlap score.

```yaml
WORD_MATCHING:
  PARENTAL_CATEGORIES: # This configuration is not equal to the default configuration
    - text
    - title
    - list
    - cell
  RULE: ioa
  THRESHOLD: 0.6
  MAX_PARENT_ONLY: True
```

### Example usage
```yaml
WORD_MATCHING:
  PARENTAL_CATEGORIES: # This configuration is not equal to the default configuration
    - text
    - title
    - list
    - cell
  RULE: ioa
  THRESHOLD: 0.6
  MAX_PARENT_ONLY: True
```

### Example usage
```text
## Reading Order

In the final step of the pipeline, words and layout segments must be arranged to form coherent, continuous 
text. This 
task is handled by the `TextOrderService` component.

!!! info

    Words that have been assigned to layout segments are grouped into lines, which are then read from top to 
bottom. To 
    sort layout segments effectively, auxiliary columns are constructed. These columns are further grouped 
into 
    **contiguous blocks** that vertically span the page. The reading order is then determined by traversing:

    * columns within a block from **left to right**, and
    * contiguous blocks from **top to bottom**.

    ![pipelines](./_imgs/analyzer_configuration_01.png)

It’s important to note that this method imposes an **artificial reading order**, which may not align with the 
true 
semantic structure of more complex or unconventional layouts.

Additionally, if layout detection is imprecise, the resulting reading order may be flawed. This is a known 
limitation 
and should always be kept in mind.

The `TextOrderService` can be configured using four key parameters:

* `TEXT_CONTAINER`: defines the category containing textual elements, such as `word`. Technically speaking, a 
text 
* container is an `ImageAnnotation` with the subcategory `WordType.CHARACTERS`. In most cases, this refers to 
* individual words. However, there are also OCR systems that return their results line by line, using the 
layout 
* type `LayoutType.LINE`.
* `TEXT_ORDERING.TEXT_BLOCK_CATEGORIES`: lists the layout segments to which words have been assigned and which
should 
   be ordered. In general you should list layout segments that have been added to 
   `TEXT_ORDERING.WORD_MATCHING.PARENTAL_CATEGORIES`.  
* `TEXT_ORDERING.FLOATING_TEXT_BLOCK_CATEGORIES`: defines segments that are not part of the main document flow
but 
   should still be considered (e.g., footnotes or side notes). A common question is whether tables should be 
part of 
   the main body text—by default, they are excluded.
* `TEXT_ORDERING.INCLUDE_RESIDUAL_TEXT_CONTAINER`: controls whether *orphan words* (those not assigned to any 
layout 
   segment) should be included in the output.

!!! note

    Let’s revisit the topic of **orphan words**:

    In the word matching process it is possible that some words do not overlap with any layout segment. 
    If `INCLUDE_RESIDUAL_TEXT_CONTAINER` is set to `False`, these words will not receive a `reading_order` and
will be 
    excluded from the text output.
    If set to `True`, orphan words are grouped into `line`s and included in the output, ensuring no text is 
lost. This 
    setting is often crucial and may need to be adjusted depending on your use case. We already covered this 
topic in 
    the [**More_on_parsing notebook**](Analyzer_More_On_Parsing.md)
```

---

# docs/tutorials/Analyzer_Configuration_Samples.md - Analyzer Configuration Samples

<p align="center"> <img 
src="https://github.com/deepdoctection/deepdoctection/raw/master/docs/tutorials/_imgs/dd_logo.png" alt="Deep 
Doctection Logo" width="60%"> <h3 align="center"> </h3> </p>.

## Code Examples

### General configuration
```python
import deepdoctection as dd

from matplotlib import pyplot as plt
from IPython.core.display import HTML

analyzer =dd.get_dd_analyzer(config_overwrite=
   ["PT.LAYOUT.WEIGHTS=microsoft/table-transformer-detection/pytorch_model.bin",
    "TEXT_ORDERING.INCLUDE_RESIDUAL_TEXT_CONTAINER=False", # (1) 
    "TEXT_ORDERING.PARAGRAPH_BREAK=0.01",]) # (2) 

analyzer.pipe_component_list[0].predictor.config.threshold = 0.8  # (3) 

path="/path/to/dir/sample/2312.13560.pdf"

df = analyzer.analyze(path=path)
df.reset_state()
df_iter = iter(df)

dp = next(df_iter)
np_image = dp.viz()

plt.figure(figsize = (25,17))
plt.axis('off')
plt.imshow(np_image)
```

### Example usage
```text
1. Deactivating line detection. Only table content
2. TATR table detection model
3. Default threshold is at 0.1

    
![png](./_imgs/analyzer_configuration_samples_01.png)


```python
dp.text  # (1)
```

### Example usage
```python
dp.text  # (1)
```

### Example usage
```text
1. Because of TEXT_ORDERING.INCLUDE_RESIDUAL_TEXT_CONTAINER=False, we do not generate text


```python
_ = next(df_iter)
dp = next(df_iter)
np_image = dp.viz()


plt.figure(figsize = (25,17))
plt.axis('off')
plt.imshow(np_image)
```

### Example usage
```python
_ = next(df_iter)
dp = next(df_iter)
np_image = dp.viz()


plt.figure(figsize = (25,17))
plt.axis('off')
plt.imshow(np_image)
```

### Example usage
```text
![png](./_imgs/analyzer_configuration_samples_02.png)
    



```python
dp.tables[0].csv
```

### Example usage
```python
dp.tables[0].csv
```

### Example usage
```text
??? info "Output"

    [['Dataset ', 'A-1 ', 'A-2 ', 'Libri-Adapt ', 'Avg. '],
     ['CTC ', '5.18 ', '6.18 ', '12.81 ', '8.06 '],
     ['KNN-CTC (full) ', '4.81 ', '5.53 ', '12.42 ', '7.59 '],
     ['Datastore size (G) ', '7.12 ', '47.12 ', '4.82 ', '19.69 '],
     ['KNN-CTC (pruned) ', '4.73 ', '5.46 ', '12.66 ', '7.62 '],
     ['Datastore size (G) ', '0.99 ', '6.65 ', '1.49 ', '3.04 ']]




```python
dp.tables[0].number_of_rows, dp.tables[0].row_header_cells # (1)
```

### Example usage
```python
dp.tables[0].number_of_rows, dp.tables[0].row_header_cells # (1)
```

### Example usage
```text
1. Does not detect row headers

??? info "Output"

    (6, [])




```python
dp = next(df_iter)
np_image = dp.viz()

plt.figure(figsize = (25,17))
plt.axis('off')
plt.imshow(np_image)
```

### Example usage
```python
dp = next(df_iter)
np_image = dp.viz()

plt.figure(figsize = (25,17))
plt.axis('off')
plt.imshow(np_image)
```

### Example usage
```text
![png](./_imgs/analyzer_configuration_samples_03.png)
    



```python
from IPython.core.display import HTML

HTML(dp.tables[1].html)
```

### Example usage
```python
from IPython.core.display import HTML

HTML(dp.tables[1].html)
```

### Example usage
```text
??? info "Output"

        <table><tr><td rowspan=2>Source Domain Target Domain</td><td 
colspan=7>Wenetspeech</td></tr><tr><td>AISHELL-1 
        (A-1)</td><td>Mandarin</td><td>JiangHuai</td><td>JiLu</td><td>ZhongYuan</td><td>Southwestern</td><td>A
vg.</td></tr><tr>
        <td>CTC</td><td>5.02</td><td>11.13</td><td>40.87</td><td>29.76</td><td>31.94</td><td>29.2</td><td>24.6
5</td></tr><tr>
        <td>KNN-CTC 
(full)</td><td>4.78</td><td>10.27</td><td>39.95</td><td>28.61</td><td>30.04</td><td>28.24</td><td>23.65</td>
        </tr><tr><td>Datastore size 
(G)</td><td>7.12</td><td>48.38</td><td>3.88</td><td>5.05</td><td>6.99</td><td>6.34</td>
        <td>12.96</td></tr><tr><td>KNN-CTC 
(pruned)</td><td>4.83</td><td>10.95</td><td>40.34</td><td>28.86</td><td>30.53</td>
        <td>28.41</td><td>23.99</td></tr><tr><td>Datastore Size 
(G)</td><td>0.99</td><td>5.27</td><td>0.54</td><td>0.52</td>
        <td>0.76</td><td>0.68</td><td>1.46</td></tr></table>


## Legacy Default Setting

Until release `v.0.42`, this configuration was the default setting. Please note the dependencies on Tesseract 
and 
Detectron2 (for PyTorch) and on Tensorpack (on Tensorflow).

It works well on scientific papers.


```python
analyzer = dd.get_dd_analyzer(config_overwrite=
        ["PT.LAYOUT.WEIGHTS=layout/d2_model_0829999_layout_inf_only.pt",
         "PT.ITEM.WEIGHTS=item/d2_model_1639999_item_inf_only.pt",
         "PT.ITEM.FILTER=None",
         "SEGMENTATION.REMOVE_IOU_THRESHOLD_ROWS=0.001",
         "SEGMENTATION.REMOVE_IOU_THRESHOLD_COLS=0.001",
         "WORD_MATCHING.THRESHOLD=0.6",
         "WORD_MATCHING.PARENTAL_CATEGORIES=['text','title','list','figure','cell','spanning']",
         "TEXT_ORDERING.TEXT_BLOCK_CATEGORIES=['text','title','list','figure','cell','spanning']",
         "TEXT_ORDERING.FLOATING_TEXT_BLOCK_CATEGORIES=['text','title','list','figure']",
         "TEXT_ORDERING.INCLUDE_RESIDUAL_TEXT_CONTAINER=False",
         "USE_LAYOUT_LINK=False",
         "LAYOUT_LINK.PARENTAL_CATEGORIES=[]",
         "LAYOUT_LINK.CHILD_CATEGORIES=[]",
         "OCR.USE_DOCTR=False",
         "OCR.USE_TESSERACT=True",
         "USE_LAYOUT_NMS=False",
         "USE_TABLE_REFINEMENT=True",
         "USE_LINE_MATCHER=False",
         "LAYOUT_NMS_PAIRS.COMBINATIONS=None",
         "LAYOUT_NMS_PAIRS.THRESHOLDS=None",
         "LAYOUT_NMS_PAIRS.PRIORITY=None"])

df = analyzer.analyze(path=path)
df.reset_state()
df_iter = iter(df)

dp = next(df_iter)
np_image = dp.viz()

plt.figure(figsize=(25, 17))
plt.axis('off')
plt.imshow(np_image)
```

### Example usage
```python
analyzer = dd.get_dd_analyzer(config_overwrite=
        ["PT.LAYOUT.WEIGHTS=layout/d2_model_0829999_layout_inf_only.pt",
         "PT.ITEM.WEIGHTS=item/d2_model_1639999_item_inf_only.pt",
         "PT.ITEM.FILTER=None",
         "SEGMENTATION.REMOVE_IOU_THRESHOLD_ROWS=0.001",
         "SEGMENTATION.REMOVE_IOU_THRESHOLD_COLS=0.001",
         "WORD_MATCHING.THRESHOLD=0.6",
         "WORD_MATCHING.PARENTAL_CATEGORIES=['text','title','list','figure','cell','spanning']",
         "TEXT_ORDERING.TEXT_BLOCK_CATEGORIES=['text','title','list','figure','cell','spanning']",
         "TEXT_ORDERING.FLOATING_TEXT_BLOCK_CATEGORIES=['text','title','list','figure']",
         "TEXT_ORDERING.INCLUDE_RESIDUAL_TEXT_CONTAINER=False",
         "USE_LAYOUT_LINK=False",
         "LAYOUT_LINK.PARENTAL_CATEGORIES=[]",
         "LAYOUT_LINK.CHILD_CATEGORIES=[]",
         "OCR.USE_DOCTR=False",
         "OCR.USE_TESSERACT=True",
         "USE_LAYOUT_NMS=False",
         "USE_TABLE_REFINEMENT=True",
         "USE_LINE_MATCHER=False",
         "LAYOUT_NMS_PAIRS.COMBINATIONS=None",
         "LAYOUT_NMS_PAIRS.THRESHOLDS=None",
         "LAYOUT_NMS_PAIRS.PRIORITY=None"])

df = analyzer.analyze(path=path)
df.reset_state()
df_iter = iter(df)

dp = next(df_iter)
np_image = dp.viz()

plt.figure(figsize=(25, 17))
plt.axis('off')
plt.imshow(np_image)
```

### Example usage
```text
![png](./_imgs/analyzer_configuration_samples_04.png)
    



```python
print(dp.text)
```

### Example usage
```python
print(dp.text)
```

### Example usage
```text
??? info "Output"

    KNN-CTC: ENHANCING ASR VIA RETRIEVAL OF CTC PSEUDO LABELS
    Jiaming Zhou', Shiwan Zhao*, Yagi Liu?, Wenjia Zeng’, Yong Chen’, Yong Qin'*
    ' Nankai University, Tianjin, China ? Beijing University of Technology, Beijing, China 3 Lingxi (Beijing) 
Technology 
    Co., Ltd.
    ABSTRACT
    The success of retrieval-augmented language models in var- ious natural language processing (NLP) tasks 
has been 
    con- strained in automatic speech recognition (ASR) applications due to challenges in constructing 
fine-grained 
    audio-text datastores. This paper presents KNN-CTC, a novel approach that overcomes these challenges by 
leveraging 
    Connection- ist Temporal Classification (CTC) pseudo labels to establish frame-level audio-text key-value 
pairs, 
    circumventing the need for precise ground truth alignments. We further in- troduce a “skip-blank” 
strategy, which 
    strategically ignores CTC blank frames, to reduce datastore size. By incorpo- rating a k-nearest neighbors
retrieval 
    mechanism into pre- trained CTC ASR systems and leveraging a fine-grained, pruned datastore, KNN-CTC 
consistently 
    achieves substan- tial improvements in performance under various experimental settings. Our code is 
available at 
    https://github.com/NKU- HLT/KNN-CTC.
    Index Terms— _ speech recognition, CTC, retrieval- augmented method, datastore construction
    1. INTRODUCTION
    In recent years, retrieval-augmented language models [1, 2, 3, 4, 5], which refine a pre-trained language 
model by 
    linearly interpolating the output word distribution with a k-nearest neighbors (KNN) model, have achieved 
remarkable 
    success across a broad spectrum of NLP tasks, encompassing lan- guage modeling, question answering, and 
machine 
    transla- tion. Central to the success of KNN language models is the construction of a high-quality 
key-value 
    datastore.
    Despite these advancements in NLP tasks, applications in speech tasks, particularly in automatic speech 
recognition 
    (ASR), remain constrained due to the challenges associ- ated with constructing a fine-grained datastore 
for the 
    audio modality. Early exemplar-based ASR [6, 7] utilized KNN to improve the conventional GMM-HMM or 
DNN-HMM based 
    approaches. Recently, Yusuf et al. [8] proposed enhancing
    + Corresponding author. This work was supported in part by NSF China (Grant No. 62271270).
    a transducer-based ASR model by incorporating a retrieval mechanism that searches an external text corpus 
for 
    poten- tial completions of partial ASR hypotheses. However, this method still falls under the KNN language
model 
    category, which only enhances the text modality of RNN-T [9]. Chan et al. [10] employed Text To Speech 
(TTS) to 
    generate audio and used the audio embeddings and semantic text embed- dings as key-value pairs to 
construct a 
    datastore, and then augmented the Conformer [11] with KNN fusion layers to en- hance contextual ASR. 
However, this 
    approach is restricted to contextual ASR, and the key-value pairs are coarse-grained, with both key and 
value at 
    the phrase level. Consequently, the challenge of constructing a fine-grained key-value datastore remains a
    substantial obstacle in the ASR domain.
    In addition to ASR, there have been a few works in other speech-related tasks. For instance, RAMP [12] 
incorporated 
    kKNN into mean opinion score (MOS) prediction by merg- ing the parametric model and the KNN-based 
non-parametric 
    model. Similarly, Wang et al. [13] proposed a speech emotion recognition (SER) framework that utilizes 
contrastive 
    learn- ing to separate different classes and employs KNN during in- ference to harness improved distances.
However, 
    both ap- proaches still rely on the utterance-level audio embeddings as the key, with ground truth labels 
as the 
    value.
    The construction of a fine-grained datastore for the audio modality in ASR tasks is challenged by two 
significant 
    obsta- cles: (i) the absence of precise alignment knowledge between audio and transcript characters, which
poses a 
    substantial dif- ficulty in acquiring the ground-truth labels (i.e., the values) necessary for the 
creation of 
    key-value pairs, and (ii) the im- mense volume of entries generated when processing audio at the frame 
level. In 
    this study, we present KNN-CTC, a novel approach that overcomes these challenges by utilizing CTC 
(Connectionist 
    Temporal Classification) [14] pseudo labels. This innovative method results in significant improvements in
ASR task 
    performance. By utilizing CTC pseudo labels, we are able to establish frame-level key-value pairs, 
eliminating the 
    need for precise ground-truth alignments. Additionally, we introduce a ’skip-blank’ strategy that exploits
the 
    inher- ent characteristics of CTC to strategically omit blank frames, thereby reducing the size of the 
datastore. 
    KNN-CTC attains comparable performance on the pruned datastore, and even
```

---

# docs/tutorials/Analyzer_Doclaynet_With_YOLO.md - Writing a predictor from a third party library

<p align="center"> <img 
src="https://github.com/deepdoctection/deepdoctection/raw/master/docs/tutorials/_imgs/dd_logo.png" alt="Deep 
Doctection Logo" width="60%"> <h3 align="center"> </h3> </p>.

## Code Examples

### Example usage
```python
import deepdoctection as dd
```

### Example usage
```text
```python
!pip install ultralytics
```

### Example usage
```python
!pip install ultralytics
```

### Example usage
```text
## Adding the model wrapper for YOLO


```python
from __future__ import annotations 

from typing import Mapping
from deepdoctection.utils.types import PixelValues, PathLikeOrStr
from deepdoctection.utils.settings import TypeOrStr
from deepdoctection.utils.file_utils import Requirement

from ultralytics import YOLO

def _yolo_to_detectresult(results, categories) -> list[dd.DetectionResult]:
    """
    Converts YOLO detection results into DetectionResult objects using inference speed as confidence.

    :param results: YOLO detection results
    :param categories: List of category names or LayoutType enums for YOLO classes.
    :return: A list of DetectionResult objects
    """

    all_results: list[dd.DetectionResult] = []

    categories_name = categories.get_categories(as_dict=True)

            
    # Use inference speed as the confidence score (e.g., using 'inference' time as a proxy)
    confidence = results.speed.get('inference', 0) / 100  # Normalize by 100 if you want a scale between 0-1
    
    # Loop through each detected box
    for i, box in enumerate(results.boxes):
        # Extract and normalize bounding box coordinates
        x1, y1, x2, y2 = box.xyxy.tolist()[0]
        
        # Assign class_id based on detection order or results.boxes.cls if available
        class_id = int(box.cls)+1  # Get class ID based on available keys
        class_name = categories_name.get(class_id, "Unknown") # Directly retrieve the class name from 
categories
        
        # Create a DetectionResult object with inferred confidence
        detection = dd.DetectionResult(
            box=[x1, y1, x2, y2],
            score=confidence,  # Set the normalized speed as confidence
            class_id=class_id,
            class_name=class_name
        )
        
        # Append the DetectionResult to the list
        all_results.append(detection)

    return all_results

def predict_yolo(np_img: PixelValues, 
                 model, 
                 conf_threshold: float, 
                 iou_threshold: float, 
                 categories: dd.ModelCategories) -> list[dd.DetectionResult]:
    """
    Run inference using the YOLO model.
    
    :param np_img: Input image as numpy array (BGR format)
    :param model: YOLO model instance
    :param conf_threshold: Confidence threshold for detections
    :param iou_threshold: Intersection-over-Union threshold for non-max suppression
    :param categories: List of category names or LayoutType enums for YOLO classes.
    :return: A list of detection results
    """
    # Run the model
    results = model(source=np_img, conf=conf_threshold, iou=iou_threshold)[0]
    
    # Convert results to DetectionResult format
    all_results = _yolo_to_detectresult(results, categories)
    
    return all_results
    
class YoloDetector(dd.ObjectDetector):
    """
    Document detector using YOLO engine for layout analysis.
    
    Model weights must be placed at `.cache/deepdoctection/weights/yolo/`.
    
    The detector predicts different categories of document elements such as text, tables, figures, headers, 
etc.
    """
    def __init__(self, 
                 conf_threshold: float, 
                 iou_threshold: float, 
                 model_weights: PathLikeOrStr, 
                 categories: Mapping[int, TypeOrStr]) -> None:
        """
        :param conf_threshold: Confidence threshold for YOLO detections.
        :param iou_threshold: IoU threshold for YOLO detections.
        :param model_weights: Path to the YOLO model weights file.
        :param categories: List of category names or LayoutType enums for YOLO classes.
        """
        self.name = "yolo_detector"
        self.model_id = self.get_model_id()
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold

        # Load YOLO model with specified weights
        self.model = YOLO(model_weights)

        if categories is None:
            raise ValueError("A dictionary of category mappings must be provided.")
        self.categories =dd.ModelCategories(init_categories=categories)
        
    def predict(self, np_img: PixelValues) -> list[dd.DetectionResult]:
        """
        Perform inference on a document image using YOLOv10 and return detection results.
        
        :param np_img: Input image as numpy array (BGR format)
        :return: A list of DetectionResult objects.
        """
        return predict_yolo(np_img, self.model, self.conf_threshold, self.iou_threshold, self.categories)

    @classmethod
    def get_requirements(cls) -> list[Requirement]:
        # You could write a function get_ultralytics_requirement() that reminds you to install ultralytics 
which is necessary to run this
        # predictor. 
        return []

    def clone(self) -> YoloDetector:
        """
        Clone the current detector instance.
        """
        return self.__class__(conf_threshold=self.conf_threshold, 
                              iou_threshold=self.iou_threshold, 
                              model_weights=self.model.model_path,
                              categories = self.categories)

    def get_category_names(self) -> tuple[ObjectTypes, ...]:
        """
        Get the category names used by YOLO for document detection.
        """
        return self.categories.get_categories(as_dict=False)
```

### Adding the model wrapper for YOLO
```python
from __future__ import annotations 

from typing import Mapping
from deepdoctection.utils.types import PixelValues, PathLikeOrStr
from deepdoctection.utils.settings import TypeOrStr
from deepdoctection.utils.file_utils import Requirement

from ultralytics import YOLO

def _yolo_to_detectresult(results, categories) -> list[dd.DetectionResult]:
    """
    Converts YOLO detection results into DetectionResult objects using inference speed as confidence.

    :param results: YOLO detection results
    :param categories: List of category names or LayoutType enums for YOLO classes.
    :return: A list of DetectionResult objects
    """

    all_results: list[dd.DetectionResult] = []

    categories_name = categories.get_categories(as_dict=True)

            
    # Use inference speed as the confidence score (e.g., using 'inference' time as a proxy)
    confidence = results.speed.get('inference', 0) / 100  # Normalize by 100 if you want a scale between 0-1
    
    # Loop through each detected box
    for i, box in enumerate(results.boxes):
        # Extract and normalize bounding box coordinates
        x1, y1, x2, y2 = box.xyxy.tolist()[0]
        
        # Assign class_id based on detection order or results.boxes.cls if available
        class_id = int(box.cls)+1  # Get class ID based on available keys
        class_name = categories_name.get(class_id, "Unknown") # Directly retrieve the class name from 
categories
        
        # Create a DetectionResult object with inferred confidence
        detection = dd.DetectionResult(
            box=[x1, y1, x2, y2],
            score=confidence,  # Set the normalized speed as confidence
            class_id=class_id,
            class_name=class_name
        )
        
        # Append the DetectionResult to the list
        all_results.append(detection)

    return all_results

def predict_yolo(np_img: PixelValues, 
                 model, 
                 conf_threshold: float, 
                 iou_threshold: float, 
                 categories: dd.ModelCategories) -> list[dd.DetectionResult]:
    """
    Run inference using the YOLO model.
    
    :param np_img: Input image as numpy array (BGR format)
    :param model: YOLO model instance
    :param conf_threshold: Confidence threshold for detections
    :param iou_threshold: Intersection-over-Union threshold for non-max suppression
    :param categories: List of category names or LayoutType enums for YOLO classes.
    :return: A list of detection results
    """
    # Run the model
    results = model(source=np_img, conf=conf_threshold, iou=iou_threshold)[0]
    
    # Convert results to DetectionResult format
    all_results = _yolo_to_detectresult(results, categories)
    
    return all_results
    
class YoloDetector(dd.ObjectDetector):
    """
    Document detector using YOLO engine for layout analysis.
    
    Model weights must be placed at `.cache/deepdoctection/weights/yolo/`.
    
    The detector predicts different categories of document elements such as text, tables, figures, headers, 
etc.
    """
    def __init__(self, 
                 conf_threshold: float, 
                 iou_threshold: float, 
                 model_weights: PathLikeOrStr, 
                 categories: Mapping[int, TypeOrStr]) -> None:
        """
        :param conf_threshold: Confidence threshold for YOLO detections.
        :param iou_threshold: IoU threshold for YOLO detections.
        :param model_weights: Path to the YOLO model weights file.
        :param categories: List of category names or LayoutType enums for YOLO classes.
        """
        self.name = "yolo_detector"
        self.model_id = self.get_model_id()
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold

        # Load YOLO model with specified weights
        self.model = YOLO(model_weights)

        if categories is None:
            raise ValueError("A dictionary of category mappings must be provided.")
        self.categories =dd.ModelCategories(init_categories=categories)
        
    def predict(self, np_img: PixelValues) -> list[dd.DetectionResult]:
        """
        Perform inference on a document image using YOLOv10 and return detection results.
        
        :param np_img: Input image as numpy array (BGR format)
        :return: A list of DetectionResult objects.
        """
        return predict_yolo(np_img, self.model, self.conf_threshold, self.iou_threshold, self.categories)

    @classmethod
    def get_requirements(cls) -> list[Requirement]:
        # You could write a function get_ultralytics_requirement() that reminds you to install ultralytics 
which is necessary to run this
        # predictor. 
        return []

    def clone(self) -> YoloDetector:
        """
        Clone the current detector instance.
        """
        return self.__class__(conf_threshold=self.conf_threshold, 
                              iou_threshold=self.iou_threshold, 
                              model_weights=self.model.model_path,
                              categories = self.categories)

    def get_category_names(self) -> tuple[ObjectTypes, ...]:
        """
        Get the category names used by YOLO for document detection.
        """
        return self.categories.get_categories(as_dict=False)
```

### Example usage
```text
## Adding the model to the `ModelCatalog`

Next, we need to register the model artifact. Registering the model will make it much easier to use the later 
with the Analyzer. We use the `yolov10x_best.pt` checkpoint from 
[here](https://huggingface.co/omoured/YOLOv10-Document-Layout-Analysis).

By the way, the source code for training this model can be found 
[here](https://github.com/moured/YOLOv10-Document-Layout-Analysis.git).

Save the model under `dd.get_weights_dir_path() / "yolo/yolov10x_best.pt"`. Alternatively, provide 
`hf_repo_id`, `hf_model_name`. This model does not require a config file.


```python
dd.ModelCatalog.register("yolo/yolov10x_best.pt", dd.ModelProfile(
    name="yolo/yolov10x_best.pt",
    description="YOLOv10 model for layout analysis",
    tp_model=False,
    size=[0],
    categories={
        1: dd.LayoutType.CAPTION,
        2: dd.LayoutType.FOOTNOTE,
        3: dd.LayoutType.FORMULA,
        4: dd.LayoutType.LIST_ITEM,
        5: dd.LayoutType.PAGE_FOOTER,
        6: dd.LayoutType.PAGE_HEADER,
        7: dd.LayoutType.FIGURE,
        8: dd.LayoutType.SECTION_HEADER,
        9: dd.LayoutType.TABLE,
        10: dd.LayoutType.TEXT,
        11: dd.LayoutType.TITLE,
    },
    model_wrapper="YoloDetector",
    hf_model_name="yolov10x_best.pt",
    dl_library="PT",
    hf_repo_id="omoured/YOLOv10-Document-Layout-Analysis",
    hf_config_file=[]
))
```

### Example usage
```python
dd.ModelCatalog.register("yolo/yolov10x_best.pt", dd.ModelProfile(
    name="yolo/yolov10x_best.pt",
    description="YOLOv10 model for layout analysis",
    tp_model=False,
    size=[0],
    categories={
        1: dd.LayoutType.CAPTION,
        2: dd.LayoutType.FOOTNOTE,
        3: dd.LayoutType.FORMULA,
        4: dd.LayoutType.LIST_ITEM,
        5: dd.LayoutType.PAGE_FOOTER,
        6: dd.LayoutType.PAGE_HEADER,
        7: dd.LayoutType.FIGURE,
        8: dd.LayoutType.SECTION_HEADER,
        9: dd.LayoutType.TABLE,
        10: dd.LayoutType.TEXT,
        11: dd.LayoutType.TITLE,
    },
    model_wrapper="YoloDetector",
    hf_model_name="yolov10x_best.pt",
    dl_library="PT",
    hf_repo_id="omoured/YOLOv10-Document-Layout-Analysis",
    hf_config_file=[]
))
```

### Example usage
```text
## Modifying the factory class to build the Analyzer

The Analyzer is built with help of a `ServiceFactory`. This class is responsible to build a pipeline with a 
given config from the basic blocks, e.g. `Predictor`s, `PipelineComponent`s and many other things. If you want
to avoid writing lots of code for a custom pipeline we suggest to only modify the static method of the 
`ServiceFactory`.

In our situation we want to add the `YoloDetector` once we select the newly registered model in the config 
parameter `PT.LAYOUT.WEIGHT`. Everything else must run in the same way. 

We therefore write a small function `build_layout_detector` with our custom cude and replace its static method
with the new function. (Yes, it looks hacky, but it is faster than writing a derived class...)



```python
def build_layout_detector(config: AttrDict, mode: str = ""):
    # We want to return the YoloDetector if the profile in config.PT.LAYOUT.WEIGHTS points to a ModelProfile 
with a registered Yolo model.
    weights = getattr(config.PT, mode).WEIGHTS
    profile = dd.ModelCatalog.get_profile(weights)
    if profile.model_wrapper == "YoloDetector":
        model_weights = dd.ModelDownloadManager.maybe_download_weights_and_configs(weights)
        return YoloDetector(conf_threshold=0.2,
                            iou_threshold=0.8,
                            model_weights=model_weights,
                            categories=profile.categories)

    else:
        # the code for building the many other layout/table/table segmentation predictors is hidden behind 
_build_layout_detector.
        return dd.ServiceFactory._build_layout_detector(config, mode)
    
dd.ServiceFactory.build_layout_detector=build_layout_detector
```

### Example usage
```python
def build_layout_detector(config: AttrDict, mode: str = ""):
    # We want to return the YoloDetector if the profile in config.PT.LAYOUT.WEIGHTS points to a ModelProfile 
with a registered Yolo model.
    weights = getattr(config.PT, mode).WEIGHTS
    profile = dd.ModelCatalog.get_profile(weights)
    if profile.model_wrapper == "YoloDetector":
        model_weights = dd.ModelDownloadManager.maybe_download_weights_and_configs(weights)
        return YoloDetector(conf_threshold=0.2,
                            iou_threshold=0.8,
                            model_weights=model_weights,
                            categories=profile.categories)

    else:
        # the code for building the many other layout/table/table segmentation predictors is hidden behind 
_build_layout_detector.
        return dd.ServiceFactory._build_layout_detector(config, mode)
    
dd.ServiceFactory.build_layout_detector=build_layout_detector
```

### # the code for building the many other layout/table/table segmentation predictors is hidden behind 
_build_layout_detector.
```text
```python
model_weights = dd.ModelDownloadManager.maybe_download_weights_and_configs("yolo/yolov10x_best.pt")
```

### Example usage
```python
model_weights = dd.ModelDownloadManager.maybe_download_weights_and_configs("yolo/yolov10x_best.pt")
```

### Example usage
```text
## Running the Analyzer with the YoloDetector

Next we want to build the Analyzer with the new layout model. We change `PT.LAYOUT.WEIGHTS` to 
`yolo/yolov10x_best.pt` and switch everything else off for demo purposes.

One additional but not very obvious configuration step is crucial though: In order to show all layout sections
the model is able to detect,
we need to list them in `TEXT_ORDERING.FLOATING_TEXT_BLOCK_CATEGORIES`. Otherwise, we will only display the 
default layout sections which are those defined by the `Publaynet` dataset: `text,title,list,table,figure`. 



```python
config_overwrite = ["PT.LAYOUT.WEIGHTS=yolo/yolov10x_best.pt",
                    "USE_TABLE_SEGMENTATION=False",
                    "USE_OCR=False",
                    "TEXT_ORDERING.FLOATING_TEXT_BLOCK_CATEGORIES=
                                        ['caption',
                                         'footnote', 
                                         'formula',
                                         'list_item',
                                         'page_footer',
                                         'page_header', 
                                         'figure',
                                         'section_header',
                                         'table',
                                         'text',
                                         'title']"]
analyzer = dd.get_dd_analyzer(config_overwrite=config_overwrite)
```

### Example usage
```python
config_overwrite = ["PT.LAYOUT.WEIGHTS=yolo/yolov10x_best.pt",
                    "USE_TABLE_SEGMENTATION=False",
                    "USE_OCR=False",
                    "TEXT_ORDERING.FLOATING_TEXT_BLOCK_CATEGORIES=
                                        ['caption',
                                         'footnote', 
                                         'formula',
                                         'list_item',
                                         'page_footer',
                                         'page_header', 
                                         'figure',
                                         'section_header',
                                         'table',
                                         'text',
                                         'title']"]
analyzer = dd.get_dd_analyzer(config_overwrite=config_overwrite)
```

### Example usage
```text
```python
path="/path/to/dir/document.pdf"

df = analyzer.analyze(path=path)
df.reset_state()

dp = next(iter(df))
```

### Example usage
```python
path="/path/to/dir/document.pdf"

df = analyzer.analyze(path=path)
df.reset_state()

dp = next(iter(df))
```

### Example usage
```text
```python
from matplotlib import pyplot as plt

img = dp.viz(interactive=False)
plt.figure(figsize = (25,17))
plt.axis('off')
plt.imshow(img)
```

### Example usage
```python
from matplotlib import pyplot as plt

img = dp.viz(interactive=False)
plt.figure(figsize = (25,17))
plt.axis('off')
plt.imshow(img)
```

### Example usage
```text
![png](./_imgs/analyzer_doclaynet_with_yolo_01.png)
```

---

# docs/tutorials/Analyzer_Get_Started.md - Parsing

<p align="center"> <img 
src="https://github.com/deepdoctection/deepdoctection/raw/master/docs/tutorials/_imgs/dd_logo.png" alt="Deep 
Doctection Logo" width="60%"> <h3 align="center"> </h3> </p>.

## Code Examples

### Example usage
```python
import deepdoctection as dd

analyzer = dd.get_dd_analyzer()
```

### Example usage
```text
If the analyzer uses deep learning models (which is generally the case), they are now loaded into memory.

!!! info 

    The analyzer is an example of a pipeline that can be built depending on the problem you want to tackle. 
This 
    particular pipeline is built from various building blocks. We will come back to this later. 


## Analyze method

Once all models have been loaded, we can process a directory with images (.png, .jpf), a single multi page 
PDF-document or outputs of another **deep**doctection pipeline.


=== "Image directory"

    ```python
    path ="path/to/image_dir"
    
    df = analyzer.analyze(path=path)
    df.reset_state() # (1)
```

### Example usage
```python
doc=iter(df)
page = next(doc)
```

### Example usage
```text
## Page

For each iteration, i.e. for each page document we receive a `Page` object.  Let's also have a look on some 
top 
level information. 


```python
print(f" height: {page.height}
         width: {page.width}
         file_name: {page.file_name}
         document_id: {page.document_id}
         image_id: {page.image_id}\n")
```

### Example usage
```python
print(f" height: {page.height}
         width: {page.width}
         file_name: {page.file_name}
         document_id: {page.document_id}
         image_id: {page.image_id}\n")
```

### Example usage
```text
??? info "Output"
```

### Example usage
```python
page.get_attribute_names()
```

### Example usage
```text
??? info "Output"
```

### Example usage
```python
page.viz(interactive=True,
         show_tables=True,
         show_layouts= True,
         show_figures=True,
         show_residual_layouts=True) # (1)
```

### Example usage
```text
1. If you set `interactive=True` a viewer will pop up. Use `+` and `-` to zoom out/in. Use `q` to close the 
page. If you
   set `interactive=False` the image will be returned as a numpy array. You can visualize it e.g. with 
matplotlib.

![title](./_imgs/analyzer_get_started_02.png)

We can get layout segments from the `layouts` attribute.

```python
for layout in page.layouts:
    print(f"Layout segment: {layout.category_name}, \n 
            score: {layout.score}, \n 
            reading_order: {layout.reading_order}, \n
            bounding_box: {layout.bounding_box}, \n 
            annotation_id: {layout.annotation_id} \n \n 
            text: {layout.text} \n")
```

### Example usage
```python
for layout in page.layouts:
    print(f"Layout segment: {layout.category_name}, \n 
            score: {layout.score}, \n 
            reading_order: {layout.reading_order}, \n
            bounding_box: {layout.bounding_box}, \n 
            annotation_id: {layout.annotation_id} \n \n 
            text: {layout.text} \n")
```

### Example usage
```text
??? info "Output"
```

### Example usage
```python
page.chunks[0]
```

### Example usage
```text
??? info "Output"
```

### Tables
```python
table = page.tables[0]
table.get_attribute_names()
```

### Example usage
```text
??? info "Output"
```

### Example usage
```python
print(f" number of rows: {table.number_of_rows} \n 
         number of columns: {table.number_of_columns} \n 
         reading order:{table.reading_order}, \n 
         score: {table.score}")
```

### Example usage
```text
??? info "Output"
```

### Example usage
```python
table.kv_header_rows(2)
```

### Example usage
```text
??? info "Key-Value: Header-Rows"
```

### Cells
```python
cell = table.cells[0]
cell.get_attribute_names()
```

### Example usage
```text
??? info "Cell attributes"

    {'bbox',
     'body',
     'column_header',
     'column_number',
     'column_span',
     'header',
     'layout_link',
     'np_image',
     'projected_row_header',
     'reading_order',
     'row_header',
     'row_number',
     'row_span',
     'spanning',
     'text',
     'words'}


```python
print(f"column number: {cell.column_number} \n 
      row_number: {cell.row_number}  \n 
      bounding_box: {cell.bounding_box}\n 
      text: {cell.text} \n 
      annotation_id: {cell.annotation_id}")
      annotation_id}")
```

### Example usage
```python
print(f"column number: {cell.column_number} \n 
      row_number: {cell.row_number}  \n 
      bounding_box: {cell.bounding_box}\n 
      text: {cell.text} \n 
      annotation_id: {cell.annotation_id}")
      annotation_id}")
```

### Example usage
```text
??? info "Output"
```

### Example usage
```python
word = page.words[0] 
word.get_attribute_names()
```

### Example usage
```text
??? info "Output"

    {'bbox',
     'block',
     'character_type',
     'characters',
     'handwritten',
     'layout_link',
     'np_image',
     'printed',
     'reading_order',
     'tag',
     'text_line',
     'token_class',
     'token_tag'}

```python

print(f"score: {word.score} \n 
        characters: {word.characters} \n 
        reading_order: {word.reading_order} \n 
        bounding_box: {word.bounding_box}")
```

### Example usage
```python
print(f"score: {word.score} \n 
        characters: {word.characters} \n 
        reading_order: {word.reading_order} \n 
        bounding_box: {word.bounding_box}")
```

### Example usage
```text
??? info "Output"
```

### Text
```python
print(page.text)
```

### Example usage
```text
Text from tables is separated from the narrative text. This allows filtering tables from other content.



## Saving and reading


```python
page.save(image_to_json=True, # (1)
          highest_hierarchy_only=True, # (2)
          path="path/to/dir/sample_2.json") # (3)
```

### Saving and reading
```python
page.save(image_to_json=True, # (1)
          highest_hierarchy_only=True, # (2)
          path="path/to/dir/sample_2.json") # (3)
```

### Example usage
```text
1. The image will be saved as a base64 encoded string in the JSON file.
2. Reduce superfluous information that can be reconstructed later.
3. Either specify the file name or the directory only. The later will save the JSON with its `image_id`.


## Re-loading JSON

```python
page = dd.Page.from_file(file_path="path/to/dir/sample.json")
```

### Re-loading JSON
```python
page = dd.Page.from_file(file_path="path/to/dir/sample.json")
```

### Re-loading JSON
```text
<div class="grid cards" markdown>
- :material-arrow-right-bold:[More about parsing](Analyzer_More_On_Parsing.md)
- :material-arrow-right-bold:[Analyzer Configuration](Analyzer_Configuration.md)  
</div>
```

---

# docs/tutorials/Analyzer_Model_Registry_And_New_Models.md - Adding new models and running with 
**deep**doctection

<p align="center"> <img 
src="https://github.com/deepdoctection/deepdoctection/raw/master/docs/tutorials/_imgs/dd_logo.png" alt="Deep 
Doctection Logo" width="60%"> <h3 align="center"> </h3> </p>.

## Code Examples

### Example usage
```python
import os

import deepdoctection as dd
from matplotlib import pyplot as plt

dd.ModelCatalog.get_profile_list()
```

### Example usage
```text
??? info "Output"

    <pre>
    ['layout/model-800000_inf_only.data-00000-of-00001',
     'cell/model-1800000_inf_only.data-00000-of-00001',
     'item/model-1620000_inf_only.data-00000-of-00001',
     'layout/d2_model_0829999_layout_inf_only.pt',
     'layout/d2_model_0829999_layout_inf_only.ts',
     'cell/d2_model_1849999_cell_inf_only.pt',
     'cell/d2_model_1849999_cell_inf_only.ts',
     'item/d2_model_1639999_item_inf_only.pt',
     'item/d2_model_1639999_item_inf_only.ts',
     'nielsr/lilt-xlm-roberta-base/pytorch_model.bin',
     'SCUT-DLVCLab/lilt-infoxlm-base/pytorch_model.bin',
     'SCUT-DLVCLab/lilt-roberta-en-base/pytorch_model.bin',
     'microsoft/layoutlm-base-uncased/pytorch_model.bin',
     'microsoft/layoutlm-large-uncased/pytorch_model.bin',
     'microsoft/layoutlmv2-base-uncased/pytorch_model.bin',
     'microsoft/layoutxlm-base/pytorch_model.bin',
     'microsoft/layoutlmv3-base/pytorch_model.bin',
     'microsoft/table-transformer-detection/pytorch_model.bin',
     'microsoft/table-transformer-structure-recognition/pytorch_model.bin',
     'doctr/db_resnet50/pt/db_resnet50-ac60cadc.pt',
     'doctr/db_resnet50/tf/db_resnet50-adcafc63.zip',
     'doctr/crnn_vgg16_bn/pt/crnn_vgg16_bn-9762b0b0.pt',
     'doctr/crnn_vgg16_bn/tf/crnn_vgg16_bn-76b7f2c6.zip',
     'FacebookAI/xlm-roberta-base/pytorch_model.bin',
     'fasttext/lid.176.bin',
     'deepdoctection/tatr_tab_struct_v2/pytorch_model.bin',
     'layout/d2_model_0829999_layout.pth',
     'cell/d2_model_1849999_cell.pth',
     'item/d2_model_1639999_item.pth',
     'Felix92/doctr-torch-parseq-multilingual-v1/pytorch_model.bin',
     'doctr/crnn_vgg16_bn/pt/master-fde31e4a.pt',
     'Aryn/deformable-detr-DocLayNet/model.safetensors']
         </pre>



```python
import pathlib

dd.ModelCatalog.get_full_path_weights('layout/d2_model_0829999_layout_inf_only.pt').replace(str(pathlib.Path.h
ome()),"~")
```

### Example usage
```python
import pathlib

dd.ModelCatalog.get_full_path_weights('layout/d2_model_0829999_layout_inf_only.pt').replace(str(pathlib.Path.h
ome()),"~")
```

### Example usage
```text
??? info "Output"

    '~/.cache/deepdoctection/weights/layout/d2_model_0829999_layout_inf_only.pt'


```python
dd.ModelCatalog.get_full_path_configs('layout/d2_model_0829999_layout_inf_only.pt').replace(str(pathlib.Path.h
ome()),"~")
```

### Example usage
```python
dd.ModelCatalog.get_full_path_configs('layout/d2_model_0829999_layout_inf_only.pt').replace(str(pathlib.Path.h
ome()),"~")
```

### Example usage
```text
??? info "Output"

    '~/.cache/deepdoctection/configs/dd/d2/layout/CASCADE_RCNN_R_50_FPN_GN.yaml'




```python
from dataclasses import asdict

asdict(dd.ModelCatalog.get_profile('layout/d2_model_0829999_layout_inf_only.pt'))
```

### Example usage
```python
from dataclasses import asdict

asdict(dd.ModelCatalog.get_profile('layout/d2_model_0829999_layout_inf_only.pt'))
```

### Example usage
```text
??? info "Output"

    <pre>
    {'name': 'layout/d2_model_0829999_layout_inf_only.pt',
     'description': 'Detectron2 layout detection model trained on Publaynet',
     'size': [274632215],
     'tp_model': False,
     'config': 'dd/d2/layout/CASCADE_RCNN_R_50_FPN_GN.yaml',
     'preprocessor_config': None,
     'hf_repo_id': 'deepdoctection/d2_casc_rcnn_X_32xd4_50_FPN_GN_2FC_publaynet_inference_only',
     'hf_model_name': 'd2_model_0829999_layout_inf_only.pt',
     'hf_config_file': ['Base-RCNN-FPN.yaml', 'CASCADE_RCNN_R_50_FPN_GN.yaml'],
     'urls': None,
     'categories': {1: <LayoutType.TEXT>,
      2: <LayoutType.TITLE>,
      3: <LayoutType.LIST>,
      4: <LayoutType.TABLE>,
      5: <LayoutType.FIGURE>},
     'categories_orig': None,
     'dl_library': 'PT',
     'model_wrapper': 'D2FrcnnDetector',
     'architecture': None,
     'padding': None}
    </pre>



## Registering a new model

We now demonstrate how to register a pre-trained model and subsequently use it within the **deep**doctection 
pipeline.

For this purpose, we use a pre-trained model from the [**Layout-Parser**](https://layout-parser.github.io) 
repository.
This model is supported by Detectron2. The model weights can be found 
[**here**](https://www.dropbox.com/s/6ewh6g8rqt2ev3a/model_final.pth?dl=1), 
and the model configuration [**here**](https://www.dropbox.com/s/6ewh6g8rqt2ev3a/model_final.pth?dl=1). The 
model has been pre-trained on a historical newspaper dataset and
detects the following layout segments: PHOTOGRAPH, ILLUSTRATION, MAP, COMIC, EDITORIAL_CARTOON, HEADLINE, and
ADVERTISEMENT. These categories do not yet exist in the **deep**doctection ecosystem and must be registered 
beforehand.


### Registering the new layout categories

```python
@dd.object_types_registry.register("NewspaperType")
class NewspaperExtension(dd.ObjectTypes):
    """Additional Newspaper labels not registered yet"""

    PHOTOGRAPH ="Photograph",
    ILLUSTRATION = "Illustration",
    MAP = "Map",
    COMIC = "Comics/Cartoon",
    EDITORIAL_CARTOON = "Editorial Cartoon",
    HEADLINE = "Headline",
    ADVERTISEMENT =  "Advertisement"
```

### Registering the new layout categories
```python
@dd.object_types_registry.register("NewspaperType")
class NewspaperExtension(dd.ObjectTypes):
    """Additional Newspaper labels not registered yet"""

    PHOTOGRAPH ="Photograph",
    ILLUSTRATION = "Illustration",
    MAP = "Map",
    COMIC = "Comics/Cartoon",
    EDITORIAL_CARTOON = "Editorial Cartoon",
    HEADLINE = "Headline",
    ADVERTISEMENT =  "Advertisement"
```

### Example usage
```text
We also need to specify how these layout sections should behave. Ultimately, they should be treated in the 
same way 
as residual layout sections.

```python
from deepdoctection.datapoint import IMAGE_DEFAULTS

IMAGE_DEFAULTS.IMAGE_ANNOTATION_TO_LAYOUTS.update({i: dd.Layout for i in NewspaperExtension})
IMAGE_DEFAULTS.RESIDUAL_TEXT_BLOCK_CATEGORIES= IMAGE_DEFAULTS.RESIDUAL_TEXT_BLOCK_CATEGORIES + tuple(cat for 
cat in NewspaperExtension)
```

### Example usage
```python
from deepdoctection.datapoint import IMAGE_DEFAULTS

IMAGE_DEFAULTS.IMAGE_ANNOTATION_TO_LAYOUTS.update({i: dd.Layout for i in NewspaperExtension})
IMAGE_DEFAULTS.RESIDUAL_TEXT_BLOCK_CATEGORIES= IMAGE_DEFAULTS.RESIDUAL_TEXT_BLOCK_CATEGORIES + tuple(cat for 
cat in NewspaperExtension)
```

### Example usage
```text
Adding the model `layoutparser/newspaper/model_final.pth` requires to save weights to 
`~/.cache/deepdoctection/layoutparser/newspaper/model_final.pth` and the config to 
`~/.cache/deepdoctection/layoutparser/newspaper/config.yml`.


```python
dd.ModelCatalog.save_profiles_to_file("/path/to/target/profiles.jsonl")

dd.ModelCatalog.register("layoutparser/newspaper/model_final.pth", dd.ModelProfile(
    name="layoutparser/newspaper/model_final.pth",
    description="layout detection ",
    config="layoutparser/newspaper/config.yml",
    size=[],
    tp_model=False,
    categories={1: NewspaperExtension.PHOTOGRAPH,
                2: NewspaperExtension.ILLUSTRATION,
                3: NewspaperExtension.MAP,
                4: NewspaperExtension.COMIC,
                5: NewspaperExtension.EDITORIAL_CARTOON,
                6: NewspaperExtension.HEADLINE,
                7: NewspaperExtension.ADVERTISEMENT},
    model_wrapper="D2FrcnnDetector",
))
```

### Example usage
```python
dd.ModelCatalog.save_profiles_to_file("/path/to/target/profiles.jsonl")

dd.ModelCatalog.register("layoutparser/newspaper/model_final.pth", dd.ModelProfile(
    name="layoutparser/newspaper/model_final.pth",
    description="layout detection ",
    config="layoutparser/newspaper/config.yml",
    size=[],
    tp_model=False,
    categories={1: NewspaperExtension.PHOTOGRAPH,
                2: NewspaperExtension.ILLUSTRATION,
                3: NewspaperExtension.MAP,
                4: NewspaperExtension.COMIC,
                5: NewspaperExtension.EDITORIAL_CARTOON,
                6: NewspaperExtension.HEADLINE,
                7: NewspaperExtension.ADVERTISEMENT},
    model_wrapper="D2FrcnnDetector",
))
```

### Example usage
```text
Once the model is registered we can use this model in the `analyzer`:


```python
analyzer = dd.get_dd_analyzer(config_overwrite=["PT.LAYOUT.WEIGHTS=layoutparser/newspaper/model_final.pth",
                                                "USE_OCR=False",
                                                "USE_TABLE_SEGMENTATION=False",])

df = analyzer.analyze(path="/path/to/dir/newspaper_layout")
df.reset_state()

df_iter = iter(df)
dp = next(df_iter)

image = dp.viz(show_residual_layouts=True)

plt.figure(figsize = (25,17))
plt.axis('off')
plt.imshow(image)
```

### Once the model is registered we can use this model in the `analyzer`
```python
analyzer = dd.get_dd_analyzer(config_overwrite=["PT.LAYOUT.WEIGHTS=layoutparser/newspaper/model_final.pth",
                                                "USE_OCR=False",
                                                "USE_TABLE_SEGMENTATION=False",])

df = analyzer.analyze(path="/path/to/dir/newspaper_layout")
df.reset_state()

df_iter = iter(df)
dp = next(df_iter)

image = dp.viz(show_residual_layouts=True)

plt.figure(figsize = (25,17))
plt.axis('off')
plt.imshow(image)
```

### Example usage
```text
![layoutparser_3.png](./_imgs/analyzer_model_registry_and_new_models_01.png)


```python
dp.residual_layouts
```

### Example usage
```python
dp.residual_layouts
```

### Example usage
```text
??? info "Output"

    [Layout(active=True, _annotation_id='df22c03b-896c-323c-b5ae-2e4b1fd1faf3', service_id='9dcc2fbd', 
model_id='cfa02246', session_id=None, category_name=<NewspaperExtension.PHOTOGRAPH>, 
_category_name=<NewspaperExtension.PHOTOGRAPH>, category_id=1, score=0.9747101664543152, sub_categories={}, 
relationships={}, bounding_box=BoundingBox(absolute_coords=True, ulx=453, uly=806, lrx=786, lry=1291, 
width=333, height=485)),
     Layout(active=True, _annotation_id='77d4e101-e45a-35fe-ab2c-53465c9c2a14', service_id='9dcc2fbd', 
model_id='cfa02246', session_id=None, category_name=<NewspaperExtension.HEADLINE>, 
_category_name=<NewspaperExtension.HEADLINE>, category_id=6, score=0.8193893432617188, sub_categories={}, 
relationships={}, bounding_box=BoundingBox(absolute_coords=True, ulx=33, uly=286, lrx=868, lry=456, width=835,
height=170)),
     Layout(active=True, _annotation_id='ab329403-f1c3-3d41-8166-e476867c1eeb', service_id='9dcc2fbd', 
model_id='cfa02246', session_id=None, category_name=<NewspaperExtension.PHOTOGRAPH>, 
_category_name=<NewspaperExtension.PHOTOGRAPH>, category_id=1, score=0.793633222579956, sub_categories={}, 
relationships={}, bounding_box=BoundingBox(absolute_coords=True, ulx=24, uly=789, lrx=443, lry=1275, 
width=419, height=486)),
     Layout(active=True, _annotation_id='c0d708e1-4632-39f4-ad46-9f469a41fc48', service_id='9dcc2fbd', 
model_id='cfa02246', session_id=None, category_name=<NewspaperExtension.ILLUSTRATION>, 
_category_name=<NewspaperExtension.ILLUSTRATION>, category_id=2, score=0.7907929420471191, sub_categories={}, 
relationships={}, bounding_box=BoundingBox(absolute_coords=True, ulx=43, uly=450, lrx=456, lry=815, width=413,
height=365))]
```

---

# docs/tutorials/Analyzer_More_On_Parsing.md - More on Parsing

<p align="center"> <img 
src="https://github.com/deepdoctection/deepdoctection/raw/master/docs/tutorials/_imgs/dd_logo.png" alt="Deep 
Doctection Logo" width="60%"> <h3 align="center"> </h3> </p>.

## Code Examples

### First config changes
```python
import deepdoctection as dd
from matplotlib import pyplot as plt

analyzer = dd.get_dd_analyzer(config_overwrite=['USE_LAYOUT_LINK=True']) # (1)

df = analyzer.analyze(path="/path/to/dir/2312.13560.pdf")
df.reset_state()
doc=iter(df)
page = next(doc)

plt.figure(figsize = (25,17))
plt.axis('off')
plt.imshow(page.viz())
```

### Example usage
```text
1. We set the `USE_LAYOUT_LINK` parameter to `True`. This enables the analyzer to link captions to figures and
tables.

    
![png](./_imgs/analyzer_more_on_parsing_01.png)


!!! info "Note"
        
    You may notice that some `line`s are labeled with the category line. This layout section is artificial and
generated
    by the `analyzer`. Every word recognized by the OCR must be assigned to a layout section. If this is not 
possible
    for certain `word`s, they are grouped together and merged into a `line`.


The watermark on the left is noticeable — it is not displayed. These are `residual_layouts` like `page_header`
and 
`page_footer`. These special layout sections can be displayed if needed.


```python
plt.figure(figsize = (25,17))
plt.axis('off')
plt.imshow(page.viz(page_header="category_name", 
                    page_footer="category_name")) # (1)
```

### Example usage
```python
plt.figure(figsize = (25,17))
plt.axis('off')
plt.imshow(page.viz(page_header="category_name", 
                    page_footer="category_name")) # (1)
```

### Example usage
```text
1. Pass the layout section`s category_name as argument. It`s value is the value we want to display, in this 
case it`s 
   `category_name`. You can also display other attributes, e.g. `annotation_id`.

![png](./_imgs/analyzer_more_on_parsing_02.png)
    

!!! info "Note"
    The **deep**doctection reading order algorithm is rule-based but can handle various layout types, such as 
    multi-column layouts. However, there are also page layouts where determining the correct reading order 
fails.


```python
print(page.text)
```

### Example usage
```python
print(page.text)
```

### Example usage
```text
??? info "Output"

    KNN-CTC: ENHANCING ASR VIA RETRIEVAL OF CTC PSEUDO LABELS
    Jiaming Zhou', Shiwan Zhao*, Yaqi Liu, Wenjia Zengs, Yong Chen, Yong Qin't
    Nankai University, Tianjin, China 2 Beijing University of Technology, Beijing, China 3 Lingxi (Beijing) 
Technology 
    Co., Ltd.
    ABSTRACT
    The success of retrieval-augmented language models in var- ious natural language processing (NLP) tasks 
has been 
    con- strained in automatic speech recognition (ASR) applications due to challenges in constructing 
fine-grained 
    audio-text datastores. This paper presents KNN-CTC, a novel approach that overcomes these challenges by 
leveraging 
    Connection- ist Temporal Classification (CTC) pseudo labels to establish frame-level audio-text key-value 
pairs, 
    circumventing the need for precise ground truth alignments. We further in- troduce a "skip-blank" 
strategy, which 
    strategically ignores CTC blank frames, to reduce datastore size. By incorpo- rating a k-nearest neighbors
retrieval 
    mechanism into pre- trained CTC ASR systems and leveraging a fine-grained, pruned datastore, KNN-CTC 
consistently 
    achieves substan- tial improvements in performance under various experimental settings. Our code is 
available at 
    htps/gihuhcomNKU: HLT/KNN-CTC.
    Index Terms- speech recognition, CTC, retrieval- augmented method, datastore construction
    1. INTRODUCTION
    In recent years, retrieval-augmented language models [1,2,3, 4, 5], which refine a pre-trained language 
model by 
    linearly interpolating the output word distribution with a k-nearest neighbors (KNN) model, have achieved 
remarkable 
    success across a broad spectrum of NLP tasks, encompassing lan- guage modeling, question answering, and 
machine 
    transla- tion. Central to the success of KNN language models is the construction of a high-quality 
key-value datastore.
    Despite these advancements in NLP tasks, applications in speech tasks, particularly in automatic speech 
recognition 
    (ASR), remain constrained due to the challenges associ- ated with constructing a fine-grained datastore 
for the 
    audio modality. Early exemplar-based ASR [6, 7] utilized KNN to improve the conventional GMM-HMM or 
DNN-HMM based 
    approaches. Recently, Yusuf et al. [8] proposed enhancing
    Independent researcher.
    TCorresponding author. This work was supported in part by NSF China (Grant No. 62271270).
    a transducer-based ASR model by incorporating a retrieval mechanism that searches an external text corpus 
for poten- 
    tial completions of partial ASR hypotheses. However, this method still falls under the KNN language model 
category, 
    which only enhances the text modality of RNN-T [9]. Chan etal. [10] employed Text To Speech (TTS) to 
generate audio 
    and used the audio embeddings and semantic text embed- dings as key-value pairs to construct a datastore, 
and then 
    augmented the Conformer [11] with KNN fusion layers to en- hance contextual ASR. However, this approach is
    restricted to contextual ASR, and the key-value pairs are coarse-grained, with both key and value at the 
phrase 
    level. Consequently, the challenge of constructing a fine-grained key-value datastore remains a 
substantial obstacle 
    in the ASR domain.
    In addition to ASR, there have been a few works in other speech-related tasks. For instance, RAMP [12] 
incorporated 
    KNN into mean opinion score (MOS) prediction by merg- ing the parametric model and the KNN-based 
non-parametric model. 
    Similarly, Wang et al. [13] proposed a speech emotion recognition (SER) framework that utilizes 
contrastive learn- 
    ing to separate different classes and employs KNN during in- ference to harness improved distances. 
However, both ap- 
    proaches still rely on the utterance-level audio embeddings as the key, with ground truth labels as the 
value.
    The construction of a fine-grained datastore for the audio modality in ASR tasks is challenged by two 
significant 
    obsta- cles: (i) the absence of precise alignment knowledge between audio and transcript characters, which
poses a 
    substantial dif- ficulty in acquiring the ground-truth labels (i.e., the values) necessary for the 
creation of 
    key-value pairs, and (i) the im- mense volume of entries generated when processing audio at the frame 
level. In this 
    study, we present KNN-CTC, a novel approach that overcomes these challenges by utilizing CTC 
(Connectionist 
    Temporal Classification) [14] pseudo labels. This innovative method results in significant improvements in
ASR task 
    performance. By utilizing CTC pseudo labels, W6 are able to establish frame-level key-value pairs, 
eliminating the 
    need for precise ground-truth alignments. Additionally we introduce a 'skip-blank' strategy that exploits 
the inher 
    ent characteristics of CTC to strategically omit blank frames thereby reducing the size of the datastore. 
KNN-CTC 
    attains comparable performance on the pruned datastore, and ever



```python
figure = page.figures[0]
plt.figure(figsize = (25,17))
plt.axis('off')
plt.imshow(figure.image.viz()) # (1)
```

### Example usage
```python
figure = page.figures[0]
plt.figure(figsize = (25,17))
plt.axis('off')
plt.imshow(figure.image.viz()) # (1)
```

### Example usage
```text
1. `figure.image.viz()` returns a NumPy array containing the image segment enclosed by the bounding box.
 

![png](./_imgs/analyzer_more_on_parsing_04.png)
    
We can save the figure as a single `.png`. 

```python
dd.viz_handler.write_image(f"/path/to/dir/{figure.annotation_id}.png", figure.image.image)
```

### Example usage
```python
dd.viz_handler.write_image(f"/path/to/dir/{figure.annotation_id}.png", figure.image.image)
```

### Example usage
```text
## Layout Linking

By setting `USE_LAYOUT_LINK=True`, we enabled a component that links `caption`s to `table`s or `figure`s. The 
linking 
is rule-based: if a `table` or `figure` is present, a `caption` is associated with the nearest one in terms of
spatial 
proximity.


```python
caption = figure.layout_link[0]
print(f"annotation_id: {caption.annotation_id}, text: {caption.text}")
```

### Example usage
```python
caption = figure.layout_link[0]
print(f"annotation_id: {caption.annotation_id}, text: {caption.text}")
```

### Example usage
```text
??? info "Output"

    text: Fig. 1. Overview of our KNN-CTC framework, which com- bines CTC and KNN models. The KNN model 
consists of two
    stages: datastore construction (blue dashed lines) and candi- date retrieval (orange lines)., 
annotation_id: 
    46bd4e42-8d50-30fb-883a-6c4d82b236af


We conclude  with some special features. Suppose you have a specific layout segment. Using get_layout_context,
we can 
retrieve the surrounding layout segments within a given context_size, i.e., the `k` layout segments that 
appear before
and after it in the reading order.


```python
for layout in page.get_layout_context(annotation_id="13a5f0ea-19e5-3317-b50c-e4c829a73d09", context_size=1):
    print(f"annotation_id: {layout.annotation_id}, text: {layout.text}")
```

### Example usage
```python
for layout in page.get_layout_context(annotation_id="13a5f0ea-19e5-3317-b50c-e4c829a73d09", context_size=1):
    print(f"annotation_id: {layout.annotation_id}, text: {layout.text}")
```

### for layout in page.get_layout_context(annotation_id="13a5f0ea-19e5-3317-b50c-e4c829a73d09", 
context_size=1)
```text
??? info "Output"

    annotation_id: 40d63bea-9815-3e97-906f-76b501c67667, text: (2)
    annotation_id: 13a5f0ea-19e5-3317-b50c-e4c829a73d09, text: Candidate retrieval: During the decoding phase,
our 
    process commences by generating the intermediate represen-
    annotation_id: 13cb9477-f605-324a-b497-9f42335c747d, text: tation f(Xi) alongside the CTC output 
PCTC(YIx). Pro- 
    ceeding further, we leverage the intermediate representations f(Xi) as queries, facilitating the retrieval
of the 
    k-nearest neighbors N. We then compute a softmax probability distri- bution over the neighbors, 
aggregating the 
    probability mass for each vocabulary item by:

## Analyzer metadata 

What does the analyzer predict? 

We can use the meta annotations to find out which attributes are determined for which object types. The 
attribute 
`image_annotations` represent all layout segments constructed by the analyzer. Ultimately, `ImageAnnotation`s 
are 
everything that can be enclosed by a bounding box. 


```python
meta_annotations = analyzer.get_meta_annotation()
meta_annotations.image_annotations
```

### Example usage
```python
meta_annotations = analyzer.get_meta_annotation()
meta_annotations.image_annotations
```

### Example usage
```text
??? info "Output"
    
    <pre>
     (DefaultType.DEFAULT_TYPE,
     LayoutType.CAPTION,
     LayoutType.TEXT,
     LayoutType.TITLE,
     LayoutType.FOOTNOTE,
     LayoutType.FORMULA,
     LayoutType.LIST_ITEM,
     LayoutType.PAGE_FOOTER,
     LayoutType.PAGE_HEADER,
     LayoutType.FIGURE,
     LayoutType.SECTION_HEADER,
     LayoutType.TABLE,
     LayoutType.COLUMN,
     LayoutType.ROW,
     CellType.COLUMN_HEADER,
     CellType.PROJECTED_ROW_HEADER,
     CellType.SPANNING,
     LayoutType.WORD,
     LayoutType.LINE)
     </pre>


The `sub_categories` represent attributes associated with specific `ImageAnnotations`. For a table cell, for 
example,
these include: `<CellType.COLUMN_NUMBER>, <CellType.COLUMN_SPAN>, <CellType.ROW_NUMBER> and 
<CellType.ROW_SPAN>`. 


```python
meta_annotations.sub_categories
```

### The `sub_categories` represent attributes associated with specific `ImageAnnotations`. For a table cell, 
for example,
```python
meta_annotations.sub_categories
```

### Example usage
```text
??? info "Output"

    <pre>
    {LayoutType.CELL: {CellType.COLUMN_NUMBER,
                      CellType.COLUMN_SPAN,
                      CellType.ROW_NUMBER,
                      CellType.ROW_SPAN}, 
    CellType.SPANNING: {CellType.COLUMN_NUMBER,
                      CellType.COLUMN_SPAN,
                      CellType.ROW_NUMBER,
                      CellType.ROW_SPAN},
    CellType.ROW_HEADER: {CellType.COLUMN_NUMBER,
                      CellType.COLUMN_SPAN,
                      CellType.ROW_NUMBER,
                      CellType.ROW_SPAN},
    CellType.COLUMN_HEADER: {CellType.COLUMN_NUMBER,
                      CellType.COLUMN_SPAN,
                      CellType.ROW_NUMBER,
                      CellType.ROW_SPAN},
    CellType.PROJECTED_ROW_HEADER: {CellType.COLUMN_NUMBER,
                      CellType.COLUMN_SPAN,
                      CellType.ROW_NUMBER,
                      CellType.ROW_SPAN},
    LayoutType.ROW: {CellType.ROW_NUMBER},
    LayoutType.COLUMN: {CellType.COLUMN_NUMBER},
    LayoutType.WORD: {WordType.CHARACTERS, Relationships.READING_ORDER},
    LayoutType.TEXT: {Relationships.READING_ORDER},
    LayoutType.TITLE: {Relationships.READING_ORDER},
    LayoutType.LIST: {Relationships.READING_ORDER},
    LayoutType.KEY_VALUE_AREA: {Relationships.READING_ORDER},
    LayoutType.LINE: {Relationships.READING_ORDER}}
    </pre>


The relationships represent one or more relations between different `ImageAnnotation`s. 


```python
meta_annotations.relationships
```

### Example usage
```python
meta_annotations.relationships
```

### Example usage
```text
??? info "Output"

    <pre>
    {LayoutType.TABLE: {Relationships.CHILD, 
                        Relationships.LAYOUT_LINK},
    LayoutType.TABLE_ROTATED: {Relationships.CHILD},
    LayoutType.TEXT: {Relationships.CHILD},
    LayoutType.TITLE: {Relationships.CHILD},
    LayoutType.LIST_ITEM: {Relationships.CHILD},
    LayoutType.LIST: {Relationships.CHILD},
    LayoutType.CAPTION: {Relationships.CHILD},
    LayoutType.PAGE_HEADER: {Relationships.CHILD},
    LayoutType.PAGE_FOOTER: {Relationships.CHILD},
    LayoutType.PAGE_NUMBER: {Relationships.CHILD},
    LayoutType.MARK: {Relationships.CHILD},
    LayoutType.KEY_VALUE_AREA: {Relationships.CHILD},
    LayoutType.FIGURE: {Relationships.CHILD, 
                        Relationships.LAYOUT_LINK},
    CellType.SPANNING: {Relationships.CHILD},
    LayoutType.CELL: {Relationships.CHILD}}
    </pre>


The summaries describe facts presented at the page level — for instance, a `document_type`. This pipeline does
not have
a document type classifier.


```python
meta_annotations.summaries
```

### Example usage
```python
meta_annotations.summaries
```

### Example usage
```text
??? info "Output"

    ()


By the way, don’t be confused by the obscure way the different categories are displayed. The categories are 
specific 
enum members. Each enum member can be converted into a string type, and vice versa — a string type can be 
converted 
back into an enum member:


```python
dd.LayoutType.CELL, dd.LayoutType.CELL.value, dd.get_type('cell')
```

### back into an enum member
```python
dd.LayoutType.CELL, dd.LayoutType.CELL.value, dd.get_type('cell')
```

### Example usage
```text
??? info "Output"

    (LayoutType.CELL, 'cell', LayoutType.CELL)
```

---

# docs/tutorials/Architecture.md - Architecture

<p align="center"> <img 
src="https://github.com/deepdoctection/deepdoctection/raw/master/docs/tutorials/_imgs/dd_logo.png" alt="Deep 
Doctection Logo" width="60%"> <h3 align="center"> </h3> </p>.

## Code Examples

### Example usage
```python
import deepdoctection as dd 

df = dd.SerializerJsonlines.load("path/to/dir",max_datapoints=100)
df.reset_state()
for dp in df:
        page = dd.Page.from_dict(dp)
```

### for dp in df
```text
or 

```python 
df = dd.SerializerCoco("path/to/dir")
df.reset_state()
for dp in df:
        # dp is a dict with {'image':{'id',...},
                                                 'annotations':[{'id':…,'bbox':...}]}
```

### Example usage
```python
df = dd.SerializerCoco("path/to/dir")
df.reset_state()
for dp in df:
        # dp is a dict with {'image':{'id',...},
                                                 'annotations':[{'id':…,'bbox':...}]}
```

### for dp in df
```text
We can load a pdf and stream the document page by page:

```python
df = dd.SerializerPdfDoc.load("path/to/dir/pdf_file.pdf",)
df.reset_state()

for dp in df:
   # dp is a dict with keys: path, file_name, pdf_bytes, page_number and a document_id
```

### We can load a pdf and stream the document page by page
```python
df = dd.SerializerPdfDoc.load("path/to/dir/pdf_file.pdf",)
df.reset_state()

for dp in df:
   # dp is a dict with keys: path, file_name, pdf_bytes, page_number and a document_id
```

### for dp in df
```text
## Datapoint


The [datapoint][deepdoctection.datapoint] package adds the internal data structure to the library. We can 
interpret a 
datapoint as a document page. When processing images or document everything that can will be captured in a 
page will be
saved in the [`Image`][deepdoctection.datapoint.image] object.


```python
image = dd.Image(file_name="image_1.png", location = "path/to/dir")
```

### Example usage
```python
image = dd.Image(file_name="image_1.png", location = "path/to/dir")
```

### Example usage
```text
Layout sections and all other visual lower level objects are instances of the [`ImageAnnotation`]
[deepdoctection.datapoint.annotation.ImageAnnotation] class. They have, attributes like `category_name`, 
`category_id`, 
`score` and a `bounding_box`.

```python

bounding_box = dd.BoundingBox(absolute_coords=True,ulx=100,uly=120,lrx=200,lry=250)
table = dd.ImageAnnotation(bounding_box = bounding_box,
                                                category_name = LayoutType.TABLE,
                                                category_id=1)  # (1)
image.dump(table)    # (2)
```

### Example usage
```python
bounding_box = dd.BoundingBox(absolute_coords=True,ulx=100,uly=120,lrx=200,lry=250)
table = dd.ImageAnnotation(bounding_box = bounding_box,
                                                category_name = LayoutType.TABLE,
                                                category_id=1)  # (1)
image.dump(table)    # (2)
```

### Example usage
```text
1. The `category_id` is used for training models.
2. When dumping an `ImageAnnotation` to an `Image`, a unique identifier is generated for the annotation.


To store additional attributes that depend on the object type (think of table cells where row and column 
numbers
are needed), a generic attribute `sub_categories` is provided. `sub_categories` is a dictionary that stores 
`CategoryAnnotation` by a given key.

```python

cell = dd.ImageAnnotation(bounding_box, category_name=LayoutType.CELL,  category_id=2)
row_num = dd.CategoryAnnotation(category_name=CellType.ROW_NUMBER, category_id=6)
cell.dump_sub_category(sub_category_name=CellType.ROW_NUMBER, 
                                           annotation=row_num)
```

### Example usage
```python
cell = dd.ImageAnnotation(bounding_box, category_name=LayoutType.CELL,  category_id=2)
row_num = dd.CategoryAnnotation(category_name=CellType.ROW_NUMBER, category_id=6)
cell.dump_sub_category(sub_category_name=CellType.ROW_NUMBER, 
                                           annotation=row_num)
```

### Example usage
```text
A generic `relationships` allows to save object specific attributes that relate different `ImageAnnotation` to
each 
other.

```python

cell = dd.ImageAnnotation(bounding_box, category_name="cell", category_id=2)

for word in word_in_cell:
    cell.dump_relationship(Relationships.CHILD, word.annotation_id)
```

### Example usage
```python
cell = dd.ImageAnnotation(bounding_box, category_name="cell", category_id=2)

for word in word_in_cell:
    cell.dump_relationship(Relationships.CHILD, word.annotation_id)
```

### for word in word_in_cell
```text
## Datasets

Please check [`Datasets`](Datasets.md) for additional information regarding this package.


## Extern


Models from third party packages must be wrapped into a **deep**doctection class structure so that they are
available for pipelines in an unified way. This package provides these wrapper classes.

In many cases, model wrappers will be instantiated by providing a config file, some weights
and a mapping of `category_id`s to `category_name`s.

```python

path_weights = dd.ModelCatalog.get_full_path_weights(model_name)
path_yaml = dd.ModelCatalog.get_full_path_configs(model_name)
categories = dd.ModelCatalog.get_profile(model_name).categories
d2_detector = dd.D2FrcnnDetector(path_yaml,path_weights,categories)
```

### Example usage
```python
path_weights = dd.ModelCatalog.get_full_path_weights(model_name)
path_yaml = dd.ModelCatalog.get_full_path_configs(model_name)
categories = dd.ModelCatalog.get_profile(model_name).categories
d2_detector = dd.D2FrcnnDetector(path_yaml,path_weights,categories)
```

### Example usage
```text
## Mapper

Mappers are arbitrary functions (not generators!). They accept a data point
(as a JSON object, an `Image` instance , a `Page` instance, ...) and return a data point. 

```python
def my_func(dp: dd.Image) -> dd.Image:
        # do something
        return dp

df = dd.Dataflow(df)
df = dd.MapData(df, my_func)

# or if my_func does some heavy transformation and turns out to be the bottleneck

df = dd.Dataflow(df)
df = dd.MultiProcessMapData(df, my_func)
```

### Example usage
```python
def my_func(dp: dd.Image) -> dd.Image:
        # do something
        return dp

df = dd.Dataflow(df)
df = dd.MapData(df, my_func)

# or if my_func does some heavy transformation and turns out to be the bottleneck

df = dd.Dataflow(df)
df = dd.MultiProcessMapData(df, my_func)
```

### Example usage
```text
!!! info "Multi-Thread and Multi-Process"

    The snippet above already shows how we transform our data structure or how we perform any other operation:
We 
    write a mapper function `my_func` and use [`MapData`][deepdoctection.dataflow.common.MapData] to transform
the 
    function into a generator. If we see that `my_func` is a bottleneck in our data processing pipeline we can
speed up 
    the bottleneck function by using a 
[`MultiProcessMapData`][deepdoctection.dataflow.parallel_map.MultiProcessMapData] 
    or [`MultiThreadMapData`][deepdoctection.dataflow.parallel_map.MultiThreadMapData]. This class will spawn 
multiple
    processes and parallelize the mapping function to increase throughput. There are some caveats, though: 
    Multi-threading and multi-processing only work if we have an inifinite dataflow and if you do not bother 
about 
    procssing samples multiple times.



Mappers must be compatible with dataflows. On the other hand, mappers should be flexible enough, and therefore
they
must be able to accept additional arguments for configuration purposes. That means, that if we have a function
`my_func`
that accepts some arguments and returns a function that accepts the datapoint we want to process in our 
pipeline: 

```python
dp = my_func(cfg_param_1, cfg_param_2)(dp)
```

### that accepts some arguments and returns a function that accepts the datapoint we want to process in our 
pipeline
```python
dp = my_func(cfg_param_1, cfg_param_2)(dp)
```

### that accepts some arguments and returns a function that accepts the datapoint we want to process in our 
pipeline
```text
then we can use it this type of function in a dataflow: 

```python
df = # some Dataflow
df = dd.MapData(df, my_func(cfg_param_1, cfg_param_2))
...
```

### then we can use it this type of function in a dataflow
```python
df = # some Dataflow
df = dd.MapData(df, my_func(cfg_param_1, cfg_param_2))
...
```

### Example usage
```text
The [`curry`][deepdoctection.mapper.maputils.curry] decorator disentangles the first argument of a function 
from the
remaining ones.

```python
@curry # (1)
def  my_func(dp: Image, config_1, config_2) -> dd.Image:
        ...
        return dp
```

### Example usage
```python
@curry # (1)
def  my_func(dp: Image, config_1, config_2) -> dd.Image:
        ...
        return dp
```

### def  my_func(dp: Image, config_1, config_2) -> dd.Image
```text
1. This makes `my_mapper` callable twice


## Pipelines

This package provides us with pipeline components for tasks like layout detection, OCR and several other 
services
needed. Chained pipeline components will form a pipeline. Check [`Building a custom 
pipeline`](Custom_Pipeline.md)
to learn, how to build pipelines for a concrete task. Here, we will be giving only a short overview.

There is a registry

```python
print(pipeline_component_registry.get_all())
```

### Example usage
```python
print(pipeline_component_registry.get_all())
```

### Example usage
```text
??? info "Output"

    <pre>
    {'ImageCroppingService': <class 'deepdoctection.pipe.concurrency.MultiThreadPipelineComponent'>, 
     'MatchingService': <class 'deepdoctection.pipe.common.MatchingService'>, 
     'PageParsingService': <class 'deepdoctection.pipe.common.PageParsingService'>, 
     'AnnotationNmsService': <class 'deepdoctection.pipe.common.AnnotationNmsService'>, 
     'ImageParsingService': <class 'deepdoctection.pipe.common.ImageParsingService'>, 
     'LanguageDetectionService': <class 'deepdoctection.pipe.language.LanguageDetectionService'>, 
     'ImageLayoutService': <class 'deepdoctection.pipe.layout.ImageLayoutService'>, 
     'LMTokenClassifierService': <class 'deepdoctection.pipe.lm.LMTokenClassifierService'>, 
     'LMSequenceClassifierService': <class 'deepdoctection.pipe.lm.LMSequenceClassifierService'>, 
     'TextOrderService': <class 'deepdoctection.pipe.order.TextOrderService'>, 
     'TableSegmentationRefinementService': <class 
'deepdoctection.pipe.refine.TableSegmentationRefinementService'>, 
     'TableSegmentationService': <class 'deepdoctection.pipe.segment.TableSegmentationService'>, 
     'SubImageLayoutService': <class 'deepdoctection.pipe.sub_layout.SubImageLayoutService'>, 
     'TextExtractionService': <class 'deepdoctection.pipe.text.TextExtractionService'>, 
     'SimpleTransformService': <class 'deepdoctection.pipe.transform.SimpleTransformService'>}
    </pre>


The following is a full OCR system with a word detector (generating bounding boxes around words) and a text 
recognizer (recognizing text within each word bounding box defines by the word detector) powered by DocTr.

```python
path_weights = dd.ModelCatalog.get_full_path_weights("doctr/db_resnet50/pt/db_resnet50-ac60cadc.pt")
architecture = dd.ModelCatalog.get_profile("doctr/db_resnet50/pt/db_resnet50-ac60cadc.pt").architecture
categories = dd.ModelCatalog.get_profile("doctr/db_resnet50/pt/db_resnet50-ac60cadc.pt").categories

text_line_predictor = dd.DoctrTextlineDetector(architecture=architecture, 
                                                                                           path_weights=path_w
eights, 
                                                                                           categories=categori
es,
                                                                                           device = "cpu")

layout = dd.ImageLayoutService(text_line_predictor,
                                                           to_image=True)  # (1)
                                                                                           
path_weights = dd.ModelCatalog.get_full_path_weights("doctr/crnn_vgg16_bn/pt/crnn_vgg16_bn-9762b0b0.pt")
architecture = dd.ModelCatalog.get_profile("doctr/crnn_vgg16_bn/pt/crnn_vgg16_bn-9762b0b0.pt").architecture

text_recognizer = dd.DoctrTextRecognizer(architecture=architecture, 
                                                                                 path_weights=path_weights)
text = dd.TextExtractionService(text_recognizer, extract_from_roi="word") # (2) 
analyzer = dd.DoctectionPipe(pipeline_component_list=[layout, text]) 


path_to_pdf = "path/to/doc.pdf"

df = analyzer.analyze(path=path_to_pdf)
dd.SerializerJsonlines.save(df, path= "path/to/target_dir",
                                                                file_name="doc.jsonl",
                                                                max_datapoints=20)
```

### The following is a full OCR system with a word detector (generating bounding boxes around words) and a 
text
```python
path_weights = dd.ModelCatalog.get_full_path_weights("doctr/db_resnet50/pt/db_resnet50-ac60cadc.pt")
architecture = dd.ModelCatalog.get_profile("doctr/db_resnet50/pt/db_resnet50-ac60cadc.pt").architecture
categories = dd.ModelCatalog.get_profile("doctr/db_resnet50/pt/db_resnet50-ac60cadc.pt").categories

text_line_predictor = dd.DoctrTextlineDetector(architecture=architecture, 
                                                                                           path_weights=path_w
eights, 
                                                                                           categories=categori
es,
                                                                                           device = "cpu")

layout = dd.ImageLayoutService(text_line_predictor,
                                                           to_image=True)  # (1)
                                                                                           
path_weights = dd.ModelCatalog.get_full_path_weights("doctr/crnn_vgg16_bn/pt/crnn_vgg16_bn-9762b0b0.pt")
architecture = dd.ModelCatalog.get_profile("doctr/crnn_vgg16_bn/pt/crnn_vgg16_bn-9762b0b0.pt").architecture

text_recognizer = dd.DoctrTextRecognizer(architecture=architecture, 
                                                                                 path_weights=path_weights)
text = dd.TextExtractionService(text_recognizer, extract_from_roi="word") # (2) 
analyzer = dd.DoctectionPipe(pipeline_component_list=[layout, text]) 


path_to_pdf = "path/to/doc.pdf"

df = analyzer.analyze(path=path_to_pdf)
dd.SerializerJsonlines.save(df, path= "path/to/target_dir",
                                                                file_name="doc.jsonl",
                                                                max_datapoints=20)
```

### Example usage
```text
1. `ImageAnnotation` created from this service will receive an `Image` instance defined by the bounding boxes 
of its 
   annotation. This is helpful if we want to call a service only on the region of the `ImageAnnotation`. 
2. Text recognition on the region of interest defined by all `ImageAnnotation` instances of 
`category_name="word"`.
```

---

# docs/tutorials/Custom_Pipeline.md - Project: Building a custom pipeline

<p align="center"> <img 
src="https://github.com/deepdoctection/deepdoctection/raw/master/docs/tutorials/_imgs/dd_logo.png" alt="Deep 
Doctection Logo" width="60%"> <h3 align="center"> </h3> </p>.

## Code Examples

### Getting the pre-trained model
```python
categories=dd.ModelCatalog.get_profile("fasttext/lid.176.bin").categories
categories_orig = dd.ModelCatalog.get_profile("fasttext/lid.176.bin").categories_orig
dd.ModelCatalog.get_profile("fasttext/lid.176.bin").model_wrapper # (1)
```

### Example usage
```text
1. `model_wrapper` is the name of the model wrapper we need to use from the `deepdoctection.extern` module.

??? info "Output"

    'FasttextLangDetector'


```python
path_weights=dd.ModelDownloadManager.maybe_download_weights_and_configs("fasttext/lid.176.bin")
```

### Example usage
```python
path_weights=dd.ModelDownloadManager.maybe_download_weights_and_configs("fasttext/lid.176.bin")
```

### Example usage
```text
## Model wrapper

We know from the `ModelCatalog` which wrapper we must use for the fasttext model, namely 
`FasttextLangDetector`.


```python
fast_text = dd.FasttextLangDetector(path_weights=path_weights, 
                                                                        categories=categories, 
                                                                        categories_orig=categories_orig)
```

### Example usage
```python
fast_text = dd.FasttextLangDetector(path_weights=path_weights, 
                                                                        categories=categories, 
                                                                        categories_orig=categories_orig)
```

### Example usage
```text
We still need to choose how to extract text. 


```python
tess_ocr_config_path = dd.get_configs_dir_path() / "dd/conf_tesseract.yaml" # (1)
tesseract_ocr = dd.TesseractOcrDetector(tess_ocr_config_path)
```

### Example usage
```python
tess_ocr_config_path = dd.get_configs_dir_path() / "dd/conf_tesseract.yaml" # (1)
tesseract_ocr = dd.TesseractOcrDetector(tess_ocr_config_path)
```

### Example usage
```text
1. If this file is not in your `.cache` you can find it in `deepdoctection.configs`.


## Language detection service and pipeline


```python
lang_detect_comp = dd.LanguageDetectionService(language_detector=fast_text,
                                                                                           text_detector=tesse
ract_ocr)
```

### Language detection service and pipeline
```python
lang_detect_comp = dd.LanguageDetectionService(language_detector=fast_text,
                                                                                           text_detector=tesse
ract_ocr)
```

### Example usage
```text
We can now build our very simple pipeline.


```python
pipe = dd.DoctectionPipe(pipeline_component_list=[lang_detect_comp])
```

### Example usage
```python
pipe = dd.DoctectionPipe(pipeline_component_list=[lang_detect_comp])
```

### Example usage
```text
When running the pipe, we get the language the document was written. 


```python
df = pipe.analyze(path="/path/to/image_dir")
df.reset_state()

dp = next(iter(df))
dp.language
```

### Example usage
```python
df = pipe.analyze(path="/path/to/image_dir")
df.reset_state()

dp = next(iter(df))
dp.language
```

### Example usage
```text
??? info "Output"

    Languages.GERMAN


But, when getting the text, the response is somewhat disappointing: `dp.text` returns an empty string.

!!! info

    The reason for that is that `LanguageDetectionService` is not responsible for extracting text. It has an 
OCR model, 
    but the output is only used as input feed to the language detector. The text however is not persisted. If 
we had 
    added a `TextExtractionService` before `LanguageDetectionService` we could have omitted the OCR model in 
    the `LanguageDetectionService`. 


## Tesseract OCR detector

Next, we add a component for extracting text.

```python
tesseract_ocr = dd.TesseractOcrDetector(tess_ocr_config_path.as_posix(),["LANGUAGES=deu"])
tesseract_ocr.config
```

### Tesseract OCR detector
```python
tesseract_ocr = dd.TesseractOcrDetector(tess_ocr_config_path.as_posix(),["LANGUAGES=deu"])
tesseract_ocr.config
```

### Example usage
```text
??? info "Output"

    {'LANGUAGES': 'deu', 'LINES': False, 'psm': 11}


```python
text_comp = dd.TextExtractionService(text_extract_detector=tesseract_ocr, 
                                     run_time_ocr_language_selection=True) # (1)
pipe_comp_list=[lang_detect_comp, text_comp]
pipe = dd.DoctectionPipe(pipeline_component_list=pipe_comp_list)
```

### Example usage
```python
text_comp = dd.TextExtractionService(text_extract_detector=tesseract_ocr, 
                                     run_time_ocr_language_selection=True) # (1)
pipe_comp_list=[lang_detect_comp, text_comp]
pipe = dd.DoctectionPipe(pipeline_component_list=pipe_comp_list)
```

### Example usage
```text
1. Setting `run_time_ocr_language_selection=True` will dynamically select the OCR model for text extraction 
based on 
   the predicted languages. This helps to get much improved OCR results, if you have documents with various 
languages.



```python
df = pipe.analyze(path=image_path)
df.reset_state()
dp = next(iter(df))
```

### Example usage
```python
df = pipe.analyze(path=image_path)
df.reset_state()
dp = next(iter(df))
```

### Example usage
```text
There is something unexpected: `dp.text` is still an empty string. On the other hand, we can clearly see that 
the 
`TextExtractionService` did its job.


```python
word_sample = dp.words[0]
len(dp.words), word_sample.characters, word_sample.bbox, word_sample.reading_order
```

### Example usage
```python
word_sample = dp.words[0]
len(dp.words), word_sample.characters, word_sample.bbox, word_sample.reading_order
```

### Example usage
```text
??? info "Output"

    (553, 'Anleihemärkte', [137.0, 158.0, 472.0, 195.0], None)


## Text ordering

The reason is, that we do not have inferred a reading order. If there is no reading order, there is no 
contiguous text. 
We treat text extraction as a character recognition problem only. If we want a reading order of predicted 
words, 
we need to do it by adding a designated service. 


```python
order_comp = dd.TextOrderService(text_container=dd.LayoutType.WORD)

pipe_comp_list=[lang_detect_comp, text_comp, order_comp]
pipe = dd.DoctectionPipe(pipeline_component_list=pipe_comp_list)

df = pipe.analyze(path=image_path)
df.reset_state()
dp = next(iter(df))
dp.text
```

### Example usage
```python
order_comp = dd.TextOrderService(text_container=dd.LayoutType.WORD)

pipe_comp_list=[lang_detect_comp, text_comp, order_comp]
pipe = dd.DoctectionPipe(pipeline_component_list=pipe_comp_list)

df = pipe.analyze(path=image_path)
df.reset_state()
dp = next(iter(df))
dp.text
```

### Example usage
```text
??? info "Output"

     Anleihemärkte im Geschäftsjahr\nbis zum 31.12.2018\nSchwieriges Marktumfeld\nDie internationalen 
Anleihe-\nmärkte
     entwickelten sich im\nGeschäftsjahr 2018 unter-\nschiedlich und phasenweise\nsehr volatil. Dabei machte 
sich\nbei 
     den Investoren zunehmend\nNervosität breit, was in steigen-\nden Risikoprämien zum Aus-\ndruck kam. Grund
hierfür 
     waren\nTurbulenzen auf der weltpoli-\ntischen Bühne, die die politi-\nschen Risiken erhöhten. 
Dazu\nzählten unter 
     anderem populis-\ntische Strömungen nicht nur\nin den USA und Europa, auch\nin den Emerging Markets, 
     wie\nzuletzt in Brasilien und Mexiko,\nwo Populisten in die Regie-\nrungen gewählt wurden. 
Der\neskalierende 
     Handelskonflikt\nzwischen den USA einerseits\nsowie Europa und China ande-\nrerseits tat sein übriges. 
Zudem\nging 
     Italien im Rahmen seiner\nHaushaltspolitik auf Konfronta-\ntionskurs zur Europäischen Uni-\non (EU). 
Darüber 
     hinaus verun-\nsicherte weiterhin der drohende\nBrexit die Marktteilnehmer,\ninsbesondere dahingehend, 
ob\nder 
     mögliche Austritt des Ver-\neinigten Königreiches aus der\nEU geordnet oder - ohne ein\nÜbereinkommen - 
     ungeordnet\nvollzogen wird. Im Gegensatz\nzu den politischen Unsicher-\nheiten standen die bislang 
     eher\nzuversichtlichen, konventionel-\nlen Wirtschaftsindikatoren. So\nexpandierte die 
Weltwirtschaft\nkräftig, 
     wenngleich sich deren\nWachstum im Laufe der zwei-\nten Jahreshälfte 2018 etwas\nverlangsamte. Die 
     Geldpolitik\nwar historisch gesehen immer\nnoch sehr locker, trotz der welt-\nweit sehr hohen 
Verschuldung\nund 
     der Zinserhöhungen der\nUS-Notenbank.\nEntwicklung der Leitzinsen in den USA und im Euroraum\n%p.a.
     \nu\nu\nu\nu\nu\nu\nu\nu\nu\nu\n12/08 12/09 12/10 12/11 12/12 12/13 12/14 12/15 12/16 12/17 12/18\nBE 
     Fed-Leitzins\nQuelle: Thomson Financial Datastream\nBE E28-Leitzins\nStand: 31.12.2018\n-1 u\nZinswende 
nach 
     Rekordtiefs\nbei Anleiherenditen?\nIm Berichtszeitraum kam es an\nden Anleihemärkten - wenn\nauch 
uneinheitlich 
     und unter-\nschiedlich stark ausgeprägt -\nunter Schwankungen zu stei-\ngenden Renditen auf 
teilweise\nimmer noch 
     sehr niedrigem\nNiveau, begleitet von nachge-\nbenden Kursen. Dabei konnten\nsich die Zinsen vor allem in
den\nUSA 
     weiter von ihren histori-\nschen Tiefs lösen. Gleichzeitig\nwurde die Zentralbankdivergenz\nzwischen den 
USA und 
     dem\nEuroraum immer deutlicher. An-\ngesichts des Wirtschaftsbooms\nin den USA hob die US-Noten-\nbank 
Fed im 
     Berichtszeitraum\nden Leitzins in vier Schritten\nweiter um einen Prozentpunkt\nauf einen Korridor von 
2,25% -\n2,
     50% p.a. an. Die Europäische\nZentralbank (EZB) hingegen\nhielt an ihrer Nullzinspolitik fest\nund die 
Bank of 
     Japan beließ\nihren Leitzins bei -0,10% p.a.\nDie Fed begründete ihre Zinser-\nhöhungen mit der 
     Wachstums-\nbeschleunigung und der Voll-\nbeschäftigung am Arbeitsmarkt\nin den USA. 
     Zinserhöhungen\nermöglichten der US-Notenbank\neiner Überhitzung der US-Wirt-\nschaft vorzubeugen, die 
durch\ndie 
     prozyklische expansive\nFiskalpolitik des US-Präsidenten\nDonald Trump in Form von\nSteuererleichterungen
und 
     einer\nErhöhung der Staatsausgaben\nnoch befeuert wurde. Vor die-\nsem Hintergrund verzeichneten\ndie 
     US-Bondmärkte einen spür-\nbaren Renditeanstieg, der mit\nmerklichen Kursermäßigungen\neinherging. Per 
saldo 
     stiegen\ndie Renditen zehnjähriger US-\nStaatsanleihen auf Jahressicht\nvon 2,4% p.a. auf 3,1% 
p.a.\nDiese 
     Entwicklung in den USA\nhatte auf den Euroraum jedoch\nnur phasenweise und partiell,\ninsgesamt aber kaum
     einen\nzinstreibenden Effekt auf Staats-\nanleihen aus den europäischen\nKernmärkten wie 
     beispielsweise\nDeutschland und Frankreich.\nSo gaben zehnjährige deutsche\nBundesanleihen im 
Jahresver-\nlauf 
     2018 unter Schwankungen\nper saldo sogar von 0,42% p.a.\nauf 0,25% p. a. nach. Vielmehr\nstanden die 
     Anleihemärkte\nder Euroländer - insbeson-\ndere ab dem zweiten Quartal\n2018 - unter dem Einfluss 
der\npolitischen 
     und wirtschaftlichen\nEntwicklung in der Eurozone,\nvor allem in den Ländern mit\nhoher Verschuldung und 
     nied-\nrigem Wirtschaftswachstum.\nIn den Monaten Mai und Juni


At least, we got some text. The beginning sounds good. But once the text comes to the region where the second 
and 
third column also have text lines, the order service does not distinguish between columns. So we must identify
columns. 
For that we use the layout analyzer.

## Layout service


```python
path_weights = dd.ModelCatalog.get_full_path_weights("layout/d2_model_0829999_layout_inf_only.pt")
path_configs = dd.ModelCatalog.get_full_path_configs("layout/d2_model_0829999_layout_inf_only.pt")
categories = dd.ModelCatalog.get_profile("layout/d2_model_0829999_layout_inf_only.pt").categories

layout_detector = dd.D2FrcnnDetector(path_yaml=path_configs,
                                     path_weights=path_weights,
                                     categories=categories,
                                     device="cpu")
layout_comp = dd.ImageLayoutService(layout_detector)
```

### Layout service
```python
path_weights = dd.ModelCatalog.get_full_path_weights("layout/d2_model_0829999_layout_inf_only.pt")
path_configs = dd.ModelCatalog.get_full_path_configs("layout/d2_model_0829999_layout_inf_only.pt")
categories = dd.ModelCatalog.get_profile("layout/d2_model_0829999_layout_inf_only.pt").categories

layout_detector = dd.D2FrcnnDetector(path_yaml=path_configs,
                                     path_weights=path_weights,
                                     categories=categories,
                                     device="cpu")
layout_comp = dd.ImageLayoutService(layout_detector)
```

### Example usage
```text
We need to make sure, that the `ImageLayoutService` has been invoked before `TextOrderService`.  


```python
pipe_comp_list=[layout_comp, lang_detect_comp, text_comp, order_comp]
pipe = dd.DoctectionPipe(pipeline_component_list=pipe_comp_list)


df = pipe.analyze(path=image_path)
df.reset_state()

dp = next(iter(df))
dp.text, dp.layouts[0].text
```

### Example usage
```python
pipe_comp_list=[layout_comp, lang_detect_comp, text_comp, order_comp]
pipe = dd.DoctectionPipe(pipeline_component_list=pipe_comp_list)


df = pipe.analyze(path=image_path)
df.reset_state()

dp = next(iter(df))
dp.text, dp.layouts[0].text
```

### Example usage
```text
??? info "Output"

    ('\nAnleihemärkte im Geschäftsjahr\nbis zum 31.12.2018\nSchwieriges Marktumfeld\n\nDie internationalen 
Anleihe-
    \nmärkte entwickelten sich im\nGeschäftsjahr 2018 unter-\nschiedlich und phasenweise\nsehr volatil. Dabei 
machte 
    sich\nbei den Investoren zunehmend\nNervosität breit, was in steigen-\nden Risikoprämien zum Aus-\ndruck 
kam. 
    Grund hierfür waren\nTurbulenzen auf der weltpoli-\ntischen Bühne, die die politi-\nschen Risiken 
erhöhten. 
    Dazu\nzählten unter anderem populis-\ntische Strömungen nicht nur\nin den USA und Europa, auch\nin den 
Emerging 
    Markets, wie\nzuletzt in Brasilien und Mexiko,\nwo Populisten in die Regie-\nrungen gewählt wurden. 
    Der\neskalierende Handelskonflikt\nzwischen den USA einerseits\nsowie Europa und China ande-\nrerseits tat
sein 
    übriges. Zudem\nging Italien im Rahmen seiner\nHaushaltspolitik auf Konfronta-\ntionskurs zur Europäischen
    Uni-\non (EU). Darüber hinaus verun-\nsicherte weiterhin der drohende\nBrexit die 
Marktteilnehmer,\ninsbesondere 
    dahingehend, ob\nder mögliche Austritt des Ver-\neinigten Königreiches aus der\nEU geordnet oder - ohne 
    ein\nÜbereinkommen - ungeordnet\nvollzogen wird. Im Gegensatz\nzu den politischen Unsicher-\nheiten 
standen die 
    bislang eher\nzuversichtlichen, konventionel-\nlen Wirtschaftsindikatoren. So\nexpandierte die 
    Weltwirtschaft\nkräftig, wenngleich sich deren\nWachstum im Laufe der zwei-\nten Jahreshälfte 2018 
    etwas\nverlangsamte. Die Geldpolitik\nwar historisch gesehen immer\nnoch sehr locker, trotz der 
welt-\nweit sehr 
    hohen Verschuldung\nund der Zinserhöhungen der\nUS-Notenbank.\n\nBE Fed-Leitzins\nQuelle: Thomson 
Financial 
    Datastream\nBE E28-Leitzins\nStand: 31.12.2018\n\nUSA weiter von ihren histori-\nvon 2,4% p.a. auf 3,1% 
p.a.
    \nschen Tiefs lösen. Gleichzeitig\nwurde die Zentralbankdivergenz\nDiese Entwicklung in den 
USA\n\nzwischen den 
    USA und dem\nhatte auf den Euroraum jedoch\nEuroraum immer deutlicher. An-\nnur phasenweise und 
partiell,\ngesichts 
    des Wirtschaftsbooms\ninsgesamt aber kaum einen\nin den USA hob die US-Noten-\nzinstreibenden Effekt auf 
    Staats-\nbank Fed im Berichtszeitraum\nanleihen aus den europäischen\nden Leitzins in vier 
Schritten\nKernmärkten 
    wie beispielsweise\nweiter um einen Prozentpunkt\nDeutschland und Frankreich.\nauf einen Korridor von 
2,25% 
    -\nSo gaben zehnjährige deutsche\n2,50% p.a. an. Die Europäische\nBundesanleihen im 
Jahresver-\nZentralbank (EZB) 
    hingegen\nlauf 2018 unter Schwankungen\nIn den Monaten Mai und Juni\n\nEntwicklung der Leitzinsen in den 
USA und 
    im Euroraum\n%p.a.\n-1 u\nu\nu\nu\nu\nu\nu\nu\nu\nu\nu\n12/08 12/09 12/10 12/11 12/12 12/13 12/14 12/15 
12/16 
    12/17 12/18\nZinswende nach Rekordtiefs\n\nFiskalpolitik des US-Präsidenten\nbei Anleiherenditen?\nDonald 
Trump 
    in Form von\nIm Berichtszeitraum kam es an\nSteuererleichterungen und einer\nden Anleihemärkten - 
wenn\nErhöhung 
    der Staatsausgaben\nauch uneinheitlich und unter-\nnoch befeuert wurde. Vor die-\nschiedlich stark 
ausgeprägt 
    -\nsem Hintergrund verzeichneten\nunter Schwankungen zu stei-\ndie US-Bondmärkte einen spür-\ngenden 
Renditen auf 
    teilweise\nbaren Renditeanstieg, der mit\nimmer noch sehr niedrigem\nmerklichen Kursermäßigungen\nNiveau, 
    begleitet von nachge-\neinherging. Per saldo stiegen\nbenden Kursen. Dabei konnten\ndie Renditen 
zehnjähriger 
    US-\nsich die Zinsen vor allem in den\nStaatsanleihen auf Jahressicht\nhielt an ihrer Nullzinspolitik 
fest\nper 
    saldo sogar von 0,42% p.a.\nund die Bank of Japan beließ\nauf 0,25% p. a. nach. Vielmehr\nihren Leitzins 
bei -0,
    10% p.a.\nstanden die Anleihemärkte\nDie Fed begründete ihre Zinser-\nder Euroländer - insbeson-\nhöhungen
mit 
    der Wachstums-\ndere ab dem zweiten Quartal\nbeschleunigung und der Voll-\n2018 - unter dem Einfluss 
    der\nbeschäftigung am Arbeitsmarkt\npolitischen und wirtschaftlichen\nin den USA. 
Zinserhöhungen\nEntwicklung in 
    der Eurozone,\nermöglichten der US-Notenbank\nvor allem in den Ländern mit\neiner Überhitzung der 
US-Wirt-\nhoher 
    Verschuldung und nied-\nschaft vorzubeugen, die durch\nrigem Wirtschaftswachstum.\ndie prozyklische 
expansive',
     '')



Now this looks weird again. However the reason is still quite simple. We now get an empty text string 
because once we have a non-empty `dp.layouts` the routine responsible for creating `dp.text` will try to get 
the text 
from the `Layout`s. But we haven't run any method that maps a `word` to some `Layout` object. We need to 
specify this 
by running a `MatchingService`. We will also have to slightly change the configuration of the  
`TextOrderService`.


```python
map_comp = dd.MatchingService(parent_categories=["text","title","list","table","figure"], 
                              child_categories=["word"],
                              matching_rule = 'ioa', 
                              threshold=0.6)

order_comp = dd.TextOrderService(text_container=dd.LayoutType.WORD,
                                 floating_text_block_categories=["text","title","list", "figure"],
                                 text_block_categories=["text","title","list","table","figure"])

pipe_comp_list = [layout_comp, lang_detect_comp, text_comp, map_comp, order_comp]
pipe = dd.DoctectionPipe(pipeline_component_list=pipe_comp_list)
df = pipe.analyze(path=image_path)
df.reset_state()
dp = next(iter(df))

dp.text
```

### Example usage
```python
map_comp = dd.MatchingService(parent_categories=["text","title","list","table","figure"], 
                              child_categories=["word"],
                              matching_rule = 'ioa', 
                              threshold=0.6)

order_comp = dd.TextOrderService(text_container=dd.LayoutType.WORD,
                                 floating_text_block_categories=["text","title","list", "figure"],
                                 text_block_categories=["text","title","list","table","figure"])

pipe_comp_list = [layout_comp, lang_detect_comp, text_comp, map_comp, order_comp]
pipe = dd.DoctectionPipe(pipeline_component_list=pipe_comp_list)
df = pipe.analyze(path=image_path)
df.reset_state()
dp = next(iter(df))

dp.text
```

### Example usage
```text
??? info "Output"

    Anleihemärkte im Geschäftsjahr bis zum 31.12.2018\nSchwieriges Marktumfeld Die internationalen Anleihe- 
märkte
    entwickelten sich im Geschäftsjahr 2018 unter- schiedlich und phasenweise sehr volatil. Dabei machte sich 
bei den 
    Investoren zunehmend Nervosität breit, was in steigen- den Risikoprämien zum Aus- druck kam. Grund hierfür
waren 
    Turbulenzen auf der weltpoli- tischen Bühne, die die politi- schen Risiken erhöhten. Dazu zählten unter 
anderem 
    populis- tische Strömungen nicht nur in den USA und Europa, auch in den Emerging Markets, wie zuletzt in 
    Brasilien und Mexiko, wo Populisten in die Regie- rungen gewählt wurden. Der eskalierende Handelskonflikt 
zwischen 
    den USA einerseits sowie Europa und China ande- rerseits tat sein übriges. Zudem ging Italien im Rahmen 
seiner 
    Haushaltspolitik auf Konfronta- tionskurs zur Europäischen Uni- on (EU). Darüber hinaus verun- sicherte 
weiterhin 
    der drohende Brexit die Marktteilnehmer, insbesondere dahingehend, ob der mögliche Austritt des Ver- 
einigten 
    Königreiches aus der EU geordnet oder - ohne ein Übereinkommen - ungeordnet vollzogen wird. Im Gegensatz 
zu den 
    politischen Unsicher- heiten standen die bislang eher zuversichtlichen, konventionel- len 
Wirtschaftsindikatoren. 
    So expandierte die Weltwirtschaft kräftig, wenngleich sich deren Wachstum im Laufe der zwei- ten 
Jahreshälfte 
    2018 etwas verlangsamte. Die Geldpolitik war historisch gesehen immer noch sehr locker, trotz der welt- 
weit 
    sehr hohen Verschuldung und der Zinserhöhungen der US-Notenbank.\nEntwicklung der Leitzinsen in den USA 
und im 
    Euroraum %p.a.\nZinswende nach Rekordtiefs\nbei Anleiherenditen? Im Berichtszeitraum kam es an den 
Anleihemärkten 
    - wenn auch uneinheitlich und unter- schiedlich stark ausgeprägt - unter Schwankungen zu stei- genden 
Renditen auf 
    teilweise immer noch sehr niedrigem Niveau, begleitet von nachge- benden Kursen. Dabei konnten sich die 
Zinsen 
    vor allem in den USA weiter von ihren histori- schen Tiefs lösen. Gleichzeitig wurde die 
Zentralbankdivergenz 
    zwischen den USA und dem Euroraum immer deutlicher. An- gesichts des Wirtschaftsbooms in den USA hob die 
US-Noten- 
    bank Fed im Berichtszeitraum den Leitzins in vier Schritten weiter um einen Prozentpunkt auf einen 
Korridor von 2,
    25% - 2,50% p.a. an. Die Europäische Zentralbank (EZB) hingegen hielt an ihrer Nullzinspolitik fest und 
die Bank 
    of Japan beließ ihren Leitzins bei -0,10% p.a. Die Fed begründete ihre Zinser- höhungen mit der Wachstums-
    beschleunigung und der Voll- beschäftigung am Arbeitsmarkt in den USA. Zinserhöhungen ermöglichten der 
    US-Notenbank einer Überhitzung der US-Wirt- schaft vorzubeugen, die durch die prozyklische expansive\n-1 u
u u u 
    u u u u u u u 12/08 12/09 12/10 12/11 12/12 12/13 12/14 12/15 12/16 12/17 12/18\nBE Fed-Leitzins\nQuelle: 
    Thomson Financial Datastream\nBE E28-Leitzins\nStand: 31.12.2018\nFiskalpolitik des US-Präsidenten Donald 
Trump in 
    Form von Steuererleichterungen und einer Erhöhung der Staatsausgaben noch befeuert wurde. Vor die- sem 
Hintergrund 
    verzeichneten die US-Bondmärkte einen spür- baren Renditeanstieg, der mit merklichen Kursermäßigungen 
einherging. 
    Per saldo stiegen die Renditen zehnjähriger US- Staatsanleihen auf Jahressicht von 2,4% p.a. auf 3,1% p.a.
    \nDiese Entwicklung in den USA hatte auf den Euroraum jedoch nur phasenweise und partiell, insgesamt aber 
kaum 
    einen zinstreibenden Effekt auf Staats- anleihen aus den europäischen Kernmärkten wie beispielsweise 
Deutschland 
    und Frankreich. So gaben zehnjährige deutsche Bundesanleihen im Jahresver- lauf 2018 unter Schwankungen 
per saldo 
    sogar von 0,42% p.a. auf 0,25% p. a. nach. Vielmehr standen die Anleihemärkte der Euroländer - insbeson- 
dere ab 
    dem zweiten Quartal 2018 - unter dem Einfluss der politischen und wirtschaftlichen Entwicklung in der 
Eurozone, vor 
    allem in den Ländern mit hoher Verschuldung und nied- rigem Wirtschaftswachstum. In den Monaten Mai und 
Juni



Finally, we got it!
```

---

# docs/tutorials/Data_Structure.md - Data structure

<p align="center"> <img 
src="https://github.com/deepdoctection/deepdoctection/raw/master/docs/tutorials/_imgs/dd_logo.png" alt="Deep 
Doctection Logo" width="60%"> <h3 align="center"> </h3> </p>.

## Code Examples

### Example usage
```python
import deepdoctection as dd

path = "/path/to/dir/parsed_image.json"
page = dd.Page.from_file(file_path=path)

image = page.image_orig
```

### Example usage
```text
The `Image` object has an `image_id`, which is a uuid that depends on the location where the original image 
has been 
loaded.

!!! info

    On the other hand there is a `state_id` that changes once the whole `image` instance changes.


```python
print(f"image_id: {image.image_id} state_id: {image.state_id}")
```

### Example usage
```python
print(f"image_id: {image.image_id} state_id: {image.state_id}")
```

### Example usage
```text
??? info "Output"

    image_id: 2aa98b36-196e-3cdf-af09-8f2d885d5f88 state_id: 98eebb5d-f319-3094-94af-fb0f02229dad


## `ImageAnnotation`s

We have a 1:1 correspondence between a `Layout`, `Word`, `Table`, `Cell` on the `Page` level and 
`ImageAnnotation` on 
the `Image` level. In fact, all layout sections are sub classes of `ImageAnnotation`:


```python
word.__class__.__bases__[0].__bases__[0]
```

### the `Image` level. In fact, all layout sections are sub classes of `ImageAnnotation`
```python
word.__class__.__bases__[0].__bases__[0]
```

### Example usage
```text
??? info "Output"

    deepdoctection.datapoint.annotation.ImageAnnotation


We can even retrieve the `ImageAnnotation` instance from which the `word` instance has been derived by its 
`annotation_id`.


```python
ann = image.get_annotation(annotation_ids='844631a5-5ddb-3ba8-b81a-bb9f05604d58')[0]
```

### Example usage
```python
ann = image.get_annotation(annotation_ids='844631a5-5ddb-3ba8-b81a-bb9f05604d58')[0]
```

### Example usage
```text
Categories and keys are stored as members of special classes called `ObjectTypes`.


```python
ann.sub_categories.keys()
```

### Example usage
```python
ann.sub_categories.keys()
```

### Example usage
```text
??? info "Output"

    dict_keys([WordType.CHARACTERS, WordType.BLOCK, WordType.TEXT_LINE, Relationships.READING_ORDER])

```python
ann.category_name
```

### Example usage
```python
ann.category_name
```

### Example usage
```text
??? info "Output"

    LayoutType.WORD



## `ObjectTypes`

`ObjectTypes` is a string based enum. For related keys or categories a subclass of `ObjectTypes` is formed.
The `object_types_registry` is responsible for cataloging the `ObjectTypes`.


```python
dd.object_types_registry.get_all()
```

### Example usage
```python
dd.object_types_registry.get_all()
```

### Example usage
```text
??? info "Output"

     <pre>
    {'DefaultType': <enum 'DefaultType'>,
     'PageType': <enum 'PageType'>,
     'SummaryType': <enum 'SummaryType'>,
     'DocumentType': <enum 'DocumentType'>,
     'LayoutType': <enum 'LayoutType'>,
     'TableType': <enum 'TableType'>,
     'CellType': <enum 'CellType'>,
     'WordType': <enum 'WordType'>,
     'TokenClasses': <enum 'TokenClasses'>,
     'BioTag': <enum 'BioTag'>,
     'TokenClassWithTag': <enum 'TokenClassWithTag'>,
     'Relationships': <enum 'Relationships'>,
     'Languages': <enum 'Languages'>,
     'DatasetType': <enum 'DatasetType'>}
     </pre>



```python
word = dd.object_types_registry.get("WordType")
for word_type in word:
    print(word_type)
```

### Example usage
```python
word = dd.object_types_registry.get("WordType")
for word_type in word:
    print(word_type)
```

### for word_type in word
```text
??? info "Output"

    WordType.CHARACTERS
    WordType.BLOCK
    WordType.TOKEN_CLASS
    WordType.TAG
    WordType.TOKEN_TAG
    WordType.TEXT_LINE
    WordType.CHARACTER_TYPE
    WordType.PRINTED
    WordType.HANDWRITTEN


### Modifying `ObjectTypes`

We have already mentioned that it is not directly possible to modify values using the `Page` attributes. We 
need to
access the `ImageAnnotation` or `CategoryAnnotation` in order to modify values.


```python
character_ann = ann.get_sub_category("characters")
character_ann
```

### Example usage
```python
character_ann = ann.get_sub_category("characters")
character_ann
```

### Example usage
```text
??? info "Output"

    ContainerAnnotation(active=True, 
                        _annotation_id='ded39c8a-72c0-335b-853f-e6c8b50fbfbc', 
                        service_id=None, 
                        model_id=None, 
                        session_id=None, 
                        category_name=<WordType.CHARACTERS>, 
                        _category_name=<WordType.CHARACTERS>, 
                        category_id=-1, 
                        score=0.91, 
                        sub_categories={}, 
                        relationships={}, 
                        value='Gesamtvergütung')



Beside `ImageAnnotation` and `CategoryAnnotation` there is also a `ContainerAnnotation` class. It only differs
from `CategoryAnnotation` by having an attribute `value` that can store a string or a value. 


```python
character_ann.value="Gesamtvergütungsbericht"
ann.category_name="line"
```

### Example usage
```python
character_ann.value="Gesamtvergütungsbericht"
ann.category_name="line"
```

### Example usage
```text
As already mentioned, `category_name` and sub category keys require values that are `ObjectTypes` members. If 
the value 
does not exist as registered `ObjectTypes` members an error is raised.


```python
ann.category_name="headline"
```

### Example usage
```python
ann.category_name="headline"
```

### Example usage
```text
??? Info "Output"

    ---------------------------------------------------------------------------

    KeyError                                  Traceback (most recent call last)

    Cell In[16], line 1
    ----> 1 ann.category_name="headline"


    File ~/Documents/Repos/deepdoctection_pt/deepdoctection/deepdoctection/datapoint/annotation.py:293, in 
CategoryAnnotation.category_name(self, category_name)
        291 """category name setter"""
        292 if not isinstance(category_name, property):
    --> 293     self._category_name = get_type(category_name)


    File ~/Documents/Repos/deepdoctection_pt/deepdoctection/deepdoctection/utils/settings.py:414, in 
get_type(obj_type)
        412 return_value = _ALL_TYPES_DICT.get(obj_type)
        413 if return_value is None:
    --> 414     raise KeyError(f"String {obj_type} does not correspond to a registered ObjectType")
        415 return return_value


    KeyError: 'String headline does not correspond to a registered ObjectType'


Adding an `ObjectTypes` with the required Enum member, registering and updating will then
allow you to use this category.


```python
@dd.object_types_registry.register("NewspaperType")
class NewspaperType(dd.ObjectTypes):

    headline = "headline"
    advertising = "advertising"
    
dd.update_all_types_dict()
```

### Example usage
```python
@dd.object_types_registry.register("NewspaperType")
class NewspaperType(dd.ObjectTypes):

    headline = "headline"
    advertising = "advertising"
    
dd.update_all_types_dict()
```

### Example usage
```text
```python
ann.category_name="headline" # (1)
```

### Example usage
```python
ann.category_name="headline" # (1)
```

### Example usage
```text
1. No key error anymore


## Adding an `ImageAnnotation`

Suppose, we want to add a new word to the page corpus. We have to define an `ImageAnnotation` and need to dump
it. 


```python
new_ann = dd.ImageAnnotation(category_name="word")
new_ann  # (1)
```

### Example usage
```python
new_ann = dd.ImageAnnotation(category_name="word")
new_ann  # (1)
```

### Example usage
```text
1. No annotation_id has been assigned yet. This will happen once we dump the ImageAnnotation to the image.

??? Info "Output"

    ImageAnnotation(active=True, 
    _annotation_id=None, 
    service_id=None, 
    model_id=None, 
    session_id=None, 
    category_name=<LayoutType.WORD>, 
    _category_name=<LayoutType.WORD>, 
    category_id=-1, 
    score=None, 
    sub_categories={}, 
    relationships={}, 
    bounding_box=None)



```python
bbox = dd.BoundingBox(absolute_coords=False, ulx=0.5,uly=0.7,lrx=0.6,lry=0.9) # setting up a bounding box
new_ann.bounding_box = bbox
image.dump(new_ann) # (1)
new_ann.annotation_id # (2)
```

### Example usage
```python
bbox = dd.BoundingBox(absolute_coords=False, ulx=0.5,uly=0.7,lrx=0.6,lry=0.9) # setting up a bounding box
new_ann.bounding_box = bbox
image.dump(new_ann) # (1)
new_ann.annotation_id # (2)
```

### Example usage
```text
1. Dump the annotation to the image
2. There is an annotation_id available right now


??? Info "Output"

   0de5d9cf-f136-321d-b177-08c06157e600


```python
print(f"image_id: {image.image_id} state_id: {image.state_id}") # (1)
```

### Example usage
```python
print(f"image_id: {image.image_id} state_id: {image.state_id}") # (1)
```

### Example usage
```text
1. The state_id has changed because we have added a new annotation to the image.

??? Info "Output"

    image_id: 2aa98b36-196e-3cdf-af09-8f2d885d5f88 
    state_id: b673b2b1-18c6-3b94-bbc1-14432b564ce4


## Adding a `ContainerAnnotation` to an `ImageAnnotation`


```python
container_ann = dd.ContainerAnnotation(category_name=dd.WordType.CHARACTERS, value='Gesamtvergütung')
new_ann.dump_sub_category(dd.WordType.CHARACTERS, container_ann)
```

### Adding a `ContainerAnnotation` to an `ImageAnnotation`
```python
container_ann = dd.ContainerAnnotation(category_name=dd.WordType.CHARACTERS, value='Gesamtvergütung')
new_ann.dump_sub_category(dd.WordType.CHARACTERS, container_ann)
```

### Example usage
```text
## Sub images from given `ImageAnnotation`

In some situation we want to operate on a specific part of the whole image that is defined by 
some `ImageAnnotation`. E.g. when building table recognition system, first we detect the table region, then we
crop
the table and perform cell/row/column detection on the sub image.

We therefore need a simple way to convert an `ImageAnnotation` into a corresponding `Image` object.


```python
image.image_ann_to_image(annotation_id='844631a5-5ddb-3ba8-b81a-bb9f05604d58')
```

### Example usage
```python
image.image_ann_to_image(annotation_id='844631a5-5ddb-3ba8-b81a-bb9f05604d58')
```

### Example usage
```text
`image_ann_to_image` adds an `Image` object to the `ImageAnnotation` with `image_id` being the same as the 
`annotation_id`. 


```python
ann = image.get_annotation(annotation_ids='844631a5-5ddb-3ba8-b81a-bb9f05604d58')[0]
ann.image
```

### Example usage
```python
ann = image.get_annotation(annotation_ids='844631a5-5ddb-3ba8-b81a-bb9f05604d58')[0]
ann.image
```

### Example usage
```text
??? Info "Output"

    Image(file_name='sample_2.png', 
          location='/home/janis/Public/notebooks/pics/samples/sample_2/sample_2.png', 
          document_id='844631a5-5ddb-3ba8-b81a-bb9f05604d58', 
          _image_id='844631a5-5ddb-3ba8-b81a-bb9f05604d58', 
          embeddings={'844631a5-5ddb-3ba8-b81a-bb9f05604d58': 
              BoundingBox(absolute_coords=True, ulx=0, uly=0, lrx=131, lry=15, height=15, width=131), 
                      '2aa98b36-196e-3cdf-af09-8f2d885d5f88': 
              BoundingBox(absolute_coords=True, ulx=146, uly=1481, lrx=277, lry=1496, height=15, width=131)},
          annotations=[])



There are also embedding bounding boxes that describe the relative position to the full image. 


```python
ann.image.get_embedding(image.image_id)
```

### Example usage
```python
ann.image.get_embedding(image.image_id)
```

### Example usage
```text
??? Info "Output"

    BoundingBox(absolute_coords=True, ulx=146, uly=1481, lrx=277, lry=1496, height=15, width=131)



There is a second bounding box that describes the position of the image in terms of its own coordinates. 


```python
ann.image.get_embedding(ann.annotation_id)
```

### Example usage
```python
ann.image.get_embedding(ann.annotation_id)
```

### Example usage
```text
??? Info "Output"

    BoundingBox(absolute_coords=True, ulx=0, uly=0, lrx=131, lry=15, height=15, width=131)


Setting `crop_image=True` will even store the pixel values of the sub image.


```python
image.image_ann_to_image(annotation_id='844631a5-5ddb-3ba8-b81a-bb9f05604d58',crop_image=True)
```

### Example usage
```python
image.image_ann_to_image(annotation_id='844631a5-5ddb-3ba8-b81a-bb9f05604d58',crop_image=True)
```

### Example usage
```text
```python
plt.figure(figsize = (25,17))
plt.axis('off')
plt.imshow(ann.image.image)
```

### Example usage
```python
plt.figure(figsize = (25,17))
plt.axis('off')
plt.imshow(ann.image.image)
```

### Example usage
```text
![png](./_imgs/data_structure_03.png)
```

---

# docs/tutorials/Datasets.md - Datasets

<p align="center"> <img 
src="https://github.com/deepdoctection/deepdoctection/raw/master/docs/tutorials/_imgs/dd_logo.png" alt="Deep 
Doctection Logo" width="60%"> <h3 align="center"> </h3> </p>.

## Code Examples

### Example usage
```python
my_custom_dataset = CustomDataset(name="some name",
                                                                  dataset_type=dd.DatasetType.object_detection
,
                                                                  location = "custom_dataset",
                                                                  ...)
my_custom_dataset.dataflow.get_workdir()
```

### Example usage
```text
will point to the sub folder `custom_dataset`. Moreover, we have to map every dataset to a `dataset_type`. 
This must
be one of the members of the `DatasetType`. The most crucial part is to build a a sub class of 
the `DataFlowBaseBuilder`.

## Custom `DataflowBuilder`

```python

class CustomDataflow(DataFlowBaseBuilder):

        def build(**kwargs):

                path =  self.get_workdir() / annotation_file.jsonl
                df = SerializerJsonLines.load(path)                      # will stream every .json linewise
                ...
                return df
```

### Custom `DataflowBuilder`
```python
class CustomDataflow(DataFlowBaseBuilder):

        def build(**kwargs):

                path =  self.get_workdir() / annotation_file.jsonl
                df = SerializerJsonLines.load(path)                      # will stream every .json linewise
                ...
                return df
```

### Example usage
```text
Note, that `build` must yield an [`Image`][deepdoctection.datapoint.image.Image]. It is therefore crucial to 
map the
data structure of the annotation file into an `Image`. Fortunately, there are already some mappings made 
available.
For COCO-style annotation, we can simply do:

```python

class CustomDataflow(DataFlowBaseBuilder):

        def build(**kwargs):

                path =  self.get_workdir() / annotation_file.json
                df = SerializerCoco.load(path) # (1) 
                 
                coco_mapper = coco_to_image(self.categories.get_categories(init=True), # (2)
                                                                         load_image= False)
                df = MapData(df, coco_mapper)
                return df
```

### For COCO-style annotation, we can simply do
```python
class CustomDataflow(DataFlowBaseBuilder):

        def build(**kwargs):

                path =  self.get_workdir() / annotation_file.json
                df = SerializerCoco.load(path) # (1) 
                 
                coco_mapper = coco_to_image(self.categories.get_categories(init=True), # (2)
                                                                         load_image= False)
                df = MapData(df, coco_mapper)
                return df
```

### Example usage
```text
1. This will load a coco style annotation file and combine image and their annotations.
2. A callable with some configuration (mapping category ids and category names/ skipping the image loading)


This dataflow has a very basic behaviour. We can add some more functionalities, e.g. filtering some 
categories.


```python

class CustomDataflow(DataFlowBaseBuilder):

        def build(**kwargs):
                ...
                df = MapData(df, coco_mapper)

                if self.categories.is_filtered():
                        df = MapData(df, filter_cat(self.categories.get_categories(as_dict=False, 
filtered=True),
                                                                                self.categories.get_categories
(as_dict=False, filtered=False),
                                                 ),
                        )
                ...
                return df
```

### Example usage
```python
class CustomDataflow(DataFlowBaseBuilder):

        def build(**kwargs):
                ...
                df = MapData(df, coco_mapper)

                if self.categories.is_filtered():
                        df = MapData(df, filter_cat(self.categories.get_categories(as_dict=False, 
filtered=True),
                                                                                self.categories.get_categories
(as_dict=False, filtered=False),
                                                 ),
                        )
                ...
                return df
```

### Example usage
```text
Having added this to our dataflow, we can now customize our categories:

```python

my_custom_dataset = CustomDataset("train_data",
                                                                   DatasetType.object_detection,
                                                                   "custom_dataset_location",
                                                                   [LayoutType.TEXT, LayoutType.TITLE, 
LayoutType.TABLE],
                                                                   CustomDataflow("custom_dataset_location",{"
train": "annotation_file.json"}))

my_custom_dataset.dataflow.categories.filter_categories(categories="table")

df = my_custom_dataset.dataflow.build()
df.reset_state()
for dp in df:
        ... # (1)
```

### Having added this to our dataflow, we can now customize our categories
```python
my_custom_dataset = CustomDataset("train_data",
                                                                   DatasetType.object_detection,
                                                                   "custom_dataset_location",
                                                                   [LayoutType.TEXT, LayoutType.TITLE, 
LayoutType.TABLE],
                                                                   CustomDataflow("custom_dataset_location",{"
train": "annotation_file.json"}))

my_custom_dataset.dataflow.categories.filter_categories(categories="table")

df = my_custom_dataset.dataflow.build()
df.reset_state()
for dp in df:
        ... # (1)
```

### for dp in df
```text
1. dp has now only has 'table' labels in our samples. 'text' and 'title' has been filtered out.

!!! info "How to build datasets the long way"

    We assume that in *custom_dataset* the data set was physically placed in the following the structure:
```

### Example usage
```python
dataset = dd.get_dataset("dataset_name")
   df = dataset.dataflow.build(**kwargs_config)

   for sample in df:
       print(sample)
```

### for sample in df
```text
We can print a list of all built-in datsets:


```python
dd.print_dataset_infos(add_license=False, add_info=False)
```

### We can print a list of all built-in datsets
```python
dd.print_dataset_infos(add_license=False, add_info=False)
```

### Example usage
```text
??? info "Output"

    ╒════════════════════╕
    │ dataset            │
    ╞════════════════════╡
    │ doclaynet          │
    ├────────────────────┤
    │ doclaynet-seq      │
    ├────────────────────┤
    │ fintabnet          │
    ├────────────────────┤
    │ funsd              │
    ├────────────────────┤
    │ iiitar13k          │
    ├────────────────────┤
    │ testlayout         │
    ├────────────────────┤
    │ publaynet          │
    ├────────────────────┤
    │ pubtables1m_det    │
    ├────────────────────┤
    │ pubtables1m_struct │
    ├────────────────────┤
    │ pubtabnet          │
    ├────────────────────┤
    │ rvl-cdip           │
    ├────────────────────┤
    │ xfund              │
    ╘════════════════════╛


With `get_dataset("doclaynet")` we can create an instance of a built-in dataset.


```python
doclaynet = dd.get_dataset("doclaynet")

print(doclaynet.dataset_info.description)
```

### Example usage
```python
doclaynet = dd.get_dataset("doclaynet")

print(doclaynet.dataset_info.description)
```

### Example usage
```text
??? info "Output"

    DocLayNet is a human-annotated document layout segmentation dataset containing 80863 pages from a broad 
variety of 
    document sources. DocLayNet provides page-by-page layout segmentation ground-truth using bounding-boxes 
for 11 
    distinct class labels on 80863 unique pages from 6 document categories. It provides several unique 
features compared 
    to related work such as PubLayNet or DocBank: Human Annotation: DocLayNet is hand-annotated by 
well-trained experts, 
    providing a gold-standard in layout segmentation through human recognition and interpretation of each page
layout 
    Large layout variability: DocLayNet includes diverse and complex layouts from a large variety of public 
sources in 
    Finance, Science, Patents, Tenders, Law texts and Manuals Detailed label set: DocLayNet defines 11 class 
labels to 
    distinguish layout features in high detail. 
    Redundant annotations: A fraction of the pages in DocLayNet are double- or triple-annotated, allowing to 
estimate 
    annotation uncertainty and an upper-bound of achievable prediction accuracy with ML models Pre-defined 
train- test- 
    and validation-sets: DocLayNet provides fixed sets for each to ensure proportional representation of the 
    class-labels and avoid leakage of unique layout styles across the sets.


In **deep**doctection there is no function that automatically downloads a dataset from its remote storage.  


To install the dataset, we go to the url below and download the zip-file. We will then have to unzip and place
the 
dataset in our local **.cache/deepdoctection/dataset** directory.  


```python
doclaynet.dataset_info.url
```

### Example usage
```python
doclaynet.dataset_info.url
```

### Example usage
```text
??? info "Output"

    'https://codait-cos-dax.s3.us.cloud-object-storage.appdomain.cloud/dax-doclaynet/1.0.0/DocLayNet_core.zip'

```python
print(dd.datasets.instances.doclaynet.__doc__)
```

### Example usage
```python
print(dd.datasets.instances.doclaynet.__doc__)
```

### Example usage
```text
??? info  "Output"  

    Module for DocLayNet dataset. Place the dataset as follows
    
        DocLayNet_core
        ├── COCO
        │ ├── test.json
        │ ├── val.json
        ├── PNG
        │ ├── 0a0d43e301facee9e99cc33b9b16e732dd207135f4027e75f6aea2bf117535a2.png
    
To produce samples, we need to instantiate a dataflow. Most built-in datasets have a split and can stream
datapoint samples from the specified split.


```python
df = doclaynet.dataflow.build(split="train") # (1)
df.reset_state() 

df_iter = iter(df) 

datapoint = next(df_iter)
datapoint_dict = datapoint.as_dict() 
datapoint_dict["file_name"],datapoint_dict["_image_id"], datapoint_dict["annotations"][0]
```

### Example usage
```python
df = doclaynet.dataflow.build(split="train") # (1)
df.reset_state() 

df_iter = iter(df) 

datapoint = next(df_iter)
datapoint_dict = datapoint.as_dict() 
datapoint_dict["file_name"],datapoint_dict["_image_id"], datapoint_dict["annotations"][0]
```

### Example usage
```text
1. Instantiate the dataflow

??? info "Output"

        ('c6effb847ae7e4a80431696984fa90c98bb08c266481b9a03842422459c43bdd.png',
     '4385125b-dd1e-3025-880f-3311517cc8d5',
     {'active': True,
      'external_id': 0,
      '_annotation_id': '4385125b-dd1e-3025-880f-3311517cc8d5',
      'service_id': None,
      'model_id': None,
      'session_id': None,
      'category_name': LayoutType.PAGE_HEADER,
      '_category_name': LayoutType.PAGE_HEADER,
      'category_id': 6,
      'score': None,
      'sub_categories': {DatasetType.PUBLAYNET: {'active': True,
        'external_id': None,
        '_annotation_id': '4f10073e-a211-3336-8347-8b34e8a2e59a',
        'service_id': None,
        'model_id': None,
        'session_id': None,
        'category_name': LayoutType.TITLE,
        '_category_name': LayoutType.TITLE,
        'category_id': 11,
        'score': None,
        'sub_categories': {},
        'relationships': {}}},
      'relationships': {},
      'bounding_box': {'absolute_coords': True,
       'ulx': 72,
       'uly': 55,
       'lrx': 444,
       'lry': 75},
      'image': None})

!!! info "Note on the `build` method"

    Depending on the dataset, different configurations of the `build` method can yield different 
representations of 
    datapoints. For example, the underlying image is not loaded by default. Passing the parameter 
`load_image=True` will 
    load the image numpy array.

!!! note "Standard image format in **deep**doctection is 'BGR'"

    Under the hood **deep*doctection uses OpenCV or Pillow for loading images, depending what library is 
installed and
    what is configured. If you have your own image loader and want to pass a numpy array to an 
**deep**doctection 
    object, make sure that you pass the numpy array in `BGR` format.


```python
df = doclaynet.dataflow.build(split="train",load_image=True)
df.reset_state()

df_iter = iter(df)
datapoint = next(df_iter)

plt.figure(figsize = (15,12))
plt.axis('off')
plt.imshow(datapoint.image[:,:,::-1])
```

### Example usage
```python
df = doclaynet.dataflow.build(split="train",load_image=True)
df.reset_state()

df_iter = iter(df)
datapoint = next(df_iter)

plt.figure(figsize = (15,12))
plt.axis('off')
plt.imshow(datapoint.image[:,:,::-1])
```

### Example usage
```text
![png](./_imgs/datasets_01.png)
```

---

# docs/tutorials/Evaluation.md - Evaluation

<p align="center"> <img 
src="https://github.com/deepdoctection/deepdoctection/raw/master/docs/tutorials/_imgs/dd_logo.png" alt="Deep 
Doctection Logo" width="60%"> <h3 align="center"> </h3> </p>.

## Code Examples

### Example usage
```python
config_yaml_path = dd.ModelCatalog.get_full_path_configs("layout/d2_model_0829999_layout_inf_only.pt")
weights_path = dd.ModelCatalog.get_full_path_weights("layout/d2_model_0829999_layout_inf_only.pt")
categories = dd.ModelCatalog.get_profile("layout/d2_model_0829999_layout_inf_only.pt").categories
layout_detector = dd.D2FrcnnDetector(config_yaml_path,weights_path,categories)
layout_service = dd.ImageLayoutService(layout_detector)
```

### Example usage
```text
Next, we need a metric.


```python
coco_metric = dd.get_metric("coco")
```

### Example usage
```python
coco_metric = dd.get_metric("coco")
```

### Example usage
```text
Now for the dataset. Doclaynet has several other labels but there is a mapping that collapses all Doclaynet 
labels into
Publaynet labels. 


```python
doclaynet.dataflow.categories.get_categories()
```

### Example usage
```python
doclaynet.dataflow.categories.get_categories()
```

### Example usage
```text
??? info "Output"

    <pre>
    {1: LayoutType.CAPTION, 
     2: LayoutType.FOOTNOTE, 
     3: LayoutType.FORMULA, 
     4: LayoutType.LIST, 
     5: LayoutType.PAGE_FOOTER, 
     6: LayoutType.PAGE_HEADER, 
     7: LayoutType.FIGURE, 
     8: LayoutType.SECTION_HEADER, 
     9: LayoutType.TABLE, 
     10: LayoutType.TEXT, 
     11: LayoutType.TITLE}
    </pre>


```python
doclaynet.dataflow.categories._init_sub_categories
```

### Example usage
```python
doclaynet.dataflow.categories._init_sub_categories
```

### Example usage
```text
??? info "Output"

    <pre>
    {LayoutType.CAPTION: {DatasetType.PUBLAYNET: [LayoutType.TEXT]},
    LayoutType.FOOTNOTE: {DatasetType.PUBLAYNET: [LayoutType.TEXT]},
    LayoutType.FORMULA: {DatasetType.PUBLAYNET: [LayoutType.TEXT]},
    LayoutType.LIST: {DatasetType.PUBLAYNET: [LayoutType.LIST]},
    LayoutType.PAGE_FOOTER: {DatasetType.PUBLAYNET: [LayoutType.TEXT]},
    LayoutType.PAGE_HEADER: {DatasetType.PUBLAYNET: [LayoutType.TITLE]},
    LayoutType.FIGURE: {DatasetType.PUBLAYNET: [LayoutType.FIGURE]},
    LayoutType.SECTION_HEADER: {DatasetType.PUBLAYNET: [LayoutType.TITLE]},
    LayoutType.TABLE: {DatasetType.PUBLAYNET: [LayoutType.TABLE]},
    LayoutType.TEXT: {DatasetType.PUBLAYNET: [LayoutType.TEXT]},
    LayoutType.TITLE: {DatasetType.PUBLAYNET: [LayoutType.TITLE]}}
    </pre>


The sub category `DatasetType.PUBLAYNET` provides the mapping into Publaynet labels.


```python
cat_to_sub_cat = doclaynet.dataflow.categories.get_sub_categories()
cat_to_sub_cat = {key:val[0] for key, val in cat_to_sub_cat.items()}
doclaynet.dataflow.categories.set_cat_to_sub_cat(cat_to_sub_cat)
```

### Example usage
```python
cat_to_sub_cat = doclaynet.dataflow.categories.get_sub_categories()
cat_to_sub_cat = {key:val[0] for key, val in cat_to_sub_cat.items()}
doclaynet.dataflow.categories.set_cat_to_sub_cat(cat_to_sub_cat)
```

### Example usage
```text
Now, that dataset, pipeline component and metric have been setup, we can build the evaluator.


```python
evaluator = dd.Evaluator(dataset=doclaynet,
                                                 component_or_pipeline=layout_service, 
                                                 metric=coco_metric)
```

### Example usage
```python
evaluator = dd.Evaluator(dataset=doclaynet,
                                                 component_or_pipeline=layout_service, 
                                                 metric=coco_metric)
```

### Example usage
```text
We start evaluation using the `run` method. `max_datapoints` limits the number of samples to at most 100 
samples. The 
`val` split is used by default.


```python
evaluator = dd.Evaluator(doclaynet,layout_service, coco_metric)
output= evaluator.run(max_datapoints=100)
```

### Example usage
```python
evaluator = dd.Evaluator(doclaynet,layout_service, coco_metric)
output= evaluator.run(max_datapoints=100)
```

### Example usage
```text
??? info "Output"

    creating index...
    index created!
    creating index...
    index created!
    Running per image evaluation...
    Evaluate annotation type *bbox*
    DONE (t=0.12s).
    Accumulating evaluation results...
    DONE (t=0.03s).
     Average Precision  (AP) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ] = 0.147
     Average Precision  (AP) @[ IoU=0.50      | area=   all | maxDets=100 ] = 0.195
     Average Precision  (AP) @[ IoU=0.75      | area=   all | maxDets=100 ] = 0.144
     Average Precision  (AP) @[ IoU=0.50:0.95 | area= small | maxDets=100 ] = 0.010
     Average Precision  (AP) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ] = 0.022
     Average Precision  (AP) @[ IoU=0.50:0.95 | area= large | maxDets=100 ] = 0.200
     Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=  1 ] = 0.100
     Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets= 10 ] = 0.171
     Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ] = 0.174
     Average Recall     (AR) @[ IoU=0.50:0.95 | area= small | maxDets=100 ] = 0.009
     Average Recall     (AR) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ] = 0.031
     Average Recall     (AR) @[ IoU=0.50:0.95 | area= large | maxDets=100 ] = 0.231


The result shows that Doclaynet has a very different layout compared to Publaynet where the model has been 
trained on. 
To get a feeling, results on the Publaynet test split are in the range of 0.9+ !

## Example: Evaluation of Table Recognition

In this example we will be showing how to evaluate a table recognition pipeline. We will be comparing
HTML representations from the Pubtabnet evaluation set and will be using the TEDS metric as described in 
[Zhong et. all](https://arxiv.org/abs/1911.10683). We will be evaluating the HTML skeleton only and discard 
text.

```python
import os
from typing import List

import deepdoctection as dd


def get_table_recognizer():
    cfg = dd.set_config_by_yaml("~/.cache/deepdoctection/configs/dd/conf_dd_one.yaml")
    pipe_component_list: List[dd.PipelineComponent] = []

    crop = dd.ImageCroppingService(category_names=dd.LayoutType.TABLE)
    pipe_component_list.append(crop)

    cell_config_path = dd.ModelCatalog.get_full_path_configs("cell/d2_model_1849999_cell_inf_only.ts")
    cell_weights_path = 
dd.ModelDownloadManager.maybe_download_weights_and_configs("cell/d2_model_1849999_cell_inf_only.ts")
    categories_cell = dd.ModelCatalog.get_profile("cell/d2_model_1849999_cell_inf_only.ts").categories
    d_cell = dd.D2FrcnnTracingDetector(cell_config_path, cell_weights_path, categories_cell)
        
    item_config_path = dd.ModelCatalog.get_full_path_configs("item/d2_model_1639999_item_inf_only.ts")
    item_weights_path = 
dd.ModelDownloadManager.maybe_download_weights_and_configs("item/d2_model_1639999_item_inf_only.ts")
    categories_item = dd.ModelCatalog.get_profile("item/d2_model_1639999_item_inf_only.ts").categories
    d_item = dd.D2FrcnnTracingDetector(item_config_path, item_weights_path, categories_item)

        cell_detect_result_generator = 
dd.DetectResultGenerator(categories_name_as_key=d_cell.categories.get_categories
        (as_dict=True, name_as_key=True))
    cell = dd.SubImageLayoutService(sub_image_detector=d_cell, 
                                                                        sub_image_names=dd.LayoutType.TABLE,
                                                                        service_ids=None,
                                                                        detect_result_generator=cell_detect_re
sult_generator)
    pipe_component_list.append(cell)
        
        item_detect_result_generator = 
dd.DetectResultGenerator(categories_name_as_key=d_item.categories.get_categories
        (as_dict=True, name_as_key=True))
    item = dd.SubImageLayoutService(sub_image_detector=d_item, 
                                                                        sub_image_names=dd.LayoutType.TABLE, 
                                                                        service_ids=None,
                                                                        detect_result_generator=item_detect_re
sult_generator)
    pipe_component_list.append(item)

    table_segmentation = dd.TableSegmentationService(
        cfg.SEGMENTATION.ASSIGNMENT_RULE,
        cfg.SEGMENTATION.THRESHOLD_ROWS,
        cfg.SEGMENTATION.THRESHOLD_COLS,
        cfg.SEGMENTATION.FULL_TABLE_TILING,
        cfg.SEGMENTATION.REMOVE_IOU_THRESHOLD_ROWS,
        cfg.SEGMENTATION.REMOVE_IOU_THRESHOLD_COLS,
        dd.LayoutType.TABLE,
        [dd.CellType.HEADER,dd.CellType.BODY,dd.LayoutType.CELL],
        [dd.LayoutType.ROW,dd.LayoutType.COLUMN],
        [dd.CellType.ROW_NUMBER, dd.CellType.COLUMN_NUMBER],
        cfg.SEGMENTATION.STRETCH_RULE,
    )
        
    pipe_component_list.append(table_segmentation)
    table_segmentation_refinement = dd.TableSegmentationRefinementService([LayoutType.TABLE],
                                                                          [LayoutType.CELL,
                                                                           CellType.COLUMN_HEADER,
                                                                           CellType.PROJECTED_ROW_HEADER,
                                                                           CellType.SPANNING,
                                                                           CellType.ROW_HEADER,
                                                                          ])
    pipe_component_list.append(table_segmentation_refinement)
    return dd.DoctectionPipe(pipeline_component_list=pipe_component_list)

        
pubtabnet = dd.Pubtabnet()
teds = dd.metric_registry.get("teds")
teds.structure_only = True
pipe = get_table_recognizer()
evaluator = dd.Evaluator(pubtabnet, pipe, teds)
out = evaluator.run(max_datapoints=1000, 
                                        split="val", dd_pipe_like=True)
print(out)
```

### In this example we will be showing how to evaluate a table recognition pipeline. We will be comparing
```python
import os
from typing import List

import deepdoctection as dd


def get_table_recognizer():
    cfg = dd.set_config_by_yaml("~/.cache/deepdoctection/configs/dd/conf_dd_one.yaml")
    pipe_component_list: List[dd.PipelineComponent] = []

    crop = dd.ImageCroppingService(category_names=dd.LayoutType.TABLE)
    pipe_component_list.append(crop)

    cell_config_path = dd.ModelCatalog.get_full_path_configs("cell/d2_model_1849999_cell_inf_only.ts")
    cell_weights_path = 
dd.ModelDownloadManager.maybe_download_weights_and_configs("cell/d2_model_1849999_cell_inf_only.ts")
    categories_cell = dd.ModelCatalog.get_profile("cell/d2_model_1849999_cell_inf_only.ts").categories
    d_cell = dd.D2FrcnnTracingDetector(cell_config_path, cell_weights_path, categories_cell)
        
    item_config_path = dd.ModelCatalog.get_full_path_configs("item/d2_model_1639999_item_inf_only.ts")
    item_weights_path = 
dd.ModelDownloadManager.maybe_download_weights_and_configs("item/d2_model_1639999_item_inf_only.ts")
    categories_item = dd.ModelCatalog.get_profile("item/d2_model_1639999_item_inf_only.ts").categories
    d_item = dd.D2FrcnnTracingDetector(item_config_path, item_weights_path, categories_item)

        cell_detect_result_generator = 
dd.DetectResultGenerator(categories_name_as_key=d_cell.categories.get_categories
        (as_dict=True, name_as_key=True))
    cell = dd.SubImageLayoutService(sub_image_detector=d_cell, 
                                                                        sub_image_names=dd.LayoutType.TABLE,
                                                                        service_ids=None,
                                                                        detect_result_generator=cell_detect_re
sult_generator)
    pipe_component_list.append(cell)
        
        item_detect_result_generator = 
dd.DetectResultGenerator(categories_name_as_key=d_item.categories.get_categories
        (as_dict=True, name_as_key=True))
    item = dd.SubImageLayoutService(sub_image_detector=d_item, 
                                                                        sub_image_names=dd.LayoutType.TABLE, 
                                                                        service_ids=None,
                                                                        detect_result_generator=item_detect_re
sult_generator)
    pipe_component_list.append(item)

    table_segmentation = dd.TableSegmentationService(
        cfg.SEGMENTATION.ASSIGNMENT_RULE,
        cfg.SEGMENTATION.THRESHOLD_ROWS,
        cfg.SEGMENTATION.THRESHOLD_COLS,
        cfg.SEGMENTATION.FULL_TABLE_TILING,
        cfg.SEGMENTATION.REMOVE_IOU_THRESHOLD_ROWS,
        cfg.SEGMENTATION.REMOVE_IOU_THRESHOLD_COLS,
        dd.LayoutType.TABLE,
        [dd.CellType.HEADER,dd.CellType.BODY,dd.LayoutType.CELL],
        [dd.LayoutType.ROW,dd.LayoutType.COLUMN],
        [dd.CellType.ROW_NUMBER, dd.CellType.COLUMN_NUMBER],
        cfg.SEGMENTATION.STRETCH_RULE,
    )
        
    pipe_component_list.append(table_segmentation)
    table_segmentation_refinement = dd.TableSegmentationRefinementService([LayoutType.TABLE],
                                                                          [LayoutType.CELL,
                                                                           CellType.COLUMN_HEADER,
                                                                           CellType.PROJECTED_ROW_HEADER,
                                                                           CellType.SPANNING,
                                                                           CellType.ROW_HEADER,
                                                                          ])
    pipe_component_list.append(table_segmentation_refinement)
    return dd.DoctectionPipe(pipeline_component_list=pipe_component_list)

        
pubtabnet = dd.Pubtabnet()
teds = dd.metric_registry.get("teds")
teds.structure_only = True
pipe = get_table_recognizer()
evaluator = dd.Evaluator(pubtabnet, pipe, teds)
out = evaluator.run(max_datapoints=1000, 
                                        split="val", dd_pipe_like=True)
print(out)
```

### Example usage
```text
??? info "Output"

    [{'teds_score': 0.810958120214249, 'num_samples': 441}]
```

---

# docs/tutorials/LayoutLM_For_Custom_Token_Class.md - Project: LayoutLM for financial report NER

The goal is to fine-tune the LayoutLM model for token classification on a custom dataset. The goal is to give 
a realistic setting and to document the findings.

## Code Examples

### Example usage
```python
import deepdoctection as dd
from collections import defaultdict
import wandb
from transformers import LayoutLMTokenizerFast

@dd.object_types_registry.register("ner_first_page")
class FundsFirstPage(dd.ObjectTypes):

    REPORT_DATE = "report_date"
    UMBRELLA = "umbrella"
    REPORT_TYPE = "report_type"
    FUND_NAME = "fund_name"

dd.update_all_types_dict()
```

### Example usage
```text
## Step 2: Downloading the dataset

Download the dataset and save it to 


```python
dd.get_dataset_dir_path() / "FRFPE"
```

### Example usage
```python
dd.get_dataset_dir_path() / "FRFPE"
```

### Example usage
```text
## Step 3: Visualization and display of ground truth


```python
path = dd.get_dataset_dir_path() / "FRFPE" / "40952248ba13ae8bfdd39f56af22f7d9_0.json"

page = dd.Page.from_file(path)
page.image =  dd.load_image_from_file(path.parents[0]  / 
                                                                          "image" / 
page.file_name.replace("pdf","png"))

page.viz(interactive=True,
                 show_words=True)  # (1)
```

### Step 3: Visualization and display of ground truth
```python
path = dd.get_dataset_dir_path() / "FRFPE" / "40952248ba13ae8bfdd39f56af22f7d9_0.json"

page = dd.Page.from_file(path)
page.image =  dd.load_image_from_file(path.parents[0]  / 
                                                                          "image" / 
page.file_name.replace("pdf","png"))

page.viz(interactive=True,
                 show_words=True)  # (1)
```

### Example usage
```text
1. Close interactive window with 'q'


```python
for word in page.words:
    print(f"word: {word.characters}, category: {word.token_class}, bio: {word.tag}")
```

### Example usage
```python
for word in page.words:
    print(f"word: {word.characters}, category: {word.token_class}, bio: {word.tag}")
```

### for word in page.words
```text
??? info "Output"

    word: GFG, category: umbrella, bio: B
    word: Funds, category: umbrella, bio: I
    word: Société, category: other, bio: O
    word: d, category: other, bio: O
    word: ', category: other, bio: O
    word: Investissement, category: other, bio: O
    word: à, category: other, bio: O
    word: Capital, category: other, bio: O
    word: Variable, category: other, bio: O
    word: incorporated, category: other, bio: O
    word: in, category: other, bio: O
    word: Luxembourg, category: other, bio: O
    word: Luxembourg, category: other, bio: O
    word: R, category: other, bio: O
    word: ., category: other, bio: O
    word: C, category: other, bio: O
    word: ., category: other, bio: O
    word: S, category: other, bio: O
    word: ., category: other, bio: O
    word: B60668, category: other, bio: O
    word: Unaudited, category: other, bio: O
    word: Semi-Annual, category: report_type, bio: B
    word: Report, category: report_type, bio: I
    word: as, category: other, bio: O
    word: at, category: other, bio: O
    word: 30.06.2021, category: report_date, bio: B


## Step 4: Defining Dataflow and Dataset

We define a dataflow and use the `CustomDataset` class.


```python
@dd.curry
def overwrite_location_and_load(dp, image_dir, load_image):
    image_file = image_dir / dp.file_name.replace("pdf","png")
    dp.location = image_file.as_posix()
    if load_image:
        dp.image = dd.load_image_from_file(image_file)
    return dp

class NerBuilder(dd.DataFlowBaseBuilder):

    def build(self, **kwargs) -> dd.DataFlow:
        load_image = kwargs.get("load_image", False)

        ann_files_dir = self.get_workdir()
        image_dir = self.get_workdir() / "image"

        df = dd.SerializerFiles.load(ann_files_dir,".json")   # (1) 
        df = dd.MapData(df, dd.Image.from_file)   # (2) 

        df = dd.MapData(df, overwrite_location_and_load(image_dir, load_image))

        if self.categories.is_filtered():
            df = dd.MapData(
                df,
                dd.filter_cat(
                    self.categories.get_categories(as_dict=False, 
                                                                                                   filtered=Tr
ue),
                    self.categories.get_categories(as_dict=False, 
                                                                                                   filtered=Fa
lse),
                ),
            )
        df = dd.MapData(df,
                         dd.re_assign_cat_ids(cat_to_sub_cat_mapping=
                         self.categories.get_sub_categories(
                                  categories=dd.LayoutType.WORD,
                                  sub_categories={dd.LayoutType.WORD: 
                                                                                                  dd.WordType.
TOKEN_CLASS},
                                  keys = False,
                                  values_as_dict=True,
                                  name_as_key=True)))

        return df
```

### Example usage
```python
@dd.curry
def overwrite_location_and_load(dp, image_dir, load_image):
    image_file = image_dir / dp.file_name.replace("pdf","png")
    dp.location = image_file.as_posix()
    if load_image:
        dp.image = dd.load_image_from_file(image_file)
    return dp

class NerBuilder(dd.DataFlowBaseBuilder):

    def build(self, **kwargs) -> dd.DataFlow:
        load_image = kwargs.get("load_image", False)

        ann_files_dir = self.get_workdir()
        image_dir = self.get_workdir() / "image"

        df = dd.SerializerFiles.load(ann_files_dir,".json")   # (1) 
        df = dd.MapData(df, dd.Image.from_file)   # (2) 

        df = dd.MapData(df, overwrite_location_and_load(image_dir, load_image))

        if self.categories.is_filtered():
            df = dd.MapData(
                df,
                dd.filter_cat(
                    self.categories.get_categories(as_dict=False, 
                                                                                                   filtered=Tr
ue),
                    self.categories.get_categories(as_dict=False, 
                                                                                                   filtered=Fa
lse),
                ),
            )
        df = dd.MapData(df,
                         dd.re_assign_cat_ids(cat_to_sub_cat_mapping=
                         self.categories.get_sub_categories(
                                  categories=dd.LayoutType.WORD,
                                  sub_categories={dd.LayoutType.WORD: 
                                                                                                  dd.WordType.
TOKEN_CLASS},
                                  keys = False,
                                  values_as_dict=True,
                                  name_as_key=True)))

        return df
```

### Example usage
```text
1. Get a stream of `.json` files
2. Load `.json` file


```python
ner = dd.CustomDataset(name = "FRFPE",
                 dataset_type=dd.DatasetType.TOKEN_CLASSIFICATION,
                 location="FRFPE",
                 init_categories=[dd.LayoutType.TEXT, 
                                                                  dd.LayoutType.TITLE, 
                                                                  dd.LayoutType.LIST, 
                                                                  dd.LayoutType.TABLE,
                                  dd.LayoutType.FIGURE, 
                                                                  dd.LayoutType.LINE, 
                                                                  dd.LayoutType.WORD],
                 init_sub_categories={dd.LayoutType.WORD: 
                                                                         {dd.WordType.TOKEN_CLASS: 
                                                                          [FundsFirstPage.REPORT_DATE,
                                                                           FundsFirstPage.REPORT_TYPE,
                                                                           FundsFirstPage.UMBRELLA,
                                                                           FundsFirstPage.FUND_NAME,
                                                                           dd.TokenClasses.OTHER],
                                      dd.WordType.TAG: []}},
                 dataflow_builder=NerBuilder)
```

### Example usage
```python
ner = dd.CustomDataset(name = "FRFPE",
                 dataset_type=dd.DatasetType.TOKEN_CLASSIFICATION,
                 location="FRFPE",
                 init_categories=[dd.LayoutType.TEXT, 
                                                                  dd.LayoutType.TITLE, 
                                                                  dd.LayoutType.LIST, 
                                                                  dd.LayoutType.TABLE,
                                  dd.LayoutType.FIGURE, 
                                                                  dd.LayoutType.LINE, 
                                                                  dd.LayoutType.WORD],
                 init_sub_categories={dd.LayoutType.WORD: 
                                                                         {dd.WordType.TOKEN_CLASS: 
                                                                          [FundsFirstPage.REPORT_DATE,
                                                                           FundsFirstPage.REPORT_TYPE,
                                                                           FundsFirstPage.UMBRELLA,
                                                                           FundsFirstPage.FUND_NAME,
                                                                           dd.TokenClasses.OTHER],
                                      dd.WordType.TAG: []}},
                 dataflow_builder=NerBuilder)
```

### Example usage
```text
## Step 5: Defining a split and saving the split distribution as W&B artifact 

- The ground truth contains some layout sections `ImageAnnotation` that we need to explicitly filter out.
- We define a split with ~90% train, ~5% validation and ~5% test samples.
- To reproduce the split later we save the split as a W&B artifact.


```python
ner.dataflow.categories.filter_categories(categories=dd.LayoutType.WORD)

merge = dd.MergeDataset(ner)
merge.buffer_datasets()
merge.split_datasets(ratio=0.1)
```

### Example usage
```python
ner.dataflow.categories.filter_categories(categories=dd.LayoutType.WORD)

merge = dd.MergeDataset(ner)
merge.buffer_datasets()
merge.split_datasets(ratio=0.1)
```

### Example usage
```text
!!! info "Output"

     ___________________ Number of datapoints per split ___________________
                   {'test': 15, 'train': 327, 'val': 15}



```python
out = merge.get_ids_by_split()

table_rows=[]
for split, split_list in out.items():
    for ann_id in split_list:
        table_rows.append([split,ann_id])
table = wandb.Table(columns=["split","annotation_id"], 
                                        data=table_rows)

wandb.init(project="FRFPE_layoutlmv1")

artifact = wandb.Artifact(merge.dataset_info.name, type='dataset')
artifact.add(table, "split")

wandb.log_artifact(artifact)
wandb.finish()
```

### Example usage
```python
out = merge.get_ids_by_split()

table_rows=[]
for split, split_list in out.items():
    for ann_id in split_list:
        table_rows.append([split,ann_id])
table = wandb.Table(columns=["split","annotation_id"], 
                                        data=table_rows)

wandb.init(project="FRFPE_layoutlmv1")

artifact = wandb.Artifact(merge.dataset_info.name, type='dataset')
artifact.add(table, "split")

wandb.log_artifact(artifact)
wandb.finish()
```

### Example usage
```text
## Step 6: LayoutLM fine-tuning

```python
path_config_json = dd.ModelCatalog.get_full_path_configs("microsoft/layoutlm-base-uncased/pytorch_model.bin")
path_weights = dd.ModelCatalog.get_full_path_weights("microsoft/layoutlm-base-uncased/pytorch_model.bin")

metric = dd.get_metric("f1")
metric.set_categories(sub_category_names={"word": ["token_class"]})
```

### Step 6: LayoutLM fine-tuning
```python
path_config_json = dd.ModelCatalog.get_full_path_configs("microsoft/layoutlm-base-uncased/pytorch_model.bin")
path_weights = dd.ModelCatalog.get_full_path_weights("microsoft/layoutlm-base-uncased/pytorch_model.bin")

metric = dd.get_metric("f1")
metric.set_categories(sub_category_names={"word": ["token_class"]})
```

### Example usage
```text
!!! info

    Remember id to label mapping:
```

### Example usage
```python
dd.train_hf_layoutlm(path_config_json,
                     merge,
                     path_weights,
                     config_overwrite=["max_steps=2000",
                                       "per_device_train_batch_size=8",
                                       "eval_steps=100",
                                       "save_steps=400",
                                       "use_wandb=True",
                                       "wandb_project=FRFPE_layoutlmv1",
                                      ],
                     log_dir="/path/to/dir/Experiments/FRFPE/layoutlmv1",
                     dataset_val=merge,
                     metric=metric,
                     use_token_tag=False,
                     pipeline_component_name="LMTokenClassifierService")
```

### Example usage
```text
## Step 7: Evaluation with confusion matrix



```python
categories = ner.dataflow.categories.get_sub_categories(categories="word",
                                                        sub_categories={"word": ["token_class"]},
                                                        keys=False)["word"]["token_class"]

path_config_json = "/path/to/dir/Experiments/FRFPE/layoutlmv1/checkpoint-1600/config.json"
path_weights = "/path/to/dir/Experiments/FRFPE/layoutlmv1/checkpoint-1600/model.safetensors"

layoutlm_classifier = dd.HFLayoutLmTokenClassifier(path_config_json,
                                                   path_weights,
                                                   categories=categories)

tokenizer_fast = LayoutLMTokenizerFast.from_pretrained("microsoft/layoutlm-base-uncased")
pipe_component = dd.LMTokenClassifierService(tokenizer_fast,
                                             layoutlm_classifier,
                                             use_other_as_default_category=True)
metric = dd.get_metric("confusion")
metric.set_categories(sub_category_names={"word": ["token_class"]})
evaluator = dd.Evaluator(merge, pipe_component, metric)
_ = evaluator.run(split="val")
```

### Step 7: Evaluation with confusion matrix
```python
categories = ner.dataflow.categories.get_sub_categories(categories="word",
                                                        sub_categories={"word": ["token_class"]},
                                                        keys=False)["word"]["token_class"]

path_config_json = "/path/to/dir/Experiments/FRFPE/layoutlmv1/checkpoint-1600/config.json"
path_weights = "/path/to/dir/Experiments/FRFPE/layoutlmv1/checkpoint-1600/model.safetensors"

layoutlm_classifier = dd.HFLayoutLmTokenClassifier(path_config_json,
                                                   path_weights,
                                                   categories=categories)

tokenizer_fast = LayoutLMTokenizerFast.from_pretrained("microsoft/layoutlm-base-uncased")
pipe_component = dd.LMTokenClassifierService(tokenizer_fast,
                                             layoutlm_classifier,
                                             use_other_as_default_category=True)
metric = dd.get_metric("confusion")
metric.set_categories(sub_category_names={"word": ["token_class"]})
evaluator = dd.Evaluator(merge, pipe_component, metric)
_ = evaluator.run(split="val")
```

### Example usage
```text
??? info "Output"

    Confusion matrix: 

    |    predictions ->  |   1 |   2 |   3 |   4 |   5 |
    |     ground truth | |     |     |     |     |     |
    |                  v |     |     |     |     |     |
    |-------------------:|----:|----:|----:|----:|----:|
    |                  1 |  41 |   0 |   0 |   0 |   4 |
    |                  2 |   0 |  19 |   0 |   0 |   8 |
    |                  3 |   0 |   0 |  20 |   4 |  14 |
    |                  4 |   0 |   0 |   0 |  25 |   5 |
    |                  5 |   0 |   0 |   1 |   1 | 657 |


###  Step 8: Visualizing predictions and ground truth


```python
result = evaluator.compare(interactive=True, split="val", show_words=True)
sample = next(iter(result))
sample.viz()
```

### Step 8: Visualizing predictions and ground truth
```python
result = evaluator.compare(interactive=True, split="val", show_words=True)
sample = next(iter(result))
sample.viz()
```

### Example usage
```text
## Step 9: Evaluation on test set

Comparing the evaluation results of eval and test split we see a deterioration of `fund_name`  F1-score (too 
many 
erroneous as `umbrella`). All remaining labels are slightly worse.


```python
categories = ner.dataflow.categories.get_sub_categories(categories="word",
                                                        sub_categories={"word": ["token_class"]},
                                                        keys=False)["word"]["token_class"]

path_config_json = "/path/to/dir/FRFPE/layoutlmv1/checkpoint-1600/config.json"
path_weights = "/path/to/dir/FRFPE/layoutlmv1/checkpoint-1600/model.safetensors"

layoutlm_classifier = dd.HFLayoutLmTokenClassifier(path_config_json,
                                                   path_weights,
                                                   categories=categories)

tokenizer_fast = LayoutLMTokenizerFast.from_pretrained("microsoft/layoutlm-base-uncased")
pipe_component = dd.LMTokenClassifierService(tokenizer_fast,
                                             layoutlm_classifier,
                                             use_other_as_default_category=True)


evaluator = dd.Evaluator(merge, pipe_component, metric)
_ = evaluator.run(split="test")
```

### Example usage
```python
categories = ner.dataflow.categories.get_sub_categories(categories="word",
                                                        sub_categories={"word": ["token_class"]},
                                                        keys=False)["word"]["token_class"]

path_config_json = "/path/to/dir/FRFPE/layoutlmv1/checkpoint-1600/config.json"
path_weights = "/path/to/dir/FRFPE/layoutlmv1/checkpoint-1600/model.safetensors"

layoutlm_classifier = dd.HFLayoutLmTokenClassifier(path_config_json,
                                                   path_weights,
                                                   categories=categories)

tokenizer_fast = LayoutLMTokenizerFast.from_pretrained("microsoft/layoutlm-base-uncased")
pipe_component = dd.LMTokenClassifierService(tokenizer_fast,
                                             layoutlm_classifier,
                                             use_other_as_default_category=True)


evaluator = dd.Evaluator(merge, pipe_component, metric)
_ = evaluator.run(split="test")
```

### Example usage
```text
???? info "Output"

    Confusion matrix:

    |    predictions ->  |   1 |   2 |   3 |   4 |   5 |
    |     ground truth | |     |     |     |     |     |
    |                  v |     |     |     |     |     |
    |-------------------:|----:|----:|----:|----:|----:|
    |                  1 |  53 |   0 |   0 |   0 |   2 |
    |                  2 |   0 |  20 |   0 |   0 |  12 |
    |                  3 |   0 |   0 |  25 |   6 |  10 |
    |                  4 |   0 |   0 |   4 | 292 |  33 |
    |                  5 |   0 |   0 |   4 |   8 | 482 |


```python
wandb.finish()
```

### Example usage
```python
wandb.finish()
```

### Example usage
```text
!!! note "Changing training parameters and settings"

    Already the first training run delivers satisfactory results. The following parameters could still be 
changed:

    `per_device_train_batch_size`
    `max_steps` 

!!! note "Sliding Window"

     `sliding_window_stride` - LayoutLM accepts a maximum of 512 tokens. For samples containing more tokens a 
sliding 
     window can be used: Assume a training sample contains 600 tokens. Without sliding window the last 88 
tokens are 
     not considered in the training. If a sliding window of 16 is set, 88 % 16 +1= 9 samples are generated. 

    *Caution:* 
    - The number `per_device_train_batch_size` can increase very fast and lead to Cuda OOM.
    - If a sample occurs that generates multiple training points due to the sliding windows setting, all other
samples 
      in the batch will be ignored and only the one data point with all its windows will be considered in this
step. 
      If you train with a dataset where the number of tokens is high for many samples, you should choose 
      `per_device_train_batch_size` to be rather small to ensure that you train with the whole dataset. 

    To avoid the situation to have a very large batch size becomes due to the sliding windos, we can add a 
    `max_batch_size`. Setting this parameter causes a selection of `max_batch_size` samples to be randomly 
sent to the 
    GPU from the generated sliding window samples.

    The training script will be looking like this:

    ```python
    dd.train_hf_layoutlm(path_config_json,
                        merge,
                        path_weights,
                        config_overwrite=["max_steps=4000",
                                          "per_device_train_batch_size=8",
                                          "eval_steps=100",
                                          "save_steps=400",
                                          "sliding_window_stride=16",
                                          "max_batch_size=8",
                                          "use_wandb=True",
                                          "wandb_project=funds_layoutlmv1"],
                        log_dir="/path/to/dir/Experiments/ner_first_page_v1_2",
                        dataset_val=merge,
                        metric=metric,
                        use_token_tag=False,
                        pipeline_component_name="LMTokenClassifierService")
```

---

# docs/tutorials/LayoutLM_For_Seq_Class.md - Project: LayoutLM for sequence classification

<p align="center"> <img 
src="https://github.com/deepdoctection/deepdoctection/raw/master/docs/tutorials/_imgs/dd_logo.png" alt="Deep 
Doctection Logo" width="60%"> <h3 align="center"> </h3> </p>.

## Code Examples

### Example usage
```python
import os
import deepdoctection as dd

def get_doctr_pipe():
    path_weights_tl = dd.ModelDownloadManager.maybe_download_weights_and_configs(
        "doctr/db_resnet50/pt/db_resnet50-ac60cadc.pt")
    categories_tl = dd.ModelCatalog.get_profile("doctr/db_resnet50/pt/db_resnet50-ac60cadc.pt").categories
    text_line_predictor = dd.DoctrTextlineDetector("db_resnet50", path_weights_tl, categories_tl, "cpu", "PT")
    layout = dd.ImageLayoutService(text_line_predictor, to_image=True, crop_image=True)

    path_weights_tr = dd.ModelDownloadManager.maybe_download_weights_and_configs(
        "doctr/crnn_vgg16_bn/pt/crnn_vgg16_bn-9762b0b0.pt")
    text_recognizer = dd.DoctrTextRecognizer("crnn_vgg16_bn", path_weights_tr, "cpu", "PT")
    text = dd.TextExtractionService(text_recognizer, extract_from_roi="word")
    analyzer = dd.DoctectionPipe(pipeline_component_list=[layout, text])

    return analyzer
```

### Example usage
```text
Next, we use the RVL-CDIP dataset from the **deep** library. This step requires the full dataset to be 
downloaded. 
The full data set has more than 300k samples with 16 different labels. We choose three labels *form*, 
*invoice* and 
*budget* and select around 1000 samples for each label. 

!!! note

    We do not know the distribution of each category. In order have all labels equally weighted we stream at 
most 1K
    samples with each label individually, pass them to the OCR-pipeline and save the OCR result for every 
image in 
    a folder with one `JSON` file.  

    

```python

path_to_save_samples =  "~/.cache/deepdoctection/datasets/rvl"

rvlcdip = dd.get_dataset("rvl-cdip")
rvlcdip.dataflow.categories.filter_categories({"budget"})
pipeline = get_doctr_pipe()

df = rvlcdip.dataflow.build(split="train", load_image=True)
df = pipeline.analyze(dataset_dataflow=df, output="image")
dd.dataflow_to_json(df, path_to_save_samples,
                    single_files=True,
                    file_name=None,
                    max_datapoints=1000,
                    save_image_in_json=False,
                    highest_hierarchy_only=True)

rvlcdip = dd.get_dataset("rvl-cdip")
rvlcdip.dataflow.categories.filter_categories({"invoice"})
pipeline = get_doctr_pipe()

df = rvlcdip.dataflow.build(split="train", load_image=True)
df = pipeline.analyze(dataset_dataflow=df, output="image")
dd.dataflow_to_json(df, path_to_save_samples,
                    single_files=True,
                    file_name=None,
                    max_datapoints=1000,
                    save_image_in_json=False,
                    highest_hierarchy_only=True)

rvlcdip = dd.get_dataset("rvl-cdip")
rvlcdip.dataflow.categories.filter_categories({"form"})
pipeline = get_doctr_pipe()

df = rvlcdip.dataflow.build(split="train", load_image=True)
df = pipeline.analyze(dataset_dataflow=df, output="image")
dd.dataflow_to_json(df, path_to_save_samples,
                    single_files=True,
                    file_name=None,
                    max_datapoints=1000,
                    save_image_in_json=False,
                    highest_hierarchy_only=True)
```

### Example usage
```python
path_to_save_samples =  "~/.cache/deepdoctection/datasets/rvl"

rvlcdip = dd.get_dataset("rvl-cdip")
rvlcdip.dataflow.categories.filter_categories({"budget"})
pipeline = get_doctr_pipe()

df = rvlcdip.dataflow.build(split="train", load_image=True)
df = pipeline.analyze(dataset_dataflow=df, output="image")
dd.dataflow_to_json(df, path_to_save_samples,
                    single_files=True,
                    file_name=None,
                    max_datapoints=1000,
                    save_image_in_json=False,
                    highest_hierarchy_only=True)

rvlcdip = dd.get_dataset("rvl-cdip")
rvlcdip.dataflow.categories.filter_categories({"invoice"})
pipeline = get_doctr_pipe()

df = rvlcdip.dataflow.build(split="train", load_image=True)
df = pipeline.analyze(dataset_dataflow=df, output="image")
dd.dataflow_to_json(df, path_to_save_samples,
                    single_files=True,
                    file_name=None,
                    max_datapoints=1000,
                    save_image_in_json=False,
                    highest_hierarchy_only=True)

rvlcdip = dd.get_dataset("rvl-cdip")
rvlcdip.dataflow.categories.filter_categories({"form"})
pipeline = get_doctr_pipe()

df = rvlcdip.dataflow.build(split="train", load_image=True)
df = pipeline.analyze(dataset_dataflow=df, output="image")
dd.dataflow_to_json(df, path_to_save_samples,
                    single_files=True,
                    file_name=None,
                    max_datapoints=1000,
                    save_image_in_json=False,
                    highest_hierarchy_only=True)
```

### Example usage
```text
## Step 2: Defining a dataset 

Having generated a dataset with features and labels at `/path/to/rvlcdip` we now copy the folder into the 
**deep**doctection cache and define a custom dataset with a custom dataflow for sequence classification.


```python
class RvlBuilder(dd.DataFlowBaseBuilder):

    def build(self, **kwargs) -> dd.DataFlow:
        load_image = kwargs.get("load_image", False)

        ann_files_dir = self.get_workdir()
        image_dir = self.get_workdir() / "image"

        df = dd.SerializerFiles.load(ann_files_dir,".json")   # get a stream of .json files
        df = dd.MapData(df, dd.load_json)   # load .json file
        categories = self.categories.get_categories(name_as_key=True)

        @dd.curry
        def map_to_img(dp, cats):
            dp = dd.Image.from_dict(**dp)
            dp.file_name= dp.file_name.replace(".tif",".png")
            dp.location = image_dir / dp.file_name
            if not os.path.isfile(dp.location): # (1) 
                return None
            if not len(dp.annotations): # (2) 
                return None
            sub_cat = dp.summary.get_sub_category(dd.PageType.DOCUMENT_TYPE)
            sub_cat.category_id = cats[sub_cat.category_name]
            if load_image:
                dp.image = dd.load_image_from_file(dp.location)
            return dp
        df = dd.MapData(df, map_to_img(categories))

        return df
    
rvlcdip = dd.CustomDataset(name = "rvl",
                 dataset_type=dd.DatasetType.SEQUENCE_CLASSIFICATION,
                 location="rvl",
                 init_categories=[dd.DocumentType.FORM, dd.DocumentType.INVOICE,dd.DocumentType.BUDGET],
                 dataflow_builder=RvlBuilder)
```

### Example usage
```python
class RvlBuilder(dd.DataFlowBaseBuilder):

    def build(self, **kwargs) -> dd.DataFlow:
        load_image = kwargs.get("load_image", False)

        ann_files_dir = self.get_workdir()
        image_dir = self.get_workdir() / "image"

        df = dd.SerializerFiles.load(ann_files_dir,".json")   # get a stream of .json files
        df = dd.MapData(df, dd.load_json)   # load .json file
        categories = self.categories.get_categories(name_as_key=True)

        @dd.curry
        def map_to_img(dp, cats):
            dp = dd.Image.from_dict(**dp)
            dp.file_name= dp.file_name.replace(".tif",".png")
            dp.location = image_dir / dp.file_name
            if not os.path.isfile(dp.location): # (1) 
                return None
            if not len(dp.annotations): # (2) 
                return None
            sub_cat = dp.summary.get_sub_category(dd.PageType.DOCUMENT_TYPE)
            sub_cat.category_id = cats[sub_cat.category_name]
            if load_image:
                dp.image = dd.load_image_from_file(dp.location)
            return dp
        df = dd.MapData(df, map_to_img(categories))

        return df
    
rvlcdip = dd.CustomDataset(name = "rvl",
                 dataset_type=dd.DatasetType.SEQUENCE_CLASSIFICATION,
                 location="rvl",
                 init_categories=[dd.DocumentType.FORM, dd.DocumentType.INVOICE,dd.DocumentType.BUDGET],
                 dataflow_builder=RvlBuilder)
```

### Example usage
```text
1. When creating the dataset some images could not be generated and we have to skip these
2. Some samples were rotated where OCR was not able to recognize text. No text -> no features


## Step 3: Downloading the LayoutLM base model

We use `layoutlm-base-uncased`. This model does not have any head yet and the top head will be specified by 
the task 
as well as by the number of labels in the training script.  


```python
dd.ModelDownloadManager.maybe_download_weights_and_configs("microsoft/layoutlm-base-uncased/pytorch_model.bin"
)
```

### Example usage
```python
dd.ModelDownloadManager.maybe_download_weights_and_configs("microsoft/layoutlm-base-uncased/pytorch_model.bin"
)
```

### Example usage
```text
## Defining the model

!!! info 

    For those who might wonder why we do not use the very handy transformer `.from_pretained` methods and 
rather 
    setup a model by passing a config file and weights: All models trainable by the **deep**doctection 
framework are 
    build using a config file and specifying a path to the artifact.


```python
path_config_json = dd.ModelCatalog.get_full_path_configs("microsoft/layoutlm-base-uncased/pytorch_model.bin")
path_weights = dd.ModelCatalog.get_full_path_weights("microsoft/layoutlm-base-uncased/pytorch_model.bin")
```

### Example usage
```python
path_config_json = dd.ModelCatalog.get_full_path_configs("microsoft/layoutlm-base-uncased/pytorch_model.bin")
path_weights = dd.ModelCatalog.get_full_path_weights("microsoft/layoutlm-base-uncased/pytorch_model.bin")
```

### Example usage
```text
## Step 4: Generating a split

Using the `MergeDataset` class we can load the dataset into memory and split it into a `train`, `val` and 
`test` set.
Specifying a ratio of 0.05 means that the `train` split will contain on 
average 90% of overall dataset with the remaining two splits sharing on average the last 10% equally. It does 
not mean 
that the train split contains exactly 90%.  


```python
merge = dd.MergeDataset(rvlcdip)
merge.buffer_datasets()
merge.split_datasets(ratio=0.1)
```

### Example usage
```python
merge = dd.MergeDataset(rvlcdip)
merge.buffer_datasets()
merge.split_datasets(ratio=0.1)
```

### Example usage
```text
??? info "Output"

    {'test': 91, 'train': 1693, 'val': 91}


## Step 5: Training


We run the training scripts more or less with default arguments as specified by the Transformers `Trainer` 
class. 
We choose `max_steps` of the training to be equal the size of the training split and 
`per_device_train_batch_size` to 
be 8.
When running with one machine this corresponds to run training for 8 epochs. We evaluate on small intervals. 
Adapt 
your parameters if you train with more machines or if you need to reduce `batch_size` because of memory 
constraints.


```python
dataset_train = merge
dataset_val = merge

metric = dd.get_metric("accuracy")
metric.set_categories(summary_sub_category_names="document_type")

dd.train_hf_layoutlm(path_config_json,
                     dataset_train,
                     path_weights,
                     log_dir="/path/to/dir",
                     dataset_val= dataset_val,
                     metric=metric,
                     pipeline_component_name="LMSequenceClassifierService")
```

### Example usage
```python
dataset_train = merge
dataset_val = merge

metric = dd.get_metric("accuracy")
metric.set_categories(summary_sub_category_names="document_type")

dd.train_hf_layoutlm(path_config_json,
                     dataset_train,
                     path_weights,
                     log_dir="/path/to/dir",
                     dataset_val= dataset_val,
                     metric=metric,
                     pipeline_component_name="LMSequenceClassifierService")
```

### Example usage
```text
### Tensorboard

Logging does not look very neat on the jupyter notebook display. We can start tensorboard from a terminal
to get an overview of current learning rate, epoch, train loss and accuracy for the validation set.

```sh
tensorboard --logdir /path/to/traindir
```

### Example usage
```sh
tensorboard --logdir /path/to/traindir
```

### Example usage
```text
## Step 6:  Running evaluation on the test set

Configuration files and checkpoints are being saved in sub folders of `/path/to/dir`. We use them to run a 
final 
evaluation on the test split.

!!! info 

    The training script already selects a tokenizer that is needed to convert raw features, i.e. words into 
tokens. It 
    also chooses the mapping framework that converts datapoints of the internal **deep**doctection image 
format into 
    layoutlm features. 

    The Evaluator however, has been designed to run evaluation on various tasks. Hence it needs a pipeline 
component. 
    The pipeline component for language model sequence classification must be instatiated by choosing the 
layoutlm 
    model, but also the right converter to generate layoutlm features from the intrinsic **deep**doctection 
data 
    model as well as the right tokenizer.

!!! info

    We only use Huggingface's fast tokenizer as it contains helpful additional outputs to generate LayoutLM 
inputs. 
    Choosing the conventional tokenizer will not work.  



```python
from transformers import LayoutLMTokenizerFast

path_config_json = "/path/to/dir/checkpoint-2500/config.json"
path_weights = "/path/to/dir/checkpoint-2500/pytorch_model.bin"

layoutlm_classifier = dd.HFLayoutLmSequenceClassifier(path_config_json,
                                                      path_weights,
                                                      merge.dataflow.categories.get_categories(as_dict=True))

tokenizer_fast = LayoutLMTokenizerFast.from_pretrained("microsoft/layoutlm-base-uncased")

pipe_component = dd.LMSequenceClassifierService(tokenizer_fast,layoutlm_classifier)

evaluator = dd.Evaluator(merge,
                         pipe_component,
                         metric)

evaluator.run(split="test")
```

### Example usage
```python
from transformers import LayoutLMTokenizerFast

path_config_json = "/path/to/dir/checkpoint-2500/config.json"
path_weights = "/path/to/dir/checkpoint-2500/pytorch_model.bin"

layoutlm_classifier = dd.HFLayoutLmSequenceClassifier(path_config_json,
                                                      path_weights,
                                                      merge.dataflow.categories.get_categories(as_dict=True))

tokenizer_fast = LayoutLMTokenizerFast.from_pretrained("microsoft/layoutlm-base-uncased")

pipe_component = dd.LMSequenceClassifierService(tokenizer_fast,layoutlm_classifier)

evaluator = dd.Evaluator(merge,
                         pipe_component,
                         metric)

evaluator.run(split="test")
```

### Example usage
```text
??? info "Output"

    [{'key': 'document_type', 'val': 0.8851351351351351, 'num_samples': 148}]


## Step 6: Building a pipeline for production

In the final step we setup a complete pipeline for running the LayoutLM model. We use the same OCR framework 
for the 
first part of the pipeline followed by the `LMSequenceClassifierService`.


```python
def get_layoutlm_pipeline():
    path_weights_tl = 
dd.ModelDownloadManager.maybe_download_weights_and_configs("doctr/db_resnet50/pt/db_resnet50-ac60cadc.pt")
    categories_tl = dd.ModelCatalog.get_profile("doctr/db_resnet50/pt/db_resnet50-ac60cadc.pt").categories
    text_line_predictor = dd.DoctrTextlineDetector("db_resnet50", path_weights_tl, categories_tl, "cpu", "PT")
    layout_component = dd.ImageLayoutService(text_line_predictor,to_image=True, crop_image=True)
    
    path_weights_tr = 
dd.ModelDownloadManager.maybe_download_weights_and_configs("doctr/crnn_vgg16_bn/pt/crnn_vgg16_bn-9762b0b0.pt")
    text_recognizer = dd.DoctrTextRecognizer("crnn_vgg16_bn", path_weights_tr, "cpu", "PT")
    text_component = dd.TextExtractionService(text_recognizer, extract_from_roi="word")
    
    
    layoutlm_classifier = dd.HFLayoutLmSequenceClassifier(path_config_json,
                                                          path_weights,
                                                          {1: 'form', 2: 'invoice', 3: 'budget'})
    
    tokenizer_fast = LayoutLMTokenizerFast.from_pretrained("microsoft/layoutlm-base-uncased")
    layoutlm_component = dd.LMSequenceClassifierService(tokenizer_fast,
                                                        layoutlm_classifier)
    
    return dd.DoctectionPipe(pipeline_component_list=[layout_component, text_component, layoutlm_component])
```

### Example usage
```python
def get_layoutlm_pipeline():
    path_weights_tl = 
dd.ModelDownloadManager.maybe_download_weights_and_configs("doctr/db_resnet50/pt/db_resnet50-ac60cadc.pt")
    categories_tl = dd.ModelCatalog.get_profile("doctr/db_resnet50/pt/db_resnet50-ac60cadc.pt").categories
    text_line_predictor = dd.DoctrTextlineDetector("db_resnet50", path_weights_tl, categories_tl, "cpu", "PT")
    layout_component = dd.ImageLayoutService(text_line_predictor,to_image=True, crop_image=True)
    
    path_weights_tr = 
dd.ModelDownloadManager.maybe_download_weights_and_configs("doctr/crnn_vgg16_bn/pt/crnn_vgg16_bn-9762b0b0.pt")
    text_recognizer = dd.DoctrTextRecognizer("crnn_vgg16_bn", path_weights_tr, "cpu", "PT")
    text_component = dd.TextExtractionService(text_recognizer, extract_from_roi="word")
    
    
    layoutlm_classifier = dd.HFLayoutLmSequenceClassifier(path_config_json,
                                                          path_weights,
                                                          {1: 'form', 2: 'invoice', 3: 'budget'})
    
    tokenizer_fast = LayoutLMTokenizerFast.from_pretrained("microsoft/layoutlm-base-uncased")
    layoutlm_component = dd.LMSequenceClassifierService(tokenizer_fast,
                                                        layoutlm_classifier)
    
    return dd.DoctectionPipe(pipeline_component_list=[layout_component, text_component, layoutlm_component])
```

### Example usage
```text
## Step 7: Running the pipeline

We use a subfolder of plain images of the `rvl` dataset to demonstrate how it works.


```python
from matplotlib import pyplot as plt

path = "/path/to/.cache/deepdoctection/rvl/image"

doc_classifier = get_layoutlm_pipeline()

df = doc_classifier.analyze(path=path)
df.reset_state()
df_iter = iter(df)

dp = next(df_iter)

plt.figure(figsize = (25,17))
plt.axis('off')
plt.imshow(dp.viz())
```

### Example usage
```python
from matplotlib import pyplot as plt

path = "/path/to/.cache/deepdoctection/rvl/image"

doc_classifier = get_layoutlm_pipeline()

df = doc_classifier.analyze(path=path)
df.reset_state()
df_iter = iter(df)

dp = next(df_iter)

plt.figure(figsize = (25,17))
plt.axis('off')
plt.imshow(dp.viz())
```

### Example usage
```text
![png](./_imgs/layoutlm_sequence_classification_01.png)


```python
dp.document_type.value
```

### Example usage
```python
dp.document_type.value
```

### Example usage
```text
??? info "Output"

    'BUDGET'


```python
dp=next(df_iter)

plt.figure(figsize = (25,17))
plt.axis('off')
plt.imshow(dp.viz())
```

### Example usage
```python
dp=next(df_iter)

plt.figure(figsize = (25,17))
plt.axis('off')
plt.imshow(dp.viz())
```

### Example usage
```text
![png](./_imgs/layoutlm_sequence_classification_02.png)


```python
dp.document_type.value
```

### Example usage
```python
dp.document_type.value
```

### Example usage
```text
??? info "Output"

    'BUDGET'
```

---

# docs/tutorials/Pipelines.md - Pipelines

<p align="center"> <img 
src="https://github.com/deepdoctection/deepdoctection/raw/master/docs/tutorials/_imgs/dd_logo.png" alt="Deep 
Doctection Logo" width="60%"> <h3 align="center"> </h3> </p>.

## Code Examples

### Example usage
```python
import deepdoctection as dd
from pathlib import Path

analyzer = dd.get_dd_analyzer()
```

### Example usage
```text
??? Info "Output"

    <pre>
    {
    'DEVICE': device(type='mps'),
    'LANGUAGE': None,
    'LAYOUT_LINK': {'CHILD_CATEGORIES': ['LayoutType.CAPTION'],
                    'PARENTAL_CATEGORIES': ['LayoutType.FIGURE', 'LayoutType.TABLE']},
    'LAYOUT_NMS_PAIRS': {'COMBINATIONS': [['LayoutType.TABLE', 'LayoutType.TITLE'],
                                          ['LayoutType.TABLE', 'LayoutType.TEXT'],
                                          ['LayoutType.TABLE', 'LayoutType.KEY_VALUE_AREA'],
                                          ['LayoutType.TABLE', 'LayoutType.LIST_ITEM'],
                                          ['LayoutType.TABLE', 'LayoutType.LIST'],
                                          ['LayoutType.TABLE', 'LayoutType.FIGURE'],
                                          ['LayoutType.TITLE', 'LayoutType.TEXT'],
                                          ['LayoutType.TEXT', 'LayoutType.KEY_VALUE_AREA'],
                                          ['LayoutType.TEXT', 'LayoutType.LIST_ITEM'],
                                          ['LayoutType.TEXT', 'LayoutType.CAPTION'],
                                          ['LayoutType.KEY_VALUE_AREA', 
                                           'LayoutType.LIST_ITEM'],
                                          ['LayoutType.FIGURE', 
                                           'LayoutType.CAPTION']],
                         'PRIORITY': ['LayoutType.TABLE', 
                                      'LayoutType.TABLE', 
                                      'LayoutType.TABLE',
                                      'LayoutType.TABLE', 
                                      'LayoutType.TABLE', 
                                      'LayoutType.TABLE',
                                      'LayoutType.TEXT', 
                                      'LayoutType.TEXT', 
                                       None, 
                                      'LayoutType.CAPTION',
                                      'LayoutType.KEY_VALUE_AREA', 
                                      'LayoutType.FIGURE'],
                         'THRESHOLDS': [0.001, 
                                        0.01, 
                                        0.01, 
                                        0.001, 
                                        0.01,  
                                        0.01, 
                                        0.05, 
                                        0.01, 
                                        0.01, 
                                        0.01,
                                        0.01, 
                                        0.001]},
    'LIB': 'PT',
    'OCR': {'CONFIG': {'TESSERACT': 'dd/conf_tesseract.yaml'},
            'USE_DOCTR': True,
            'USE_TESSERACT': False,
            'USE_TEXTRACT': False,
            'WEIGHTS': {'DOCTR_RECOGNITION': 
                        {'PT': 'doctr/crnn_vgg16_bn/pt/crnn_vgg16_bn-9762b0b0.pt',
                         'TF': 'doctr/crnn_vgg16_bn/tf/crnn_vgg16_bn-76b7f2c6.zip'},
                        'DOCTR_WORD': 
                        {'PT': 'doctr/db_resnet50/pt/db_resnet50-ac60cadc.pt',
                         'TF': 'doctr/db_resnet50/tf/db_resnet50-adcafc63.zip'}}},
    'PDF_MINER': {'X_TOLERANCE': 3, 'Y_TOLERANCE': 3},
    'PT': {'CELL': {'FILTER': None,
                    'PAD': {'BOTTOM': 60, 'LEFT': 60, 'RIGHT': 60, 'TOP': 60},
                    'PADDING': False,
                    'WEIGHTS': 'cell/d2_model_1849999_cell_inf_only.pt',
                    'WEIGHTS_TS': 'cell/d2_model_1849999_cell_inf_only.ts'},
           'ENFORCE_WEIGHTS': {'CELL': True, 'ITEM': True, 'LAYOUT': True},
           'ITEM': {'FILTER': ['table'],
                    'PAD': {'BOTTOM': 60, 'LEFT': 60, 'RIGHT': 60, 'TOP': 60},
                    'PADDING': False,
                    'WEIGHTS': 'deepdoctection/tatr_tab_struct_v2/pytorch_model.bin',
                    'WEIGHTS_TS': 'item/d2_model_1639999_item_inf_only.ts'},
           'LAYOUT': {'FILTER': None,
                      'PAD': {'BOTTOM': 0, 'LEFT': 0, 'RIGHT': 0, 'TOP': 0},
                      'PADDING': False,
                      'WEIGHTS': 'Aryn/deformable-detr-DocLayNet/model.safetensors',
                      'WEIGHTS_TS': 'layout/d2_model_0829999_layout_inf_only.ts'}},
    'SEGMENTATION': {'ASSIGNMENT_RULE': 'ioa',
                     'CELL_NAMES': ['CellType.HEADER', 
                                    'CellType.BODY', 
                                    'LayoutType.CELL'],
                     'FULL_TABLE_TILING': True,
                     'ITEM_NAMES': ['LayoutType.ROW', 'LayoutType.COLUMN'],
                     'PUBTABLES_CELL_NAMES': ['LayoutType.CELL'],
                     'PUBTABLES_ITEM_HEADER_CELL_NAMES': ['CellType.COLUMN_HEADER',
                                                          'CellType.ROW_HEADER',
                                                          'CellType.PROJECTED_ROW_HEADER'],
                     'PUBTABLES_ITEM_HEADER_THRESHOLDS': [0.6, 0.0001],
                     'PUBTABLES_ITEM_NAMES': ['LayoutType.ROW', 'LayoutType.COLUMN'],
                     'PUBTABLES_SPANNING_CELL_NAMES': ['CellType.SPANNING'],
                     'PUBTABLES_SUB_ITEM_NAMES': ['CellType.ROW_NUMBER', 
                                                  'CellType.COLUMN_NUMBER'],
                     'REMOVE_IOU_THRESHOLD_COLS': 0.2,
                     'REMOVE_IOU_THRESHOLD_ROWS': 0.2,
                     'STRETCH_RULE': 'equal',
                     'SUB_ITEM_NAMES': ['CellType.ROW_NUMBER', 'CellType.COLUMN_NUMBER'],
                     'TABLE_NAME': 'LayoutType.TABLE',
                     'THRESHOLD_COLS': 0.4,
                     'THRESHOLD_ROWS': 0.4},
    'TEXT_CONTAINER': 'LayoutType.WORD',
    'TEXT_ORDERING': {'BROKEN_LINE_TOLERANCE': 0.003,
                      'FLOATING_TEXT_BLOCK_CATEGORIES': ('LayoutType.TEXT', 
                                                         'LayoutType.TITLE',
                                                         'LayoutType.LIST',
                                                         'LayoutType.KEY_VALUE_AREA'),
                      'HEIGHT_TOLERANCE': 2.0,
                      'INCLUDE_RESIDUAL_TEXT_CONTAINER': True,
                      'PARAGRAPH_BREAK': 0.035,
                      'STARTING_POINT_TOLERANCE': 0.005,
                      'TEXT_BLOCK_CATEGORIES': ('LayoutType.TEXT', 
                                                'LayoutType.TITLE',
                                                'LayoutType.LIST_ITEM', 
                                                'LayoutType.LIST',
                                                'LayoutType.CAPTION', 
                                                'LayoutType.PAGE_HEADER',
                                                'LayoutType.PAGE_FOOTER', 
                                                'LayoutType.PAGE_NUMBER',
                                                'LayoutType.MARK', 
                                                'LayoutType.KEY_VALUE_AREA',
                                                'LayoutType.FIGURE', 
                                                'CellType.SPANNING',
                                                'LayoutType.CELL')},
    'TF': {'CELL': {'FILTER': None, 
                    'WEIGHTS': 'cell/model-1800000_inf_only.data-00000-of-00001'},
           'ITEM': {'FILTER': None, 
                    'WEIGHTS': 'item/model-1620000_inf_only.data-00000-of-00001'},
           'LAYOUT': {'FILTER': None, 
                      'WEIGHTS': 'layout/model-800000_inf_only.data-00000-of-00001'}},
    'USE_LAYOUT': True,
    'USE_LAYOUT_LINK': False,
    'USE_LAYOUT_NMS': True,
    'USE_LINE_MATCHER': False,
    'USE_OCR': True,
    'USE_PDF_MINER': False,
    'USE_ROTATOR': False,
    'USE_TABLE_REFINEMENT': False,
    'USE_TABLE_SEGMENTATION': True,
    'WORD_MATCHING': {'MAX_PARENT_ONLY': True,
                      'PARENTAL_CATEGORIES': ('LayoutType.TEXT', 
                                              'LayoutType.TITLE',
                                              'LayoutType.LIST_ITEM', 
                                              'LayoutType.LIST',
                                              'LayoutType.CAPTION', 
                                              'LayoutType.PAGE_HEADER',
                                              'LayoutType.PAGE_FOOTER', 
                                              'LayoutType.PAGE_NUMBER',
                                              'LayoutType.MARK', 
                                              'LayoutType.KEY_VALUE_AREA',
                                              'LayoutType.FIGURE', 
                                              'CellType.SPANNING',
                                              'LayoutType.CELL'),
                      'RULE': 'ioa',
                      'THRESHOLD': 0.3}
    }
    </pre>

Let's take a closer look at the **deep**doctection analyzer. 

![pipeline](./_imgs/pipelines_02.png)

The architecture is modular, and a pipeline consists of individual components, each typically performing a 
single 
processing step. We have already explored the [**configuration**](Analyzer_Configuration.md) options. When the
analyzer 
is instantiated, a dictionary is printed to the logs, which begins approximately like this:

??? Info "Output"

    <pre>
    {'DEVICE': device(type='mps'),
     'LANGUAGE': None,
     'LAYOUT_LINK': {'CHILD_CATEGORIES': ['caption'], 
                     'PARENTAL_CATEGORIES': ['figure', 'table']},
     'LAYOUT_NMS_PAIRS': {'COMBINATIONS': 
                          [['table', 'title'], 
                           ['table', 'text'], 
                           ['table', 'key_value_area'], 
                           ['table', 'list_item'],
                           ['table', 'list'], 
                           ['table', 'figure'], 
                           ['title', 'text'],
                           ['text', 'key_value_area'], 
                           ['text', 'list_item'],
                           ['key_value_area', 'list_item']],
     'PRIORITY': ['table', 
                  'table', 
                  'table', 
                  'table', 
                  'table', 
                  'table', 
                  'text',
                  'text', 
                   None, 
                  'key_value_area'],
     'THRESHOLDS': [0.001, 
                    0.01, 
                    0.01, 
                    0.001, 
                    0.01, 
                    0.01, 
                    0.05, 
                    0.01, 
                    0.01, 
                    0.01]},
     ...
    }
    </pre>


Having a pipeline, we can list the components with `get_pipeline_info()`. It returns a dictionary with the a 
so 
called `service_id` and a name of the component. Note, that the name of the component depends not only on the 
service 
itself but also on the model that is being chosen.


```python
analyzer.get_pipeline_info()
```

### Example usage
```python
analyzer.get_pipeline_info()
```

### Example usage
```text
??? Info "Output"

    <pre>
    {'5497d92c': 'image_Transformers_Tatr_deformable-detr-DocLayNet_model.safetensors',
     '3b56c997': 'nms',
     '8c23055e': 'sub_image_Transformers_Tatr_tatr_tab_struct_v2_pytorch_model.bin',
     '03844ddb': 'table_transformer_segment',
     '01a15bff': 'image_doctr_db_resnet50pt_db_resnet50-ac60cadc.pt',
     '1cedc14d': 'text_extract_doctr_crnn_vgg16_bnpt_crnn_vgg16_bn-9762b0b0.pt',
     'd6219eba': 'matching',
     'f10aa678': 'text_order'}
        </pre>


```python
component = analyzer.get_pipeline_component(service_id="5497d92c")
component.name
```

### Example usage
```python
component = analyzer.get_pipeline_component(service_id="5497d92c")
component.name
```

### Example usage
```text
??? Info "Output"

    'image_Transformers_Tatr_deformable-detr-DocLayNet_model.safetensors'



Each pipeline component has a `DatapointManager`, which manages the dataclass responsible for collecting all 
information 
related to a page. The results are then provided through the `Page` object, which generates the corresponding 
`JSON` 
output. If a service uses a model, the model will also receive a `model_id`. If we want to process a pile of 
documents 
with a pipeline, we can pass a `service_id` to the `analyze` method which allows you to version the run. The 
`service_id` will be added in our JSON output. Note, that the analyzer will not generate a `session_id` by 
itself.

The `get_meta_annotation()` method allows us to see which elements are being detected. 

!!! Info 
    
    We already mentioned this method in the [**More on parsing**](Analyzer_More_On_Parsing.md) notebook. It 
exists 
    both at the level of individual pipeline components and at the level of the entire pipeline.

At the pipeline level, all `get_meta_annotation()` outputs from the individual components are aggregated.

```python
component.dp_manager.model_id, component.dp_manager.service_id, component.dp_manager.session_id
```

### Example usage
```python
component.dp_manager.model_id, component.dp_manager.service_id, component.dp_manager.session_id
```

### Example usage
```text
??? Info "Output"

    ('af516519', '5497d92c', None)



## Pipeline operations and parsing results

Let’s now take a look at the parsed results from a technical perspective.



```python
pdf_path = "path/to/dir/sample/2312.13560.pdf"

df = analyzer.analyze(path=pdf_path, 
                                          session_id="9999z99z", 
                                          max_datapoints=3) # (1) 
df.reset_state()
all_results = [dp for dp in df]

page_2 = all_results[1]

sample_layout_section = page_2.layouts[0] # get the first layout section
print(f"service_id: {sample_layout_section.service_id}, 
        model_id: {sample_layout_section.model_id}, 
        session_id: {sample_layout_section.session_id}")
```

### Example usage
```python
pdf_path = "path/to/dir/sample/2312.13560.pdf"

df = analyzer.analyze(path=pdf_path, 
                                          session_id="9999z99z", 
                                          max_datapoints=3) # (1) 
df.reset_state()
all_results = [dp for dp in df]

page_2 = all_results[1]

sample_layout_section = page_2.layouts[0] # get the first layout section
print(f"service_id: {sample_layout_section.service_id}, 
        model_id: {sample_layout_section.model_id}, 
        session_id: {sample_layout_section.session_id}")
```

### Example usage
```text
1. `max_datapoints` limits the number of samples to at most 3

??? Info "Output"

    service_id: 5497d92c, model_id: af516519, session_id: 9999z99z



```python
sample_word = sample_layout_section.get_ordered_words()[2]
print(f"layout section text: {sample_layout_section.text} \n \n word text: {sample_word.characters}  
        service_id: {sample_word.service_id}, model_id: {sample_word.model_id}, session_id: 
{sample_word.session_id}")
```

### Example usage
```python
sample_word = sample_layout_section.get_ordered_words()[2]
print(f"layout section text: {sample_layout_section.text} \n \n word text: {sample_word.characters}  
        service_id: {sample_word.service_id}, model_id: {sample_word.model_id}, session_id: 
{sample_word.session_id}")
```

### Example usage
```text
??? Info "Output"

    layout section text: When processing audio at the frame level, an immense vol- ume of entries is 
generated, where 
    a considerable portion of the frames are assigned to the <blank * symbol due to the characteristic peak 
behavior 
    of CTC. We propose skip-blank strategy to prune the datastore and accelerat KNN retrieval. During 
datastore 
    construction, this strateg omits frames whose CTC pseudo labels correspond to th <blank " symbol, thereby 
reducing 
    the size of the data store. This process is indicated by the blue dashed lines 11 
     
    word text: audio  service_id: 01a15bff, model_id: 65b358ea, session_id: 9999z99z


As is well known, a pipeline does not only generate layout sections but also determines other elements—such as
reading 
orders or relationships between layout sections. The associated `service_id` must be extracted from the 
container that 
stores the reading order information.

!!! Info

    We can find more information about the data structure in the [**Data structure tutorial**]
    (Data_Structure.md).



```python
reading_order = sample_layout_section.get_sub_category("reading_order")
print(type(reading_order))
```

### Example usage
```python
reading_order = sample_layout_section.get_sub_category("reading_order")
print(type(reading_order))
```

### Example usage
```text
<class 'deepdoctection.datapoint.annotation.CategoryAnnotation'>



```python
print(f"position: {reading_order.category_id},
        service_id: {reading_order.service_id}  
        model_id: {reading_order.model_id}, 
        session_id: {reading_order.session_id}")
```

### Example usage
```python
print(f"position: {reading_order.category_id},
        service_id: {reading_order.service_id}  
        model_id: {reading_order.model_id}, 
        session_id: {reading_order.session_id}")
```

### Example usage
```text
??? Info "Output"

    position: 25
    service_id: f10aa678  
    model_id: None 
    session_id: 9999z99z


We can get an overview of all `service_id`'s and their `annotation_id`'s they generated.


```python
service_id_to_annotation_id = page_2.get_service_id_to_annotation_id()
service_id_to_annotation_id.keys(), service_id_to_annotation_id["01a15bff"][:10]
```

### Example usage
```python
service_id_to_annotation_id = page_2.get_service_id_to_annotation_id()
service_id_to_annotation_id.keys(), service_id_to_annotation_id["01a15bff"][:10]
```

### Example usage
```text
??? Info "Output"

    (dict_keys(['5497d92c', 'f10aa678', '01a15bff', '1cedc14d', 'd6219eba']),
     ['a0ef728f-57c7-304e-9d98-903a492b6dea',
      '9340f60a-8088-3b7c-bf5b-f41e472e61b1',
      '14bdcabc-49a6-37e7-8890-4c03f6b6bfed',
      '2c119bf0-d344-3c6c-9ec2-60f7f07c3092',
      '48e5f8f8-90d4-3d2d-bbc1-a8793961d3e1',
      '811addaf-6388-345c-97b4-0def4114822f',
      '589cbd78-dfbc-3af6-9de7-0c2a9ee31956',
      '9b4474c8-7c14-3b97-8533-3998aa832ed3',
      '29440674-f9d3-3611-942b-1f9370ac213a',
      '1b44b477-8c20-3fd2-8f14-accc04abe601'])



Conversely, for a given `annotation_id`, we can use the `AnnotationMap` to locate the position where the 
object with 
that specific `annotation_id` can be found.

In the case below, the object with `annotation_id="966e6cc7-8b2c-38c5-9416-cfe114af1cc1"` is located within 
the layout 
section with `annotation_id="6ac8cd0b-8425-392c-ae8a-76c1f198ecf0"` and represents the `sub_category = 
<Relationships.READING_ORDER>`.


```python
annotation_id_to_annotation_maps = page_2.get_annotation_id_to_annotation_maps()
annotation_id_to_annotation_maps["966e6cc7-8b2c-38c5-9416-cfe114af1cc1"]
```

### Example usage
```python
annotation_id_to_annotation_maps = page_2.get_annotation_id_to_annotation_maps()
annotation_id_to_annotation_maps["966e6cc7-8b2c-38c5-9416-cfe114af1cc1"]
```

### Example usage
```text
??? Info "Output"

    [AnnotationMap(image_annotation_id='6ac8cd0b-8425-392c-ae8a-76c1f198ecf0',
                   sub_category_key=<Relationships.READING_ORDER>, 
                   relationship_key=None, 
                   summary_key=None)]



We can retrieve the object in two steps:


```python
image_annotation = page_2.get_annotation(annotation_ids="6ac8cd0b-8425-392c-ae8a-76c1f198ecf0")[0] # (1) 
reading_order_ann = image_annotation.get_sub_category("reading_order") # (2) 
reading_order_ann.annotation_id # (3)
```

### We can retrieve the object in two steps
```python
image_annotation = page_2.get_annotation(annotation_ids="6ac8cd0b-8425-392c-ae8a-76c1f198ecf0")[0] # (1) 
reading_order_ann = image_annotation.get_sub_category("reading_order") # (2) 
reading_order_ann.annotation_id # (3)
```

### Example usage
```text
1. Get the layout section
2. Get the reading order annotation
3. Reading_order_ann is the object we were looking for

??? Info "Output"

    '966e6cc7-8b2c-38c5-9416-cfe114af1cc1'



## Undoing a pipeline component operation

Not only the creation of objects but also the revision of a parsing structure can be important. In particular,
the output of a component can be reverted using `undo`. In this example, we remove all word positions that 
were 
identified by the DocTr text detection model.


```python
text_detection_component = analyzer.get_pipeline_component(service_id="01a15bff")
df = dd.DataFromList([dp.image_orig for dp in all_results]) # (1) 
df = text_detection_component.undo(df)
df.reset_state()

all_results_modified = [dp for dp in df]
```

### the output of a component can be reverted using `undo`. In this example, we remove all word positions that
were
```python
text_detection_component = analyzer.get_pipeline_component(service_id="01a15bff")
df = dd.DataFromList([dp.image_orig for dp in all_results]) # (1) 
df = text_detection_component.undo(df)
df.reset_state()

all_results_modified = [dp for dp in df]
```

### Example usage
```text
1. Check the notebook [Data_structure](Data_Structure.md)  in order to understand why we use `dp.image_orig`.

!!! Info

    Note that not only the objects generated by the pipeline itself are affected, but also those from all 
pipeline 
    components that build upon its results. In this case, objects related to text ordering and layout segments
remain. 
    The fact that text ordering objects persist might be surprising, but it can be explained by the fact that 
not only 
    the words, but also the layout segments themselves are ordered. As a result, the reading order determined 
for these 
    segments leads to the retention of objects from this service.



```python
page_2_modified = all_results_modified[1]
service_id_to_annotation_id_modified = page_2_modified.get_service_id_to_annotation_id()
service_id_to_annotation_id_modified.keys(), service_id_to_annotation_id_modified.get("01a15bff")
```

### Example usage
```python
page_2_modified = all_results_modified[1]
service_id_to_annotation_id_modified = page_2_modified.get_service_id_to_annotation_id()
service_id_to_annotation_id_modified.keys(), service_id_to_annotation_id_modified.get("01a15bff")
```

### Example usage
```text
??? Info "Output"

    (dict_keys(['5497d92c', 'f10aa678']), None)


## Analyzer Factory


How is an Analyzer constructed and where does the configuration come from? The configuration is provided by a 
default 
instance called `cfg`, which can be modified by defrosting it.



```python
from deepdoctection.analyzer import cfg, ServiceFactory

cfg.USE_OCR
```

### Example usage
```python
from deepdoctection.analyzer import cfg, ServiceFactory

cfg.USE_OCR
```

### Example usage
```text
??? Info "Output"

    True


```python
cfg.freeze(False)
cfg.USE_OCR=False  # (1) 
cfg.freeze(True)
```

### Example usage
```python
cfg.freeze(False)
cfg.USE_OCR=False  # (1) 
cfg.freeze(True)
```

### Example usage
```text
1. After defrosting we can change values and add new attributes


For constructing predictors (layout, table segmentation, OCR, etc.), pipeline components, and the default 
pipeline, a 
`ServiceFactory` offers a variety of methods. We will not cover all the methods provided by the factory here, 
but 
rather give just one example.


```python
rotation_detector = ServiceFactory.build_rotation_detector() # (1)
transform_service = ServiceFactory.build_transform_service(transform_predictor=rotation_detector)
pipeline = dd.DoctectionPipe(pipeline_component_list=[transform_service])
```

### rather give just one example.
```python
rotation_detector = ServiceFactory.build_rotation_detector() # (1)
transform_service = ServiceFactory.build_transform_service(transform_predictor=rotation_detector)
pipeline = dd.DoctectionPipe(pipeline_component_list=[transform_service])
```

### Example usage
```text
1. A very simple example of a pipeline includes a rotation detector that determines the rotation angle 
   of a page (in multiples of 90 degrees) and rotates each page so that the text is in its correct,
   readable orientation.
```

---

# docs/tutorials/Project_Training.md - Project: Training a model on several datasets

<p align="center"> <img 
src="https://github.com/deepdoctection/deepdoctection/raw/master/docs/tutorials/_imgs/dd_logo.png" alt="Deep 
Doctection Logo" width="60%"> <h3 align="center"> </h3> </p>.

## Code Examples

### Example usage
```python
from collections import defaultdict
import numpy as np

from fvcore.transforms import ScaleTransform
import wandb

import deepdoctection as dd

@dd.curry
def scale_transform(dp, scaler, apply_image=False):
    dp._bbox = None
    dp.set_width_height(1654,2339)
    if apply_image:
        dp.image = scaler.apply_image(dp.image)
    anns = dp.get_annotation()
    boxes = np.array([ann.bounding_box.to_list(mode="xyxy") for ann in anns])
    scaled_boxes = scaler.apply_box(boxes)
    for box, ann in zip(scaled_boxes[:,],anns):
        ann.bounding_box= dd.BoundingBox(ulx=box[0],uly=box[1],lrx=box[2],lry=box[3],absolute_coords=True)
    return dp


def filter_list_images(dp):
    if dp.summary.get_sub_category(dd.LayoutType.LIST).category_id != 0:
        return None
    return dp
```

### if dp.summary.get_sub_category(dd.LayoutType.LIST).category_id != 0
```text
We save all resized images in DocLayNet_core/PNG_resized. We run the code for the splits `train`,`val` and 
`test`. 
We will need around 50GB of space. If this is too much, we can also play with smaller `new_h`, `new_w` values.


```python
doclaynet = dd.get_dataset("doclaynet")

df = doclaynet.dataflow.build(split="train", load_image=True)

scaler = ScaleTransform(h=1025,w=1025,new_h=2339,new_w=1654,interp="bilinear")

df = dd.MapData(df, scale_transform(scaler,True))
df.reset_state()

for idx, dp in enumerate(df):
    print(f"processing: {idx}")
    path = dd.get_dataset_dir_path() / "DocLayNet_core/PNG_resized" / dp.file_name
        dd.viz_handler.write_image(path, dp.image)
```

### We save all resized images in DocLayNet_core/PNG_resized. We run the code for the splits `train`,`val` and
`test`.
```python
doclaynet = dd.get_dataset("doclaynet")

df = doclaynet.dataflow.build(split="train", load_image=True)

scaler = ScaleTransform(h=1025,w=1025,new_h=2339,new_w=1654,interp="bilinear")

df = dd.MapData(df, scale_transform(scaler,True))
df.reset_state()

for idx, dp in enumerate(df):
    print(f"processing: {idx}")
    path = dd.get_dataset_dir_path() / "DocLayNet_core/PNG_resized" / dp.file_name
        dd.viz_handler.write_image(path, dp.image)
```

### for idx, dp in enumerate(df)
```text
## Step 2: Merging datasets

Doclaynet and Publaynet have different labels. Therefore we re-label some Doclaynet categories in order so 
that we
get `text`,`title`, `list`, `table`, `figure`. We already covered this [here](Evaluation.md).

After re-scaling the images, we also have to re-scale the ground truth label coordinates.  

One other thing we observed is that the style how `list` have been annotated is different to
how the annotation style in Publaynet: Doclaynet labels each list items separately in one bounding box wheres 
in 
Publaynet a `list` bounding box encloses all list items.    
    

```python
doclaynet = dd.get_dataset("doclaynet")

doclaynet.dataflow.categories.set_cat_to_sub_cat({
    dd.LayoutType.CAPTION: dd.DatasetType.PUBLAYNET,
    dd.LayoutType.FOOTNOTE: dd.DatasetType.PUBLAYNET,
    dd.LayoutType.FORMULA: dd.DatasetType.PUBLAYNET,
    dd.LayoutType.LIST: dd.DatasetType.PUBLAYNET,
    dd.LayoutType.PAGE_FOOTER: dd.DatasetType.PUBLAYNET,
    dd.LayoutType.PAGE_HEADER: dd.DatasetType.PUBLAYNET,
    dd.LayoutType.FIGURE: dd.DatasetType.PUBLAYNET,
    dd.LayoutType.SECTION_HEADER: dd.DatasetType.PUBLAYNET,
    dd.LayoutType.TABLE: dd.DatasetType.PUBLAYNET,
    dd.LayoutType.TEXT: dd.DatasetType.PUBLAYNET,
    dd.LayoutType.TITLE: dd.DatasetType.PUBLAYNET})

doclaynet.dataflow.categories._categories_update = [dd.LayoutType.TEXT,
                                                    dd.LayoutType.TITLE,
                                                    dd.LayoutType.LIST,
                                                    dd.LayoutType.TABLE,
                                                    dd.LayoutType.FIGURE]

df_doc = doclaynet.dataflow.build(split="train", resized=True)  
df_doc_val = doclaynet.dataflow.build(split="val", resized=True)
df_doc_test = doclaynet.dataflow.build(split="test", resized=True) 

scaler = ScaleTransform(h=1025,
                        w=1025,
                        new_h=2339,
                        new_w=1654,
                        interp="bilinear")

df_doc = dd.MapData(df_doc, filter_list_images)
df_doc = dd.MapData(df_doc, scale_transform(scaler))

df_doc_val = dd.MapData(df_doc_val, filter_list_images)
df_doc_val = dd.MapData(df_doc_val, scale_transform(scaler))

df_doc_test = dd.MapData(df_doc_test, filter_list_images)
df_doc_test = dd.MapData(df_doc_test, scale_transform(scaler))

publaynet = dd.get_dataset("publaynet")
df_pub = publaynet.dataflow.build(split="train", max_datapoints=25000)

merge = dd.MergeDataset(publaynet)
merge.explicit_dataflows(df_doc, df_doc_val, df_doc_test, df_pub)
merge.buffer_datasets()
merge.split_datasets(ratio=0.01)
```

### Example usage
```python
doclaynet = dd.get_dataset("doclaynet")

doclaynet.dataflow.categories.set_cat_to_sub_cat({
    dd.LayoutType.CAPTION: dd.DatasetType.PUBLAYNET,
    dd.LayoutType.FOOTNOTE: dd.DatasetType.PUBLAYNET,
    dd.LayoutType.FORMULA: dd.DatasetType.PUBLAYNET,
    dd.LayoutType.LIST: dd.DatasetType.PUBLAYNET,
    dd.LayoutType.PAGE_FOOTER: dd.DatasetType.PUBLAYNET,
    dd.LayoutType.PAGE_HEADER: dd.DatasetType.PUBLAYNET,
    dd.LayoutType.FIGURE: dd.DatasetType.PUBLAYNET,
    dd.LayoutType.SECTION_HEADER: dd.DatasetType.PUBLAYNET,
    dd.LayoutType.TABLE: dd.DatasetType.PUBLAYNET,
    dd.LayoutType.TEXT: dd.DatasetType.PUBLAYNET,
    dd.LayoutType.TITLE: dd.DatasetType.PUBLAYNET})

doclaynet.dataflow.categories._categories_update = [dd.LayoutType.TEXT,
                                                    dd.LayoutType.TITLE,
                                                    dd.LayoutType.LIST,
                                                    dd.LayoutType.TABLE,
                                                    dd.LayoutType.FIGURE]

df_doc = doclaynet.dataflow.build(split="train", resized=True)  
df_doc_val = doclaynet.dataflow.build(split="val", resized=True)
df_doc_test = doclaynet.dataflow.build(split="test", resized=True) 

scaler = ScaleTransform(h=1025,
                        w=1025,
                        new_h=2339,
                        new_w=1654,
                        interp="bilinear")

df_doc = dd.MapData(df_doc, filter_list_images)
df_doc = dd.MapData(df_doc, scale_transform(scaler))

df_doc_val = dd.MapData(df_doc_val, filter_list_images)
df_doc_val = dd.MapData(df_doc_val, scale_transform(scaler))

df_doc_test = dd.MapData(df_doc_test, filter_list_images)
df_doc_test = dd.MapData(df_doc_test, scale_transform(scaler))

publaynet = dd.get_dataset("publaynet")
df_pub = publaynet.dataflow.build(split="train", max_datapoints=25000)

merge = dd.MergeDataset(publaynet)
merge.explicit_dataflows(df_doc, df_doc_val, df_doc_test, df_pub)
merge.buffer_datasets()
merge.split_datasets(ratio=0.01)
```

### Example usage
```text
## Step 3: Saving the split as Artifact

To reproduce results and know what datapoint belongs to what split, we create and log an artifact that saves 
the 
mapping between `image_id` of each datapoint and its split class. 


```python
out = merge.get_ids_by_split()

table_rows=[]
for split, split_list in out.items():
    for ann_id in split_list:
        table_rows.append([split,ann_id])
table = wandb.Table(columns=["split","annotation_id"], data=table_rows)

wandb.init(project="layout_detection")

artifact = wandb.Artifact(merge.dataset_info.name, type='dataset')
artifact.add(table, "split")

wandb.log_artifact(artifact)
wandb.finish()
```

### Example usage
```python
out = merge.get_ids_by_split()

table_rows=[]
for split, split_list in out.items():
    for ann_id in split_list:
        table_rows.append([split,ann_id])
table = wandb.Table(columns=["split","annotation_id"], data=table_rows)

wandb.init(project="layout_detection")

artifact = wandb.Artifact(merge.dataset_info.name, type='dataset')
artifact.add(table, "split")

wandb.log_artifact(artifact)
wandb.finish()
```

### Example usage
```text
## Step 4: Setup training and monitoring training process

Next we setup our configuration and start our training. To monitor the training process with W&B dashboard 
we set `WANDB.USE_WANDB=True` as well as `WANDB.PROJECT=layout_detection`. We can stop the training process at
each step 
we want.


```python
path_config = dd.ModelCatalog.get_full_path_configs("layout/d2_model_0829999_layout.pth")
path_weights = dd.ModelCatalog.get_full_path_weights("layout/d2_model_0829999_layout.pth")
categories = dd.ModelCatalog.get_profile("layout/d2_model_0829999_layout.pth").categories
coco = dd.metric_registry.get("coco")

dd.train_d2_faster_rcnn(path_config_yaml=path_config,
                        dataset_train=merge,
                        path_weights=path_weights,
                        config_overwrite= ["SOLVER.IMS_PER_BATCH=2", 
                                           "SOLVER.MAX_ITER=240000", 
                                           "SOLVER.CHECKPOINT_PERIOD=4000",
                                           "SOLVER.STEPS=(160000, 190000)", 
                                           "TEST.EVAL_PERIOD=4000", 
                                           "MODEL.BACKBONE.FREEZE_AT=0",
                                           "WANDB.USE_WANDB=True", 
                                           "WANDB.PROJECT=layout_detection"],
                        log_dir="/path/to/dir",
                        build_train_config=None,
                        dataset_val=merge,
                        build_val_config=None,
                        metric_name=None,
                        metric=coco,
                        pipeline_component_name="ImageLayoutService")
```

### Example usage
```python
path_config = dd.ModelCatalog.get_full_path_configs("layout/d2_model_0829999_layout.pth")
path_weights = dd.ModelCatalog.get_full_path_weights("layout/d2_model_0829999_layout.pth")
categories = dd.ModelCatalog.get_profile("layout/d2_model_0829999_layout.pth").categories
coco = dd.metric_registry.get("coco")

dd.train_d2_faster_rcnn(path_config_yaml=path_config,
                        dataset_train=merge,
                        path_weights=path_weights,
                        config_overwrite= ["SOLVER.IMS_PER_BATCH=2", 
                                           "SOLVER.MAX_ITER=240000", 
                                           "SOLVER.CHECKPOINT_PERIOD=4000",
                                           "SOLVER.STEPS=(160000, 190000)", 
                                           "TEST.EVAL_PERIOD=4000", 
                                           "MODEL.BACKBONE.FREEZE_AT=0",
                                           "WANDB.USE_WANDB=True", 
                                           "WANDB.PROJECT=layout_detection"],
                        log_dir="/path/to/dir",
                        build_train_config=None,
                        dataset_val=merge,
                        build_val_config=None,
                        metric_name=None,
                        metric=coco,
                        pipeline_component_name="ImageLayoutService")
```

### Example usage
```text
## Step 5: Resume training

If we want to resume training we need to re-create our dataset split.

So we need to execute Step 2 to re-load annotations and the artifact with splits information from Weights & 
Biases. 
With `create_split_by_id` we can easily reconstruct our split and resume training. 

!!! info

    If we do not change the logging dir Detectron2 will use the last checkpoint we saved and resume training 
from 
    there. 


```python
wandb.init(project="layout_detection", resume=True)
artifact = wandb.use_artifact('jm76/layout_detection/merge_publaynet:v0', type='dataset')
table = artifact.get("split")

split_dict = defaultdict(list)
for row in table.data:
    split_dict[row[0]].append(row[1])
    
merge.create_split_by_id(split_dict)

dd.train_d2_faster_rcnn(path_config_yaml=path_config,
                        dataset_train=merge,
                        path_weights=path_weights,
                        config_overwrite=[
                                                 "SOLVER.IMS_PER_BATCH=2", 
                                                 "SOLVER.MAX_ITER=240000", 
                         "SOLVER.CHECKPOINT_PERIOD=4000",
                         "SOLVER.STEPS=(160000, 190000)", 
                         "TEST.EVAL_PERIOD=4000", 
                         "MODEL.BACKBONE.FREEZE_AT=0",
                         "WANDB.USE_WANDB=True", 
                         "WANDB.PROJECT=layout_detection"],
                         log_dir="/path/to/dir",
                         build_train_config=None,
                         dataset_val=merge,
                         build_val_config=None,
                         metric_name=None,
                         metric=coco,
                         pipeline_component_name="ImageLayoutService")
```

### Example usage
```python
wandb.init(project="layout_detection", resume=True)
artifact = wandb.use_artifact('jm76/layout_detection/merge_publaynet:v0', type='dataset')
table = artifact.get("split")

split_dict = defaultdict(list)
for row in table.data:
    split_dict[row[0]].append(row[1])
    
merge.create_split_by_id(split_dict)

dd.train_d2_faster_rcnn(path_config_yaml=path_config,
                        dataset_train=merge,
                        path_weights=path_weights,
                        config_overwrite=[
                                                 "SOLVER.IMS_PER_BATCH=2", 
                                                 "SOLVER.MAX_ITER=240000", 
                         "SOLVER.CHECKPOINT_PERIOD=4000",
                         "SOLVER.STEPS=(160000, 190000)", 
                         "TEST.EVAL_PERIOD=4000", 
                         "MODEL.BACKBONE.FREEZE_AT=0",
                         "WANDB.USE_WANDB=True", 
                         "WANDB.PROJECT=layout_detection"],
                         log_dir="/path/to/dir",
                         build_train_config=None,
                         dataset_val=merge,
                         build_val_config=None,
                         metric_name=None,
                         metric=coco,
                         pipeline_component_name="ImageLayoutService")
```

### Example usage
```text

```

---

# docs/tutorials/Training_And_Fine_Tuning.md - Fine tuning

<p align="center"> <img 
src="https://github.com/deepdoctection/deepdoctection/raw/master/docs/tutorials/_imgs/dd_logo.png" alt="Deep 
Doctection Logo" width="60%"> <h3 align="center"> </h3> </p>.

## Code Examples

### Example usage
```python
config_overwrite=["SOLVER.MAX_ITER=100000",    # (1)
                  "TEST.EVAL_PERIOD=20000",                           
                  "SOLVER.CHECKPOINT_PERIOD=20000",                   
                  "MODEL.BACKBONE.FREEZE_AT=0",                       
                  "SOLVER.BASE_LR=1e-3",                              
                  "SOLVER.IMS_PER_BATCH=2"] # (2)  

build_train_config = ["max_datapoints=86000"]  # (3)  

dd.train_d2_faster_rcnn(path_config_yaml=config_yaml_path,
                  dataset_train= doclaynet,
                  path_weights=weights_path,
                  config_overwrite=config_overwrite,
                  log_dir="/path/to/dir",
                  build_train_config=build_train_config,
                  dataset_val=doclaynet,
                  build_val_config=None,
                  metric=coco_metric,
                  pipeline_component_name="ImageLayoutService"
                 )
```

### Example usage
```text
1. Tensorpack equivalent:  TRAIN.LR_SCHEDULE=[100000], TRAIN.EVAL_PERIOD=40 (run a 500 samples * 40), 
   TRAIN.CHECKPOINT_PERIOD=40, BACKBONE.FREEZE_AT=0 (train the every layer of the backbone and do not freeze 
the bottom 
   layers), TRAIN.BASE_LR=1e-3.
2. If we encounter CUDA out of memory, we can reduce SOLVER.IMS_PER_BATCH to 1.
3. We can also change the setting if you want to train with less samples.


??? info "Output"

    |  category  | #box   |  category  | #box   |  category  | #box   |
    |:----------:|:-------|:----------:|:-------|:----------:|:-------|
    |   figure   | 39667  |   table    | 30070  |    list    | 161818 |
    |   title    | 171000 |    text    | 538568 |            |        |
    |   total    | 941123 |            |        |            |        |

     CUDNN_BENCHMARK: False
    DATALOADER:
      ASPECT_RATIO_GROUPING: True
      FILTER_EMPTY_ANNOTATIONS: True
      NUM_WORKERS: 4
      REPEAT_SQRT: True
      REPEAT_THRESHOLD: 0.0
      SAMPLER_TRAIN: TrainingSampler
    DATASETS:
      PRECOMPUTED_PROPOSAL_TOPK_TEST: 1000
      PRECOMPUTED_PROPOSAL_TOPK_TRAIN: 2000
      PROPOSAL_FILES_TEST: ()
      PROPOSAL_FILES_TRAIN: ()
      TEST: ('doclaynet',)
      TRAIN: ('doclaynet',)
    GLOBAL:
      HACK: 1.0
    INPUT:
      CROP:
        ENABLED: False
        SIZE: [0.9, 0.9]
        TYPE: relative_range
      FORMAT: BGR
      MASK_FORMAT: polygon
      MAX_SIZE_TEST: 1333
      MAX_SIZE_TRAIN: 1333
      MIN_SIZE_TEST: 800
      MIN_SIZE_TRAIN: (800, 1200)
      MIN_SIZE_TRAIN_SAMPLING: choice
      RANDOM_FLIP: horizontal
    MODEL:
      ANCHOR_GENERATOR:
        ANGLES: [[-90, 0, 90]]
        ASPECT_RATIOS: [[0.5, 1.0, 2.0]]
        NAME: DefaultAnchorGenerator
        OFFSET: 0.0
        SIZES: [[32], [64], [128], [256], [512]]
      BACKBONE:
        FREEZE_AT: 0
        NAME: build_resnet_fpn_backbone
      DEVICE: cuda
      FPN:
        FUSE_TYPE: sum
        IN_FEATURES: ['res2', 'res3', 'res4', 'res5']
        NORM: GN
        OUT_CHANNELS: 256
      KEYPOINT_ON: False
      LOAD_PROPOSALS: False
      MASK_ON: False
      META_ARCHITECTURE: GeneralizedRCNN
      PANOPTIC_FPN:
        COMBINE:
          ENABLED: True
          INSTANCES_CONFIDENCE_THRESH: 0.5
          OVERLAP_THRESH: 0.5
          STUFF_AREA_LIMIT: 4096
        INSTANCE_LOSS_WEIGHT: 1.0
      PIXEL_MEAN: [238.234, 238.14, 238.145]
      PIXEL_STD: [7.961, 7.876, 7.81]
      PROPOSAL_GENERATOR:
        MIN_SIZE: 0
        NAME: RPN
      RESNETS:
        DEFORM_MODULATED: False
        DEFORM_NUM_GROUPS: 1
        DEFORM_ON_PER_STAGE: [False, False, False, False]
        DEPTH: 50
        NORM: GN
        NUM_GROUPS: 32
        OUT_FEATURES: ['res2', 'res3', 'res4', 'res5']
        RES2_OUT_CHANNELS: 256
        RES5_DILATION: 1
        STEM_OUT_CHANNELS: 64
        STRIDE_IN_1X1: False
        WIDTH_PER_GROUP: 4
      RETINANET:
        BBOX_REG_LOSS_TYPE: smooth_l1
        BBOX_REG_WEIGHTS: (1.0, 1.0, 1.0, 1.0)
        FOCAL_LOSS_ALPHA: 0.25
        FOCAL_LOSS_GAMMA: 2.0
        IN_FEATURES: ['p3', 'p4', 'p5', 'p6', 'p7']
        IOU_LABELS: [0, -1, 1]
        IOU_THRESHOLDS: [0.4, 0.5]
        NMS_THRESH_TEST: 0.5
        NORM: 
        NUM_CLASSES: 80
        NUM_CONVS: 4
        PRIOR_PROB: 0.01
        SCORE_THRESH_TEST: 0.05
        SMOOTH_L1_LOSS_BETA: 0.1
        TOPK_CANDIDATES_TEST: 1000
      ROI_BOX_CASCADE_HEAD:
        BBOX_REG_WEIGHTS: ((10.0, 10.0, 5.0, 5.0), (20.0, 20.0, 10.0, 10.0), (30.0, 30.0, 15.0, 15.0))
        IOUS: (0.5, 0.6, 0.7)
      ROI_BOX_HEAD:
        BBOX_REG_LOSS_TYPE: smooth_l1
        BBOX_REG_LOSS_WEIGHT: 1.0
        BBOX_REG_WEIGHTS: (10.0, 10.0, 5.0, 5.0)
        CLS_AGNOSTIC_BBOX_REG: True
        CONV_DIM: 256
        FC_DIM: 1024
        FED_LOSS_FREQ_WEIGHT_POWER: 0.5
        FED_LOSS_NUM_CLASSES: 50
        NAME: FastRCNNConvFCHead
        NORM: 
        NUM_CONV: 0
        NUM_FC: 2
        POOLER_RESOLUTION: 7
        POOLER_SAMPLING_RATIO: 0
        POOLER_TYPE: ROIAlignV2
        SMOOTH_L1_BETA: 0.0
        TRAIN_ON_PRED_BOXES: False
        USE_FED_LOSS: False
        USE_SIGMOID_CE: False
      ROI_HEADS:
        BATCH_SIZE_PER_IMAGE: 512
        IN_FEATURES: ['p2', 'p3', 'p4', 'p5']
        IOU_LABELS: [0, 1]
        IOU_THRESHOLDS: [0.5]
        NAME: CascadeROIHeads
        NMS_THRESH_TEST: 0.001
        NUM_CLASSES: 5
        POSITIVE_FRACTION: 0.25
        PROPOSAL_APPEND_GT: True
        SCORE_THRESH_TEST: 0.1
      ROI_KEYPOINT_HEAD:
        CONV_DIMS: (512, 512, 512, 512, 512, 512, 512, 512)
        LOSS_WEIGHT: 1.0
        MIN_KEYPOINTS_PER_IMAGE: 1
        NAME: KRCNNConvDeconvUpsampleHead
        NORMALIZE_LOSS_BY_VISIBLE_KEYPOINTS: True
        NUM_KEYPOINTS: 17
        POOLER_RESOLUTION: 14
        POOLER_SAMPLING_RATIO: 0
        POOLER_TYPE: ROIAlignV2
      ROI_MASK_HEAD:
        CLS_AGNOSTIC_MASK: False
        CONV_DIM: 256
        NAME: MaskRCNNConvUpsampleHead
        NORM: 
        NUM_CONV: 4
        POOLER_RESOLUTION: 14
        POOLER_SAMPLING_RATIO: 0
        POOLER_TYPE: ROIAlignV2
      RPN:
        BATCH_SIZE_PER_IMAGE: 256
        BBOX_REG_LOSS_TYPE: smooth_l1
        BBOX_REG_LOSS_WEIGHT: 1.0
        BBOX_REG_WEIGHTS: (1.0, 1.0, 1.0, 1.0)
        BOUNDARY_THRESH: -1
        CONV_DIMS: [-1]
        HEAD_NAME: StandardRPNHead
        IN_FEATURES: ['p2', 'p3', 'p4', 'p5', 'p6']
        IOU_LABELS: [0, -1, 1]
        IOU_THRESHOLDS: [0.3, 0.7]
        LOSS_WEIGHT: 1.0
        NMS_THRESH: 0.7
        POSITIVE_FRACTION: 0.5
        POST_NMS_TOPK_TEST: 1000
        POST_NMS_TOPK_TRAIN: 1000
        PRE_NMS_TOPK_TEST: 1000
        PRE_NMS_TOPK_TRAIN: 2000
        SMOOTH_L1_BETA: 0.0
      SEM_SEG_HEAD:
        COMMON_STRIDE: 4
        CONVS_DIM: 128
        IGNORE_VALUE: 255
        IN_FEATURES: ['p2', 'p3', 'p4', 'p5']
        LOSS_WEIGHT: 1.0
        NAME: SemSegFPNHead
        NORM: GN
        NUM_CLASSES: 54
      WEIGHTS: /media/janis/Elements/.cache/deepdoctection/weights/layout/d2_model_0829999_layout_inf_only.pt
    NMS_THRESH_CLASS_AGNOSTIC: 0.001
    OUTPUT_DIR: /home/janis/Documents/Experiments/Tests/
    SEED: -1
    SOLVER:
      AMP:
        ENABLED: False
      BASE_LR: 0.001
      BASE_LR_END: 0.0
      BIAS_LR_FACTOR: 1.0
      CHECKPOINT_PERIOD: 20000
      CLIP_GRADIENTS:
        CLIP_TYPE: value
        CLIP_VALUE: 1.0
        ENABLED: False
        NORM_TYPE: 2.0
      GAMMA: 0.1
      IMS_PER_BATCH: 2
      LR_SCHEDULER_NAME: WarmupMultiStepLR
      MAX_ITER: 100000
      MOMENTUM: 0.9
      NESTEROV: False
      NUM_DECAYS: 3
      REFERENCE_WORLD_SIZE: 0
      RESCALE_INTERVAL: False
      STEPS: (60000, 80000)
      WARMUP_FACTOR: 0.001
      WARMUP_ITERS: 1000
      WARMUP_METHOD: linear
      WEIGHT_DECAY: 0.0001
      WEIGHT_DECAY_BIAS: None
      WEIGHT_DECAY_NORM: 0.0
    TEST:
      AUG:
        ENABLED: False
        FLIP: True
        MAX_SIZE: 4000
        MIN_SIZES: (400, 500, 600, 700, 800, 900, 1000, 1100, 1200)
      DETECTIONS_PER_IMAGE: 100
      DO_EVAL: True
      EVAL_PERIOD: 20000
      EXPECTED_RESULTS: []
      KEYPOINT_OKS_SIGMAS: []
      PRECISE_BN:
        ENABLED: False
        NUM_ITER: 200
    VERSION: 2
    VIS_PERIOD: 0
    WANDB:
      PROJECT: None
      REPO: deepdoctection
      USE_WANDB: False

## Example: Tensorpack Training Scripts

The following are the training scripts for the cell and row/column detection models 
trained on Pubtabnet.

### Cell detection

```python

 import os
 import deepdoctection as dd

 pubtabnet = dd.get_dataset("pubtabnet")
 pubtabnet.dataflow.categories.filter_categories(categories="cell")
 
 path_config_yaml=os.path.join(dd.get_configs_dir_path(),"tp/cell/conf_frcnn_cell.yaml")
 path_weights = "/path/to/dir/model-3540000.data-00000-of-00001"
 
config_overwrite=["TRAIN.LR_SCHEDULE=2x", 
                "TRAIN.STEPS_PER_EPOCH=500",
                "TRAIN.EVAL_PERIOD=20",
                "PREPROC.TRAIN_SHORT_EDGE_SIZE=[400,600]",
                "TRAIN.CHECKPOINT_PERIOD=20",
                "BACKBONE.FREEZE_AT=0"]
  
 dataset_train = pubtabnet
 build_train_config=["max_datapoints=500000"]
 
 dataset_val = pubtabnet
 build_val_config = ["max_datapoints=4000"]
 
 coco_metric = dd.metric_registry.get("coco")
 coco_metric.set_params(max_detections=[50,200,600], 
                        area_range=[[0,1000000],[0,200],[200,800],[800,1000000]])
 
 dd.train_faster_rcnn(path_config_yaml=path_config_yaml,
                      dataset_train=dataset_train,
                      path_weights=path_weights,
                      config_overwrite=config_overwrite,
                      log_dir="/path/to/dir/train",
                      build_train_config=build_train_config,
                      dataset_val=dataset_val,
                      build_val_config=build_val_config,
                      metric=coco_metric,
                      pipeline_component_name="ImageLayoutService"
                      )
```

### Cell detection
```python
import os
 import deepdoctection as dd

 pubtabnet = dd.get_dataset("pubtabnet")
 pubtabnet.dataflow.categories.filter_categories(categories="cell")
 
 path_config_yaml=os.path.join(dd.get_configs_dir_path(),"tp/cell/conf_frcnn_cell.yaml")
 path_weights = "/path/to/dir/model-3540000.data-00000-of-00001"
 
config_overwrite=["TRAIN.LR_SCHEDULE=2x", 
                "TRAIN.STEPS_PER_EPOCH=500",
                "TRAIN.EVAL_PERIOD=20",
                "PREPROC.TRAIN_SHORT_EDGE_SIZE=[400,600]",
                "TRAIN.CHECKPOINT_PERIOD=20",
                "BACKBONE.FREEZE_AT=0"]
  
 dataset_train = pubtabnet
 build_train_config=["max_datapoints=500000"]
 
 dataset_val = pubtabnet
 build_val_config = ["max_datapoints=4000"]
 
 coco_metric = dd.metric_registry.get("coco")
 coco_metric.set_params(max_detections=[50,200,600], 
                        area_range=[[0,1000000],[0,200],[200,800],[800,1000000]])
 
 dd.train_faster_rcnn(path_config_yaml=path_config_yaml,
                      dataset_train=dataset_train,
                      path_weights=path_weights,
                      config_overwrite=config_overwrite,
                      log_dir="/path/to/dir/train",
                      build_train_config=build_train_config,
                      dataset_val=dataset_val,
                      build_val_config=build_val_config,
                      metric=coco_metric,
                      pipeline_component_name="ImageLayoutService"
                      )
```

### Example usage
```text
### Row and Column detection

```python

 import os
 import deepdoctection as dd
 
 pubtabnet = dd.get_dataset("pubtabnet")
 pubtabnet.dataflow.categories.set_cat_to_sub_cat({"item":"item"})
 pubtabnet.dataflow.categories.filter_categories(["row","column"])
 
 path_config_yaml=os.path.join(dd.get_configs_dir_path(),"tp/rows/conf_frcnn_rows.yaml")
 path_weights = os.path.join(dd.get_weights_dir_path(),"item/model-1750000.data-00000-of-00001")
 
config_overwrite=["TRAIN.STEPS_PER_EPOCH=5000",
                  "TRAIN.EVAL_PERIOD=20",
                  "TRAIN.STARTING_EPOCH=1",
                  "PREPROC.TRAIN_SHORT_EDGE_SIZE=[400,600]",
                  "TRAIN.CHECKPOINT_PERIOD=20",
                  "BACKBONE.FREEZE_AT=0"]
  
 dataset_train = pubtabnet
 build_train_config=["max_datapoints=500000","rows_and_cols=True"]
 
 dataset_val = pubtabnet
 build_val_config = ["max_datapoints=4000","rows_and_cols=True"]
 
 dd.train_faster_rcnn(path_config_yaml=path_config_yaml,
                      dataset_train=pubtabnet,
                      path_weights=path_weights,
                      config_overwrite=config_overwrite,
                      log_dir="/path/to/dir/train",
                      build_train_config=build_train_config,
                      dataset_val=dataset_val,
                      build_val_config=build_val_config,
                      metric_name="coco",
                      pipeline_component_name="ImageLayoutService"
                      )
```

### Row and Column detection
```python
import os
 import deepdoctection as dd
 
 pubtabnet = dd.get_dataset("pubtabnet")
 pubtabnet.dataflow.categories.set_cat_to_sub_cat({"item":"item"})
 pubtabnet.dataflow.categories.filter_categories(["row","column"])
 
 path_config_yaml=os.path.join(dd.get_configs_dir_path(),"tp/rows/conf_frcnn_rows.yaml")
 path_weights = os.path.join(dd.get_weights_dir_path(),"item/model-1750000.data-00000-of-00001")
 
config_overwrite=["TRAIN.STEPS_PER_EPOCH=5000",
                  "TRAIN.EVAL_PERIOD=20",
                  "TRAIN.STARTING_EPOCH=1",
                  "PREPROC.TRAIN_SHORT_EDGE_SIZE=[400,600]",
                  "TRAIN.CHECKPOINT_PERIOD=20",
                  "BACKBONE.FREEZE_AT=0"]
  
 dataset_train = pubtabnet
 build_train_config=["max_datapoints=500000","rows_and_cols=True"]
 
 dataset_val = pubtabnet
 build_val_config = ["max_datapoints=4000","rows_and_cols=True"]
 
 dd.train_faster_rcnn(path_config_yaml=path_config_yaml,
                      dataset_train=pubtabnet,
                      path_weights=path_weights,
                      config_overwrite=config_overwrite,
                      log_dir="/path/to/dir/train",
                      build_train_config=build_train_config,
                      dataset_val=dataset_val,
                      build_val_config=build_val_config,
                      metric_name="coco",
                      pipeline_component_name="ImageLayoutService"
                      )
```

### Example usage
```text

```

---

# requirements.txt - # This file is autogenerated by pip-compile with Python 3.9

attrs==21.4.0 catalogue==2.0.10 certifi==2021.10.8 charset-normalizer==2.0.12 filelock==3.6.0 fsspec==2023.9.2
huggingface-hub==0.28.1 idna==3.3 importlib-metadata==7.1.0 jsonlines==3.1.0 lazy-imports==0.3.1 mock==4.0.3 
networkx==2.7.1 numpy==1.26.4 packaging==21.3 pillow==10.0.1 pyparsing==3.0.7 pypdf==6.0.0 pypdfium2==4.30.0 
pyyaml==6.0.1 pyzmq==24.0.1 requests==2.27.1 scipy==1.13.1 tabulate==0.8.10 termcolor==2.0.1 tqdm==4.64.0 
typing-extensions==4.1.1 urllib3==1.26.8 zipp==3.7.0.

---

# tests/test_objects/test_file.txt - test_file

imagesg/g/t/h/gth35e00/2024525661.tif 11 imagesi/i/y/k/iyk38c00/512015827+-5827.tif 0 
imagesr/r/r/e/rre21e00/87103403.tif 0 imagesk/k/s/u/ksu44c00/03636607.tif 4 
imagesr/r/a/i/rai09d00/50437856-7857.tif 14.

---



---

## Code Analysis

### Classes

#### deepdoctection/analyzer/factory.py

**`class ServiceFactory`**
  - Location: line 88-1723
  - Factory class for building various components of the deepdoctection analyzer pipeline.
    This class uses the `cfg` configuration object from `config.py`, which is an instance of the `AttrDict` 
class.
    The configuration is not passed explicitly in an `__init__` method but is accessed directly within the 
methods.
    The class provides static methods to build different services and detectors required for the pipeline, 
such as
    layout detectors, OCR detectors, table segmentation services, and more. The methods disentangle the 
creation
    of predictors (e.g., `ObjectDetector`, `TextRecognizer`) from the configuration, allowing for flexible and
    modular construction of the pipeline components.
    Extending the Class:
    This class can be extended by using inheritance and adding new methods or overriding existing ones.
    To extend the configuration attributes, you can modify the `cfg` object in `config.py` to include new
    settings or parameters required for the new methods.
  - Public methods (25):
    - `build_analyzer(config: AttrDict) -> DoctectionPipe`
    - `build_doctr_word_detector(config: AttrDict) -> DoctrTextlineDetector`
    - `build_doctr_word_detector_service(detector: DoctrTextlineDetector) -> ImageLayoutService`
    - `build_layout_detector(
        config: AttrDict, mode: str
    ) -> Union[D2FrcnnDetector, TPFrcnnDetector, HFDetrDerivedDetector, D2FrcnnTracingDetector]`
    - `build_layout_link_matching_service(config: AttrDict) -> MatchingService`
    - `build_layout_nms_service(config: AttrDict) -> AnnotationNmsService`
    - `build_layout_service(config: AttrDict, detector: ObjectDetector, mode: str) -> ImageLayoutService`
    - `build_line_matching_service(config: AttrDict) -> MatchingService`
    - `build_ocr_detector(config: AttrDict) -> Union[TesseractOcrDetector, DoctrTextRecognizer, 
TextractOcrDetector]`
    - `build_padder(config: AttrDict, mode: str) -> PadTransform`
    - `build_page_parsing_service(config: AttrDict) -> PageParsingService`
    - `build_pdf_miner_text_service(detector: PdfMiner) -> TextExtractionService`
    - `build_pdf_text_detector(config: AttrDict) -> PdfPlumberTextDetector`
    - `build_rotation_detector(rotator_name: Literal["tesseract", "doctr"]) -> RotationTransformer`
    - `build_sequence_classifier(config: AttrDict) -> Union[LayoutSequenceModels, LmSequenceModels]`
    - `build_sequence_classifier_service(
        config: AttrDict, sequence_classifier: Union[LayoutSequenceModels, LmSequenceModels]
    ) -> LMSequenceClassifierService`
    - `build_sub_image_service(config: AttrDict, detector: ObjectDetector, mode: str) -> 
SubImageLayoutService`
    - `build_table_refinement_service(config: AttrDict) -> TableSegmentationRefinementService`
    - `build_table_segmentation_service(
        config: AttrDict,
        detector: ObjectDetector,
    ) -> Union[PubtablesSegmentationService, TableSegmentationService]`
    - `build_text_extraction_service(
        config: AttrDict, detector: Union[TesseractOcrDetector, DoctrTextRecognizer, TextractOcrDetector]
    ) -> TextExtractionService`
    - `build_text_order_service(config: AttrDict) -> TextOrderService`
    - `build_token_classifier(config: AttrDict) -> Union[LayoutTokenModels, LmTokenModels]`
    - `build_token_classifier_service(
        config: AttrDict, token_classifier: Union[LayoutTokenModels, LmTokenModels]
    ) -> LMTokenClassifierService`
    - `build_transform_service(transform_predictor: ImageTransformer) -> SimpleTransformService`
    - `build_word_matching_service(config: AttrDict) -> MatchingService`
  - Private methods (44):
    - `_build_doctr_word_detector(
        weights: str, profile: ModelProfile, device: Literal["cuda", "cpu"], lib: Literal["PT", "TF"]
    ) -> DoctrTextlineDetector`
    - `_build_doctr_word_detector_service(detector: DoctrTextlineDetector) -> ImageLayoutService`
    - `_build_layout_detector(
        weights: str,
        filter_categories: list[str],
        profile: ModelProfile,
        device: Literal["cpu", "cuda"],
        lib: Literal["TF", "PT", None],
    ) -> Union[D2FrcnnDetector, TPFrcnnDetector, HFDetrDerivedDetector, D2FrcnnTracingDetector]`
    - `_build_layout_link_matching_service(
        parental_categories: Union[Sequence[ObjectTypes], ObjectTypes, None],
        child_categories: Union[Sequence[ObjectTypes], ObjectTypes, None],
    ) -> MatchingService`
    - `_build_layout_nms_service(
        nms_pairs: Sequence[Sequence[Union[ObjectTypes, str]]],
        thresholds: Union[float, Sequence[float]],
        priority: Sequence[Union[ObjectTypes, str, None]],
    ) -> AnnotationNmsService`
    - `_build_layout_service(detector: ObjectDetector, padder: PadTransform) -> ImageLayoutService`
    - `_build_line_matching_service(
        matching_rule: Literal["iou", "ioa"], threshold: float, max_parent_only: bool
    ) -> MatchingService`
    - `_build_ocr_detector(
        use_tesseract: bool,
        use_doctr: bool,
        use_textract: bool,
        ocr_config_path: str,
        languages: Union[list[str], None],
        weights: str,
        credentials_kwargs: dict[str, Any],
        lib: Literal["TF", "PT", None],
        device: Literal["cuda", "cpu"],
    ) -> Union[TesseractOcrDetector, DoctrTextRecognizer, TextractOcrDetector]`
    - `_build_padder(top: int, right: int, bottom: int, left: int) -> PadTransform`
    - `_build_page_parsing_service(
        text_container: Union[ObjectTypes, str],
        floating_text_block_categories: Sequence[str],
        include_residual_text_container: bool,
    ) -> PageParsingService`
    - `_build_pdf_miner_text_service(detector: PdfMiner) -> TextExtractionService`
    - `_build_pdf_text_detector(x_tolerance: int, y_tolerance: int) -> PdfPlumberTextDetector`
    - `_build_rotation_detector(rotator_name: Literal["tesseract", "doctr"]) -> RotationTransformer`
    - `_build_sequence_classifier(
        config_path: str,
        weights_path: str,
        categories: Mapping[int, Union[ObjectTypes, str]],
        device: Literal["cuda", "cpu"],
        use_xlm_tokenizer: bool,
        model_wrapper: str,
    ) -> Union[LayoutSequenceModels, LmSequenceModels]`
    - `_build_sequence_classifier_service(
        sequence_classifier: Union[LayoutSequenceModels, LmSequenceModels], use_other_as_default_category: 
bool
    ) -> LMSequenceClassifierService`
    - `_build_sub_image_service(
        detector: ObjectDetector, padder: Optional[PadTransform], exclude_category_names: list[ObjectTypes]
    ) -> SubImageLayoutService`
    - `_build_table_refinement_service(
        table_names: Sequence[ObjectTypes], cell_names: Sequence[ObjectTypes]
    ) -> TableSegmentationRefinementService`
    - `_build_table_segmentation_service(
        detector: ObjectDetector,
        segment_rule: Literal["iou", "ioa"],
        threshold_rows: float,
        threshold_cols: float,
        tile_table_with_items: bool,
        remove_iou_threshold_rows: float,
        remove_iou_threshold_cols: float,
        table_name: Union[ObjectTypes, str],
        cell_names: Sequence[Union[ObjectTypes, str]],
        spanning_cell_names: Sequence[Union[ObjectTypes, str]],
        item_names: Sequence[Union[ObjectTypes, str]],
        sub_item_names: Sequence[Union[ObjectTypes, str]],
        item_header_cell_names: Sequence[Union[ObjectTypes, str]],
        item_header_thresholds: Sequence[float],
        stretch_rule: Literal["left", "equal"],
    ) -> Union[PubtablesSegmentationService, TableSegmentationService]`
    - `_build_text_extraction_service(
        detector: Union[TesseractOcrDetector, DoctrTextRecognizer, TextractOcrDetector],
        extract_from_roi: Union[Sequence[ObjectTypes], ObjectTypes, None] = None,
    ) -> TextExtractionService`
    - `_build_text_order_service(
        text_container: str,
        text_block_categories: Sequence[str],
        floating_text_block_categories: Sequence[str],
        include_residual_text_container: bool,
        starting_point_tolerance: float,
        broken_line_tolerance: float,
        height_tolerance: float,
        paragraph_break: float,
    ) -> TextOrderService`
    - `_build_token_classifier(
        config_path: str,
        weights_path: str,
        categories: Mapping[int, Union[ObjectTypes, str]],
        device: Literal["cpu", "cuda"],
        use_xlm_tokenizer: bool,
        model_wrapper: str,
    ) -> Union[LayoutTokenModels, LmTokenModels]`
    - `_build_token_classifier_service(
        token_classifier: Union[LayoutTokenModels, LmTokenModels],
        use_other_as_default_category: bool,
        segment_positions: Union[LayoutType, Sequence[LayoutType], None],
        sliding_window_stride: int,
    ) -> LMTokenClassifierService`
    - `_build_transform_service(transform_predictor: ImageTransformer) -> SimpleTransformService`
    - `_build_word_matching_service(
        matching_rule: Literal["iou", "ioa"],
        threshold: float,
        max_parent_only: bool,
        parental_categories: Union[Sequence[ObjectTypes], ObjectTypes, None],
        text_container: Union[Sequence[ObjectTypes], ObjectTypes, None],
    ) -> MatchingService`
    - `_get_doctr_word_detector_kwargs_from_config(config: AttrDict) -> dict[str, Any]`
    - `_get_layout_detector_kwargs_from_config(config: AttrDict, mode: str) -> dict[str, Any]`
    - `_get_layout_link_matching_service_kwargs_from_config(config: AttrDict) -> dict[str, Any]`
    - `_get_layout_nms_service_kwargs_from_config(config: AttrDict) -> dict[str, Any]`
    - `_get_layout_service_kwargs_from_config(config: AttrDict, mode: str) -> dict[str, Any]`
    - `_get_line_matching_service_kwargs_from_config(config: AttrDict) -> dict[str, Any]`
    - `_get_ocr_detector_kwargs_from_config(config: AttrDict) -> dict[str, Any]`
    - `_get_padder_kwargs_from_config(config: AttrDict, mode: str) -> dict[str, Any]`
    - `_get_page_parsing_service_kwargs_from_config(config: AttrDict) -> dict[str, Any]`
    - `_get_pdf_text_detector_kwargs_from_config(config: AttrDict) -> dict[str, Any]`
    - `_get_sequence_classifier_kwargs_from_config(config: AttrDict) -> dict[str, Any]`
    - `_get_sequence_classifier_service_kwargs_from_config(config: AttrDict) -> dict[str, Any]`
    - `_get_sub_image_layout_service_kwargs_from_config(detector: ObjectDetector, mode: str) -> dict[str, 
Any]`
    - `_get_table_refinement_service_kwargs_from_config(config: AttrDict) -> dict[str, Any]`
    - `_get_table_segmentation_service_kwargs_from_config(config: AttrDict, detector_name: str) -> dict[str, 
Any]`
    - `_get_text_extraction_service_kwargs_from_config(config: AttrDict) -> dict[str, Any]`
    - `_get_text_order_service_kwargs_from_config(config: AttrDict) -> dict[str, Any]`
    - `_get_token_classifier_kwargs_from_config(config: AttrDict) -> dict[str, Any]`
    - `_get_token_classifier_service_kwargs_from_config(config: AttrDict) -> dict[str, Any]`
    - `_get_word_matching_service_kwargs_from_config(config: AttrDict) -> dict[str, Any]`

#### deepdoctection/dataflow/base.py

**`class DataFlowReentrantGuard`**
  - Location: line 20-38
  - A tool to enforce non-reentrancy.
    Mostly used on DataFlow whose `get_data` is stateful,
    so that multiple instances of the iterator cannot co-exist.
  - Private methods (3):
    - `__enter__(self) -> None`
    - `__exit__(self, exc_type, exc_val, exc_tb)`
    - `__init__(self) -> None`

**`class DataFlow`**
  - Location: line 41-112
  - Base class for all DataFlow
  - Public methods (1):
    - `reset_state(self) -> None`
  - Private methods (2):
    - `__iter__(self) -> Iterator[Any]`
    - `__len__(self) -> int`

**`class RNGDataFlow`**
  - Location: line 115-126
  - Inherits: DataFlow, ABC
  - A DataFlow with RNG
  - Public methods (1):
    - `reset_state(self) -> None`

**`class ProxyDataFlow`**
  - Location: line 129-163
  - Inherits: DataFlow
  - Base class for DataFlow that proxies another.
    Every method is proxied to ``self.df`` unless overriden by a subclass.
  - Public methods (1):
    - `reset_state(self) -> None`
  - Private methods (3):
    - `__init__(self, df: DataFlow) -> None`
    - `__iter__(self) -> Iterator[Any]`
    - `__len__(self) -> int`

#### deepdoctection/dataflow/common.py

**`class FlattenData`**
  - Location: line 64-82
  - Inherits: ProxyDataFlow
  - FlattenData flattens an iterator within a datapoint. Will flatten the datapoint if it is a list or a 
tuple.
    Example:
    ```python
    dp_1 = ['a','b']
    dp_2 = ['c','d']
    yields:
    ['a'], ['b'], ['c'], ['d']
    ```
  - Private methods (1):
    - `__iter__(self) -> Any`

**`class MapData`**
  - Location: line 85-114
  - Inherits: ProxyDataFlow
  - MapData applies a mapper/filter on the datapoints of a DataFlow.
    Notes:
    1. Please ensure that `func` does not modify its arguments in-place unless it is safe.
    2. If some datapoints are discarded, `len(MapData(ds))` will be incorrect.
    Example:
    ```python
    df = ... # a DataFlow where each datapoint is [img, label]
    ds = MapData(ds, lambda dp: [dp[0] * 255, dp[1]])
    ```
  - Private methods (2):
    - `__init__(self, df: DataFlow, func: Callable[[Any], Any]) -> None`
    - `__iter__(self) -> Iterator[Any]`

**`class MapDataComponent`**
  - Location: line 117-153
  - Inherits: MapData
  - MapDataComponent applies a mapper/filter on a component of a datapoint.
    Notes:
    1. This DataFlow itself does not modify the datapoints. Please ensure that `func` does not modify its 
arguments
    in-place unless it is safe.
    2. If some datapoints are discarded, `len(MapDataComponent(ds, ..))` will be incorrect.
    Example:
    ```python
    df = ... # a DataFlow where each datapoint is [img, label]
    ds = MapDataComponent(ds, lambda img: img * 255, 0)  # maps the 0th component
    ```
  - Private methods (2):
    - `__init__(self, df: DataFlow, func: Callable[[Any], Any], index: Union[int, str] = 0) -> None`
    - `_mapper(self, dp: Any) -> Any`

**`class RepeatedData`**
  - Location: line 156-195
  - Inherits: ProxyDataFlow
  - RepeatedData takes datapoints from another DataFlow and produces them until they are exhausted for a 
certain number
    of repetitions.
    Example:
    ```python
    dp1, dp2, .... dpn, dp1, dp2, ....dpn
    ```
  - Private methods (3):
    - `__init__(self, df: DataFlow, num: int) -> None`
    - `__iter__(self) -> Iterator[Any]`
    - `__len__(self) -> int`

**`class ConcatData`**
  - Location: line 198-229
  - Inherits: DataFlow
  - ConcatData concatenates multiple DataFlows. Produces datapoints from each DataFlow and starts the next 
when one
    DataFlow is exhausted. Use this DataFlow to process multiple .pdf files in one step.
    Example:
    ```python
    df_1 = analyzer.analyze(path="path/to/pdf_1.pdf")
    df_2 = analyzer.analyze(path="path/to/pdf_2.pdf")
    df = ConcatData([df_1, df_2])
    ```
  - Public methods (1):
    - `reset_state(self) -> None`
  - Private methods (3):
    - `__init__(self, df_lists: list[DataFlow]) -> None`
    - `__iter__(self) -> Iterator[Any]`
    - `__len__(self) -> int`

**`class JoinData`**
  - Location: line 232-286
  - Inherits: DataFlow
  - JoinData joins the components from each DataFlow. See below for its behavior. It is not possible to join a
DataFlow
    that produces lists with one that produces dictionaries.
    Example:
    ```python
    df1 produces: [[c1], [c2]]
    df2 produces: [[c3], [c4]]
    joined: [[c1, c3], [c2, c4]]
    df1 produces: {"a": c1, "b": c2}
    df2 produces: {"c": c3}
    joined: {"a": c1, "b": c2, "c": c3}
    ```
    `JoinData` stops once the first DataFlow raises a `StopIteration`.
  - Public methods (1):
    - `reset_state(self) -> None`
  - Private methods (3):
    - `__init__(self, df_lists: list[DataFlow]) -> None`
    - `__iter__(self) -> Iterator[Any]`
    - `__len__(self) -> int`

**`class BatchData`**
  - Location: line 289-337
  - Inherits: ProxyDataFlow
  - BatchData stacks datapoints into batches. It produces datapoints with the same number of components as 
`df`, but
    each datapoint is now a list of datapoints.
    Example:
    ```python
    df produces: [[c1], [c2], [c3], [c4]]
    batch_size = 2
    yields: [[c1, c2], [c3, c4]]
    ```
  - Private methods (3):
    - `__init__(self, df: DataFlow, batch_size: int, remainder: bool = False) -> None`
    - `__iter__(self) -> Iterator[Any]`
    - `__len__(self) -> int`

#### deepdoctection/dataflow/custom.py

**`class CacheData`**
  - Location: line 37-97
  - Inherits: ProxyDataFlow
  - Completely cache the first pass of a DataFlow in memory,
    and produce from the cache thereafter.
    Note:
    The user should not stop the iterator before it has reached the end.
    Otherwise, the cache may be incomplete.
    Example:
    ```python
    df_list = CacheData(df).get_cache() # Buffers the whole dataflow and return a list of all datapoints
    ```
  - Public methods (2):
    - `get_cache(self) -> list[Any]`
    - `reset_state(self) -> None`
  - Private methods (2):
    - `__init__(self, df: DataFlow, shuffle: bool = False) -> None`
    - `__iter__(self) -> Iterator[Any]`

**`class CustomDataFromList`**
  - Location: line 100-175
  - Inherits: DataFromList
  - Wraps a list of datapoints to a dataflow. Compared to `Tensorpack.DataFlow.DataFromList`
    implementation you can specify a number of datapoints after that the iteration stops.
    You can also pass a re-balance function that filters on that list.
    Example:
    ```python
    def filter_first(lst):
    return lst.pop(0)
    df = CustomDataFromList(lst=[["a","b"],["c","d"]], rebalance_func=filter_first)
    df.reset_state()
    will yield:
    ["c","d"]
    ```
  - Private methods (3):
    - `__init__(
        self,
        lst: list[Any],
        shuffle: bool = False,
        max_datapoints: Optional[int] = None,
        rebalance_func: Optional[Callable[[list[Any]], list[Any]]] = None,
    )`
    - `__iter__(self) -> Iterator[Any]`
    - `__len__(self) -> int`

**`class CustomDataFromIterable`**
  - Location: line 178-203
  - Inherits: DataFromIterable
  - Wrap an iterable of datapoints to a dataflow. Can stop iteration after max_datapoints.
  - Private methods (2):
    - `__init__(self, iterable: Iterable[Any], max_datapoints: Optional[int] = None)`
    - `__iter__(self) -> Any`

#### deepdoctection/dataflow/custom_serialize.py

**`class FileClosingIterator`**
  - Location: line 58-112
  - A custom iterator that closes the file object once the iteration is complete.
    This iterator is used to ensure that the file object is properly closed after
    reading the data from it. It is used in the context of reading data from a file
    in a streaming manner, where the data is not loaded into memory all at once.
    Example:
    ```python
    file = open(path, "r")
    iterator = Reader(file)
    closing_iterator = FileClosingIterator(file, iter(iterator))
    df = CustomDataFromIterable(closing_iterator, max_datapoints=max_datapoints)
    ```
  - Private methods (3):
    - `__init__(self, file_obj: TextIO, iterator: Iterator[Any])`
    - `__iter__(self) -> FileClosingIterator`
    - `__next__(self) -> Any`

**`class SerializerJsonlines`**
  - Location: line 115-172
  - Serialize a dataflow from a jsonlines file. Alternatively, save a dataflow of `JSON` objects to a `.jsonl`
file.
    Example:
    ```python
    df = SerializerJsonlines.load("path/to/file.jsonl")
    df.reset_state()
    for dp in df:
    ... # is a dict
    ```
  - Public methods (2):
    - `load(path: PathLikeOrStr, max_datapoints: Optional[int] = None) -> CustomDataFromIterable`
    - `save(df: DataFlow, path: PathLikeOrStr, file_name: str, max_datapoints: Optional[int] = None) -> None`

**`class SerializerTabsepFiles`**
  - Location: line 175-229
  - Serialize a dataflow from a tab separated text file. Alternatively, save a dataflow of plain text
    to a `.txt` file.
    Example:
    ```python
    df = SerializerTabsepFiles.load("path/to/file.txt")
    will yield each text line of the file.
    ```
  - Public methods (2):
    - `load(path: PathLikeOrStr, max_datapoints: Optional[int] = None) -> CustomDataFromList`
    - `save(df: DataFlow, path: PathLikeOrStr, file_name: str, max_datapoints: Optional[int] = None) -> None`

**`class SerializerFiles`**
  - Location: line 232-307
  - Serialize files from a directory and all subdirectories. Only one file type can be serialized. Once 
specified, all
    other types will be filtered out.
    Example:
    ```python
    df = SerializerFiles.load("path/to/dir",file_type=".pdf")
    will yield absolute paths to all `.pdf` files in the directory and all subdirectories.
    ```
  - Public methods (2):
    - `load(
        path: PathLikeOrStr,
        file_type: Union[str, Sequence[str]],
        max_datapoints: Optional[int] = None,
        shuffle: Optional[bool] = False,
        sort: Optional[bool] = True,
    ) -> DataFlow`
    - `save() -> None`

**`class CocoParser`**
  - Location: line 310-547
  - A simplified version of the COCO helper class for reading  annotations. It currently supports only
    bounding box annotations
    Args:
    annotation_file: Location of annotation file
  - Public methods (7):
    - `get_ann_ids(
        self,
        img_ids: Optional[Union[int, Sequence[int]]] = None,
        cat_ids: Optional[Union[int, Sequence[int]]] = None,
        area_range: Optional[Sequence[int]] = None,
        is_crowd: Optional[bool] = None,
    ) -> Sequence[int]`
    - `get_cat_ids(
        self,
        category_names: Optional[Union[str, Sequence[str]]] = None,
        super_category_names: Optional[Union[str, Sequence[str]]] = None,
        category_ids: Optional[Union[int, Sequence[int]]] = None,
    ) -> Sequence[int]`
    - `get_image_ids(
        self, img_ids: Optional[Union[int, Sequence[int]]] = None, cat_ids: Optional[Union[int, 
Sequence[int]]] = None
    ) -> Sequence[int]`
    - `info(self) -> None`
    - `load_anns(self, ids: Optional[Union[int, Sequence[int]]] = None) -> List[JsonDict]`
    - `load_cats(self, ids: Optional[Union[int, Sequence[int]]] = None) -> List[JsonDict]`
    - `load_imgs(self, ids: Optional[Union[int, Sequence[int]]] = None) -> List[JsonDict]`
  - Private methods (2):
    - `__init__(self, annotation_file: Optional[PathLikeOrStr] = None) -> None`
    - `_create_index(self) -> None`

**`class SerializerCoco`**
  - Location: line 550-605
  - Class for serializing annotation files in COCO format. COCO comes in `JSON` format which is a priori not
    serialized. This class implements only the very basic methods to generate a dataflow. It wraps the coco 
class
    from `pycocotools` and assembles annotations that belong to the image.
    Note:
    Conversion into the core `Image` has to be done by yourself.
    Example:
    ```python
    df = SerializerCoco.load("path/to/annotations.json")
    df.reset_state()
    for dp in df:
    # {'image':{'id',...},'annotations':[{'id':…,'bbox':...}]}
    ```
    """
  - Public methods (2):
    - `ad(path: PathLikeOrStr, max_datapoints: Optional[int] = None) - -> taFlow:
`
    - `ve() - -> ne:
`

**`class rializerPdfDoc:
`**
  - Location: line 608-674
  - Serialize a pdf document with an arbitrary number of pages.
    Example:
    ```python
    df = SerializerPdfDoc.load("path/to/document.pdf")
    will yield datapoints:
    {"path": "path/to/document.pdf", "file_name" document_page_1.pdf, "pdf_bytes": b"some-bytes"}
    ```
    """
  - Public methods (3):
    - `ad(path: PathLikeOrStr, max_datapoints: Optional[int] = None) - -> taFlow:
`
    - `lit(
        path: PathLikeOrStr, path_target: Optional[PathLikeOrStr] = None, max_datapoint: Optional[int] = None
    ) - -> ne:
`
    - `ve(path: PathLikeOrStr) - -> ne:
`

#### deepdoctection/dataflow/parallel_map.py

**(private) `class _ParallelMapData`**
  - Location: line 82-160
  - Inherits: ProxyDataFlow, ABC
  - Public methods (3):
    - `get_data_non_strict(self) -> Any`
    - `get_data_strict(self) -> Any`
    - `reset_state(self) -> None`
  - Private methods (6):
    - `__init__(self, df: DataFlow, buffer_size: int, strict: bool = False) -> None`
    - `__iter__(self) -> Iterator[Any]`
    - `_fill_buffer(self, cnt=None)`
    - `_recv(self)`
    - `_recv_filter_none(self)`
    - `_send(self, dp: Any)`

**`class MultiThreadMapData`**
  - Location: line 163-286
  - Inherits: _ParallelMapData
  - Same as `MapData`, but start threads to run the mapping function.
    This is useful when the mapping function is the bottleneck, but you don't
    want to start processes for the entire dataflow pipeline.
    The semantics of this class is **identical** to `MapData` except for the ordering.
    Threads run in parallel and can take different time to run the
    mapping function. Therefore, the order of datapoints won't be preserved.
    When `strict=True`, `MultiThreadMapData(df, ...)`
    is guaranteed to produce the exact set of data as `MapData(df, ...)`,
    if both are iterated until `StopIteration`. But the produced data will have different ordering.
    The behavior of strict mode is undefined if the given dataflow `df` is infinite.
    When `strict=False`, the data that's produced by `MultiThreadMapData(df, ...)`
    is a re-ordering of the data produced by `RepeatedData(MapData(df, ...), -1)`.
    In other words, first pass of `MultiThreadMapData.__iter__` may contain
    datapoints from the second pass of `df.__iter__`.
    Note:
    1. You should avoid starting many threads in your main process to reduce GIL contention.
    The threads will only start in the process which calls `reset_state()`.
    Therefore you can use `MultiProcessRunnerZMQ(MultiThreadMapData(...), 1)`
    to reduce GIL contention.
  - Public methods (1):
    - `reset_state(self) -> None`
  - Private methods (5):
    - `__del__(self) -> Any`
    - `__init__(
        self,
        df: DataFlow,
        num_thread: int,
        map_func: Callable[[Any], Any],
        *,
        buffer_size: int = 200,
        strict: bool = False,
    )`
    - `__iter__(self) -> Iterator[Any]`
    - `_recv(self) -> Any`
    - `_send(self, dp: Any) -> None`

**(private) `class _Worker`**
  - Location: line 187-212
  - Inherits: StoppableThread

**(private) `class _MultiProcessZMQDataFlow`**
  - Location: line 289-326
  - Inherits: DataFlow, ABC
  - Public methods (1):
    - `reset_state(self) -> Any`
  - Private methods (3):
    - `__del__(self) -> None`
    - `__init__(self) -> None`
    - `_start_processes(self) -> Any`

**`class MultiProcessMapData`**
  - Location: line 344-452
  - Inherits: _ParallelMapData, _MultiProcessZMQDataFlow
  - Same as `MapData`, but start processes to run the mapping function,
    and communicate with ZeroMQ pipe.
    The semantics of this class is identical to `MapData` except for the ordering.
    Processes run in parallel and can take different time to run the
    mapping function. Therefore, the order of datapoints won't be preserved.
    When `strict=True`, `MultiProcessMapData(df, ...)`
    is guaranteed to produce the exact set of data as `MapData(df, ...)`,
    if both are iterated until `StopIteration`. But the produced data will have different ordering.
    The behavior of strict mode is undefined if the given dataflow `df` is infinite.
    When `strict=False`, the data that's produced by `MultiProcessMapData(df, ...)`
    is a reordering of the data produced by `RepeatedData(MapData(df, ...), -1)`.
    In other words, first pass of `MultiProcessMapData.__iter__` may contain
    datapoints from the second pass of `df.__iter__`.
  - Public methods (1):
    - `reset_state(self) -> None`
  - Private methods (5):
    - `__init__(
        self,
        df: DataFlow,
        num_proc: int,
        map_func: Callable[[Any], Any],
        *,
        buffer_size: int = 200,
        strict: bool = False,
    ) -> None`
    - `__iter__(self) -> Iterator[Any]`
    - `_create_worker(self, idx, pipename, hwm)`
    - `_recv(self)`
    - `_send(self, dp: Any)`

**(private) `class _Worker`**
  - Location: line 361-382
  - Inherits: mp.Process

#### deepdoctection/dataflow/serialize.py

**`class DataFromList`**
  - Location: line 23-49
  - Inherits: RNGDataFlow
  - Wrap a list of datapoints to a DataFlow
  - Private methods (3):
    - `__init__(self, lst: list[Any], shuffle: bool = True) -> None`
    - `__iter__(self) -> Iterator[Any]`
    - `__len__(self) -> int`

**`class DataFromIterable`**
  - Location: line 52-76
  - Inherits: DataFlow
  - Wrap an iterable of datapoints to a DataFlow
  - Public methods (1):
    - `reset_state(self) -> None`
  - Private methods (3):
    - `__init__(self, iterable: Iterable[Any]) -> None`
    - `__iter__(self) -> Iterator[Any]`
    - `__len__(self) -> int`

**`class FakeData`**
  - Location: line 79-133
  - Inherits: RNGDataFlow
  - Generate fake data of given shapes
  - Private methods (3):
    - `__init__(
        self,
        shapes: list[Union[list[Any], tuple[Any]]],
        size: int = 1000,
        random: bool = True,
        dtype: str = "float32",
        domain: tuple[Union[float, int], Union[float, int]] = (0, 1),
    )`
    - `__iter__(self) -> Iterator[Any]`
    - `__len__(self) -> int`

**`class PickleSerializer`**
  - Location: line 136-153
  - A Serializer to load and to dump objects
  - Public methods (2):
    - `dumps(obj: Any) -> bytes`
    - `loads(buf: Any) -> Any`

#### deepdoctection/dataflow/stats.py

**`class MeanFromDataFlow`**
  - Location: line 32-153
  - Inherits: ProxyDataFlow
  - Get the mean of some dataflow. Takes a component from a dataflow and calculates iteratively the mean.
    Example:
    ```python
    df: some dataflow
    MeanFromDataFlow(df).start() # If you want to put MeanFromDataFlow at the end of a dataflow
    or
    df: some dataflow
    df = MeanFromDataFlow(df)
    is also possible. Testing with the progress bar will stop once the requested size has been reached.
    ```
  - Public methods (2):
    - `reset_state(self) -> None`
    - `start(self) -> npt.NDArray[Any]`
  - Private methods (2):
    - `__init__(
        self,
        df: DataFlow,
        axis: Optional[Union[int, tuple[int], tuple[int, int], tuple[int, int, int]]] = None,
        key: Optional[str] = None,
        max_datapoints: Optional[int] = None,
    )`
    - `__iter__(self) -> Any`

**`class StdFromDataFlow`**
  - Location: line 156-284
  - Inherits: ProxyDataFlow
  - Gets the standard deviation of some dataflow. Takes a component from a dataflow and calculates iteratively
    the standard deviation.
    Example:
    ```python
    df= ...
    StdFromDataFlow(df).start()
    if you want to put  StdFromDataFlow at the end of a dataflow
    df: some dataflow
    df = StdFromDataFlow(df)
    is also possible. The testing with the progress bar will stop once the requested size has been reached.
    ```
  - Public methods (2):
    - `reset_state(self) -> None`
    - `start(self) -> npt.NDArray[Any]`
  - Private methods (2):
    - `__init__(
        self,
        df: DataFlow,
        axis: Optional[Union[int, tuple[int], tuple[int, int], tuple[int, int, int]]] = None,
        key: Optional[str] = None,
        max_datapoints: Optional[int] = None,
    )`
    - `__iter__(self) -> Any`

#### deepdoctection/datapoint/annotation.py

**`class AnnotationMap`**
  - Location: line 72-78
  - AnnotationMap to store all sub categories, relationship keys and summary keys of an annotation

**`class Annotation`**
  - Location: line 82-270
  - Inherits: ABC
  - Abstract base class for all types of annotations. This abstract base class only implements general methods
for
    correctly assigning annotation_ids. It also has an active flag which is set to True. Only active 
annotations will be
    returned when querying annotations from image containers.
    Annotation id should never be assigned by yourself. One possibility of assigning an id depending on an 
external
    value is to set an external id, which in turn creates an annotation id as a function of this.
    An annotation id can only be explicitly set, provided the value is a md5 hash.
    Note:
    Ids will be generated automatically if the annotation object is dumped in a parent container,
    either an image or an annotation (e.g. sub-category). If no id is supplied, the `annotation_id` is created
    depending on the defining attributes (key and value pairs) as specified in the return value of
    `get_defining_attributes`.
    Attributes:
    active: Always set to `True`. You can change the value using `deactivate` .
    external_id: A string or integer value for generating an annotation id. Note, that the resulting 
annotation
    id will not depend on the defining attributes.
    _annotation_id: Unique id for annotations. Will always be given as string representation of a md5-hash.
    service_id: Service that generated the annotation. This will be the name of a pipeline component
    model_id: Model that generated the annotation. This will be the name of a model in a component
    session_id: Session id for the annotation. This will be the id of the session in which the annotation was
    created.
  - Public methods (9):
    - `annotation_id(self) -> str`
    - `annotation_id(self, input_id: str) -> None`
    - `as_dict(self) -> AnnotationDict`
    - `deactivate(self) -> None`
    - `from_dict(cls, **kwargs: AnnotationDict) -> Annotation`
    - `get_defining_attributes(self) -> list[str]`
    - `get_state_attributes() -> list[str]`
    - `set_annotation_id(annotation: CategoryAnnotation, *container_id_context: Optional[str]) -> str`
    - `state_id(self) -> str`
  - Private methods (2):
    - `__post_init__(self) -> None`
    - `_assert_attributes_have_str(self, state_id: bool = False) -> None`

**`class CategoryAnnotation`**
  - Location: line 277-456
  - Inherits: Annotation
  - A general class for storing categories (labels/classes) as well as sub categories (sub-labels/subclasses),
    relationships and prediction scores.
    Sub-categories and relationships are stored in a dict, which are populated via the `dum_sub_category` or
    `dump_relationship`. If a key is already available as a sub-category, it must be explicitly removed using 
the
    `remove_sub_category` before replacing the sub-category.
    Note:
    Sub categories are only accepted as category annotations. Relationships, on the other hand, are only
    managed by passing the `annotation_id`.
    Attributes:
    category_name: String will be used for selecting specific annotations. Use upper case strings.
    category_id: When setting a value will accept strings and ints. Will be stored as string.
    score: Score of a prediction.
    sub_categories: Do not access the dict directly. Rather use the access `get_sub_category` resp.
    `dump_sub_category`.
    relationships: Do not access the dict directly either. Use `get_relationship` or
    `dump_relationship` instead.
  - Public methods (12):
    - `category_name(self) -> ObjectTypes`
    - `category_name(self, category_name: TypeOrStr) -> None`
    - `dump_relationship(self, key: TypeOrStr, annotation_id: str) -> None`
    - `dump_sub_category(
        self, sub_category_name: TypeOrStr, annotation: CategoryAnnotation, *container_id_context: 
Optional[str]
    ) -> None`
    - `from_dict(cls, **kwargs: AnnotationDict) -> CategoryAnnotation`
    - `get_defining_attributes(self) -> list[str]`
    - `get_relationship(self, key: ObjectTypes) -> list[str]`
    - `get_state_attributes() -> list[str]`
    - `get_sub_category(self, sub_category_name: ObjectTypes) -> CategoryAnnotation`
    - `remove_keys() -> list[str]`
    - `remove_relationship(self, key: ObjectTypes, annotation_ids: Optional[Union[list[str], str]] = None) -> 
None`
    - `remove_sub_category(self, key: ObjectTypes) -> None`
  - Private methods (1):
    - `__post_init__(self) -> None`

**`class ImageAnnotation`**
  - Location: line 460-546
  - Inherits: CategoryAnnotation
  - A general class for storing annotations related to object detection tasks. In addition to the inherited 
attributes,
    the class contains a bounding box and an image attribute. The image attribute is optional and is suitable 
for
    generating an image from the annotation and then saving it there. Compare with the method `image.Image.
    image_ann_to_image`, which naturally populates this attribute.
    Attributes:
    bounding_box: Regarding the coordinate system, if you have to define a prediction, use the system of the
    image where the object has been detected.
    image: Image, defined by the bounding box and cropped from its parent image. Populate this attribute with
    `Image.image_ann_to_image`.
  - Public methods (6):
    - `from_dict(cls, **kwargs: AnnotationDict) -> ImageAnnotation`
    - `get_annotation_map(self) -> defaultdict[str, list[AnnotationMap]]`
    - `get_bounding_box(self, image_id: Optional[str] = None) -> BoundingBox`
    - `get_defining_attributes(self) -> list[str]`
    - `get_state_attributes() -> list[str]`
    - `get_summary(self, key: ObjectTypes) -> CategoryAnnotation`

**`class ContainerAnnotation`**
  - Location: line 550-569
  - Inherits: CategoryAnnotation
  - A dataclass for transporting values along with categorical attributes. Use these types of annotations as 
special
    types of sub categories.
    Attributes:
    value: Attribute to store the value. Use strings.
  - Public methods (2):
    - `from_dict(cls, **kwargs: AnnotationDict) -> ContainerAnnotation`
    - `get_defining_attributes(self) -> list[str]`

#### deepdoctection/datapoint/box.py

**`class BoundingBox`**
  - Location: line 164-554
  - Rectangular bounding box that stores coordinates and allows different representations.
    This implementation differs from the previous version by using internal integer storage with precision 
scaling
    for both absolute and relative coordinates. Coordinates are stored internally as integers `(_ulx, _uly, 
etc.)`
    with relative coordinates multiplied by `RELATIVE_COORD_CONVERTER` for precision. Properties `(ulx, uly, 
etc.)`
    handle the conversion between internal storage and exposed values.
    Note:
    You can define an instance by passing:
    - Upper left point `(ulx, uly) + width` and height, OR
    - Upper left point `(ulx, uly) + lower right point (lrx, lry)`
    Note:
    - When `absolute_coords=True`, coordinates will be rounded to integers
    - When `absolute_coords=False`, coordinates must be between 0 and 1
    - The box is validated on initialization to ensure coordinates are valid
    Attributes:
    absolute_coords: Whether the coordinates are absolute pixel values (`True`) or normalized
    `[0,1]` values (`False`).
    _ulx: Upper-left x-coordinate, stored as an integer.
    _uly: Upper-left y-coordinate, stored as an integer.
    _lrx: Lower-right x-coordinate, stored as an integer.
    _lry: Lower-right y-coordinate, stored as an integer.
    _height: Height of the bounding box, stored as an integer.
    _width: Width of the bounding box, stored as an integer.
  - Public methods (23):
    - `area(self) -> Union[int, float]`
    - `center(self) -> tuple[BoxCoordinate, BoxCoordinate]`
    - `cx(self) -> BoxCoordinate`
    - `cy(self) -> BoxCoordinate`
    - `from_dict(cls, **kwargs) -> BoundingBox`
    - `get_legacy_string(self) -> str`
    - `height(self) -> BoxCoordinate`
    - `height(self, value: BoxCoordinate) -> None`
    - `lrx(self) -> BoxCoordinate`
    - `lrx(self, value: BoxCoordinate) -> None`
    - `lry(self) -> BoxCoordinate`
    - `lry(self, value: BoxCoordinate) -> None`
    - `remove_keys() -> list[str]`
    - `replace_keys() -> dict[str, str]`
    - `to_list(self, mode: str, scale_x: float = 1.0, scale_y: float = 1.0) -> list[BoxCoordinate]`
    - `to_np_array(self, mode: str, scale_x: float = 1.0, scale_y: float = 1.0) -> npt.NDArray[np.float32]`
    - `transform(
        self,
        image_width: float,
        image_height: float,
        absolute_coords: bool = False,
    ) -> BoundingBox`
    - `ulx(self) -> BoxCoordinate`
    - `ulx(self, value: BoxCoordinate) -> None`
    - `uly(self) -> BoxCoordinate`
    - `uly(self, value: BoxCoordinate) -> None`
    - `width(self) -> BoxCoordinate`
    - `width(self, value: BoxCoordinate) -> None`
  - Private methods (4):
    - `__init__(
        self,
        absolute_coords: bool,
        ulx: BoxCoordinate,
        uly: BoxCoordinate,
        lrx: BoxCoordinate = 0,
        lry: BoxCoordinate = 0,
        width: BoxCoordinate = 0,
        height: BoxCoordinate = 0,
    )`
    - `__post_init__(self) -> None`
    - `__repr__(self) -> str`
    - `__str__(self) -> str`

#### deepdoctection/datapoint/image.py

**`class MetaAnnotationDict`**
  - Location: line 43-49
  - Inherits: TypedDict
  - MetaAnnotationDict

**`class MetaAnnotation`**
  - Location: line 53-89
  - An immutable dataclass that stores information about what `Image` are being
    modified through a pipeline component.
    Attributes:
    image_annotations: Tuple of `ObjectTypes` representing image annotations.
    sub_categories: Dictionary mapping `ObjectTypes` to dicts of `ObjectTypes` to sets of `ObjectTypes`
    for sub-categories.
    relationships: Dictionary mapping `ObjectTypes` to sets of `ObjectTypes` for relationships.
    summaries: Tuple of `ObjectTypes` representing summaries.
  - Public methods (1):
    - `as_dict(self) -> MetaAnnotationDict`

**`class Image`**
  - Location: line 93-900
  - The image object is the enclosing data class that is used in the core data model to manage, retrieve or 
store
    all information during processing. It contains metadata belonging to the image, but also the image itself
    and annotations, either given as ground truth or determined via a processing path. In addition, there are
    storage options in order not to recalculate coordinates in relation to other images.
    Data points from datasets must be mapped in this format so that the processing tools (pipeline components)
can
    be called up without further adjustment.
    An image can be provided with an `image_id` by providing the `external_id`, which can be clearly 
identified
    as a `md5` hash. If such an id is not given, an `image_id` will be derived from `file_name` and, if 
necessary,
    from `location`.
    All other attributes represent containers (lists or dicts) that can be populated and managed using their 
own method.
    In `image`, the image may be saved as `np.array`. Allocation as `base64` encoding string or as pdf bytes 
are
    possible and are converted via a `image.setter`. Other formats are rejected.
    If an image of a given size is added, the width and height of the image are determined.
    Using `embeddings`, various bounding boxes can be saved that describe the position of the image as a
    sub-image. The bounding box is accessed in relation to the embedding image via the `annotation_id`.
    Embeddings are often used in connection with annotations in which the `image` is populated.
    All `ImageAnnotations` of the image are saved in the list annotations. Other types of annotation are
    not permitted.
    Args:
    file_name: Should be equal to the name of a physical file representing the image. If the image is part
    of a larger document (e.g. pdf-document) the file_name should be populated as a concatenation of
    the document file and its page number.
    location: Full path to the document or to the physical file. Loading functions from disk use this 
attribute.
    document_id: A unique identifier for the document. If not set, it will be set to the `image_id`.
    page_number: The page number of the image in the document. If not set, it will be set to 0.
    external_id: A string or integer value for generating an `image_id`.
    _image_id: A unique identifier for the image. If not set, it will be set to a generated `uuid`.
    _image: The image as a numpy array. If not set, it will be set to None. Do not set this attribute 
directly.
    _bbox: The bounding box of the image. If not set, it will be set to None. Do not set this attribute 
directly.
    embeddings: A dictionary of `image_id` to `BoundingBox`es. If not set, it will be set to an empty dict.
    annotations: A list of `ImageAnnotation` objects. Use `get_annotation` to retrieve annotations.
    _annotation_ids: A list of `annotation_id`s. Used internally to ensure uniqueness of annotations.
    _summary: A `CategoryAnnotation` for image-level informations. If not set, it will be set to None.
  - Public methods (34):
    - `as_dict(self) -> dict[str, Any]`
    - `as_json(self) -> str`
    - `clear_image(self, clear_bbox: bool = False) -> None`
    - `define_annotation_id(self, annotation: Annotation) -> str`
    - `dump(self, annotation: ImageAnnotation) -> None`
    - `from_dict(cls, **kwargs) -> Image`
    - `from_file(cls, file_path: str) -> Image`
    - `get_annotation(
        self,
        category_names: Optional[Union[str, ObjectTypes, Sequence[Union[str, ObjectTypes]]]] = None,
        annotation_ids: Optional[Union[str, Sequence[str]]] = None,
        service_ids: Optional[Union[str, Sequence[str]]] = None,
        model_id: Optional[Union[str, Sequence[str]]] = None,
        session_ids: Optional[Union[str, Sequence[str]]] = None,
        ignore_inactive: bool = True,
    ) -> list[ImageAnnotation]`
    - `get_annotation_id_to_annotation_maps(self) -> defaultdict[str, list[AnnotationMap]]`
    - `get_categories_from_current_state(self) -> set[str]`
    - `get_embedding(self, image_id: str) -> BoundingBox`
    - `get_image(self) -> _Img`
    - `get_service_id_to_annotation_id(self) -> defaultdict[str, list[str]]`
    - `get_state_attributes() -> list[str]`
    - `height(self) -> BoxCoordinate`
    - `image(self) -> Optional[PixelValues]`
    - `image(self, image: Optional[Union[str, PixelValues, bytes]]) -> None`
    - `image_ann_to_image(self, annotation_id: str, crop_image: bool = False) -> None`
    - `image_id(self) -> str`
    - `image_id(self, input_id: str) -> None`
    - `maybe_ann_to_sub_image(self, annotation_id: str, category_names: Union[str, list[str]]) -> None`
    - `pdf_bytes(self) -> Optional[bytes]`
    - `pdf_bytes(self, pdf_bytes: bytes) -> None`
    - `remove(
        self,
        annotation_ids: Optional[Union[str, Sequence[str]]] = None,
        service_ids: Optional[Union[str, Sequence[str]]] = None,
    ) -> None`
    - `remove_embedding(self, image_id: str) -> None`
    - `remove_image_from_lower_hierarchy(self, pixel_values_only: bool = False) -> None`
    - `remove_keys() -> list[str]`
    - `save(
        self,
        image_to_json: bool = True,
        highest_hierarchy_only: bool = False,
        path: Optional[PathLikeOrStr] = None,
        dry: bool = False,
    ) -> Optional[Union[ImageDict, str]]`
    - `set_embedding(self, image_id: str, bounding_box: BoundingBox) -> None`
    - `set_width_height(self, width: BoxCoordinate, height: BoxCoordinate) -> None`
    - `state_id(self) -> str`
    - `summary(self) -> CategoryAnnotation`
    - `summary(self, summary_annotation: CategoryAnnotation) -> None`
    - `width(self) -> BoxCoordinate`
  - Private methods (3):
    - `__post_init__(self) -> None`
    - `_remove_by_annotation_id(self, annotation_id: str, location_dict: AnnotationMap) -> None`
    - `_self_embedding(self) -> None`

#### deepdoctection/datapoint/view.py

**`class Text_`**
  - Location: line 53-96
  - Immutable dataclass for storing structured text extraction results.
    Attributes:
    text: The concatenated text string.
    words: List of word strings.
    ann_ids: List of annotation IDs for each word.
    token_classes: List of token class names for each word.
    token_class_ann_ids: List of annotation IDs for each token class.
    token_tags: List of token tag names for each word.
    token_tag_ann_ids: List of annotation IDs for each token tag.
    token_class_ids: List of token class IDs.
    token_tag_ids: List of token tag IDs.
  - Public methods (1):
    - `as_dict(self) -> dict[str, Union[list[str], str]]`

**`class ImageAnnotationBaseView`**
  - Location: line 99-233
  - Inherits: ImageAnnotation
  - Consumption class for having easier access to categories added to an `ImageAnnotation`.
    Note:
    `ImageAnnotation` is a generic class in the sense that different categories might have different
    sub categories collected while running through a pipeline. In order to get properties for a specific
    category one has to understand the internal data structure.
    To circumvent this obstacle `ImageAnnotationBaseView` provides the `__getattr__` so that
    to gather values defined by `ObjectTypes`. To be more precise: A sub class will have attributes either
    defined explicitly by a `@property` or by the set of `get_attribute_names()` . Do not define any attribute
    setter method and regard this class as a view to the super class.
    The class does contain its base page, which mean, that it is possible to retrieve all annotations that 
have a
    relation.
    Attributes:
    base_page: `Page` class instantiated by the lowest hierarchy `Image`
  - Public methods (5):
    - `b64_image(self) -> Optional[str]`
    - `bbox(self) -> list[float]`
    - `from_dict(cls, **kwargs: AnnotationDict) -> ImageAnnotationBaseView`
    - `get_attribute_names(self) -> set[str]`
    - `viz(self, interactive: bool = False) -> Optional[PixelValues]`
  - Private methods (1):
    - `__getattr__(self, item: str) -> Optional[Union[str, int, list[str], list[ImageAnnotationBaseView]]]`

**`class Word`**
  - Location: line 236-249
  - Inherits: ImageAnnotationBaseView
  - Word specific subclass of `ImageAnnotationBaseView` modelled by `WordType`.
  - Public methods (1):
    - `get_attribute_names(self) -> set[str]`

**`class Layout`**
  - Location: line 252-394
  - Inherits: ImageAnnotationBaseView
  - Layout specific subclass of `ImageAnnotationBaseView`. In order check what ImageAnnotation will be wrapped
    into `Layout`, please consult `IMAGE_ANNOTATION_TO_LAYOUTS`.
    Attributes:
    text_container: Pass the `LayoutObject` that is supposed to be used for `words`. It is possible that the
    text_container is equal to `self.category_name`, in which case `words` returns `self`.
  - Public methods (5):
    - `get_attribute_names(self) -> set[str]`
    - `get_ordered_words(self) -> list[ImageAnnotationBaseView]`
    - `text(self) -> str`
    - `text_(self) -> Text_`
    - `words(self) -> list[ImageAnnotationBaseView]`
  - Private methods (1):
    - `__len__(self) -> int`

**`class Cell`**
  - Location: line 397-404
  - Inherits: Layout
  - Cell specific subclass of `ImageAnnotationBaseView` modelled by `CellType`.
  - Public methods (1):
    - `get_attribute_names(self) -> set[str]`

**`class List`**
  - Location: line 407-456
  - Inherits: Layout
  - List specific subclass of `ImageAnnotationBaseView` modelled by `LayoutType`.
  - Public methods (3):
    - `get_ordered_words(self) -> list[ImageAnnotationBaseView]`
    - `list_items(self) -> list[ImageAnnotationBaseView]`
    - `words(self) -> list[ImageAnnotationBaseView]`

**`class Table`**
  - Location: line 459-768
  - Inherits: Layout
  - Table specific subclass of `ImageAnnotationBaseView` modelled by `TableType`.
  - Public methods (16):
    - `cells(self) -> list[Cell]`
    - `column(self, column_number: int) -> list[ImageAnnotationBaseView]`
    - `column_header_cells(self) -> list[Cell]`
    - `columns(self) -> list[ImageAnnotationBaseView]`
    - `csv(self) -> csv`
    - `csv_(self) -> list[list[list[Text_]]]`
    - `get_attribute_names(self) -> set[str]`
    - `get_ordered_words(self) -> list[ImageAnnotationBaseView]`
    - `html(self) -> HTML`
    - `kv_header_rows(self, row_number: int) -> Mapping[str, str]`
    - `row(self, row_number: int) -> list[ImageAnnotationBaseView]`
    - `row_header_cells(self) -> list[Cell]`
    - `rows(self) -> list[ImageAnnotationBaseView]`
    - `text(self) -> str`
    - `text_(self) -> Text_`
    - `words(self) -> list[ImageAnnotationBaseView]`
  - Private methods (1):
    - `__str__(self) -> str`

**`class ImageDefaults`**
  - Location: line 772-822
  - ImageDefaults

**`class Page`**
  - Location: line 855-1582
  - Inherits: Image
  - Consumer class for its super `Image` class. It comes with some `@property`s as well as
    custom `__getattr__` to give easier access to various information that are stored in the base class
    as `ImageAnnotation` or `CategoryAnnotation`.
    Info:
    Its factory function `Page().from_image(image, text_container, text_block_names)` creates for every
    `ImageAnnotation` a corresponding subclass of `ImageAnnotationBaseView` which drives the object towards
    less generic classes with custom attributes that are controlled some `ObjectTypes`.
    Attributes:
    text_container: The `LayoutType` that is used to extract the text from.
    floating_text_block_categories: Categories that are considered as floating text blocks, e.g. 
`LayoutType.TEXT`
    image_orig: Base image
    residual_text_block_categories: Categories that are considered as residual text blocks, e.g.
    `LayoutType.page_header`
  - Public methods (19):
    - `add_attribute_name(cls, attribute_name: Union[str, ObjectTypes]) -> None`
    - `b64_image(self) -> Optional[str]`
    - `chunks(self) -> Chunks`
    - `figures(self) -> list[ImageAnnotationBaseView]`
    - `from_file(
        cls,
        file_path: str,
        text_container: Optional[ObjectTypes] = None,
        floating_text_block_categories: Optional[list[ObjectTypes]] = None,
        residual_text_block_categories: Optional[Sequence[ObjectTypes]] = None,
        include_residual_text_container: bool = True,
    ) -> Page`
    - `from_image(
        cls,
        image_orig: Image,
        text_container: Optional[ObjectTypes] = None,
        floating_text_block_categories: Optional[Sequence[ObjectTypes]] = None,
        residual_text_block_categories: Optional[Sequence[ObjectTypes]] = None,
        include_residual_text_container: bool = True,
        base_page: Optional[Page] = None,
    ) -> Page`
    - `get_annotation(  # type: ignore
        self,
        category_names: Optional[Union[str, ObjectTypes, Sequence[Union[str, ObjectTypes]]]] = None,
        annotation_ids: Optional[Union[str, Sequence[str]]] = None,
        service_ids: Optional[Union[str, Sequence[str]]] = None,
        model_id: Optional[Union[str, Sequence[str]]] = None,
        session_ids: Optional[Union[str, Sequence[str]]] = None,
        ignore_inactive: bool = True,
    ) -> list[ImageAnnotationBaseView]`
    - `get_attribute_names(cls) -> set[str]`
    - `get_entities(self) -> list[Mapping[str, str]]`
    - `get_layout_context(self, annotation_id: str, context_size: int = 3) -> list[ImageAnnotationBaseView]`
    - `layouts(self) -> list[ImageAnnotationBaseView]`
    - `residual_layouts(self) -> list[ImageAnnotationBaseView]`
    - `save(
        self,
        image_to_json: bool = True,
        highest_hierarchy_only: bool = False,
        path: Optional[PathLikeOrStr] = None,
        dry: bool = False,
    ) -> Optional[Union[ImageDict, str]]`
    - `tables(self) -> list[ImageAnnotationBaseView]`
    - `text(self) -> str`
    - `text_(self) -> Text_`
    - `text_no_line_break(self) -> str`
    - `viz(
        self,
        show_tables: bool = True,
        show_layouts: bool = True,
        show_figures: bool = False,
        show_residual_layouts: bool = False,
        show_cells: bool = True,
        show_table_structure: bool = True,
        show_words: bool = False,
        show_token_class: bool = True,
        ignore_default_token_class: bool = False,
        interactive: bool = False,
        scaled_width: int = 600,
        **debug_kwargs: str,
    ) -> Optional[PixelValues]`
    - `words(self) -> list[ImageAnnotationBaseView]`
  - Private methods (5):
    - `__copy__(self) -> Page`
    - `__getattr__(self, item: str) -> Any`
    - `_ann_viz_bbox(self, ann: ImageAnnotationBaseView) -> list[float]`
    - `_make_text(self, line_break: bool = True) -> str`
    - `_order(self, block: str) -> list[ImageAnnotationBaseView]`

#### deepdoctection/datasets/adapter.py

**`class DatasetAdapter`**
  - Location: line 43-177
  - Inherits: IterableDataset
  - A helper class derived from `torch.utils.data.IterableDataset` to process datasets within
    pytorch frameworks (e.g. Detectron2). It wraps the dataset and defines the compulsory
    `__iter__` using  `dataflow.build` .
    `DatasetAdapter` is meant for training and will therefore produce an infinite number of datapoints
    by shuffling and restart iteration once the previous dataflow is exhausted.
  - Private methods (4):
    - `__getitem__(self, item: Any) -> None`
    - `__init__(
        self,
        name_or_dataset: Union[str, DatasetBase],
        cache_dataset: bool,
        image_to_framework_func: Optional[Callable[[DP], Optional[JsonDict]]] = None,
        use_token_tag: bool = True,
        number_repetitions: int = -1,
        **build_kwargs: str,
    ) -> None`
    - `__iter__(self) -> Iterator[Image]`
    - `__len__(self) -> int`

#### deepdoctection/datasets/base.py

**`class DatasetBase`**
  - Location: line 44-119
  - Inherits: ABC
  - Base class for a dataset. Requires to implement `_categories`, `_info` and `_builder` by
    yourself. These methods must return a `DatasetCategories`, a `DatasetInfo` and a `DataFlow_Builder` 
instance, which
    together give a complete description of the dataset. Compare some specific dataset cards in the 
`instance`.
  - Public methods (4):
    - `dataflow(self) -> DataFlowBaseBuilder`
    - `dataset_available(self) -> bool`
    - `dataset_info(self) -> DatasetInfo`
    - `is_built_in() -> bool`
  - Private methods (4):
    - `__init__(self) -> None`
    - `_builder(self) -> DataFlowBaseBuilder`
    - `_categories(self) -> DatasetCategories`
    - `_info(cls) -> DatasetInfo`

**(private) `class _BuiltInDataset`**
  - Location: line 122-134
  - Inherits: DatasetBase, ABC
  - Dataclass for built-in dataset. Do not use this
  - Public methods (1):
    - `is_built_in() -> bool`

**`class SplitDataFlow`**
  - Location: line 137-174
  - Inherits: DataFlowBaseBuilder
  - Dataflow builder for splitting datasets
  - Public methods (1):
    - `build(self, **kwargs: Union[str, int]) -> DataFlow`
  - Private methods (1):
    - `__init__(self, train: list[Image], val: list[Image], test: Optional[list[Image]])`

**`class MergeDataset`**
  - Location: line 177-406
  - Inherits: DatasetBase
  - A class for merging dataset ready to feed a training or an evaluation script. The dataflow builder will 
generate
    samples from all datasets and will exhaust if every dataflow of the merged datasets are exhausted as well.
To
    guarantee flexibility it is possible to pass customized dataflows explicitly to maybe reduce the dataflow 
size from
    one dataset or to use different splits from different datasets.
    Note:
    When yielding datapoints from `build` dataflows, note that one dataset will pass all its samples 
successively
    which might reduce randomness for training. Buffering all datasets (without loading heavy components like
    images) is therefore possible and the merged dataset can be shuffled.
    When the datasets that are buffered are split functionality one can divide the buffered samples into an 
`train`,
    `val` and `test` set.
    While the selection of categories is given by the union of all categories of all datasets, sub categories 
need to
    be handled with care: Only sub categories for one specific category are available provided that every 
dataset has
    this sub category available for this specific category. The range of sub category values again is defined 
as the
    range of all values from all datasets.
    Example:
    ```python
    dataset_1 = get_dataset("dataset_1")
    dataset_2 = get_dataset("dataset_2")
    union_dataset = MergeDataset(dataset_1,dataset_2)
    union_dataset.buffer_datasets(split="train")     # will cache the train split of dataset_1 and dataset_2
    merge.split_datasets(ratio=0.1, add_test=False)  # will create a new split of the union.
    ```
    Example:
    ```python
    dataset_1 = get_dataset("dataset_1")
    dataset_2 = get_dataset("dataset_2")
    df_1 = dataset_1.dataflow.build(max_datapoints=20)  # handle separate dataflow configs ...
    df_2 = dataset_1.dataflow.build(max_datapoints=30)
    union_dataset = MergeDataset(dataset_1,dataset_2)
    union_dataset.explicit_dataflows(df_1,df_2)   # ... and pass them explicitly. Filtering is another
    # possibility
    ```
  - Public methods (5):
    - `buffer_datasets(self, **kwargs: Union[str, int]) -> None`
    - `create_split_by_id(
        self, split_dict: Mapping[str, Sequence[str]], **dataflow_build_kwargs: Union[str, int]
    ) -> None`
    - `explicit_dataflows(self, *dataflows: DataFlow) -> None`
    - `get_ids_by_split(self) -> dict[str, list[str]]`
    - `split_datasets(self, ratio: float = 0.1, add_test: bool = True) -> None`
  - Private methods (4):
    - `__init__(self, *datasets: DatasetBase)`
    - `_builder(self) -> DataFlowBaseBuilder`
    - `_categories(self) -> DatasetCategories`
    - `_info(cls) -> DatasetInfo`

**`class DatasetCardDict`**
  - Location: line 409-419
  - Inherits: TypedDict
  - DatasetCardDict

**`class DatasetCard`**
  - Location: line 427-594
  - An immutable dataclass representing the metadata of a dataset, including categories, sub-categories,
    storage location, annotation files, and description. It facilitates management and consistency checks
    for annotations generated by pipeline components.
    Attributes:
    name: Name of the dataset.
    dataset_type: Type of the dataset as `ObjectTypes`.
    location: Storage location of the dataset as `Path`.
    init_categories: List of all initial categories (`ObjectTypes`) present in the dataset.
    init_sub_categories: Mapping from main categories to sub-categories and their possible values.
    annotation_files: Optional mapping from split names to annotation files.
    description: Description of the dataset.
    service_id_to_meta_annotation: Mapping from service IDs to `MetaAnnotation` objects, storing
    annotation structure for different pipeline components.
  - Public methods (4):
    - `as_dict(self, keep_object_types: bool = False) -> DatasetCardDict`
    - `load_dataset_card(file_path: PathLikeOrStr) -> DatasetCard`
    - `save_dataset_card(self, file_path: Union[str, Path]) -> None`
    - `update_from_pipeline(
        self, meta_annotations: MetaAnnotation, service_id_to_meta_annotation: Mapping[str, MetaAnnotation]
    ) -> None`
  - Private methods (1):
    - `__post_init__(self) -> None`

**`class CustomDataset`**
  - Location: line 597-709
  - Inherits: DatasetBase
  - A simple dataset interface that implements the boilerplate code and reduces complexity by merely leaving
    the user to write a `DataFlowBaseBuilder` (mapping the annotation format into deepdoctection data model is
    something that has to be left to the user for obvious reasons). Check the tutorial on how to approach the 
mapping
    problem.
  - Public methods (1):
    - `from_dataset_card(file_path: PathLikeOrStr, dataflow_builder: Type[DataFlowBaseBuilder]) -> 
CustomDataset`
  - Private methods (4):
    - `__init__(
        self,
        name: str,
        dataset_type: TypeOrStr,
        location: PathLikeOrStr,
        init_categories: Sequence[ObjectTypes],
        dataflow_builder: Type[DataFlowBaseBuilder],
        init_sub_categories: Optional[Mapping[ObjectTypes, Mapping[ObjectTypes, Sequence[ObjectTypes]]]] = 
None,
        annotation_files: Optional[Mapping[str, Union[str, Sequence[str]]]] = None,
        description: Optional[str] = None,
    )`
    - `_builder(self) -> DataFlowBaseBuilder`
    - `_categories(self) -> DatasetCategories`
    - `_info(self) -> DatasetInfo`

#### deepdoctection/datasets/dataflow_builder.py

**`class DataFlowBaseBuilder`**
  - Location: line 32-126
  - Inherits: ABC
  - Abstract base class for building the dataflow of a dataset.
    DataFlowBase has an abstract `build` that returns the dataflow of a dataset. The dataflow should be
    designed in such a way that each data point is already mapped in the form of the core data model and thus
    corresponds to a `datapoint.Image` instance. Any characteristics can be passed as arguments and 
implemented,
    which influence the return of the dataflow. These include, for example, the `split`, `max_datapoints` but 
also
    specific further transformations, such as cutting and returning an annotation as a sub image. Within this 
method,
    checks and consistency checks should also be carried out so that a curated data flow is available as 
return value.
    Such specific transformations should be implemented by transferring a value of the argument `build_mode`.
  - Public methods (8):
    - `build(self, **kwargs: Union[str, int]) -> DataFlow`
    - `categories(self) -> DatasetCategories`
    - `categories(self, categories: DatasetCategories) -> None`
    - `get_annotation_file(self, split: str) -> str`
    - `get_split(self, key: str) -> str`
    - `get_workdir(self) -> Path`
    - `splits(self) -> Mapping[str, str]`
    - `splits(self, splits: Mapping[str, str]) -> None`
  - Private methods (1):
    - `__init__(
        self,
        location: PathLikeOrStr,
        annotation_files: Optional[Mapping[str, Union[str, Sequence[str]]]] = None,
    )`

#### deepdoctection/datasets/info.py

**`class DatasetInfo`**
  - Location: line 70-104
  - `DatasetInfo` is a simple dataclass that stores some meta-data information about a dataset.
    Attributes:
    name: Name of the dataset. Using the name you can retrieve the dataset from the 
`registry.DatasetRegistry`.
    description: Short description of the dataset.
    license: License to the dataset.
    url: url, where the dataset can be downloaded from.
    splits: A `dict` of splits. The value must store the relative path, where the split can be found.
    type: The type describes whether this is a dataset for object detection (pass 'OBJECT_DETECTION'),
    sequence classification (pass 'SEQUENCE_CLASSIFICATION') or token classification ('TOKEN_CLASSIFICATION').
    Optionally, pass `None`.
  - Public methods (1):
    - `get_split(self, key: str) -> str`

**`class DatasetCategories`**
  - Location: line 108-385
  - Categories and their sub-categories are managed in this separate class. Since categories can be filtered 
or
    sub-categories can be swapped with categories, the list of all categories must be adapted at the same time
    after replacement/filtering. DatasetCategories manages these transformations. The class is also 
responsible
    for the index/category name relationship and guarantees that a sequence of natural numbers for the 
categories
    is always returned as the category-id even after replacing and/or filtering.
    Attributes:
    init_categories: A list of `category_name`s. The list must include all categories that can occur within 
the
    annotations.
    init_sub_categories: A dict of categories/sub-categories. Each sub-category that can appear in the
    annotations in combination with a category must be listed.
    Example:
    An annotation file hast the category/sub-category combinations for three datapoints:
    ```python
    (cat1,s1),(cat1,s2), (cat2,s2).
    ```
    You must list `init_categories`, `init_sub_categories` as follows:
    ```python
    init_categories = [cat1,cat2]
    init_sub_categories = {cat1: [s1,s2],cat2: [s2]}
    ```
    Use `filter_categories` or `set_cat_to_sub_cat` to filter or swap categories with sub-categories.
  - Public methods (11):
    - `cat_to_sub_cat(self) -> Optional[Mapping[ObjectTypes, ObjectTypes]]`
    - `filter_categories(self, categories: Union[TypeOrStr, list[TypeOrStr]]) -> None`
    - `get_categories(
        self, *, name_as_key: Literal[True], init: bool = ..., filtered: bool = ...
    ) -> Mapping[ObjectTypes, int]`
    - `get_categories(
        self, *, name_as_key: Literal[False] = ..., init: bool = ..., filtered: bool = ...
    ) -> Mapping[int, ObjectTypes]`
    - `get_categories(
        self, as_dict: Literal[False], name_as_key: bool = False, init: bool = False, filtered: bool = False
    ) -> Sequence[ObjectTypes]`
    - `get_categories(
        self, as_dict: Literal[True] = ..., name_as_key: bool = False, init: bool = False, filtered: bool = 
False
    ) -> Union[Mapping[ObjectTypes, int], Mapping[int, ObjectTypes]]`
    - `get_categories(
        self, as_dict: bool = True, name_as_key: bool = False, init: bool = False, filtered: bool = False
    ) -> Union[Sequence[ObjectTypes], Mapping[ObjectTypes, int], Mapping[int, ObjectTypes]]`
    - `get_sub_categories(
        self,
        categories: Optional[Union[TypeOrStr, Sequence[TypeOrStr]]] = None,
        sub_categories: Optional[Mapping[TypeOrStr, Union[TypeOrStr, Sequence[TypeOrStr]]]] = None,
        keys: bool = True,
        values_as_dict: bool = True,
        name_as_key: bool = False,
    ) -> Mapping[ObjectTypes, Any]`
    - `is_cat_to_sub_cat(self) -> bool`
    - `is_filtered(self) -> bool`
    - `set_cat_to_sub_cat(self, cat_to_sub_cat: dict[TypeOrStr, TypeOrStr]) -> None`
  - Private methods (2):
    - `__post_init__(self) -> None`
    - `_init_sanity_check(self) -> None`

#### deepdoctection/datasets/instances/doclaynet.py

**`class `DocLayNe`**
  - Location: line 103-124
  - Inherits: `
    """


  - assmethod
    def _info(cls
  - Public methods (3):
    - `        return -> LayNetBuilder(lo`
    - `es:
        retur -> tasetCategories(i`
    - `eturn Data -> nfo(
      `

**`class ):
    """
    ``**
  - Location: line 127-194
  - Inherits: ocLayNetBuilder` da
  - builder
    """
    def build(self, **kwargs: Unio
  - Public methods (1):
    - `]) -> DataFlow:
        """
        Re -> s a data`

**`class    DocLayNet`**
  - Location: line 210-223
  - Inherits: eq is the D
  - t dataset where the dataflow has been prepared to perform sequence classification
    """
    @classmethod
    def _info(cls
  - Public methods (3):
    - `es:
        retur -> tasetCategories(i`
    - `eturn Data -> nfo(name=_N`
    - `r:
        ret -> DocLayNetSeqBuilder`

**`class der):
    """
    D`**
  - Location: line 226-301
  - Inherits: cLayNetSeqBuilder d
  - builder
    """
    def build(self, **kwargs: Unio
  - Public methods (1):
    - `]) -> DataFlow:
        """
        Re -> s a data`

#### deepdoctection/datasets/instances/fintabnet.py

**`class ME

    @`**
  - Location: line 124-147
  - Inherits: lassmethod
    
  - fo(cls) -> DatasetInfo:
  - Public methods (3):
    - `AME,
      ->    short_de`
    - `nit_categories=_I -> CATEGORIES, init_`
    - `on=_LOCATION,  -> tation_files=_AN`

**`class ""

    def buil`**
  - Location: line 150-288
  - Inherits: (self, **kwargs: Un
  - , int]) -> DataFlow:
    """
  - Public methods (1):
    - `turns a dataflow from which you can st ->  datapoi`

#### deepdoctection/datasets/instances/funsd.py

**`class -> Da`**
  - Location: line 113-136
  - Inherits: asetInfo:
     
  - rn DatasetInfo(
  - Public methods (3):
    - ` init_sub_categor -> _SUB_CATEGORIES)
`
    - `ON_FILES)


cl -> FunsdBuilder`
    - `on=_SHORT_ -> RIPTION,
  `

**`class s: Union[str`**
  - Location: line 139-205
  - Inherits:  int]) -> DataFlow:
  - """
    Returns a dataflow from
  - Public methods (1):
    - `can stream datapoints of images. The f -> wing arg`

#### deepdoctection/datasets/instances/iiitar13k.py

**`class  _info(cl`**
  - Location: line 91-114
  - Inherits: ) -> DatasetInf
  - return DatasetInfo(
  - Public methods (3):
    - `IES)

    def _bu -> r(self) -> IIITar`
    - `es=_ANNOTATION -> ES)


class IIIT`
    - `iption=_SH -> DESCRIPTION`

**`class elf, **kwargs: U`**
  - Location: line 117-196
  - Inherits: ion[str, int]) -> D
  - :
    """
    Returns a dataflow f
  - Public methods (1):
    - `you can stream datapoints of images. T -> ollowing`

#### deepdoctection/datasets/instances/layouttest.py

**`class  """
    ``**
  - Location: line 67-89
  - Inherits: ayoutTest`
    
  - _name = _NAME
    @classm
  - Public methods (3):
    - `   return  -> setInfo(
  `
    - `der:
        r -> n LayoutTestBuild`
    - `gories:
        r -> n DatasetCategori`

**`class ilder):
    """
 `**
  - Location: line 92-134
  - Inherits:   LayoutTest datafl
  - der
    """
    def build(self, **kwargs:
  - Public methods (1):
    - ` int]) -> DataFlow:
        """
       -> turns a `

#### deepdoctection/datasets/instances/publaynet.py

**`class  = _NAME
`**
  - Location: line 74-97
  - Inherits:     @classmetho
  - ef _info(cls) -> DatasetInf
  - Public methods (3):
    - `cation=_LOCATI -> annotation_files`
    - `e=_NAME,
  ->        shor`
    - `es(init_categorie -> NIT_CATEGORIES)

`

**`class builder
    """
`**
  - Location: line 100-151
  - Inherits:     def build(self,
  - gs: Union[str, int]) -> DataFlow:
  - Public methods (1):
    - `  Returns a dataflow from which you ca -> ream dat`

#### deepdoctection/datasets/instances/pubtables1m.py

**`class     return Dat`**
  - Location: line 94-117
  - Inherits: setInfo(
      
  - ame=_NAME,
    short_d
  - Public methods (3):
    - `cription=_ -> RIPTION,
  `
    - `les1MBuilder:
    ->  return Pubtables`
    - `s1MBuilder(Dat -> wBaseBuilder):
   `

**`class ataFlow:
        "`**
  - Location: line 120-195
  - Inherits: "
        Returns a
  - ow from which you can stream datapoints of ima
  - Public methods (1):
    - `ollowing arguments affect the returns
 ->     of t`

**`class setInfo:
        `**
  - Location: line 223-240
  - Inherits: eturn DatasetIn
  - name=_NAME_STRUCT, descr
  - Public methods (3):
    - `T)


class Pub -> es1MBuilderStruct(DataFl`
    - `tables1MBuilderSt -> :
        return `
    - `ts=_SPLITS -> pe=_TYPE
  `

**`class -> DataFlow:
        """`**
  - Location: line 243-334
  - Inherits:         Returns a d
  - from which you can stream datapoints of ima
  - Public methods (1):
    - `ollowing arguments affect the return
  ->    value`

#### deepdoctection/datasets/instances/pubtabnet.py

**`class     """

`**
  - Location: line 110-133
  - Inherits:    _name = _NAM
  - @classmethod
    def _info(
  - Public methods (3):
    - `o(
        ->  name=_NAME`
    - `rn DatasetCategor -> init_categories=_`
    - `ubtabnetBuilde -> cation=_LOCATION`

**`class ubtabnet dataflo`**
  - Location: line 136-212
  - Inherits:  builder
    """

 
  - build(self, **kwargs: Union[str, int]) ->
  - Public methods (1):
    - `        """
        Returns a dataflow -> m which `

#### deepdoctection/datasets/instances/rvlcdip.py

**`class name = `**
  - Location: line 93-116
  - Inherits: NAME

    @clas
  - def _info(cls) ->
  - Public methods (3):
    - `       nam -> AME,
      `
    - `der(location=_ -> TION, annotati`
    - `etCategories(init -> egories=_INIT_CAT`

**`class aflow builder
`**
  - Location: line 119-182
  - Inherits:    """

    def bui
  - , **kwargs: Union[str, int]) -> DataFlow
  - Public methods (1):
    - `"""
        Returns a dataflow from wh -> you can `

#### deepdoctection/datasets/instances/xfund.py

**`class "

  `**
  - Location: line 98-121
  - Inherits:  _name = _NAME

  - lassmethod
    def _i
  - Public methods (3):
    - `fundBuilder(lo -> on=_LOCATION`
    - `return DatasetCat -> ies(init_categori`
    - `tInfo(
    ->      name=_`

**`class fund dataflo`**
  - Location: line 124-243
  - Inherits:  builder
    """

 
  - build(self, **kwargs: Union[str, int])
  - Public methods (1):
    - `ow:
        """
        Returns a data ->  from wh`

#### deepdoctection/eval/accmetric.py

**`class ClassificationMetric`**
  - Location: line 220-392
  - Inherits: MetricBase
  - Base metric class for classification metrics.
    Attributes:
    mapper: Function to map images to `category_id`
    _cats: Optional sequence of `ObjectTypes`
    _sub_cats: Optional mapping of object types to object types or sequences of `ObjectTypes`
    _summary_sub_cats: Optional sequence of `ObjectTypes` for summary
  - Public methods (7):
    - `dump(
        cls, dataflow_gt: DataFlow, dataflow_predictions: DataFlow, categories: DatasetCategories
    ) -> tuple[dict[str, list[int]], dict[str, list[int]]]`
    - `get_distance(
        cls, dataflow_gt: DataFlow, dataflow_predictions: DataFlow, categories: DatasetCategories
    ) -> list[MetricResults]`
    - `get_requirements(cls) -> list[Requirement]`
    - `print_result(cls) -> None`
    - `set_categories(
        cls,
        category_names: Optional[Union[TypeOrStr, Sequence[TypeOrStr]]] = None,
        sub_category_names: Optional[
            Union[Mapping[TypeOrStr, TypeOrStr], Mapping[TypeOrStr, Sequence[TypeOrStr]]]
        ] = None,
        summary_sub_category_names: Optional[Union[TypeOrStr, Sequence[TypeOrStr]]] = None,
    ) -> None`
    - `sub_cats(
        self,
    ) -> Optional[Union[Mapping[ObjectTypes, ObjectTypes], Mapping[ObjectTypes, Sequence[ObjectTypes]]]]`
    - `summary_sub_cats(self) -> Optional[Sequence[ObjectTypes]]`
  - Private methods (1):
    - `_category_sanity_checks(cls, categories: DatasetCategories) -> None`

**`class AccuracyMetric`**
  - Location: line 396-402
  - Inherits: ClassificationMetric
  - Metric induced by `accuracy`

**`class ConfusionMetric`**
  - Location: line 406-449
  - Inherits: ClassificationMetric
  - Metric induced by `confusion`
  - Public methods (2):
    - `get_distance(
        cls, dataflow_gt: DataFlow, dataflow_predictions: DataFlow, categories: DatasetCategories
    ) -> list[MetricResults]`
    - `print_result(cls) -> None`

**`class PrecisionMetric`**
  - Location: line 453-481
  - Inherits: ClassificationMetric
  - Metric induced by `precision`. Will calculate the precision per category
  - Public methods (1):
    - `get_distance(
        cls, dataflow_gt: DataFlow, dataflow_predictions: DataFlow, categories: DatasetCategories
    ) -> list[MetricResults]`

**`class RecallMetric`**
  - Location: line 485-491
  - Inherits: PrecisionMetric
  - Metric induced by `recall`. Will calculate the recall per category

**`class F1Metric`**
  - Location: line 495-501
  - Inherits: PrecisionMetric
  - Metric induced by `f1_score`. Will calculate the F1 per category

**`class PrecisionMetricMicro`**
  - Location: line 505-530
  - Inherits: ClassificationMetric
  - Metric induced by `precision`. Will calculate the micro average precision
  - Public methods (1):
    - `get_distance(
        cls, dataflow_gt: DataFlow, dataflow_predictions: DataFlow, categories: DatasetCategories
    ) -> list[MetricResults]`

**`class RecallMetricMicro`**
  - Location: line 534-540
  - Inherits: PrecisionMetricMicro
  - Metric induced by `recall`. Will calculate the micro average recall

**`class F1MetricMicro`**
  - Location: line 544-550
  - Inherits: PrecisionMetricMicro
  - Metric induced by `f1_score`. Will calculate the micro average F1

#### deepdoctection/eval/base.py

**`class MetricBase`**
  - Location: line 32-147
  - Inherits: ABC
  - Base class for metrics. Metrics only exist as classes and are not instantiated. They consist of two class 
variables:
    - A metric function that reads ground truth and prediction in an already transformed data format and
    returns a distance as an evaluation result.
    - A mapping function that transforms an image datapoint into a valid input format ready to ingest by the 
metric
    function.
    Using `get_distance`, ground truth and prediction dataflow can be read in and evaluated.
    `dump` is a helper method that is often called via `get_distance`. Here, the dataflows should be
    executed and the results should be saved in separate lists.
    Attributes:
    name (str): Name of the metric, usually the class name.
    metric (Callable[[Any, Any], Optional[Any]]): The metric function that computes the distance.
    _results (list[MetricResults]): Internal storage for results of the metric computation.
  - Public methods (5):
    - `dump(
        cls, dataflow_gt: DataFlow, dataflow_predictions: DataFlow, categories: DatasetCategories
    ) -> tuple[Any, Any]`
    - `get_distance(
        cls, dataflow_gt: DataFlow, dataflow_predictions: DataFlow, categories: DatasetCategories
    ) -> list[MetricResults]`
    - `get_requirements(cls) -> list[Requirement]`
    - `print_result(cls) -> None`
    - `result_list_to_dict(cls, results: list[MetricResults]) -> MetricResults`
  - Private methods (1):
    - `__new__(cls, *args, **kwargs)`

#### deepdoctection/eval/cocometric.py

**`class CocoMetric`**
  - Location: line 146-293
  - Inherits: MetricBase
  - Metric induced by `pycocotools.cocoeval.COCOeval`.
  - Public methods (5):
    - `dump(
        cls, dataflow_gt: DataFlow, dataflow_predictions: DataFlow, categories: DatasetCategories
    ) -> tuple[COCO, COCO]`
    - `get_distance(
        cls, dataflow_gt: DataFlow, dataflow_predictions: DataFlow, categories: DatasetCategories
    ) -> list[MetricResults]`
    - `get_requirements(cls) -> list[Requirement]`
    - `get_summary_default_parameters(cls) -> list[JsonDict]`
    - `set_params(
        cls,
        max_detections: Optional[list[int]] = None,
        area_range: Optional[list[list[int]]] = None,
        f1_score: bool = False,
        f1_iou: float = 0.9,
        per_category: bool = False,
    ) -> None`

#### deepdoctection/eval/eval.py

**`class Evaluator`**
  - Location: line 53-353
  - The API for evaluating pipeline components or pipelines on a given dataset. For a given model, a given 
dataset and
    a given metric, this class will stream the dataset, call the predictor(s) and will evaluate the 
predictions against
    the ground truth with respect to the given metric.
    After initializing the evaluator the process itself will start after calling the `run`.
    The following takes place under the hood:
    Setup of the dataflow according to the build- and split inputs. The `datasets.DataFlowBaseBuilder.build` 
will
    be invoked twice as one dataflow must be kept with its ground truth while the other must go through an 
annotation
    erasing process and after that passing the predictor. Predicted and gt datapoints will be converted into 
the
    required metric input format and dumped into lists. Both lists will be passed to 
`MetricBase.get_distance`.
    Note:
    You can evaluate the predictor on a subset of categories by filtering the ground truth dataset. When using
    the coco metric all predicted objects that are not in the set of filtered objects will be not taken into
    account.
    Example:
    ```python
    publaynet = get_dataset("publaynet")
    publaynet.dataflow.categories.filter_categories(categories=["TEXT","TITLE"])
    coco_metric = metric_registry.get("coco")
    profile = ModelCatalog.get_profile("layout/d2_model_0829999_layout_inf_only.pt")
    path_weights = ModelCatalog.get_full_path_weights("layout/d2_model_0829999_layout_inf_only.pt")
    path_config_yaml= ModelCatalog.get_full_path_configs("layout/d2_model_0829999_layout_inf_only.pt")
    layout_detector = D2FrcnnDetector(path_config_yaml, path_weights, profile.categories)
    layout_service = ImageLayoutService(layout_detector)
    evaluator = Evaluator(publaynet, layout_service, coco_metric)
    output = evaluator.run(max_datapoints=10)
    ```
    For another example check the script in `Evaluation` of table recognition`
  - Public methods (4):
    - `compare(self, interactive: bool = False, **kwargs: Union[str, int]) -> Generator[PixelValues, None, 
None]`
    - `run(
        self, output_as_dict: Literal[False] = False, **dataflow_build_kwargs: Union[str, int]
    ) -> list[dict[str, float]]`
    - `run(self, output_as_dict: Literal[True], **dataflow_build_kwargs: Union[str, int]) -> dict[str, float]`
    - `run(
        self, output_as_dict: bool = False, **dataflow_build_kwargs: Union[str, int]
    ) -> Union[list[dict[str, float]], dict[str, float]]`
  - Private methods (4):
    - `__init__(
        self,
        dataset: DatasetBase,
        component_or_pipeline: Union[PipelineComponent, DoctectionPipe],
        metric: Union[Type[MetricBase], MetricBase],
        num_threads: int = 2,
        run: Optional[wandb.sdk.wandb_run.Run] = None,
    ) -> None`
    - `_clean_up_predict_dataflow_annotations(self, df_pr: DataFlow) -> DataFlow`
    - `_run_pipe_or_component(self, df_pr: DataFlow) -> DataFlow`
    - `_sanity_checks(self) -> None`

**`class WandbTableAgent`**
  - Location: line 356-463
  - A class that creates a W&B table of sample predictions and sends them to the W&B server.
    Example:
    ```python
    df ... # some dataflow
    agent = WandbTableAgent(myrun,"MY_DATASET",50,{"1":"FOO"})
    for dp in df:
    agent.dump(dp)
    agent.log()
    ```
  - Public methods (3):
    - `dump(self, dp: Image) -> Image`
    - `log(self) -> None`
    - `reset(self) -> None`
  - Private methods (3):
    - `__init__(
        self,
        wandb_run: wandb.sdk.wandb_run.Run,
        dataset_name: str,
        num_samples: int,
        categories: Mapping[int, TypeOrStr],
        sub_categories: Optional[Mapping[int, TypeOrStr]] = None,
        cat_to_sub_cat: Optional[Mapping[TypeOrStr, TypeOrStr]] = None,
    )`
    - `_build_table(self) -> Table`
    - `_use_table_as_artifact(self) -> None`

#### deepdoctection/eval/tedsmetric.py

**`class TableTree`**
  - Location: line 54-81
  - Inherits: Tree
  - TableTree is derived class from `APTED.helpers.Tree`.
  - Public methods (1):
    - `bracket(self) -> str`
  - Private methods (1):
    - `__init__(  # pylint: disable=W0231
        self,
        *children: Any,
        tag: str,
        colspan: Optional[int] = None,
        rowspan: Optional[int] = None,
        content: Optional[list[str]] = None,
    ) -> None`

**`class CustomConfig`**
  - Location: line 84-106
  - Inherits: Config
  - `CustomConfig` for calculating `APTED` tree edit distance.
    Check APTED docs for more information
  - Public methods (3):
    - `maximum(*sequences: Any) -> int`
    - `normalized_distance(self, *sequences: Any) -> float`
    - `rename(self, node1: Any, node2: Any) -> float`

**`class TEDS`**
  - Location: line 109-199
  - Tree Edit Distance similarity
  - Public methods (3):
    - `evaluate(self, inputs: tuple[str, str]) -> float`
    - `load_html_tree(self, node: TableTree, parent: Optional[TableTree] = None) -> Optional[TableTree]`
    - `tokenize(self, node: TableTree) -> None`
  - Private methods (1):
    - `__init__(self, structure_only: bool = False)`

**`class TedsMetric`**
  - Location: line 234-284
  - Inherits: MetricBase
  - Metric induced by `TEDS`
  - Public methods (3):
    - `dump(
        cls, dataflow_gt: DataFlow, dataflow_predictions: DataFlow, categories: DatasetCategories
    ) -> tuple[list[str], list[str]]`
    - `get_distance(
        cls, dataflow_gt: DataFlow, dataflow_predictions: DataFlow, categories: DatasetCategories
    ) -> list[MetricResults]`
    - `get_requirements(cls) -> list[Requirement]`

#### deepdoctection/eval/tp_eval_callback.py

**`class EvalCallback`**
  - Location: line 54-129
  - Inherits: Callback
  - A callback that runs evaluation once in a while. It supports evaluation on any pipeline component.
  - Private methods (6):
    - `__init__(  # pylint: disable=W0231
        self,
        dataset: DatasetBase,
        category_names: Optional[Union[ObjectTypes, Sequence[ObjectTypes]]],
        sub_categories: Optional[Union[Mapping[ObjectTypes, ObjectTypes], Mapping[ObjectTypes, 
Sequence[ObjectTypes]]]],
        metric: Union[Type[MetricBase], MetricBase],
        pipeline_component: PipelineComponent,
        in_names: str,
        out_names: str,
        cfg: AttrDict,
        **build_eval_kwargs: str,
    ) -> None`
    - `_before_train(self) -> None`
    - `_build_predictor(self, idx: int) -> OnlinePredictor`
    - `_eval(self) -> None`
    - `_setup_graph(self) -> None`
    - `_trigger_epoch(self) -> None`

#### deepdoctection/extern/base.py

**`class ModelCategories`**
  - Location: line 52-145
  - Categories for models (except models for NER tasks) are managed in this class.
    Different to `DatasetCategories`, these members are immutable.
    Example:
    ```python
    categories = ModelCategories(init_categories={1: "text", 2: "title"})
    cats = categories.get_categories(as_dict=True)  # {1: LayoutType.text, 2: LayoutType.title}
    categories.filter_categories = [LayoutType.text]  # filter out text
    cats = categories.get_categories(as_dict=True)  # {2: LayoutType.title}
    ```
  - Public methods (7):
    - `filter_categories(self) -> Sequence[ObjectTypes]`
    - `filter_categories(self, categories: Sequence[ObjectTypes]) -> None`
    - `get_categories(self, as_dict: Literal[False]) -> tuple[ObjectTypes, ...]`
    - `get_categories(
        self, as_dict: Literal[True] = ..., name_as_key: Literal[False] = False
    ) -> MappingProxyType[int, ObjectTypes]`
    - `get_categories(self, as_dict: Literal[True], name_as_key: Literal[True]) -> 
MappingProxyType[ObjectTypes, int]`
    - `get_categories(
        self, as_dict: bool = True, name_as_key: bool = False
    ) -> Union[MappingProxyType[int, ObjectTypes], MappingProxyType[ObjectTypes, int], tuple[ObjectTypes, 
...]]`
    - `shift_category_ids(self, shift_by: int) -> MappingProxyType[int, ObjectTypes]`
  - Private methods (1):
    - `__post_init__(self) -> None`

**`class NerModelCategories`**
  - Location: line 149-251
  - Inherits: ModelCategories
  - Categories for models for NER tasks. It can handle the merging of token classes and bio tags to build a 
new set
    of categories.
    Example:
    ```python
    categories = NerModelCategories(categories_semantics=["question", "answer"], categories_bio=["B", "I"])
    cats = categories.get_categories(as_dict=True)  # {"1": TokenClassWithTag.b_question,
    "2": TokenClassWithTag.i_question,
    "3": TokenClassWithTag.b_answer,
    "4": TokenClassWithTag.i_answer}
    ```
    You can also leave the categories unchanged:
    Example:
    ```python
    categories = NerModelCategories(init_categories={"1": "question", "2": "answer"})
    cats = categories.get_categories(as_dict=True)  # {"1": TokenClasses.question,
    "2": TokenClasses.answer}
    ```
  - Public methods (2):
    - `disentangle_token_class_and_tag(category_name: ObjectTypes) -> Optional[tuple[ObjectTypes, 
ObjectTypes]]`
    - `merge_bio_semantics_categories(
        categories_semantics: tuple[ObjectTypes, ...], categories_bio: tuple[ObjectTypes, ...]
    ) -> MappingProxyType[int, ObjectTypes]`
  - Private methods (1):
    - `__post_init__(self) -> None`

**`class PredictorBase`**
  - Location: line 254-318
  - Inherits: ABC
  - Abstract base class for all types of predictors (e.g. object detectors language models, ...)
  - Public methods (4):
    - `clear_model(self) -> None`
    - `clone(self) -> PredictorBase`
    - `get_model_id(self) -> str`
    - `get_requirements(cls) -> list[Requirement]`
  - Private methods (1):
    - `__new__(cls, *args, **kwargs)`

**`class DetectionResult`**
  - Location: line 322-357
  - Simple mutable storage for detection results.
    Attributes:
    box: [ulx,uly,lrx,lry]
    class_id: category id
    score: prediction score
    mask: binary mask
    absolute_coords: absolute coordinates
    class_name: category name
    text: text string. Used for OCR predictors
    block: block number. For reading order from some ocr predictors
    line: line number. For reading order from some ocr predictors
    uuid: uuid. For assigning detection result (e.g. text to image annotations)
    relationships: A dictionary of relationships. Each key is a relationship type and each value is a list of
    uuids of the related annotations.
    angle: angle of rotation in degrees. Only used for text detection.
    image_width: image width
    image_height: image height

**`class ObjectDetector`**
  - Location: line 360-404
  - Inherits: PredictorBase, ABC
  - Abstract base class for object detection. This can be anything ranging from layout detection to OCR.
    Use this to connect external detectors with deepdoctection predictors on images.
    Example:
    ```python
    MyFancyTensorpackPredictor(TensorpackPredictor,ObjectDetector)
    ```
    and implement the `predict`.
  - Public methods (4):
    - `accepts_batch(self) -> bool`
    - `clone(self) -> ObjectDetector`
    - `get_category_names(self) -> tuple[ObjectTypes, ...]`
    - `predict(self, np_img: PixelValues) -> list[DetectionResult]`

**`class PdfMiner`**
  - Location: line 407-464
  - Inherits: PredictorBase, ABC
  - Abstract base class for mining information from PDF documents. Reads in a bytes stream from a PDF document
page.
    Use this to connect external pdf miners and wrap them into deepdoctection predictors.
    Attributes:
    categories: ModelCategories
    _pdf_bytes: Optional[bytes]: Bytes of the PDF document page to be processed by the predictor.
  - Public methods (5):
    - `accepts_batch(self) -> bool`
    - `clone(self) -> PdfMiner`
    - `get_category_names(self) -> tuple[ObjectTypes, ...]`
    - `get_width_height(self, pdf_bytes: bytes) -> tuple[float, float]`
    - `predict(self, pdf_bytes: bytes) -> list[DetectionResult]`

**`class TextRecognizer`**
  - Location: line 467-495
  - Inherits: PredictorBase, ABC
  - Abstract base class for text recognition. In contrast to `ObjectDetector` one assumes that `predict` 
accepts
    batches of `np.arrays`. More precisely, when using `predict` pass a list of tuples with uuids (e.g. 
`image_id`,
    or `annotation_id`) or `np.array`s.
  - Public methods (3):
    - `accepts_batch(self) -> bool`
    - `get_category_names() -> tuple[ObjectTypes, ...]`
    - `predict(self, images: list[tuple[str, PixelValues]]) -> list[DetectionResult]`

**`class TokenClassResult`**
  - Location: line 499-523
  - Simple mutable storage for token classification results
    Attributes:
    id: uuid of token (not unique)
    token_id: token id
    token: token
    class_id: category id
    class_name: category name
    semantic_name: semantic name
    bio_tag: bio tag
    score: prediction score
    successor_uuid: uuid of the next token in the sequence

**`class SequenceClassResult`**
  - Location: line 527-541
  - Storage for sequence classification results
    Attributes:
    class_id: category_id
    class_name: category_name
    score: prediction score
    class_name_orig: original class name

**`class LMTokenClassifier`**
  - Location: line 544-608
  - Inherits: PredictorBase, ABC
  - Abstract base class for token classifiers. If you want to connect external token classifiers with 
deepdoctection
    predictors wrap them into a class derived from this class.
  - Public methods (4):
    - `default_kwargs_for_image_to_features_mapping() -> JsonDict`
    - `image_to_features_mapping() -> str`
    - `image_to_raw_features_mapping() -> str`
    - `predict(self, **encodings: Union[list[list[str]], torch.Tensor]) -> list[TokenClassResult]`

**`class LMSequenceClassifier`**
  - Location: line 611-670
  - Inherits: PredictorBase, ABC
  - Abstract base class for sequence classification. If you want to connect external sequence classifiers with
    deepdoctection predictors, wrap them into a class derived from this class.
  - Public methods (4):
    - `default_kwargs_for_image_to_features_mapping() -> JsonDict`
    - `image_to_features_mapping() -> str`
    - `image_to_raw_features_mapping() -> str`
    - `predict(self, **encodings: Union[list[list[str]], torch.Tensor]) -> SequenceClassResult`

**`class LanguageDetector`**
  - Location: line 673-689
  - Inherits: PredictorBase, ABC
  - Abstract base class for language detectors.
  - Public methods (1):
    - `predict(self, text_string: str) -> DetectionResult`

**`class ImageTransformer`**
  - Location: line 692-756
  - Inherits: PredictorBase, ABC
  - Abstract base class for transforming an image.
  - Public methods (6):
    - `clone(self) -> ImageTransformer`
    - `get_category_names(self) -> tuple[ObjectTypes, ...]`
    - `inverse_transform_coords(self, detect_results: Sequence[DetectionResult]) -> Sequence[DetectionResult]`
    - `predict(self, np_img: PixelValues) -> DetectionResult`
    - `transform_coords(self, detect_results: Sequence[DetectionResult]) -> Sequence[DetectionResult]`
    - `transform_image(self, np_img: PixelValues, specification: DetectionResult) -> PixelValues`

**`class DeterministicImageTransformer`**
  - Location: line 759-838
  - Inherits: ImageTransformer
  - A wrapper for BaseTransform classes that implements the ImageTransformer interface.
    This class provides a bridge between the BaseTransform system (which handles image and coordinate
    transformations like rotation, padding, etc.) and the predictors framework by implementing the
    ImageTransformer interface. It allows BaseTransform objects to be used within pipelines that
    expect ImageTransformer components.
    The transformer performs deterministic transformations on images and their associated coordinates,
    enabling operations like padding, rotation, and other geometric transformations while maintaining
    the relationship between image content and annotation coordinates.
  - Public methods (7):
    - `clone(self) -> DeterministicImageTransformer`
    - `get_category_names(self) -> tuple[ObjectTypes, ...]`
    - `get_requirements(cls) -> list[Requirement]`
    - `inverse_transform_coords(self, detect_results: Sequence[DetectionResult]) -> Sequence[DetectionResult]`
    - `predict(self, np_img: PixelValues) -> DetectionResult`
    - `transform_coords(self, detect_results: Sequence[DetectionResult]) -> Sequence[DetectionResult]`
    - `transform_image(self, np_img: PixelValues, specification: DetectionResult) -> PixelValues`
  - Private methods (1):
    - `__init__(self, base_transform: BaseTransform) -> None`

#### deepdoctection/extern/d2detect.py

**`class D2FrcnnDetectorMixin`**
  - Location: line 154-216
  - Inherits: ObjectDetector, ABC
  - Base class for D2 Faster-RCNN implementation. This class only implements the basic wrapper functions
  - Public methods (3):
    - `get_category_names(self) -> tuple[ObjectTypes, ...]`
    - `get_inference_resizer(min_size_test: int, max_size_test: int) -> InferenceResize`
    - `get_name(path_weights: PathLikeOrStr, architecture: str) -> str`
  - Private methods (2):
    - `__init__(
        self,
        categories: Mapping[int, TypeOrStr],
        filter_categories: Optional[Sequence[TypeOrStr]] = None,
    )`
    - `_map_category_names(self, detection_results: list[DetectionResult]) -> list[DetectionResult]`

**`class D2FrcnnDetector`**
  - Location: line 219-400
  - Inherits: D2FrcnnDetectorMixin
  - D2 Faster-RCNN implementation with all the available backbones, normalizations throughout the model
    as well as FPN, optional Cascade-RCNN and many more.
    Currently, masks are not included in the data model.
    Note:
    There are no adjustment to the original implementation of Detectron2. Only one post-processing step is 
followed
    by the standard D2 output that takes into account of the situation that detected objects are disjoint. For
more
    infos on this topic, see <https://github.com/facebookresearch/detectron2/issues/978>.
    Example:
    ```python
    config_path = ModelCatalog.get_full_path_configs("dd/d2/item/CASCADE_RCNN_R_50_FPN_GN.yaml")
    weights_path = ModelDownloadManager.maybe_download_weights_and_configs("item/d2_model-800000-layout.pkl")
    categories = ModelCatalog.get_profile("item/d2_model-800000-layout.pkl").categories
    d2_predictor = D2FrcnnDetector(config_path,weights_path,categories,device="cpu")
    detection_results = d2_predictor.predict(bgr_image_np_array)
    ```
  - Public methods (5):
    - `clear_model(self) -> None`
    - `clone(self) -> D2FrcnnDetector`
    - `get_requirements(cls) -> list[Requirement]`
    - `get_wrapped_model(
        path_yaml: PathLikeOrStr,
        path_weights: PathLikeOrStr,
        config_overwrite: list[str],
        device: Optional[Union[Literal["cpu", "cuda"], torch.device]] = None,
    ) -> GeneralizedRCNN`
    - `predict(self, np_img: PixelValues) -> list[DetectionResult]`
  - Private methods (5):
    - `__init__(
        self,
        path_yaml: PathLikeOrStr,
        path_weights: PathLikeOrStr,
        categories: Mapping[int, TypeOrStr],
        config_overwrite: Optional[list[str]] = None,
        device: Optional[Union[Literal["cpu", "cuda"], torch.device]] = None,
        filter_categories: Optional[Sequence[TypeOrStr]] = None,
    )`
    - `_get_d2_config_list(path_weights: PathLikeOrStr, config_overwrite: list[str]) -> list[str]`
    - `_instantiate_d2_predictor(wrapped_model: GeneralizedRCNN, path_weights: PathLikeOrStr) -> None`
    - `_set_config(path_yaml: PathLikeOrStr, d2_conf_list: list[str], device: torch.device) -> CfgNode`
    - `_set_model(config: CfgNode) -> GeneralizedRCNN`

**`class D2FrcnnTracingDetector`**
  - Location: line 403-527
  - Inherits: D2FrcnnDetectorMixin
  - D2 Faster-RCNN exported torchscript model. Using this predictor has the advantage that Detectron2 does not
have to
    be installed. The associated config setting only contains parameters that are involved in pre-and 
post-processing.
    Depending on running the model with CUDA or on a CPU, it will need the appropriate exported model.
    Note:
    There are no adjustment to the original implementation of Detectron2. Only one post-processing step is 
followed
    by the standard D2 output that takes into account of the situation that detected objects are disjoint. For
more
    infos on this topic, see <https://github.com/facebookresearch/detectron2/issues/978>.
    Example:
    ```python
    config_path = ModelCatalog.get_full_path_configs("dd/d2/item/CASCADE_RCNN_R_50_FPN_GN.yaml")
    weights_path = ModelDownloadManager.maybe_download_weights_and_configs("item/d2_model-800000-layout.pkl")
    categories = ModelCatalog.get_profile("item/d2_model-800000-layout.pkl").categories
    d2_predictor = D2FrcnnDetector(config_path,weights_path,categories)
    detection_results = d2_predictor.predict(bgr_image_np_array)
    ```
  - Public methods (6):
    - `clear_model(self) -> None`
    - `clone(self) -> D2FrcnnTracingDetector`
    - `get_category_names(self) -> tuple[ObjectTypes, ...]`
    - `get_requirements(cls) -> list[Requirement]`
    - `get_wrapped_model(path_weights: PathLikeOrStr) -> torch.jit.ScriptModule`
    - `predict(self, np_img: PixelValues) -> list[DetectionResult]`
  - Private methods (2):
    - `__init__(
        self,
        path_yaml: PathLikeOrStr,
        path_weights: PathLikeOrStr,
        categories: Mapping[int, TypeOrStr],
        config_overwrite: Optional[list[str]] = None,
        filter_categories: Optional[Sequence[TypeOrStr]] = None,
    )`
    - `_set_config(
        path_yaml: PathLikeOrStr, path_weights: PathLikeOrStr, config_overwrite: Optional[list[str]]
    ) -> AttrDict`

#### deepdoctection/extern/deskew.py

**`class Jdeskewer`**
  - Location: line 36-92
  - Inherits: ImageTransformer
  - Deskew an image following <https://phamquiluan.github.io/files/paper2.pdf>. It allows to determine that 
deskew angle
    up to 45 degrees and provides the corresponding rotation so that text lines range horizontally.
  - Public methods (5):
    - `clone(self) -> Jdeskewer`
    - `get_category_names(self) -> tuple[ObjectTypes, ...]`
    - `get_requirements(cls) -> list[Requirement]`
    - `predict(self, np_img: PixelValues) -> DetectionResult`
    - `transform_image(self, np_img: PixelValues, specification: DetectionResult) -> PixelValues`
  - Private methods (1):
    - `__init__(self, min_angle_rotation: float = 2.0)`

#### deepdoctection/extern/doctrocr.py

**`class DoctrTextlineDetectorMixin`**
  - Location: line 174-206
  - Inherits: ObjectDetector, ABC
  - Base class for DocTr text line detector. This class only implements the basic wrapper functions
  - Public methods (3):
    - `auto_select_lib() -> Literal["PT", "TF"]`
    - `get_category_names(self) -> tuple[ObjectTypes, ...]`
    - `get_name(path_weights: PathLikeOrStr, architecture: str) -> str`
  - Private methods (1):
    - `__init__(self, categories: Mapping[int, TypeOrStr], lib: Optional[Literal["PT", "TF"]] = None)`

**`class DoctrTextlineDetector`**
  - Location: line 209-331
  - Inherits: DoctrTextlineDetectorMixin
  - A deepdoctection wrapper of DocTr text line detector. We model text line detection as ObjectDetector
    and assume to use this detector in a ImageLayoutService.
    DocTr supports several text line detection implementations but provides only a subset of pre-trained 
models.
    The most usable one for document OCR for which a pre-trained model exists is DBNet as described in 
“Real-time Scene
    Text Detection with Differentiable Binarization”, with a ResNet-50 backbone. This model can be used in 
either
    Tensorflow or PyTorch.
    Some other pre-trained models exist that have not been registered in `ModelCatalog`. Please check the 
DocTr library
    and organize the download of the pre-trained model by yourself.
    Example:
    ```python
    path_weights_tl = ModelDownloadManager.maybe_download_weights_and_configs("doctr/db_resnet50/pt
    /db_resnet50-ac60cadc.pt")
    # Use "doctr/db_resnet50/tf/db_resnet50-adcafc63.zip" for Tensorflow
    categories = ModelCatalog.get_profile("doctr/db_resnet50/pt/db_resnet50-ac60cadc.pt").categories
    det = DoctrTextlineDetector("db_resnet50",path_weights_tl,categories,"cpu")
    layout = ImageLayoutService(det,to_image=True, crop_image=True)
    path_weights_tr = dd.ModelDownloadManager.maybe_download_weights_and_configs("doctr/crnn_vgg16_bn
    /pt/crnn_vgg16_bn-9762b0b0.pt")
    rec = DoctrTextRecognizer("crnn_vgg16_bn", path_weights_tr, "cpu")
    text = TextExtractionService(rec, extract_from_roi="word")
    analyzer = DoctectionPipe(pipeline_component_list=[layout,text])
    path = "/path/to/image_dir"
    df = analyzer.analyze(path = path)
    for dp in df:
    ...
    """
  - Public methods (6):
    - `e(self) ->  -> rTextlineDetector:
  `
    - `ict(self, np_img: PixelValues) ->  -> [DetectionResult]:
  `
    - `it__(
        self,
        architecture: str,
        path_weights: PathLikeOrStr,
        categories: Mapping[int, TypeOrStr],
        device: Optional[Union[Literal["cpu", "cuda"], torch.device, tf.device]] = None,
        lib: Optional[Literal["PT", "TF"]] = None,
    ) ->  -> :
  `
    - `r_model(self) ->  -> :
  `
    - `requirements(cls) ->  -> [Requirement]:
  `
    - `wrapped_model(
        architecture: str, path_weights: PathLikeOrStr, device: Union[torch.device, tf.device], lib: 
Literal["PT", "TF"]
    ) ->  -> 
  `
  - Private methods (1):
    - `_model(
        path_weights: PathLikeOrStr,
        doctr_predictor: DetectionPredictor,
        device: Union[torch.device, tf.device],
        lib: Literal["PT", "TF"],
    ) ->  -> :
  `

**`class rTextRecognizer(Tex`**
  - Location: line 334-532
  - Inherits: Recognizer):
 
  - A deepdoctection wrapper of DocTr text recognition predictor. The base class is a `TextRecognizer` that 
takes
    a batch of sub images (e.g. text lines from a text detector) and returns a list with text spotted in the 
sub images.
    DocTr supports several text recognition models but provides only a subset of pre-trained models.
    This model that is most suitable for document text recognition is the CRNN implementation with a VGG-16 
backbone as
    described in “An End-to-End Trainable Neural Network for Image-based Sequence Recognition and Its 
Application to
    Scene Text Recognition”. It can be used in either Tensorflow or PyTorch.
    For more details please check the official DocTr documentation by Mindee: 
<https://mindee.github.io/doctr/>
    Example:
    ```python
    path_weights_tl = ModelDownloadManager.maybe_download_weights_and_configs("doctr/db_resnet50/pt
    /db_resnet50-ac60cadc.pt")
    # Use "doctr/db_resnet50/tf/db_resnet50-adcafc63.zip" for Tensorflow
    categories = ModelCatalog.get_profile("doctr/db_resnet50/pt/db_resnet50-ac60cadc.pt").categories
    det = DoctrTextlineDetector("db_resnet50",path_weights_tl,categories,"cpu")
    layout = ImageLayoutService(det,to_image=True, crop_image=True)
    path_weights_tr = dd.ModelDownloadManager.maybe_download_weights_and_configs("doctr/crnn_vgg16_bn
    /pt/crnn_vgg16_bn-9762b0b0.pt")
    rec = DoctrTextRecognizer("crnn_vgg16_bn", path_weights_tr, "cpu")
    text = TextExtractionService(rec, extract_from_roi="word")
    analyzer = DoctectionPipe(pipeline_component_list=[layout,text])
    path = "/path/to/image_dir"
    df = analyzer.analyze(path = path)
    for dp in df:
    ...
    """
    de
  - Public methods (10):
    - `(
        self,
        architecture: str,
        path_weights: PathLikeOrStr,
        device: Optional[Union[Literal["cpu", "cuda"], torch.device, tf.device]] = None,
        lib: Optional[Literal["PT", "TF"]] = None,
        path_config_json: Optional[PathLikeOrStr] = None,
    ) -> None ->     `
    - `(path_weights: PathLikeOrStr, architecture: str) -> str: ->    `
    - `del(
        architecture: str, lib: Literal["TF", "PT"], path_config_json: Optional[PathLikeOrStr] = None
    ) -> Reco -> ionPredictor:
      `
    - `del(self) -> None ->     `
    - `ect_lib() -> Lite -> "PT", "TF"]:
      `
    - `el(
        path_weights: PathLikeOrStr,
        doctr_predictor: RecognitionPredictor,
        device: Union[torch.device, tf.device],
        lib: Literal["PT", "TF"],
    ) -> None ->     `
    - `irements(cls) -> list -> uirement]:
      `
    - `lf) -> Doct -> tRecognizer:
      `
    - `ped_model(
        architecture: str,
        path_weights: PathLikeOrStr,
        device: Union[torch.device, tf.device],
        lib: Literal["PT", "TF"],
        path_config_json: Optional[PathLikeOrStr] = None,
    ) -> Any: ->    `
    - `self, images: list[tuple[str, PixelValues]]) -> list -> ectionResult]:
      `

**`class ationTransformer(ImageTr`**
  - Location: line 535-614
  - Inherits: nsformer):
    "
  - The `DocTrRotationTransformer` class is a specialized image transformer that is designed to handle image 
rotation
    in the context of Optical Character Recognition (OCR) tasks. It inherits from the `ImageTransformer` base 
class and
    implements methods for predicting and applying rotation transformations to images.
    The `predict` method determines the angle of the rotated image using the `estimate_orientation` function 
from the
    `doctr.models._utils` module. The `n_ct` and `ratio_threshold_for_lines` parameters for this function can 
be
    configured when instantiating the class.
    The `transform` method applies the predicted rotation to the image, effectively rotating the image 
backwards.
    This method uses either the Pillow library or OpenCV for the rotation operation, depending on the 
configuration.
    This class can be particularly useful in OCR tasks where the orientation of the text in the image matters.
    The class also provides methods for cloning itself and for getting the requirements of the OCR system.
    Example:
    ```python
    transformer = DocTrRotationTransformer()
    detection_result = transformer.predict(np_img)
    rotated_image = transformer.transform(np_img, detection_result)
    ```
    """
    de
  - Public methods (7):
    - `(self, number_contours: int = 50, ratio_threshold_for_lines: float = 5):
      `
    - `gory_names(self) -> tupl -> jectTypes, ...]:
      `
    - `irements(cls) -> list -> uirement]:
      `
    - `lf) -> DocT -> ationTransformer:
      `
    - `m_coords(self, detect_results: Sequence[DetectionResult]) -> Sequ -> [DetectionResult]:
      `
    - `m_image(self, np_img: PixelValues, specification: DetectionResult) -> Pixe -> ues:
      `
    - `self, np_img: PixelValues) -> Dete -> nResult:
      `

#### deepdoctection/extern/fastlang.py

**`class FasttextLangDetectorMixin`**
  - Location: line 42-70
  - Inherits: LanguageDetector, ABC
  - Base class for `Fasttext` language detection implementation. This class only implements the basic wrapper 
functions.
  - Public methods (2):
    - `get_name(path_weights: PathLikeOrStr) -> str`
    - `output_to_detection_result(self, output: Union[tuple[Any, Any]]) -> DetectionResult`
  - Private methods (1):
    - `__init__(self, categories: Mapping[int, TypeOrStr], categories_orig: Mapping[str, TypeOrStr]) -> None`

**`class FasttextLangDetector`**
  - Location: line 74-132
  - Inherits: FasttextLangDetectorMixin
  - Fasttext language detector wrapper. Two models provided in the fasttext library can be used to identify 
languages.
    The background to the models can be found in the works:
    Info:
    [1] Joulin A, Grave E, Bojanowski P, Mikolov T, Bag of Tricks for Efficient Text Classification
    [2] Joulin A, Grave E, Bojanowski P, Douze M, Jégou H, Mikolov T, FastText.zip: Compressing text 
classification
    models
    When loading the models via the `ModelCatalog`, the original and unmodified models are used.
    Example:
    ```python
    path_weights = ModelCatalog.get_full_path_weights("fasttext/lid.176.bin")
    profile = ModelCatalog.get_profile("fasttext/lid.176.bin")
    lang_detector = FasttextLangDetector(path_weights,profile.categories)
    detection_result = lang_detector.predict("some text in some language")
    ```
    """
  - Public methods (4):
    - `et_requirements(cls)  -> ist[Requirement]:`
    - `et_wrapped_model(path_weights: PathLikeOrStr)  -> ny:`
    - `lone(self)  -> asttextLangDetector:`
    - `redict(self, text_string: str)  -> etectionResult:`
  - Private methods (1):
    - `_init__(
        self, path_weights: PathLikeOrStr, categories: Mapping[int, TypeOrStr], categories_orig: Mapping[str, 
TypeOrStr]
    ):`

#### deepdoctection/extern/hfdetr.py

**`class HFDetrDerivedDetectorMixin`**
  - Location: line 107-162
  - Inherits: ObjectDetector, ABC
  - Base class for Detr object detector. This class only implements the basic wrapper functions
  - Public methods (2):
    - `get_category_names(self) -> tuple[ObjectTypes, ...]`
    - `get_name(path_weights: PathLikeOrStr) -> str`
  - Private methods (2):
    - `__init__(self, categories: Mapping[int, TypeOrStr], filter_categories: Optional[Sequence[TypeOrStr]] = 
None)`
    - `_map_category_names(self, detection_results: list[DetectionResult]) -> list[DetectionResult]`

**`class HFDetrDerivedDetector`**
  - Location: line 165-363
  - Inherits: HFDetrDerivedDetectorMixin
  - Model wrapper for `TableTransformerForObjectDetection` that again is based on
    <https://github.com/microsoft/table-transformer>.
    The wrapper can be used to load pre-trained models for table detection and table structure recognition. 
Running Detr
    models trained from scratch on custom datasets is possible as well.
    Note:
    This wrapper will load `TableTransformerForObjectDetection` that is slightly different compared to
    `DetrForObjectDetection` that can be found in the transformer library as well.
    Example:
    ```python
    config_path = ModelCatalog.
    get_full_path_configs("microsoft/table-transformer-structure-recognition/pytorch_model.bin")
    weights_path = ModelDownloadManager.
    get_full_path_weights("microsoft/table-transformer-structure-recognition/pytorch_model.bin")
    feature_extractor_config_path = ModelDownloadManager.
    get_full_path_preprocessor_configs("microsoft/table-transformer-structure-recognition/pytorch_model.bin")
    categories = ModelCatalog.
    get_profile("microsoft/table-transformer-structure-recognition/pytorch_model.bin").categories
    detr_predictor = HFDetrDerivedDetector(config_path,weights_path,feature_extractor_config_path,categories)
    detection_result = detr_predictor.predict(bgr_image_np_array)
    ```
  - Public methods (8):
    - `clear_model(self) -> None`
    - `clone(self) -> HFDetrDerivedDetector`
    - `get_config(path_config: PathLikeOrStr) -> PretrainedConfig`
    - `get_model(path_weights: PathLikeOrStr, config: PretrainedConfig) -> EligibleDetrModel`
    - `get_pre_processor(path_feature_extractor_config: PathLikeOrStr, config: PretrainedConfig) -> 
DetrImageProcessor`
    - `get_requirements(cls) -> list[Requirement]`
    - `get_wrapped_model(
        path_config_json: PathLikeOrStr,
        path_weights: PathLikeOrStr,
        device: Optional[Union[Literal["cpu", "cuda"], torch.device]] = None,
    ) -> TableTransformerForObjectDetection`
    - `predict(self, np_img: PixelValues) -> list[DetectionResult]`
  - Private methods (1):
    - `__init__(
        self,
        path_config_json: PathLikeOrStr,
        path_weights: PathLikeOrStr,
        path_feature_extractor_config_json: PathLikeOrStr,
        categories: Mapping[int, TypeOrStr],
        device: Optional[Union[Literal["cpu", "cuda"], torch.device]] = None,
        filter_categories: Optional[Sequence[TypeOrStr]] = None,
    )`

#### deepdoctection/extern/hflayoutlm.py

**`class HFLayoutLmTokenClassifierBase`**
  - Location: line 242-377
  - Inherits: LMTokenClassifier, ABC
  - Abstract base class for wrapping `LayoutLM` models for token classification into the framework.
  - Public methods (6):
    - `clone(self) -> HFLayoutLmTokenClassifierBase`
    - `get_name(path_weights: PathLikeOrStr, architecture: str) -> str`
    - `get_requirements(cls) -> list[Requirement]`
    - `get_tokenizer_class_name(model_class_name: str, use_xlm_tokenizer: bool) -> str`
    - `image_to_features_mapping() -> str`
    - `image_to_raw_features_mapping() -> str`
  - Private methods (3):
    - `__init__(
        self,
        path_config_json: PathLikeOrStr,
        path_weights: PathLikeOrStr,
        categories_semantics: Optional[Sequence[TypeOrStr]] = None,
        categories_bio: Optional[Sequence[TypeOrStr]] = None,
        categories: Optional[Mapping[int, TypeOrStr]] = None,
        device: Optional[Union[Literal["cpu", "cuda"], torch.device]] = None,
        use_xlm_tokenizer: bool = False,
    )`
    - `_map_category_names(self, token_results: list[TokenClassResult]) -> list[TokenClassResult]`
    - `_validate_encodings(
        self, **encodings: Any
    ) -> tuple[list[list[str]], list[str], torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, 
list[list[str]]]`

**`class HFLayoutLmTokenClassifier`**
  - Location: line 380-494
  - Inherits: HFLayoutLmTokenClassifierBase
  - A wrapper class for `transformers.LayoutLMForTokenClassification` to use within a pipeline component.
    Check <https://huggingface.co/docs/transformers/model_doc/layoutlm> for documentation of the model itself.
    Note that this model is equipped with a head that is only useful when classifying tokens. For sequence
    classification and other things please use another model of the family.
    Example:
    ```python
    # setting up compulsory ocr service
    tesseract_config_path = ModelCatalog.get_full_path_configs("/dd/conf_tesseract.yaml")
    tess = TesseractOcrDetector(tesseract_config_path)
    ocr_service = TextExtractionService(tess)
    # hf tokenizer and token classifier
    tokenizer = LayoutLMTokenizerFast.from_pretrained("microsoft/layoutlm-base-uncased")
    layoutlm = HFLayoutLmTokenClassifier("path/to/config.json","path/to/model.bin",
    categories= ['B-answer', 'B-header', 'B-question', 'E-answer',
    'E-header', 'E-question', 'I-answer', 'I-header',
    'I-question', 'O', 'S-answer', 'S-header',
    'S-question'])
    # token classification service
    layoutlm_service = LMTokenClassifierService(tokenizer,layoutlm)
    pipe = DoctectionPipe(pipeline_component_list=[ocr_service,layoutlm_service])
    path = "path/to/some/form"
    df = pipe.analyze(path=path)
    for dp in df:
    ...
    ```
  - Public methods (3):
    - `clear_model(self) -> None`
    - `get_wrapped_model(
        path_config_json: PathLikeOrStr, path_weights: PathLikeOrStr
    ) -> LayoutLMForTokenClassification`
    - `predict(self, **encodings: Union[list[list[str]], torch.Tensor]) -> list[TokenClassResult]`
  - Private methods (1):
    - `__init__(
        self,
        path_config_json: PathLikeOrStr,
        path_weights: PathLikeOrStr,
        categories_semantics: Optional[Sequence[TypeOrStr]] = None,
        categories_bio: Optional[Sequence[TypeOrStr]] = None,
        categories: Optional[Mapping[int, TypeOrStr]] = None,
        device: Optional[Union[Literal["cpu", "cuda"], torch.device]] = None,
        use_xlm_tokenizer: bool = False,
    )`

**`class HFLayoutLmv2TokenClassifier`**
  - Location: line 497-623
  - Inherits: HFLayoutLmTokenClassifierBase
  - A wrapper class for `transformers.LayoutLMv2ForTokenClassification` to use within a pipeline component.
    Check <https://huggingface.co/docs/transformers/v4.24.0/en/model_doc/layoutlmv2>  for documentation of the
model
    itself. Note that this model is equipped with a head that is only useful when classifying tokens. For 
sequence
    classification and other things please use another model of the family.
    Note, that you must use `LayoutLMTokenizerFast` as tokenizer. `LayoutLMv2TokenizerFast` will not be 
accepted.
    Example:
    ```python
    # setting up compulsory ocr service
    tesseract_config_path = ModelCatalog.get_full_path_configs("/dd/conf_tesseract.yaml")
    tess = TesseractOcrDetector(tesseract_config_path)
    ocr_service = TextExtractionService(tess)
    # hf tokenizer and token classifier
    tokenizer = LayoutLMTokenizerFast.from_pretrained("microsoft/layoutlm-base-uncased")
    layoutlm = HFLayoutLmv2TokenClassifier("path/to/config.json","path/to/model.bin",
    categories= ['B-answer', 'B-header', 'B-question', 'E-answer',
    'E-header', 'E-question', 'I-answer', 'I-header',
    'I-question', 'O', 'S-answer', 'S-header',
    'S-question'])
    # token classification service
    layoutlm_service = LMTokenClassifierService(tokenizer,layoutlm)
    pipe = DoctectionPipe(pipeline_component_list=[ocr_service,layoutlm_service])
    path = "path/to/some/form"
    df = pipe.analyze(path=path)
    for dp in df:
    ...
    ```
  - Public methods (4):
    - `clear_model(self) -> None`
    - `default_kwargs_for_image_to_features_mapping() -> JsonDict`
    - `get_wrapped_model(
        path_config_json: PathLikeOrStr, path_weights: PathLikeOrStr
    ) -> LayoutLMv2ForTokenClassification`
    - `predict(self, **encodings: Union[list[list[str]], torch.Tensor]) -> list[TokenClassResult]`
  - Private methods (1):
    - `__init__(
        self,
        path_config_json: PathLikeOrStr,
        path_weights: PathLikeOrStr,
        categories_semantics: Optional[Sequence[TypeOrStr]] = None,
        categories_bio: Optional[Sequence[TypeOrStr]] = None,
        categories: Optional[Mapping[int, TypeOrStr]] = None,
        device: Optional[Union[Literal["cpu", "cuda"], torch.device]] = None,
        use_xlm_tokenizer: bool = False,
    )`

**`class HFLayoutLmv3TokenClassifier`**
  - Location: line 626-753
  - Inherits: HFLayoutLmTokenClassifierBase
  - A wrapper class for `transformers.LayoutLMv3ForTokenClassification` to use within a pipeline component.
    Check <https://huggingface.co/docs/transformers/v4.24.0/en/model_doc/layoutlmv3>  for documentation of the
model
    itself. Note that this model is equipped with a head that is only useful when classifying tokens. For 
sequence
    classification and other things please use another model of the family.
    Note, that you must use `RobertaTokenizerFast` as tokenizer. `LayoutLMv3TokenizerFast` will not be 
accepted.
    **Example**
    # setting up compulsory ocr service
    tesseract_config_path = ModelCatalog.get_full_path_configs("/dd/conf_tesseract.yaml")
    tess = TesseractOcrDetector(tesseract_config_path)
    ocr_service = TextExtractionService(tess)
    # hf tokenizer and token classifier
    tokenizer = RobertaTokenizerFast.from_pretrained("roberta-base")
    layoutlm = HFLayoutLmv3TokenClassifier("path/to/config.json","path/to/model.bin",
    categories= ['B-answer', 'B-header', 'B-question', 'E-answer',
    'E-header', 'E-question', 'I-answer', 'I-header',
    'I-question', 'O', 'S-answer', 'S-header',
    'S-question'])
    # token classification service
    layoutlm_service = LMTokenClassifierService(tokenizer, layoutlm)
    pipe = DoctectionPipe(pipeline_component_list=[ocr_service,layoutlm_service])
    path = "path/to/some/form"
    df = pipe.analyze(path=path)
    for dp in df:
    ...
  - Public methods (4):
    - `clear_model(self) -> None`
    - `default_kwargs_for_image_to_features_mapping() -> JsonDict`
    - `get_wrapped_model(
        path_config_json: PathLikeOrStr, path_weights: PathLikeOrStr
    ) -> LayoutLMv3ForTokenClassification`
    - `predict(self, **encodings: Union[list[list[str]], torch.Tensor]) -> list[TokenClassResult]`
  - Private methods (1):
    - `__init__(
        self,
        path_config_json: PathLikeOrStr,
        path_weights: PathLikeOrStr,
        categories_semantics: Optional[Sequence[TypeOrStr]] = None,
        categories_bio: Optional[Sequence[TypeOrStr]] = None,
        categories: Optional[Mapping[int, TypeOrStr]] = None,
        device: Optional[Union[Literal["cpu", "cuda"], torch.device]] = None,
        use_xlm_tokenizer: bool = False,
    )`

**`class HFLayoutLmSequenceClassifierBase`**
  - Location: line 756-840
  - Inherits: LMSequenceClassifier, ABC
  - Abstract base class for wrapping LayoutLM models  for sequence classification into the deepdoctection 
framework.
  - Public methods (6):
    - `clone(self) -> HFLayoutLmSequenceClassifierBase`
    - `get_name(path_weights: PathLikeOrStr, architecture: str) -> str`
    - `get_requirements(cls) -> list[Requirement]`
    - `get_tokenizer_class_name(model_class_name: str, use_xlm_tokenizer: bool) -> str`
    - `image_to_features_mapping() -> str`
    - `image_to_raw_features_mapping() -> str`
  - Private methods (2):
    - `__init__(
        self,
        path_config_json: PathLikeOrStr,
        path_weights: PathLikeOrStr,
        categories: Mapping[int, TypeOrStr],
        device: Optional[Union[Literal["cpu", "cuda"], torch.device]] = None,
        use_xlm_tokenizer: bool = False,
    )`
    - `_validate_encodings(
        self, **encodings: Union[list[list[str]], torch.Tensor]
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]`

**`class HFLayoutLmSequenceClassifier`**
  - Location: line 843-947
  - Inherits: HFLayoutLmSequenceClassifierBase
  - A wrapper class for `transformers.LayoutLMForSequenceClassification` to use within a pipeline component.
    Check <https://huggingface.co/docs/transformers/model_doc/layoutlm> for documentation of the model itself.
    Note that this model is equipped with a head that is only useful for classifying the input sequence. For 
token
    classification and other things please use another model of the family.
    Example:
    ```python
    # setting up compulsory ocr service
    tesseract_config_path = ModelCatalog.get_full_path_configs("/dd/conf_tesseract.yaml")
    tess = TesseractOcrDetector(tesseract_config_path)
    ocr_service = TextExtractionService(tess)
    # hf tokenizer and token classifier
    tokenizer = LayoutLMTokenizerFast.from_pretrained("microsoft/layoutlm-base-uncased")
    layoutlm = HFLayoutLmSequenceClassifier("path/to/config.json","path/to/model.bin",
    categories=["handwritten", "presentation", "resume"])
    # token classification service
    layoutlm_service = LMSequenceClassifierService(tokenizer,layoutlm)
    pipe = DoctectionPipe(pipeline_component_list=[ocr_service,layoutlm_service])
    path = "path/to/some/form"
    df = pipe.analyze(path=path)
    for dp in df:
    ...
    ```
  - Public methods (3):
    - `clear_model(self) -> None`
    - `get_wrapped_model(
        path_config_json: PathLikeOrStr, path_weights: PathLikeOrStr
    ) -> LayoutLMForSequenceClassification`
    - `predict(self, **encodings: Union[list[list[str]], torch.Tensor]) -> SequenceClassResult`
  - Private methods (1):
    - `__init__(
        self,
        path_config_json: PathLikeOrStr,
        path_weights: PathLikeOrStr,
        categories: Mapping[int, TypeOrStr],
        device: Optional[Union[Literal["cpu", "cuda"], torch.device]] = None,
        use_xlm_tokenizer: bool = False,
    )`

**`class HFLayoutLmv2SequenceClassifier`**
  - Location: line 950-1063
  - Inherits: HFLayoutLmSequenceClassifierBase
  - A wrapper class for `transformers.LayoutLMv2ForSequenceClassification` to use within a pipeline component.
    Check <https://huggingface.co/docs/transformers/v4.24.0/en/model_doc/layoutlmv2> for documentation of the 
model
    itself. Note that this model is equipped with a head that is only useful for classifying the input 
sequence. For
    token classification and other things please use another model of the family.
    Example:
    ```python
    # setting up compulsory ocr service
    tesseract_config_path = ModelCatalog.get_full_path_configs("/dd/conf_tesseract.yaml")
    tess = TesseractOcrDetector(tesseract_config_path)
    ocr_service = TextExtractionService(tess)
    # hf tokenizer and token classifier
    tokenizer = LayoutLMTokenizerFast.from_pretrained("microsoft/layoutlm-base-uncased")
    layoutlm = HFLayoutLmv2SequenceClassifier("path/to/config.json","path/to/model.bin",
    categories=["handwritten", "presentation", "resume"])
    # token classification service
    layoutlm_service = LMSequenceClassifierService(tokenizer,layoutlm)
    pipe = DoctectionPipe(pipeline_component_list=[ocr_service,layoutlm_service])
    path = "path/to/some/form"
    df = pipe.analyze(path=path)
    for dp in df:
    ...
    ```
  - Public methods (4):
    - `clear_model(self) -> None`
    - `default_kwargs_for_image_to_features_mapping() -> JsonDict`
    - `get_wrapped_model(
        path_config_json: PathLikeOrStr, path_weights: PathLikeOrStr
    ) -> LayoutLMv2ForSequenceClassification`
    - `predict(self, **encodings: Union[list[list[str]], torch.Tensor]) -> SequenceClassResult`
  - Private methods (1):
    - `__init__(
        self,
        path_config_json: PathLikeOrStr,
        path_weights: PathLikeOrStr,
        categories: Mapping[int, TypeOrStr],
        device: Optional[Union[Literal["cpu", "cuda"], torch.device]] = None,
        use_xlm_tokenizer: bool = False,
    )`

**`class HFLayoutLmv3SequenceClassifier`**
  - Location: line 1066-1165
  - Inherits: HFLayoutLmSequenceClassifierBase
  - A wrapper class for `transformers.LayoutLMv3ForSequenceClassification` to use within a pipeline component.
    Check <https://huggingface.co/docs/transformers/v4.24.0/en/model_doc/layoutlmv3> for documentation of the 
model
    itself. Note that this model is equipped with a head that is only useful for classifying the input 
sequence. For
    token classification and other things please use another model of the family.
    Example:
    ```python
    # setting up compulsory ocr service
    tesseract_config_path = ModelCatalog.get_full_path_configs("/dd/conf_tesseract.yaml")
    tess = TesseractOcrDetector(tesseract_config_path)
    ocr_service = TextExtractionService(tess)
    # hf tokenizer and token classifier
    tokenizer = RobertaTokenizerFast.from_pretrained("roberta-base")
    layoutlm = HFLayoutLmv3SequenceClassifier("path/to/config.json","path/to/model.bin",
    categories=["handwritten", "presentation", "resume"])
    # token classification service
    layoutlm_service = LMSequenceClassifierService(tokenizer,layoutlm)
    pipe = DoctectionPipe(pipeline_component_list=[ocr_service,layoutlm_service])
    path = "path/to/some/form"
    df = pipe.analyze(path=path)
    for dp in df:
    ...
    ```
  - Public methods (4):
    - `clear_model(self) -> None`
    - `default_kwargs_for_image_to_features_mapping() -> JsonDict`
    - `get_wrapped_model(
        path_config_json: PathLikeOrStr, path_weights: PathLikeOrStr
    ) -> LayoutLMv3ForSequenceClassification`
    - `predict(self, **encodings: Union[list[list[str]], torch.Tensor]) -> SequenceClassResult`
  - Private methods (1):
    - `__init__(
        self,
        path_config_json: PathLikeOrStr,
        path_weights: PathLikeOrStr,
        categories: Mapping[int, TypeOrStr],
        device: Optional[Union[Literal["cpu", "cuda"], torch.device]] = None,
        use_xlm_tokenizer: bool = False,
    )`

**`class HFLiltTokenClassifier`**
  - Location: line 1168-1277
  - Inherits: HFLayoutLmTokenClassifierBase
  - A wrapper class for `transformers.LiltForTokenClassification` to use within a pipeline component.
    Check <https://huggingface.co/docs/transformers/model_doc/lilt> for documentation of the model itself.
    Note that this model is equipped with a head that is only useful when classifying tokens. For sequence
    classification and other things please use another model of the family.
    Example:
    ```python
    # setting up compulsory ocr service
    tesseract_config_path = ModelCatalog.get_full_path_configs("/dd/conf_tesseract.yaml")
    tess = TesseractOcrDetector(tesseract_config_path)
    ocr_service = TextExtractionService(tess)
    # hf tokenizer and token classifier
    tokenizer = RobertaTokenizerFast.from_pretrained("roberta-base")
    lilt = HFLiltTokenClassifier("path/to/config.json","path/to/model.bin",
    categories= ['B-answer', 'B-header', 'B-question', 'E-answer',
    'E-header', 'E-question', 'I-answer', 'I-header',
    'I-question', 'O', 'S-answer', 'S-header',
    'S-question'])
    # token classification service
    lilt_service = LMTokenClassifierService(tokenizer,lilt)
    pipe = DoctectionPipe(pipeline_component_list=[ocr_service,lilt_service])
    path = "path/to/some/form"
    df = pipe.analyze(path=path)
    for dp in df:
    ...
    ```
  - Public methods (3):
    - `clear_model(self) -> None`
    - `get_wrapped_model(path_config_json: PathLikeOrStr, path_weights: PathLikeOrStr) -> 
LiltForTokenClassification`
    - `predict(self, **encodings: Union[list[list[str]], torch.Tensor]) -> list[TokenClassResult]`
  - Private methods (1):
    - `__init__(
        self,
        path_config_json: PathLikeOrStr,
        path_weights: PathLikeOrStr,
        categories_semantics: Optional[Sequence[TypeOrStr]] = None,
        categories_bio: Optional[Sequence[TypeOrStr]] = None,
        categories: Optional[Mapping[int, TypeOrStr]] = None,
        device: Optional[Union[Literal["cpu", "cuda"], torch.device]] = None,
        use_xlm_tokenizer: bool = False,
    )`

**`class HFLiltSequenceClassifier`**
  - Location: line 1280-1361
  - Inherits: HFLayoutLmSequenceClassifierBase
  - A wrapper class for `transformers.LiLTForSequenceClassification` to use within a pipeline component.
    Check <https://huggingface.co/docs/transformers/model_doc/lilt> for documentation of the model itself.
    Note that this model is equipped with a head that is only useful for classifying the input sequence. For 
token
    classification and other things please use another model of the family.
    Example:
    ```python
    # setting up compulsory ocr service
    tesseract_config_path = ModelCatalog.get_full_path_configs("/dd/conf_tesseract.yaml")
    tess = TesseractOcrDetector(tesseract_config_path)
    ocr_service = TextExtractionService(tess)
    # hf tokenizer and sequence classifier
    tokenizer = LayoutLMTokenizerFast.from_pretrained("microsoft/layoutlm-base-uncased")
    lilt = HFLiltSequenceClassifier("path/to/config.json",
    "path/to/model.bin",
    categories=["handwritten", "presentation", "resume"])
    # sequence classification service
    lilt_service = LMSequenceClassifierService(tokenizer,lilt)
    pipe = DoctectionPipe(pipeline_component_list=[ocr_service,lilt_service])
    path = "path/to/some/form"
    df = pipe.analyze(path=path)
    for dp in df:
    ...
    ```
  - Public methods (3):
    - `clear_model(self) -> None`
    - `get_wrapped_model(path_config_json: PathLikeOrStr, path_weights: PathLikeOrStr) -> Any`
    - `predict(self, **encodings: Union[list[list[str]], torch.Tensor]) -> SequenceClassResult`
  - Private methods (1):
    - `__init__(
        self,
        path_config_json: PathLikeOrStr,
        path_weights: PathLikeOrStr,
        categories: Mapping[int, TypeOrStr],
        device: Optional[Union[Literal["cpu", "cuda"], torch.device]] = None,
        use_xlm_tokenizer: bool = False,
    )`

#### deepdoctection/extern/hflm.py

**`class HFLmTokenClassifierBase`**
  - Location: line 130-260
  - Inherits: LMTokenClassifier, ABC
  - Abstract base class for wrapping Bert-like models for token classification into the framework.
  - Public methods (6):
    - `clone(self) -> HFLmTokenClassifierBase`
    - `get_name(path_weights: PathLikeOrStr, architecture: str) -> str`
    - `get_requirements(cls) -> list[Requirement]`
    - `get_tokenizer_class_name(model_class_name: str, use_xlm_tokenizer: bool) -> str`
    - `image_to_features_mapping() -> str`
    - `image_to_raw_features_mapping() -> str`
  - Private methods (3):
    - `__init__(
        self,
        path_config_json: PathLikeOrStr,
        path_weights: PathLikeOrStr,
        categories_semantics: Optional[Sequence[TypeOrStr]] = None,
        categories_bio: Optional[Sequence[TypeOrStr]] = None,
        categories: Optional[Mapping[int, TypeOrStr]] = None,
        device: Optional[Union[Literal["cpu", "cuda"], torch.device]] = None,
        use_xlm_tokenizer: bool = False,
    )`
    - `_map_category_names(self, token_results: list[TokenClassResult]) -> list[TokenClassResult]`
    - `_validate_encodings(
        self, **encodings: Any
    ) -> tuple[list[list[str]], list[str], torch.Tensor, torch.Tensor, torch.Tensor, list[list[str]]]`

**`class HFLmTokenClassifier`**
  - Location: line 263-371
  - Inherits: HFLmTokenClassifierBase
  - A wrapper class for `transformers.XLMRobertaForTokenClassification` and similar models to use within a 
pipeline
    component. Check <https://huggingface.co/docs/transformers/model_doc/xlm-roberta> for documentation of the
    model itself.
    Note that this model is equipped with a head that is only useful for classifying the tokens. For sequence
    classification and other things please use another model of the family.
    Example:
    ```python
    # setting up compulsory ocr service
    tesseract_config_path = ModelCatalog.get_full_path_configs("/dd/conf_tesseract.yaml")
    tess = TesseractOcrDetector(tesseract_config_path)
    ocr_service = TextExtractionService(tess)
    # hf tokenizer and token classifier
    tokenizer = XLMRobertaTokenizerFast.from_pretrained("FacebookAI/xlm-roberta-base")
    roberta = XLMRobertaForTokenClassification("path/to/config.json","path/to/model.bin",
    categories=["first_name", "surname", "street"])
    # token classification service
    roberta_service = LMTokenClassifierService(tokenizer,roberta)
    pipe = DoctectionPipe(pipeline_component_list=[ocr_service,roberta_service])
    path = "path/to/some/form"
    df = pipe.analyze(path=path)
    for dp in df:
    ...
    ```
  - Public methods (3):
    - `clear_model(self) -> None`
    - `get_wrapped_model(
        path_config_json: PathLikeOrStr, path_weights: PathLikeOrStr
    ) -> XLMRobertaForTokenClassification`
    - `predict(self, **encodings: Union[list[list[str]], torch.Tensor]) -> list[TokenClassResult]`
  - Private methods (1):
    - `__init__(
        self,
        path_config_json: PathLikeOrStr,
        path_weights: PathLikeOrStr,
        categories_semantics: Optional[Sequence[TypeOrStr]] = None,
        categories_bio: Optional[Sequence[TypeOrStr]] = None,
        categories: Optional[Mapping[int, TypeOrStr]] = None,
        device: Optional[Union[Literal["cpu", "cuda"], torch.device]] = None,
        use_xlm_tokenizer: bool = True,
    )`

**`class HFLmSequenceClassifierBase`**
  - Location: line 374-471
  - Inherits: LMSequenceClassifier, ABC
  - Abstract base class for wrapping Bert-type models for sequence classification into the deepdoctection 
framework.
  - Public methods (6):
    - `clone(self) -> HFLmSequenceClassifierBase`
    - `get_name(path_weights: PathLikeOrStr, architecture: str) -> str`
    - `get_requirements(cls) -> list[Requirement]`
    - `get_tokenizer_class_name(model_class_name: str, use_xlm_tokenizer: bool) -> str`
    - `image_to_features_mapping() -> str`
    - `image_to_raw_features_mapping() -> str`
  - Private methods (2):
    - `__init__(
        self,
        path_config_json: PathLikeOrStr,
        path_weights: PathLikeOrStr,
        categories: Mapping[int, TypeOrStr],
        device: Optional[Union[Literal["cpu", "cuda"], torch.device]] = None,
    )`
    - `_validate_encodings(
        self, **encodings: Union[list[list[str]], torch.Tensor]
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]`

**`class HFLmSequenceClassifier`**
  - Location: line 474-570
  - Inherits: HFLmSequenceClassifierBase
  - A wrapper class for `transformers.XLMRobertaForSequenceClassification` and similar models to use within a 
pipeline
    component. Check <https://huggingface.co/docs/transformers/model_doc/xlm-roberta> for documentation of the
    model itself.
    Note that this model is equipped with a head that is only useful for classifying the input sequence. For 
token
    classification and other things please use another model of the family.
    Example:
    ```python
    # setting up compulsory ocr service
    tesseract_config_path = ModelCatalog.get_full_path_configs("/dd/conf_tesseract.yaml")
    tess = TesseractOcrDetector(tesseract_config_path)
    ocr_service = TextExtractionService(tess)
    # hf tokenizer and token classifier
    tokenizer = XLMRobertaTokenizerFast.from_pretrained("FacebookAI/xlm-roberta-base")
    roberta = HFLmSequenceClassifier("path/to/config.json","path/to/model.bin",
    categories=["handwritten", "presentation", "resume"])
    # token classification service
    roberta_service = LMSequenceClassifierService(tokenizer,roberta)
    pipe = DoctectionPipe(pipeline_component_list=[ocr_service,roberta_service])
    path = "path/to/some/form"
    df = pipe.analyze(path=path)
    for dp in df:
    ...
    ```
  - Public methods (4):
    - `clear_model(self) -> None`
    - `default_kwargs_for_image_to_features_mapping() -> JsonDict`
    - `get_wrapped_model(
        path_config_json: PathLikeOrStr, path_weights: PathLikeOrStr
    ) -> XLMRobertaForSequenceClassification`
    - `predict(self, **encodings: Union[list[list[str]], torch.Tensor]) -> SequenceClassResult`
  - Private methods (1):
    - `__init__(
        self,
        path_config_json: PathLikeOrStr,
        path_weights: PathLikeOrStr,
        categories: Mapping[int, TypeOrStr],
        device: Optional[Union[Literal["cpu", "cuda"], torch.device]] = None,
        use_xlm_tokenizer: bool = True,
    )`

**`class HFLmLanguageDetector`**
  - Location: line 573-684
  - Inherits: LanguageDetector
  - Language detector using HuggingFace's `XLMRobertaForSequenceClassification`.
    This class wraps a multilingual sequence classification model (XLMRobertaForSequenceClassification)
    for language detection tasks. Input text is tokenized and truncated/padded to a maximum length of 512 
tokens.
    The prediction returns a `DetectionResult` containing the detected language code and its confidence score.
  - Public methods (6):
    - `clear_model(self) -> None`
    - `clone(self) -> HFLmLanguageDetector`
    - `get_name(path_weights: PathLikeOrStr, architecture: str) -> str`
    - `get_requirements(cls) -> list[Requirement]`
    - `get_wrapped_model(
        path_config_json: PathLikeOrStr, path_weights: PathLikeOrStr
    ) -> XLMRobertaForSequenceClassification`
    - `predict(self, text_string: str) -> DetectionResult`
  - Private methods (1):
    - `__init__(
        self,
        path_config_json: PathLikeOrStr,
        path_weights: PathLikeOrStr,
        categories: Mapping[int, TypeOrStr],
        device: Optional[Union[Literal["cpu", "cuda"], torch.device]] = None,
        use_xlm_tokenizer: bool = True,
    )`

#### deepdoctection/extern/model.py

**`class ModelProfile`**
  - Location: line 47-75
  - Class for model profile. Add for each model one `ModelProfile` to the `ModelCatalog`
  - Public methods (1):
    - `as_dict(self) -> dict[str, Any]`

**`class ModelCatalog`**
  - Location: line 78-304
  - Catalog of some pre-trained models. The associated config file is available as well.
    To get an overview of all registered models
    Example:
    ```python
    print(ModelCatalog.get_model_list())
    ```
    To get a model card for some specific model:
    Example:
    ```python
    profile = ModelCatalog.get_profile("layout/model-800000_inf_only.data-00000-of-00001")
    print(profile.description)
    ```
    Some models will have their weights and configs stored in the cache. To instantiate predictors one will 
sometimes
    need their path. Use
    Example:
    ```python
    path_weights = ModelCatalog.get_full_path_configs("layout/model-800000_inf_only.data-00000-of-00001")
    path_configs = ModelCatalog.get_full_path_weights("layout/model-800000_inf_only.data-00000-of-00001")
    ```
    To register a new model
    Example:
    ```python
    ModelCatalog.get_full_path_configs("my_new_model")
    ```
    Attributes:
    CATALOG (dict[str, ModelProfile]): A dict of model profiles. The key is the model name and the value is a
    `ModelProfile` object.
  - Public methods (10):
    - `get_full_path_configs(name: PathLikeOrStr) -> PathLikeOrStr`
    - `get_full_path_preprocessor_configs(name: Union[str]) -> PathLikeOrStr`
    - `get_full_path_weights(name: PathLikeOrStr) -> PathLikeOrStr`
    - `get_model_list() -> list[PathLikeOrStr]`
    - `get_profile(name: str) -> ModelProfile`
    - `get_profile_list() -> list[str]`
    - `is_registered(path_weights: PathLikeOrStr) -> bool`
    - `load_profiles_from_file(path: Optional[PathLikeOrStr] = None) -> None`
    - `register(name: str, profile: ModelProfile) -> None`
    - `save_profiles_to_file(target_path: PathLikeOrStr) -> None`

**`class ModelDownloadManager`**
  - Location: line 375-506
  - Class for organizing downloads of config files and weights from various sources. Internally, it will use 
model
    profiles to know where things are stored.
    Example:
    ```python
    # if you are not sure about the model name use the ModelCatalog
    ModelDownloadManager.maybe_download_weights_and_configs("layout/model-800000_inf_only.data-00000-of-00001"
)
    ```
  - Public methods (3):
    - `load_configs_from_hf_hub(profile: ModelProfile, absolute_path: PathLikeOrStr) -> None`
    - `load_model_from_hf_hub(profile: ModelProfile, absolute_path: PathLikeOrStr, file_names: list[str]) -> 
None`
    - `maybe_download_weights_and_configs(name: str) -> PathLikeOrStr`
  - Private methods (2):
    - `_load_from_gd(profile: ModelProfile, absolute_path: PathLikeOrStr, file_names: list[str]) -> None`
    - `_load_from_hf_hub(
        repo_id: str, file_name: str, cache_directory: PathLikeOrStr, force_download: bool = False
    ) -> int`

#### deepdoctection/extern/pdftext.py

**`class PdfPlumberTextDetector`**
  - Location: line 49-134
  - Inherits: PdfMiner
  - Text miner based on the `pdfminer.six` engine. To convert `pdfminers` result, especially group character 
to get word
    level results we use `pdfplumber`.
    Example:
    ```python
    pdf_plumber = PdfPlumberTextDetector()
    df = SerializerPdfDoc.load("path/to/document.pdf")
    df.reset_state()
    for dp in df:
    detection_results = pdf_plumber.predict(dp["pdf_bytes"])
    ```
    To use it in a more integrated way:
    Example:
    ```python
    pdf_plumber = PdfPlumberTextDetector()
    text_extract = TextExtractionService(pdf_plumber)
    pipe = DoctectionPipe([text_extract])
    df = pipe.analyze(path="path/to/document.pdf")
    df.reset_state()
    for dp in df:
    ...
    ```
  - Public methods (4):
    - `get_category_names(self) -> tuple[ObjectTypes, ...]`
    - `get_requirements(cls) -> list[Requirement]`
    - `get_width_height(self, pdf_bytes: bytes) -> tuple[float, float]`
    - `predict(self, pdf_bytes: bytes) -> list[DetectionResult]`
  - Private methods (1):
    - `__init__(self, x_tolerance: int = 3, y_tolerance: int = 3) -> None`

**`class Pdfmium2TextDetector`**
  - Location: line 137-231
  - Inherits: PdfMiner
  - Text miner based on the pypdfium2 engine. It will return text on text line level and not on word level
    Example:
    ```python
    pdfmium2 = Pdfmium2TextDetector()
    df = SerializerPdfDoc.load("path/to/document.pdf")
    df.reset_state()
    for dp in df:
    detection_results = pdfmium2.predict(dp["pdf_bytes"])
    ```
    To use it in a more integrated way:
    Example:
    ```python
    pdfmium2 = Pdfmium2TextDetector()
    text_extract = TextExtractionService(pdfmium2)
    pipe = DoctectionPipe([text_extract])
    df = pipe.analyze(path="path/to/document.pdf")
    df.reset_state()
    for dp in df:
    ...
    ```
  - Public methods (4):
    - `get_category_names(self) -> tuple[ObjectTypes, ...]`
    - `get_requirements(cls) -> list[Requirement]`
    - `get_width_height(self, pdf_bytes: bytes) -> tuple[float, float]`
    - `predict(self, pdf_bytes: bytes) -> list[DetectionResult]`
  - Private methods (1):
    - `__init__(self) -> None`

#### deepdoctection/extern/tessocr.py

**`class TesseractOcrDetector`**
  - Location: line 318-426
  - Inherits: ObjectDetector
  - Text object detector based on Tesseracts OCR engine.
    Note:
    Tesseract has to be installed separately. <https://tesseract-ocr.github.io/>
    All configuration options that are available via pytesseract can be added to the configuration file:
    <https://pypi.org/project/pytesseract/.>
    Example:
    ```python
    tesseract_config_path = ModelCatalog.get_full_path_configs("dd/conf_tesseract.yaml")
    ocr_detector = TesseractOcrDetector(tesseract_config_path)
    detection_result = ocr_detector.predict(bgr_image_as_np_array)
    ```
    To use it within a pipeline
    Example:
    ```python
    tesseract_config_path = ModelCatalog.get_full_path_configs("dd/conf_tesseract.yaml")
    ocr_detector = TesseractOcrDetector(tesseract_config_path)
    text_extract = TextExtractionService(ocr_detector)
    pipe = DoctectionPipe([text_extract])
    df = pipe.analyze(path="path/to/dir")
    for dp in df:
    ...
    ```
  - Public methods (6):
    - `clone(self) -> TesseractOcrDetector`
    - `get_category_names(self) -> tuple[ObjectTypes, ...]`
    - `get_name() -> str`
    - `get_requirements(cls) -> list[Requirement]`
    - `predict(self, np_img: PixelValues) -> list[DetectionResult]`
    - `set_language(self, language: ObjectTypes) -> None`
  - Private methods (1):
    - `__init__(
        self,
        path_yaml: PathLikeOrStr,
        config_overwrite: Optional[list[str]] = None,
    )`

**`class TesseractRotationTransformer`**
  - Location: line 429-507
  - Inherits: ImageTransformer
  - The `TesseractRotationTransformer` is designed to handle image rotations.. It inherits from the 
`ImageTransformer`
    base class and implements methods for predicting and applying rotation transformations.
    The `predict` method determines the angle of the rotated image. It can only handle angles that are 
multiples of 90
    degrees. This method uses the Tesseract OCR engine to predict the rotation angle of an image.
    The `transform` method applies the predicted rotation to the image, effectively rotating the image 
backwards.
    This method uses either the Pillow library or OpenCV for the rotation operation, depending on the 
configuration.
    This class can be particularly useful in OCR tasks where the orientation of the text in the image matters.
    The class also provides methods for cloning itself and for getting the requirements of the Tesseract OCR 
system.
    Example:
    ```python
    transformer = TesseractRotationTransformer()
    detection_result = transformer.predict(np_img)
    rotated_image = transformer.transform(np_img, detection_result)
    ```
  - Public methods (6):
    - `clone(self) -> TesseractRotationTransformer`
    - `get_category_names(self) -> tuple[ObjectTypes, ...]`
    - `get_requirements(cls) -> list[Requirement]`
    - `predict(self, np_img: PixelValues) -> DetectionResult`
    - `transform_coords(self, detect_results: Sequence[DetectionResult]) -> Sequence[DetectionResult]`
    - `transform_image(self, np_img: PixelValues, specification: DetectionResult) -> PixelValues`
  - Private methods (1):
    - `__init__(self) -> None`

#### deepdoctection/extern/texocr.py

**`class TextractOcrDetector`**
  - Location: line 98-167
  - Inherits: ObjectDetector
  - Text object detector based on AWS Textract OCR engine. Note that an AWS account as well as some additional
    installations are required, i.e `AWS CLI` and `boto3`.
    Note:
    The service is not free of charge. Additional information can be found at:
    <https://docs.aws.amazon.com/textract/?id=docs_gateway> .
    The detector only calls the base `OCR` engine and does not return additional Textract document analysis 
features.
    Example:
    ```python
    textract_predictor = TextractOcrDetector()
    detection_result = textract_predictor.predict(bgr_image_as_np_array)
    ```
    or
    ```python
    textract_predictor = TextractOcrDetector()
    text_extract = TextExtractionService(textract_predictor)
    pipe = DoctectionPipe([text_extract])
    df = pipe.analyze(path="path/to/document.pdf")
    for dp in df:
    ...
    ```
  - Public methods (4):
    - `clone(self) -> TextractOcrDetector`
    - `get_category_names(self) -> tuple[ObjectTypes, ...]`
    - `get_requirements(cls) -> list[Requirement]`
    - `predict(self, np_img: PixelValues) -> list[DetectionResult]`
  - Private methods (1):
    - `__init__(self, text_lines: bool = False, **credentials_kwargs: str) -> None`

#### deepdoctection/extern/tp/tpcompat.py

**`class ModelDescWithConfig`**
  - Location: line 47-76
  - Inherits: ModelDesc, ABC
  - A wrapper for `Tensorpack ModelDesc` for bridging the gap between Tensorpack and DD API.
    Only for storing a configuration of hyperparameters and maybe training settings.
  - Public methods (1):
    - `get_inference_tensor_names(self) -> tuple[list[str], list[str]]`
  - Private methods (1):
    - `__init__(self, config: AttrDict) -> None`

**`class TensorpackPredictor`**
  - Location: line 79-176
  - Inherits: ABC
  - The base class for wrapping a Tensorpack predictor. It takes a ModelDescWithConfig from Tensorpack and 
weights and
    builds a Tensorpack offline predictor (e.g. a default session will be generated when initializing).
    Two abstract methods need to be implemented:
    - `set_model` generates a ModelDescWithConfig from the input .yaml file and possible manual adaptions of
    the configuration.
    - `predict` the interface of this class for calling the OfflinePredictor and returning the results. This
    method will be used throughout in the context of pipeline components. If there are some pre- or
    post-processing steps, you can place them here. However, do not convert the returned results into DD 
objects
    as there is an explicit class available for this.
  - Public methods (4):
    - `get_predictor(self) -> OfflinePredictor`
    - `get_wrapped_model(
        path_yaml: PathLikeOrStr, categories: Mapping[int, ObjectTypes], config_overwrite: Union[list[str], 
None]
    ) -> ModelDescWithConfig`
    - `model(self) -> ModelDescWithConfig`
    - `predict(self, np_img: PixelValues) -> Any`
  - Private methods (2):
    - `__init__(self, model: ModelDescWithConfig, path_weights: PathLikeOrStr, ignore_mismatch: bool) -> None`
    - `_build_config(self) -> PredictConfig`

#### deepdoctection/extern/tp/tpfrcnn/common.py

**`class CustomResize`**
  - Location: line 26-61
  - Inherits: ImageAugmentor
  - Try resizing the shortest edge to a certain number while avoiding the longest edge to exceed max_size.
  - Public methods (1):
    - `get_transform(self, img)`
  - Private methods (1):
    - `__init__(self, short_edge_length, max_size, interp=1)`

#### deepdoctection/extern/tp/tpfrcnn/modeling/generalized_rcnn.py

**`class GeneralizedRCNN`**
  - Location: line 50-133
  - Inherits: ModelDescWithConfig
  - GeneralizedRCNN
  - Public methods (4):
    - `build_graph(self, *inputs)`
    - `get_inference_tensor_names(self)`
    - `optimizer(self)`
    - `preprocess(self, image)`

**`class ResNetFPNModel`**
  - Location: line 136-362
  - Inherits: GeneralizedRCNN
  - FPN and Cascade-RCNN with resnet/resnext backbone options
  - Public methods (5):
    - `backbone(self, image)`
    - `inputs(self)`
    - `roi_heads(self, image, features, proposals, targets)`
    - `rpn(self, image, features, inputs)`
    - `slice_feature_and_anchors(self, p23456, anchors)`

#### deepdoctection/extern/tp/tpfrcnn/modeling/model_box.py

**`class RPNAnchors`**
  - Location: line 188-221
  - boxes (FS x FS x NA x 4): The anchor boxes.
    gt_labels (FS x FS x NA):
    gt_boxes (FS x FS x NA x 4): Ground-truth boxes corresponding to each anchor.
  - Public methods (3):
    - `decode_logits(self, logits, preproc_max_size)`
    - `encoded_gt_boxes(self)`
    - `narrow_to(self, featuremap)`

#### deepdoctection/extern/tp/tpfrcnn/modeling/model_cascade.py

**`class CascadeRCNNHead`**
  - Location: line 28-153
  - Cascade RCNN Head
  - Public methods (5):
    - `decoded_output_boxes(self)`
    - `losses(self)`
    - `match_box_with_gt(self, boxes, iou_threshold)`
    - `output_scores(self, name=None)`
    - `run_head(self, proposals, stage)`
  - Private methods (1):
    - `__init__(
        self, proposals, roi_func, fastrcnn_head_func, gt_targets, image_shape2d, num_categories, cfg
    )`

#### deepdoctection/extern/tp/tpfrcnn/modeling/model_frcnn.py

**`class BoxProposals`**
  - Location: line 334-371
  - A structure to manage box proposals and their relations with ground truth.
  - Public methods (3):
    - `fg_boxes(self)`
    - `fg_inds(self)`
    - `fg_labels(self)`
  - Private methods (1):
    - `__init__(self, boxes, labels=None, fg_inds_wrt_gt=None)`

**`class FastRCNNHead`**
  - Location: line 374-491
  - A class to process & decode inputs/outputs of a fastrcnn classification+regression head.
  - Public methods (9):
    - `decoded_output_boxes(self)`
    - `decoded_output_boxes_class_agnostic(self)`
    - `decoded_output_boxes_for_label(self, labels)`
    - `decoded_output_boxes_for_predicted_label(self)`
    - `decoded_output_boxes_for_true_label(self)`
    - `fg_box_logits(self)`
    - `losses(self)`
    - `output_scores(self, name=None)`
    - `predicted_labels(self)`
  - Private methods (1):
    - `__init__(
        self, proposals, box_logits, label_logits, gt_boxes, bbox_regression_weights, cfg
    )`

#### deepdoctection/extern/tpdetect.py

**`class TPFrcnnDetectorMixin`**
  - Location: line 38-70
  - Inherits: ObjectDetector, ABC
  - Base class for TP FRCNN detector. This class only implements the basic wrapper functions
  - Public methods (2):
    - `get_category_names(self) -> tuple[ObjectTypes, ...]`
    - `get_name(path_weights: PathLikeOrStr, architecture: str) -> str`
  - Private methods (2):
    - `__init__(self, categories: Mapping[int, TypeOrStr], filter_categories: Optional[Sequence[TypeOrStr]] = 
None)`
    - `_map_category_names(self, detection_results: list[DetectionResult]) -> list[DetectionResult]`

**`class TPFrcnnDetector`**
  - Location: line 73-191
  - Inherits: TensorpackPredictor, TPFrcnnDetectorMixin
  - Tensorpack Faster-RCNN implementation with FPN and optional Cascade-RCNN. The backbones Resnet-50, 
Resnet-101 and
    their Resnext counterparts are also available. Normalization options (group normalization, synchronized 
batch
    normalization) for backbone in FPN can be chosen as well.
    Currently, masks are not included in the data model. However, Mask-RCNN is implemented in this version.
    There are hardly any adjustments to the original implementation of Tensorpack. As post-processing, another
round
    of NMS can be carried out for the output, which operates on a class-agnostic basis. For a discussion, see
    <https://github.com/facebookresearch/detectron2/issues/978> .
    config_path = ModelCatalog.get_full_path_configs("dd/tp/conf_frcnn_rows.yaml")
    weights_path = 
ModelDownloadManager.maybe_download_weights_and_configs("item/model-162000.data-00000-of-00001")
    categories = ModelCatalog.get_profile("item/model-162000.data-00000-of-00001").categories
    tp_predictor = TPFrcnnDetector("tp_frcnn", config_path,weights_path,categories)  # first argument is only 
a name
    detection_results = tp_predictor.predict(bgr_image_np_array)
  - Public methods (5):
    - `clear_model(self) -> None`
    - `clone(self) -> TPFrcnnDetector`
    - `get_requirements(cls) -> list[Requirement]`
    - `get_wrapped_model(
        path_yaml: PathLikeOrStr, categories: Mapping[int, TypeOrStr], config_overwrite: Union[list[str], 
None]
    ) -> ResNetFPNModel`
    - `predict(self, np_img: PixelValues) -> list[DetectionResult]`
  - Private methods (1):
    - `__init__(
        self,
        path_yaml: PathLikeOrStr,
        path_weights: PathLikeOrStr,
        categories: Mapping[int, TypeOrStr],
        config_overwrite: Optional[list[str]] = None,
        ignore_mismatch: bool = False,
        filter_categories: Optional[Sequence[TypeOrStr]] = None,
    )`

#### deepdoctection/mapper/hfstruct.py

**`class DetrDataCollator`**
  - Location: line 103-166
  - Data collator that will prepare a list of raw features to a `BatchFeature` that can be used to train a 
Detr or
    Tabletransformer model.
    Args:
    feature_extractor: `DetrFeatureExtractor`
    padder: An optional `PadTransform` instance.
    return_tensors: "pt" or None.
  - Public methods (1):
    - `maybe_pad_image_and_transform(self, feature: JsonDict) -> JsonDict`
  - Private methods (1):
    - `__call__(self, raw_features: list[JsonDict]) -> BatchFeature`

#### deepdoctection/mapper/laylmstruct.py

**`class LayoutLMDataCollator`**
  - Location: line 594-662
  - Data collator that will dynamically tokenize, pad, and truncate the inputs received.
    Args:
    tokenizer: A fast tokenizer for the model. The conventional Python-based tokenizer provided by the
    Transformers library does not return essential word_id/token_id mappings, making feature generation
    more difficult. Only fast tokenizers are allowed.
    padding: Padding strategy to be passed to the tokenizer. Must be either `max_length`, `longest`, or
    `do_not_pad`.
    truncation: If `True`, truncates to a maximum length specified with the argument `max_length` or to the
    maximum acceptable input length for the model if that argument is not provided. Truncates token by token,
    removing a token from the longest sequence in the pair if a pair of sequences (or a batch of pairs) is
    provided.
    If `False`, no truncation (i.e., can output batch with sequence lengths greater than the model maximum
    admissible input size).
    return_overflowing_tokens: If a sequence (due to a truncation strategy) overflows, the overflowing tokens 
can
    be returned as an additional batch element. In this case, the number of input batch samples will be 
smaller
    than the output batch samples.
    return_tensors: If `pt`, returns torch tensors. If not provided, batches will be lists of lists.
    sliding_window_stride: If the output of the tokenizer exceeds the `max_length` sequence length, sliding 
windows
    will be created with each window having `max_length` sequence input. When using
    `sliding_window_stride=0`, no strides will be created; otherwise, it will create slides with windows
    shifted `sliding_window_stride` to the right.
    max_batch_size: Maximum batch size.
    remove_bounding_box_features: If `True`, removes bounding box features.
  - Private methods (2):
    - `__call__(self, raw_features: Union[RawLayoutLMFeatures, list[RawLayoutLMFeatures]]) -> 
LayoutLMFeatures`
    - `__post_init__(self) -> None`

#### deepdoctection/mapper/maputils.py

**`class MappingContextManager`**
  - Location: line 41-126
  - A context for logging and catching some exceptions. Useful in a mapping function. It will remember outside
the
    context if an exception has been thrown.
  - Private methods (3):
    - `__enter__(self) -> MappingContextManager`
    - `__exit__(
        self,
        exc_type: Optional[BaseExceptionType],
        exc_val: Optional[BaseExceptionType],
        exc_tb: Optional[TracebackType],
    ) -> Optional[bool]`
    - `__init__(
        self, dp_name: Optional[str] = None, filter_level: str = "image", **kwargs: dict[str, Optional[str]]
    ) -> None`

**`class DefaultMapper`**
  - Location: line 129-158
  - A class that wraps a function and places some pre-defined values starting from the second argument  once 
the
    function is invoked.
    <https://stackoverflow.com/questions/36314/what-is-currying>
  - Private methods (2):
    - `__call__(self, dp: Any) -> Any`
    - `__init__(self, func: Callable[[DP, S], T], *args: Any, **kwargs: Any) -> None`

**`class LabelSummarizer`**
  - Location: line 210-274
  - A class for generating label statistics. Useful when mapping and generating a `SummaryAnnotation`.
    Example:
    ```python
    summarizer = LabelSummarizer({"1": "label_1", "2": "label_2"})
    for dp in some_dataflow:
    summarizer.dump(dp["label_id"])
    summarizer.print_summary_histogram()
    ```
    Args:
    categories: A dict of categories as given as in `categories.get_categories()`.
  - Public methods (3):
    - `dump(self, item: Union[Sequence[Union[str, int]], str, int]) -> None`
    - `get_summary(self) -> dict[int, int]`
    - `print_summary_histogram(self, dd_logic: bool = True) -> None`
  - Private methods (1):
    - `__init__(self, categories: Mapping[int, ObjectTypes]) -> None`

#### deepdoctection/pipe/anngen.py

**`class DatapointManager`**
  - Location: line 34-408
  - This class provides an API for manipulating image datapoints. This includes the creation and storage of
    annotations in the cache of the image as well as in the annotations themselves.
    When the image is transferred, the annotations are stored in a cache dictionary so that access via the 
annotation ID
    can be performed efficiently.
    The manager is part of each `PipelineComponent`.
  - Public methods (11):
    - `assert_datapoint_passed(self) -> None`
    - `datapoint(self) -> Image`
    - `datapoint(self, dp: Image) -> None`
    - `deactivate_annotation(self, annotation_id: str) -> None`
    - `get_annotation(self, annotation_id: str) -> ImageAnnotation`
    - `remove_annotations(self, annotation_ids: Sequence[str]) -> None`
    - `set_category_annotation(
        self,
        category_name: ObjectTypes,
        category_id: Optional[int],
        sub_cat_key: ObjectTypes,
        annotation_id: str,
        score: Optional[float] = None,
    ) -> Optional[str]`
    - `set_container_annotation(
        self,
        category_name: ObjectTypes,
        category_id: Optional[int],
        sub_cat_key: ObjectTypes,
        annotation_id: str,
        value: Union[str, list[str]],
        score: Optional[float] = None,
    ) -> Optional[str]`
    - `set_image_annotation(
        self,
        detect_result: DetectionResult,
        to_annotation_id: Optional[str] = None,
        to_image: bool = False,
        crop_image: bool = False,
        detect_result_max_width: Optional[float] = None,
        detect_result_max_height: Optional[float] = None,
    ) -> Optional[str]`
    - `set_relationship_annotation(
        self, relationship_name: ObjectTypes, target_annotation_id: str, annotation_id: str
    ) -> Optional[str]`
    - `set_summary_annotation(
        self,
        summary_key: ObjectTypes,
        summary_name: ObjectTypes,
        summary_number: Optional[int] = None,
        summary_value: Optional[str] = None,
        summary_score: Optional[float] = None,
        annotation_id: Optional[str] = None,
    ) -> Optional[str]`
  - Private methods (1):
    - `__init__(self, service_id: str, model_id: Optional[str] = None) -> None`

#### deepdoctection/pipe/base.py

**`class PipelineComponent`**
  - Location: line 39-253
  - Inherits: ABC
  - Base class for pipeline components.
    Pipeline components are the parts that make up a pipeline. They contain the
    abstract `serve`, in which the component steps are defined. Within pipelines,
    pipeline components take an image, enrich these with annotations or transform
    existing annotation and transfer the image again. The pipeline component should
    be implemented in such a way that the pythonic approach of passing arguments via
    assignment is used well. To support the pipeline component, an intrinsic
    datapoint manager is provided, which can perform operations on the image
    datapoint that are common for pipeline components. This includes the creation of
    an image, sub-category and similar annotations.
    Pipeline components do not necessarily have to contain predictors but can also
    contain rule-based transformation steps. (For pipeline components with
    predictors see `PredictorPipelineComponent`.)
    The sequential execution of pipeline components is carried out with dataflows.
    In the case of components with predictors, this allows the predictor graph to be
    set up first and then to be streamed to the processed data points.
    Note:
    Currently, predictors can only process single images. Processing higher number of batches is not planned.
  - Public methods (10):
    - `clear_predictor(self) -> None`
    - `clone(self) -> PipelineComponent`
    - `get_meta_annotation(self) -> MetaAnnotation`
    - `get_service_id(self) -> str`
    - `has_predictor(self) -> bool`
    - `pass_datapoint(self, dp: Image) -> Image`
    - `predict_dataflow(self, df: DataFlow) -> DataFlow`
    - `serve(self, dp: Image) -> None`
    - `set_inbound_filter(self, filter_func: Callable[[DP], bool]) -> None`
    - `undo(self, df: DataFlow) -> DataFlow`
  - Private methods (3):
    - `__init__(self, name: str, model_id: Optional[str] = None) -> None`
    - `_pass_datapoint(self, dp: Image) -> None`
    - `_undo(self, dp: Image) -> Image`

**`class Pipeline`**
  - Location: line 256-500
  - Inherits: ABC
  - Abstract base class for creating pipelines.
    Pipelines represent the framework with which documents can be processed by reading individual pages, 
processing the
    pages through the pipeline infrastructure and returning the extracted information.
    The infrastructure, as the backbone of the pipeline, consists of a list of pipeline components in which 
images can
    be passed through via dataflows. The order of the pipeline components in the list determines the 
processing order.
    The components for the pipeline backbone are composed in `_build_pipe`.
    The pipeline is set up via: `analyze` for a directory with single pages or a document with multiple pages.
A data
    flow is returned that is triggered via a for loop and starts the actual processing.
    This creates a pipeline using the following command arrangement:
    Example:
    ```python
    layout = LayoutPipeComponent(layout_detector ...)
    text = TextExtractPipeComponent(text_detector ...)
    simple_pipe = MyPipeline(pipeline_component = [layout, text])
    doc_dataflow = simple_pipe.analyze(input = path / to / dir)
    for page in doc_dataflow:
    print(page)
    ```
    In doing so, `page` contains all document structures determined via the pipeline (either directly from the
`Image`
    core model or already processed further).
    In addition to `analyze`, the internal `_entry` is used to bundle preprocessing steps.
    It is possible to set a session id for the pipeline. This is useful for logging purposes. The session id 
can be
    either passed to the pipeline via the `analyze` method or generated automatically.
    To generate a `session_id` automatically:
    Example:
    ```python
    pipe = MyPipeline(pipeline_component = [layout, text])
    pipe.set_session_id = True
    df = pipe.analyze(input = "path/to/dir") # session_id is generated automatically
    ```
  - Public methods (7):
    - `analyze(self, **kwargs: Any) -> DataFlow`
    - `get_meta_annotation(self) -> MetaAnnotation`
    - `get_pipeline_component(self, service_id: Optional[str] = None, name: Optional[str] = None) -> 
PipelineComponent`
    - `get_pipeline_info(
        self, service_id: Optional[str] = None, name: Optional[str] = None
    ) -> Union[str, Mapping[str, str]]`
    - `get_service_id_to_meta_annotation(self) -> Mapping[str, MetaAnnotation]`
    - `get_session_id() -> str`
    - `undo(self, df: DataFlow, service_ids: Optional[set[str]] = None) -> DataFlow`
  - Private methods (4):
    - `__init__(self, pipeline_component_list: list[PipelineComponent]) -> None`
    - `_build_pipe(self, df: DataFlow, session_id: Optional[str] = None) -> DataFlow`
    - `_entry(self, **kwargs: Any) -> DataFlow`
    - `_undo(dp: Image, service_ids: Optional[list[str]] = None) -> Image`

#### deepdoctection/pipe/common.py

**`class ImageCroppingService`**
  - Location: line 47-88
  - Inherits: PipelineComponent
  - Crop sub images given by bounding boxes of some annotations.
    This service is not necessary for `ImageLayoutService` and is more intended for saved files where sub 
images are
    generally not stored.
  - Public methods (4):
    - `clear_predictor(self) -> None`
    - `clone(self) -> ImageCroppingService`
    - `get_meta_annotation(self) -> MetaAnnotation`
    - `serve(self, dp: Image) -> None`
  - Private methods (1):
    - `__init__(
        self,
        category_names: Optional[Union[TypeOrStr, Sequence[TypeOrStr]]] = None,
        service_ids: Optional[Sequence[str]] = None,
    ) -> None`

**`class IntersectionMatcher`**
  - Location: line 91-183
  - Objects of two object classes can be assigned to one another by determining their pairwise intersection.
    If this is above a limit, a relation is created between them.
    The parent object class (based on its category) and the child object class are defined for the service.
    Either `iou` (intersection-over-union) or `ioa` (intersection-over-area) can be selected as the matching 
rule.
    Example:
    ```python
    matcher = IntersectionMatcher(matching_rule="ioa", threshold=0.7)
    match_service = MatchingService(parent_categories=["text","title"],
    child_categories="word",
    matcher=matcher,
    relationship_key=Relationships.CHILD)
    ```
    Assigning means that text and title annotation will receive a relationship called `CHILD` which is a list
    of annotation ids of mapped words.
  - Public methods (1):
    - `match(
        self,
        dp: Image,
        parent_categories: Optional[Union[TypeOrStr, Sequence[TypeOrStr]]] = None,
        child_categories: Optional[Union[TypeOrStr, Sequence[TypeOrStr]]] = None,
        parent_ann_service_ids: Optional[Union[str, Sequence[str]]] = None,
        child_ann_service_ids: Optional[Union[str, Sequence[str]]] = None,
    ) -> list[tuple[str, str]]`
  - Private methods (1):
    - `__init__(
        self,
        matching_rule: Literal["iou", "ioa"],
        threshold: float,
        use_weighted_intersections: bool = False,
        max_parent_only: bool = False,
    ) -> None`

**`class NeighbourMatcher`**
  - Location: line 186-233
  - Objects of two object classes can be assigned to one another by determining their pairwise distance.
    Example:
    ```python
    matcher = NeighbourMatcher()
    match_service = MatchingService(parent_categories=["figure"],
    child_categories="caption",
    matcher=matcher,
    relationship_key=Relationships.LAYOUT_LINK)
    ```
  - Public methods (1):
    - `match(
        self,
        dp: Image,
        parent_categories: Optional[Union[TypeOrStr, Sequence[TypeOrStr]]] = None,
        child_categories: Optional[Union[TypeOrStr, Sequence[TypeOrStr]]] = None,
        parent_ann_service_ids: Optional[Union[str, Sequence[str]]] = None,
        child_ann_service_ids: Optional[Union[str, Sequence[str]]] = None,
    ) -> list[tuple[str, str]]`

**`class FamilyCompound`**
  - Location: line 237-272
  - A family compound is a set of parent and child categories that are related by a relationship key.
    The parent categories will receive a relationship to the child categories.
    Attributes:
    relationship_key: The relationship key.
    parent_categories: Parent categories.
    child_categories: Child categories.
    parent_ann_service_ids: Parent annotation service IDs.
    child_ann_service_ids: Child annotation service IDs.
    create_synthetic_parent: Whether to create a synthetic parent.
    synthetic_parent: The synthetic parent.
  - Private methods (1):
    - `__post_init__(self) -> None`

**`class MatchingService`**
  - Location: line 276-362
  - Inherits: PipelineComponent
  - A service to match annotations of two categories by intersection or distance.
    The matched annotations will be assigned a relationship. The parent category will receive a
    relationship to the child category.
  - Public methods (4):
    - `clear_predictor(self) -> None`
    - `clone(self) -> PipelineComponent`
    - `get_meta_annotation(self) -> MetaAnnotation`
    - `serve(self, dp: Image) -> None`
  - Private methods (1):
    - `__init__(
        self,
        family_compounds: Sequence[FamilyCompound],
        matcher: Union[IntersectionMatcher, NeighbourMatcher],
    ) -> None`

**`class PageParsingService`**
  - Location: line 366-459
  - Inherits: PipelineComponent
  - A "pseudo" pipeline component that can be added to a pipeline to convert `Image`s into `Page` formats.
    It allows a custom parsing depending on customizing options of other pipeline components.
    Info:
    This component is not meant to be used in the `serve` method.
  - Public methods (5):
    - `clear_predictor(self) -> None`
    - `clone(self) -> PageParsingService`
    - `get_meta_annotation(self) -> MetaAnnotation`
    - `pass_datapoint(self, dp: Image) -> Page`
    - `serve(self, dp: Image) -> None`
  - Private methods (2):
    - `__init__(
        self,
        text_container: TypeOrStr,
        floating_text_block_categories: Optional[Union[TypeOrStr, Sequence[TypeOrStr]]] = None,
        residual_text_block_categories: Optional[Union[TypeOrStr, Sequence[TypeOrStr]]] = None,
        include_residual_text_container: bool = True,
    )`
    - `_init_sanity_checks(self) -> None`

**`class AnnotationNmsService`**
  - Location: line 463-542
  - Inherits: PipelineComponent
  - A service to pass `ImageAnnotation` to a non-maximum suppression (NMS) process for given pairs of 
categories.
    `ImageAnnotation`s are subjected to NMS process in groups:
    If `nms_pairs=[[LayoutType.text, LayoutType.table],[LayoutType.title, LayoutType.table]]` all 
`ImageAnnotation`
    subject to these categories are being selected and identified as one category.
    After NMS the discarded image annotation will be deactivated.
    Example:
    ```python
    AnnotationNmsService(nms_pairs=[[LayoutType.text, LayoutType.table],[LayoutType.title, LayoutType.table]],
    thresholds=[0.7,0.7])
    ```
    For each pair a threshold has to be provided.
    For a pair of categories, one can also select a category which has always priority even if the score is 
lower.
    This is useful if one expects some categories to be larger and want to keep them.
  - Public methods (4):
    - `clear_predictor(self) -> None`
    - `clone(self) -> PipelineComponent`
    - `get_meta_annotation(self) -> MetaAnnotation`
    - `serve(self, dp: Image) -> None`
  - Private methods (1):
    - `__init__(
        self,
        nms_pairs: Sequence[Sequence[TypeOrStr]],
        thresholds: Union[float, Sequence[float]],
        priority: Optional[Sequence[Union[Optional[TypeOrStr]]]] = None,
    )`

**`class ImageParsingService`**
  - Location: line 546-598
  - A super light service that calls `to_image` when processing datapoints.
    Might be useful if you build a pipeline that is not derived from `DoctectionPipe`.
  - Public methods (5):
    - `clear_predictor(self) -> None`
    - `clone(self) -> ImageParsingService`
    - `get_meta_annotation() -> MetaAnnotation`
    - `pass_datapoint(self, dp: Union[str, Mapping[str, Union[str, bytes]]]) -> Optional[Image]`
    - `predict_dataflow(self, df: DataFlow) -> DataFlow`
  - Private methods (1):
    - `__init__(self, dpi: Optional[int] = None)`

#### deepdoctection/pipe/concurrency.py

**`class MultiThreadPipelineComponent`**
  - Location: line 42-260
  - Inherits: PipelineComponent
  - This module provides functionality for running pipeline components in multiple threads to increase 
throughput.
    Datapoints are queued and processed once calling the `start` method.
    Note:
    The number of threads is derived from the list of `pipeline_components`. It makes no sense to create 
various
    components.
    Think of the pipeline component as an asynchronous process. Because the entire data flow is loaded into 
memory
    before the process is started, storage capacity must be guaranteed.
    If pre- and post-processing are to be carried out before the task within the wrapped pipeline component, 
this
    can also be transferred as a function. These tasks are also assigned to the threads.
    The order in the dataflow and when returning lists is generally no longer retained.
    Example:
    ```python
    some_component = SubImageLayoutService(some_predictor, some_category)
    some_component_clone = some_component.clone()
    multi_thread_comp = MultiThreadPipelineComponent(
    pipeline_components=[some_component, some_component_clone],
    pre_proc_func=maybe_load_image,
    post_proc_func=maybe_remove_image
    )
    multi_thread_comp.put_task(some_dataflow)
    output_list = multi_thread_comp.start()
    ```
    Info:
    You cannot run `MultiThreadPipelineComponent` in `DoctectionPipe` as this requires batching datapoints and
    neither can you run `MultiThreadPipelineComponent` in combination with a humble `PipelineComponent` unless
you
    take care of batching/unbatching between each component by yourself. The easiest way to build a pipeline 
with
    `MultiThreadPipelineComponent` can be accomplished as follows:
    Example:
    ```python
    # define the pipeline component
    some_component = SubImageLayoutService(some_predictor, some_category)
    some_component_clone = some_component.clone()
    # creating two threads, one for each component
    multi_thread_comp = MultiThreadPipelineComponent(
    pipeline_components=[some_component, some_component_clone],
    pre_proc_func=maybe_load_image,
    post_proc_func=maybe_remove_image
    )
    # currying `to_image`, so that you can call it in `MapData`.
    @curry
    def _to_image(dp, dpi):
    return to_image(dp, dpi)
    # set-up the dataflow/stream, e.g.
    df = SerializerPdfDoc.load(path, max_datapoints=max_datapoints)
    df = MapData(df, to_image(dpi=300))
    df = BatchData(df, batch_size=32, remainder=True)
    df = multi_thread_comp.predict_dataflow(df)
    df = FlattenData(df)
    df = MapData(df, lambda x: x[0])
    df.reset_state()
    for dp in df:
    ...
    ```
  - Public methods (8):
    - `clear_predictor(self) -> None`
    - `clone(self) -> MultiThreadPipelineComponent`
    - `get_meta_annotation(self) -> MetaAnnotation`
    - `pass_datapoints(self, dpts: list[Image]) -> list[Image]`
    - `predict_dataflow(self, df: DataFlow) -> DataFlow`
    - `put_task(self, df: Union[DataFlow, list[Image]]) -> None`
    - `serve(self, dp: Image) -> None`
    - `start(self) -> list[Image]`
  - Private methods (3):
    - `__init__(
        self,
        pipeline_components: Sequence[Union[PipelineComponent, ImageParsingService]],
        pre_proc_func: Optional[Callable[[Image], Image]] = None,
        post_proc_func: Optional[Callable[[Image], Image]] = None,
        max_datapoints: Optional[int] = None,
    ) -> None`
    - `_put_datapoints_to_queue(self, df: Union[DataFlow, list[Image]]) -> None`
    - `_thread_predict_on_queue(
        input_queue: QueueType,
        component: Union[PipelineComponent, PageParsingService, ImageParsingService],
        tqdm_bar: Optional[TqdmType] = None,
        pre_proc_func: Optional[Callable[[Image], Image]] = None,
        post_proc_func: Optional[Callable[[Image], Image]] = None,
    ) -> list[Image]`

#### deepdoctection/pipe/doctectionpipe.py

**`class DoctectionPipe`**
  - Location: line 170-381
  - Inherits: Pipeline
  - Prototype for a document layout pipeline.
    Contains implementation for loading document types (images in directory, single PDF document, dataflow 
from
    datasets), conversions in dataflows, and building a pipeline.
    See `deepdoctection.analyzer.dd` for a concrete implementation.
    See also the explanations in `base.Pipeline`.
    By default, `DoctectionPipe` will instantiate a default `PageParsingService`:
    Example:
    ```python
    pipe = DoctectionPipe([comp_1, com_2], PageParsingService(text_container= my_custom_setting))
    ```
    Note:
    You can overwrite the current setting by providing a custom `PageParsingService`.
  - Public methods (5):
    - `analyze(
        self, **kwargs: Union[str, bytes, DataFlow, bool, int, PathLikeOrStr, Union[str, List[str]]]
    ) -> DataFlow`
    - `bytes_to_dataflow(
        path: str, b_bytes: bytes, file_type: Union[str, Sequence[str]], max_datapoints: Optional[int] = None
    ) -> DataFlow`
    - `dataflow_to_page(self, df: DataFlow) -> DataFlow`
    - `doc_to_dataflow(path: PathLikeOrStr, max_datapoints: Optional[int] = None) -> DataFlow`
    - `path_to_dataflow(
        path: PathLikeOrStr,
        file_type: Union[str, Sequence[str]],
        max_datapoints: Optional[int] = None,
        shuffle: bool = False,
    ) -> DataFlow`
  - Private methods (2):
    - `__init__(
        self,
        pipeline_component_list: List[PipelineComponent],
        page_parsing_service: Optional[PageParsingService] = None,
    )`
    - `_entry(
        self, **kwargs: Union[str, bytes, DataFlow, bool, int, PathLikeOrStr, Union[str, List[str]]]
    ) -> DataFlow`

#### deepdoctection/pipe/language.py

**`class LanguageDetectionService`**
  - Location: line 33-134
  - Inherits: PipelineComponent
  - Pipeline Component for identifying the language in an image.
    There are two ways to use this component:
    1. By analyzing the already extracted and ordered text. For this purpose, a `Page` object is parsed 
internally and
    the full text is passed to the `language_detector`. This approach provides the greatest precision.
    2. By previous text extraction with an object detector and subsequent transfer of concatenated word 
elements to the
    `language_detector`. Only one OCR detector can be used here. This method can be used, for example, to 
select an OCR
    detector that specializes in a language. Although the word recognition is less accurate
    when choosing any detector, the results are confident enough to rely on, especially when extracting
    longer text passages. So, a `TextExtractionService`, for example, can be selected as the subsequent 
pipeline
    component. The words determined by the OCR detector are not transferred to the image object.
    Example:
    ```python
    lang_detector = FasttextLangDetector(path_weights, profile.categories)
    component = LanguageDetectionService(lang_detector, text_container="word",
    text_block_names=["text", "title", "table"])
    ```
  - Public methods (4):
    - `clear_predictor(self) -> None`
    - `clone(self) -> PipelineComponent`
    - `get_meta_annotation(self) -> MetaAnnotation`
    - `serve(self, dp: Image) -> None`
  - Private methods (2):
    - `__init__(
        self,
        language_detector: LanguageDetector,
        text_container: Optional[TypeOrStr] = None,
        text_detector: Optional[ObjectDetector] = None,
        floating_text_block_categories: Optional[Sequence[TypeOrStr]] = None,
    )`
    - `_get_name(predictor_name: str) -> str`

#### deepdoctection/pipe/layout.py

**`class ImageLayoutService`**
  - Location: line 68-163
  - Inherits: PipelineComponent
  - Pipeline component for determining the layout.
    Which layout blocks are determined depends on the `Detector` and thus usually on the data set on which the
    `Detector` was pre-trained. If the `Detector` has been trained on Publaynet, these are layouts such as 
text, title
    , table, list and figure. If the `Detector` has been trained on DocBank, these are rather Abstract, 
Author,
    Caption, Equation, Figure, Footer, List, Paragraph, Reference, Section, Table, Title.
    The component is usually at the beginning of the pipeline. Cropping of the layout blocks can be selected 
to
    simplify further processing.
    Example:
    ```python
    d_items = TPFrcnnDetector(item_config_path, item_weights_path, {1: 'row', 2: 'column'})
    item_component = ImageLayoutService(d_items)
    ```
  - Public methods (4):
    - `clear_predictor(self) -> None`
    - `clone(self) -> ImageLayoutService`
    - `get_meta_annotation(self) -> MetaAnnotation`
    - `serve(self, dp: Image) -> None`
  - Private methods (2):
    - `__init__(
        self,
        layout_detector: ObjectDetector,
        to_image: bool = False,
        crop_image: bool = False,
        padder: Optional[PadTransform] = None,
    )`
    - `_get_name(predictor_name: str) -> str`

#### deepdoctection/pipe/lm.py

**`class LMTokenClassifierService`**
  - Location: line 40-287
  - Inherits: PipelineComponent
  - Module for token classification pipeline.
    This module provides pipeline components for token and sequence classification using language models.
    Example:
    ```python
    # setting up compulsory ocr service
    tesseract_config_path = ModelCatalog.get_full_path_configs("/dd/conf_tesseract.yaml")
    tess = TesseractOcrDetector(tesseract_config_path)
    ocr_service = TextExtractionService(tess)
    # hf tokenizer and token classifier
    tokenizer = LayoutLMTokenizerFast.from_pretrained("microsoft/layoutlm-base-uncased")
    layoutlm = HFLayoutLmTokenClassifier(categories= ['B-answer', 'B-header', 'B-question', 'E-answer',
    'E-header', 'E-question', 'I-answer', 'I-header',
    'I-question', 'O', 'S-answer', 'S-header', 'S-question'])
    # token classification service
    layoutlm_service = LMTokenClassifierService(tokenizer, layoutlm)
    pipe = DoctectionPipe(pipeline_component_list=[ocr_service, layoutlm_service])
    path = "path/to/some/form"
    df = pipe.analyze(path=path)
    for dp in df:
    ...
    ```
  - Public methods (5):
    - `clear_predictor(self) -> None`
    - `clone(self) -> LMTokenClassifierService`
    - `get_meta_annotation(self) -> MetaAnnotation`
    - `image_to_features_func(mapping_str: str) -> Callable[..., Callable[[Image], Optional[Any]]]`
    - `serve(self, dp: Image) -> None`
  - Private methods (3):
    - `__init__(
        self,
        tokenizer: Any,
        language_model: Union[LayoutTokenModels, LmTokenModels],
        padding: Literal["max_length", "do_not_pad", "longest"] = "max_length",
        truncation: bool = True,
        return_overflowing_tokens: bool = False,
        use_other_as_default_category: bool = False,
        segment_positions: Optional[Union[LayoutType, Sequence[LayoutType]]] = None,
        sliding_window_stride: int = 0,
    ) -> None`
    - `_get_name(self) -> str`
    - `_init_sanity_checks(self) -> None`

**`class LMSequenceClassifierService`**
  - Location: line 291-438
  - Inherits: PipelineComponent
  - Pipeline component for sequence classification.
    Example:
    ```python
    # setting up compulsory ocr service
    tesseract_config_path = ModelCatalog.get_full_path_configs("/dd/conf_tesseract.yaml")
    tess = TesseractOcrDetector(tesseract_config_path)
    ocr_service = TextExtractionService(tess)
    # hf tokenizer and token classifier
    tokenizer = LayoutLMTokenizerFast.from_pretrained("microsoft/layoutlm-base-uncased")
    layoutlm = HFLayoutLmSequenceClassifier("path/to/config.json", "path/to/model.bin",
    categories=["handwritten", "presentation", "resume"])
    # token classification service
    layoutlm_service = LMSequenceClassifierService(tokenizer, layoutlm)
    pipe = DoctectionPipe(pipeline_component_list=[ocr_service, layoutlm_service])
    path = "path/to/some/form"
    df = pipe.analyze(path=path)
    for dp in df:
    ...
    ```
  - Public methods (5):
    - `clear_predictor(self) -> None`
    - `clone(self) -> LMSequenceClassifierService`
    - `get_meta_annotation(self) -> MetaAnnotation`
    - `image_to_features_func(mapping_str: str) -> Callable[..., Callable[[Image], Optional[Any]]]`
    - `serve(self, dp: Image) -> None`
  - Private methods (3):
    - `__init__(
        self,
        tokenizer: Any,
        language_model: Union[LayoutSequenceModels, LmSequenceModels],
        padding: Literal["max_length", "do_not_pad", "longest"] = "max_length",
        truncation: bool = True,
        return_overflowing_tokens: bool = False,
        use_other_as_default_category: bool = False,
    ) -> None`
    - `_get_name(self) -> str`
    - `_init_sanity_checks(self) -> None`

#### deepdoctection/pipe/order.py

**`class OrderGenerator`**
  - Location: line 44-384
  - Class for implementing text ordering logic and tasks that have preparational character.
    This includes logic for grouping word type `ImageAnnotation` into text lines, splitting text lines into 
sub-lines
    (by detecting gaps between words), as well as ordering text blocks (e.g., titles, tables, etc.).
  - Public methods (3):
    - `group_lines_into_lines(
        line_anns: Sequence[ImageAnnotation], image_id: Optional[str] = None
    ) -> list[tuple[int, int, str]]`
    - `group_words_into_lines(
        word_anns: Sequence[ImageAnnotation], image_id: Optional[str] = None
    ) -> list[tuple[int, int, str]]`
    - `order_blocks(
        self, anns: list[ImageAnnotation], image_width: float, image_height: float, image_id: Optional[str] = 
None
    ) -> Sequence[tuple[int, str]]`
  - Private methods (5):
    - `__init__(self, starting_point_tolerance: float, broken_line_tolerance: float, height_tolerance: float)`
    - `_connected_components(columns: list[BoundingBox]) -> list[dict[str, Any]]`
    - `_consolidate_columns(self, columns: list[BoundingBox]) -> dict[int, int]`
    - `_make_column_detect_results(columns: Sequence[BoundingBox]) -> Sequence[DetectionResult]`
    - `_sort_anns_grouped_by_blocks(
        block: Sequence[tuple[int, str]],
        anns: Sequence[ImageAnnotation],
        image_width: float,
        image_height: float,
        image_id: Optional[str] = None,
    ) -> list[tuple[int, str]]`

**`class TextLineGenerator`**
  - Location: line 387-520
  - Class for generating synthetic text lines from words.
    Possible to break text lines into sub-lines by using a paragraph break threshold. This allows detection of
a
    multi-column structure just by observing sub-lines.
  - Public methods (1):
    - `create_detection_result(
        self,
        word_anns: Sequence[ImageAnnotation],
        image_width: float,
        image_height: float,
        image_id: Optional[str] = None,
        highest_level: bool = True,
    ) -> Sequence[DetectionResult]`
  - Private methods (2):
    - `__init__(self, make_sub_lines: bool, paragraph_break: Optional[float] = None)`
    - `_make_detect_result(self, box: BoundingBox, relationships: dict[str, list[str]]) -> DetectionResult`

**`class TextLineServiceMixin`**
  - Location: line 523-574
  - Inherits: PipelineComponent, ABC
  - This class is used to create text lines similar to `TextOrderService`.
    It uses the logic of the `TextOrderService` but modifies it to suit its needs. It specifically uses the
    `_create_lines_for_words` method and modifies the `serve` method.
  - Private methods (2):
    - `__init__(
        self,
        name: str,
        include_residual_text_container: bool = True,
        paragraph_break: Optional[float] = None,
    )`
    - `_create_lines_for_words(self, word_anns: Sequence[ImageAnnotation]) -> Sequence[ImageAnnotation]`

**`class TextLineService`**
  - Location: line 577-623
  - Inherits: TextLineServiceMixin
  - Some OCR systems do not identify lines of text but only provide text boxes for words.
    This is not sufficient for certain applications. This service determines rule-based text lines based on 
word boxes.
    One difficulty is that text lines are not continuous but are interrupted, for example, in multi-column 
layouts.
    These interruptions are taken into account insofar as the gap between two words on almost the same page 
height must
    not be too large.
    The service constructs new `ImageAnnotation` of the category `LayoutType.line` and forms relations between
the text
    lines and the words contained in the text lines. The reading order is not arranged.
  - Public methods (3):
    - `clone(self) -> TextLineService`
    - `get_meta_annotation(self) -> MetaAnnotation`
    - `serve(self, dp: Image) -> None`
  - Private methods (1):
    - `__init__(self, paragraph_break: Optional[float] = None)`

**`class TextOrderService`**
  - Location: line 627-849
  - Inherits: TextLineServiceMixin
  - Reading order of words within floating text blocks as well as reading order of blocks within simple text 
blocks.
    To understand the difference between floating text blocks and simple text blocks, consider a page 
containing an
    article and a table. Table cells are text blocks that contain words which must be sorted. However, they do
not
    belong to floating text that encircle a table. They are rather an element that is supposed to be read 
independently.
    A heuristic argument for its ordering is used where the underlying assumption is the reading order from 
left
    to right.
    - For the reading order within a text block, text containers (i.e., image annotations that contain 
character
    sub-annotations) are sorted based on their bounding box center and then lines are formed: Each word 
induces a new
    line, provided that its center is not in a line that has already been created by an already processed 
word. The
    entire block width is defined as the line width and the upper or lower line limit of the word bounding box
as the
    upper or lower line limit. The reading order of the words is from left to right within a line. The reading
order
    of the lines is from top to bottom.
    - For the reading order of text blocks within a page, the blocks are sorted using a similar procedure, 
with the
    difference that columns are formed instead of lines. Column lengths are defined as the length of the 
entire page
    and the left and right text block boundaries as the left and right column boundaries.
    A category annotation per word is generated, which fixes the order per word in the block, as well as a 
category
    annotation per block, which saves the reading order of the block per page.
    The blocks are defined in `text_block_categories` and text blocks that should be considered when 
generating
    narrative text must be added in `floating_text_block_categories`.
    Example:
    ```python
    order = TextOrderService(
    text_container="word",
    text_block_categories=["title", "text", "list", "cell", "head", "body"],
    floating_text_block_categories=["title", "text", "list"]
    )
    ```
    Note:
    The blocks are defined in `text_block_categories` and text blocks that should be considered when 
generating
    narrative text must be added in `floating_text_block_categories`.
  - Public methods (6):
    - `clear_predictor(self) -> None`
    - `clone(self) -> TextOrderService`
    - `get_meta_annotation(self) -> MetaAnnotation`
    - `order_blocks(self, text_block_anns: list[ImageAnnotation]) -> None`
    - `order_text_in_text_block(self, text_block_ann: ImageAnnotation) -> None`
    - `serve(self, dp: Image) -> None`
  - Private methods (3):
    - `__init__(
        self,
        text_container: str,
        text_block_categories: Optional[Union[str, Sequence[TypeOrStr]]] = None,
        floating_text_block_categories: Optional[Union[str, Sequence[TypeOrStr]]] = None,
        include_residual_text_container: bool = True,
        starting_point_tolerance: float = 0.005,
        broken_line_tolerance: float = 0.003,
        height_tolerance: float = 2.0,
        paragraph_break: Optional[float] = 0.035,
    )`
    - `_create_columns(self) -> None`
    - `_init_sanity_checks(self) -> None`

#### deepdoctection/pipe/refine.py

**`class TableSegmentationRefinementService`**
  - Location: line 391-561
  - Inherits: PipelineComponent
  - Refinement of the cell segmentation. The aim of this component is to create a table structure so that an 
HTML
    structure can be created.
    Assume that the arrangement of cells, rows and in the table is as follows in the original state. There is 
only one
    column.
    +----------+
    | C1   C2  |
    +----------+
    | C3   C3  |
    +----------+
    The first two cells have the same column assignment via the segmentation and must therefore be merged. 
Note that
    the number of rows and columns does not change in the refinement process. What changes is just the number 
of cells.
    Furthermore, when merging, it must be ensured that the combined cells still have a rectangular shape. This
is also
    guaranteed in the refining process.
    +----------+
    | C1 |  C2 |
    +          +
    | C3 |  C3 |
    +----------+
    The table consists of one row and two columns. The upper cells belong together with the lower cell. 
However, this
    means that all cells must be merged with one another so that the table only consists of one cell after the
    refinement process.
    Example:
    ```python
    layout = ImageLayoutService(layout_detector, to_image=True, crop_image=True)
    cell = SubImageLayoutService(cell_detector, "TABLE")
    row_col = SubImageLayoutService(row_col_detector, "TABLE")
    table_segmentation = TableSegmentationService("ioa",0.9,0.8,True,0.0001,0.0001)
    table_segmentation_refinement = TableSegmentationRefinementService()
    table_recognition_pipe = DoctectionPipe([layout,
    cell,
    row_col,
    table_segmentation,
    table_segmentation_refinement])
    df = pipe.analyze(path="path/to/document.pdf")
    for dp in df:
    ...
    ```
  - Public methods (4):
    - `clear_predictor(self) -> None`
    - `clone(self) -> TableSegmentationRefinementService`
    - `get_meta_annotation(self) -> MetaAnnotation`
    - `serve(self, dp: Image) -> None`
  - Private methods (1):
    - `__init__(self, table_names: Sequence[ObjectTypes], cell_names: Sequence[ObjectTypes]) -> None`

#### deepdoctection/pipe/segment.py

**`class SegmentationResult`**
  - Location: line 46-62
  - Mutable storage for segmentation results.
    Args:
    annotation_id: The annotation ID.
    row_num: The row number.
    col_num: The column number.
    rs: The row span.
    cs: The column span.

**`class ItemHeaderResult`**
  - Location: line 66-71
  - Simple mutable storage for item header results

**`class TableSegmentationService`**
  - Location: line 776-990
  - Inherits: PipelineComponent
  - Table segmentation after successful cell detection. In addition, row and column detection must have been 
carried
    out.
    After cell recognition, these must be given a semantically correct position within the table. The row 
number,
    column number, row span and column span of the cell are determined. The determination takes place via an 
assignment
    via intersection.
    - Predicted rows are stretched horizontally to the edges of the table. Columns are stretched vertically. 
There is
    also the option of stretching rows and columns so that they completely pave the table (set
    `tile_table_with_items=True`).
    - Next, rows and columns are given a row or column number by sorting them vertically or horizontally
    according to the box center.
    - The averages are then determined in pairs separately for rows and columns (more precisely: `Iou` /
    intersection-over-union or `ioa` / intersection-over-area of rows and cells or columns and cells. A cell 
is
    assigned a row position if the `iou` / `ioa` is above a defined threshold.
    - The minimum row or column with which the cell was matched is used as the row and column of the cell. Row
span /
    col span result from the number of matched rows and columns.
    Note:
    It should be noted that this method means that cell positions can be assigned multiple times by different 
cells.
    If this should be excluded, `TableSegmentationRefinementService` can be used to merge cells.
  - Public methods (4):
    - `clear_predictor(self) -> None`
    - `clone(self) -> TableSegmentationService`
    - `get_meta_annotation(self) -> MetaAnnotation`
    - `serve(self, dp: Image) -> None`
  - Private methods (1):
    - `__init__(
        self,
        segment_rule: Literal["iou", "ioa"],
        threshold_rows: float,
        threshold_cols: float,
        tile_table_with_items: bool,
        remove_iou_threshold_rows: float,
        remove_iou_threshold_cols: float,
        table_name: TypeOrStr,
        cell_names: Sequence[TypeOrStr],
        item_names: Sequence[TypeOrStr],
        sub_item_names: Sequence[TypeOrStr],
        stretch_rule: Literal["left", "equal"] = "left",
    )`

**`class PubtablesSegmentationService`**
  - Location: line 993-1351
  - Inherits: PipelineComponent
  - Table segmentation for table recognition detectors trained on Pubtables1M dataset. It will require 
`ImageAnnotation`
    of type `LayoutType.row`, `LayoutType.column` and cells of at least one type `CellType.spanning`,
    `CellType.ROW_HEADER`, `CellType.COLUMN_HEADER`, `CellType.PROJECTED_ROW_HEADER`. For table recognition 
using
    this service build a pipeline as follows:
    Example:
    ```python
    layout = ImageLayoutService(layout_detector, to_image=True, crop_image=True)
    recognition = SubImageLayoutService(table_recognition_detector, LayoutType.TABLE, {1: 6, 2:7, 3:8, 4:9}, 
True)
    segment = PubtablesSegmentationService('ioa', 0.4, 0.4, True, 0.8, 0.8, 7)
    pipe = DoctectionPipe([layout, recognition, segment])
    ```
    Under the hood this service performs the following tasks:
    - Stretching of rows and columns horizontally and vertically, so that the underlying table is fully tiled 
by rows
    and columns.
    - Enumerating rows and columns.
    - For intersecting rows and columns it will create an `ImageAnnotation` of category `LayoutType.cell`.
    - Using spanning cells from the detector to determine their `row_number` and `column_number` position.
    - Using cells and spanning cells, it will generate a tiling of the table with cells. When some cells have 
a position
    with some spanning cells, it will deactivate those simple cells and prioritize the spanning cells.
    - Determining the HTML representation of table.
    Info:
    Different from the `TableSegmentationService` this service does not require a refinement service: the 
advantage
    of this method is, that the segmentation can already be 'HTMLized'.
  - Public methods (3):
    - `clone(self) -> PubtablesSegmentationService`
    - `get_meta_annotation(self) -> MetaAnnotation`
    - `serve(self, dp: Image) -> None`
  - Private methods (1):
    - `__init__(
        self,
        segment_rule: Literal["iou", "ioa"],
        threshold_rows: float,
        threshold_cols: float,
        tile_table_with_items: bool,
        remove_iou_threshold_rows: float,
        remove_iou_threshold_cols: float,
        table_name: TypeOrStr,
        cell_names: Sequence[TypeOrStr],
        spanning_cell_names: Sequence[TypeOrStr],
        item_names: Sequence[TypeOrStr],
        sub_item_names: Sequence[TypeOrStr],
        item_header_cell_names: Sequence[TypeOrStr],
        item_header_thresholds: Sequence[float],
        cell_to_image: bool = True,
        crop_cell_image: bool = False,
        stretch_rule: Literal["left", "equal"] = "left",
    ) -> None`

#### deepdoctection/pipe/sub_layout.py

**`class DetectResultGenerator`**
  - Location: line 40-154
  - Use `DetectResultGenerator` to refine raw detection results.
    Certain pipeline components depend on, for example, at least one object being detected. If this is not the
    case, the generator can generate a `DetectResult` with a default setting. If no object was discovered for 
a
    category, a `DetectResult` with the dimensions of the original image is generated and added to the 
remaining
    `DetectResults`.
  - Public methods (1):
    - `create_detection_result(self, detect_result_list: list[DetectionResult]) -> list[DetectionResult]`
  - Private methods (5):
    - `__init__(
        self,
        categories_name_as_key: Mapping[ObjectTypes, int],
        group_categories: Optional[list[list[ObjectTypes]]] = None,
        exclude_category_names: Optional[Sequence[ObjectTypes]] = None,
        absolute_coords: bool = True,
    ) -> None`
    - `_create_condition(self, detect_result_list: list[DetectionResult]) -> dict[ObjectTypes, int]`
    - `_detection_result_sanity_check(detect_result_list: list[DetectionResult]) -> list[DetectionResult]`
    - `_dummy_for_group_generated(self, category_name: ObjectTypes) -> bool`
    - `_initialize_dummy_for_group_generated(self) -> list[bool]`

**`class SubImageLayoutService`**
  - Location: line 158-311
  - Inherits: PipelineComponent
  - Component in which the selected `ImageAnnotation` can be selected with cropped images and presented to a 
detector.
    The detected `DetectResults` are transformed into `ImageAnnotations` and stored both in the cache of the 
parent
    image and in the cache of the sub image.
    If no objects are discovered, artificial objects can be added by means of a refinement process.
    Example:
    ```python
    detect_result_generator = DetectResultGenerator(categories_items)
    d_items = TPFrcnnDetector(item_config_path, item_weights_path, {1: LayoutType.row,
    2: LayoutType.column})
    item_component = SubImageLayoutService(d_items, LayoutType.table, detect_result_generator)
    ```
  - Public methods (5):
    - `clear_predictor(self) -> None`
    - `clone(self) -> SubImageLayoutService`
    - `get_meta_annotation(self) -> MetaAnnotation`
    - `prepare_np_image(self, sub_image_ann: ImageAnnotation) -> PixelValues`
    - `serve(self, dp: Image) -> None`
  - Private methods (2):
    - `__init__(
        self,
        sub_image_detector: ObjectDetector,
        sub_image_names: Union[str, Sequence[TypeOrStr]],
        service_ids: Optional[Sequence[str]] = None,
        detect_result_generator: Optional[DetectResultGenerator] = None,
        padder: Optional[PadTransform] = None,
    )`
    - `_get_name(predictor_name: str) -> str`

#### deepdoctection/pipe/text.py

**`class TextExtractionService`**
  - Location: line 41-250
  - Inherits: PipelineComponent
  - Text extraction pipeline component.
    This component is responsible for extracting text from images or selected regions of interest (ROIs) using
a
    specified detector. The detector must be able to evaluate a numpy array as an image.
    Text extraction can be performed on the entire image or on selected ROIs, which are layout components 
determined by
    a previously run pipeline component. ROI extraction is particularly useful when using an OCR component as 
the
    detector and the document has a complex structure. By transferring only the ROIs to the detector, OCR 
results can
    be significantly improved due to the simpler structure of the ROI compared to the entire document page.
    Text components (currently only words) are attached to the image as image annotations. A relation is 
assigned
    between text and ROI or between text and the entire image. When selecting ROIs, only the selected 
categories are
    processed. ROIs that are not selected are not presented to the detector.
    Example:
    ```python
    textract_predictor = TextractOcrDetector()
    text_extract = TextExtractionService(textract_predictor)
    pipe = DoctectionPipe([text_extract])
    df = pipe.analyze(path="path/to/document.pdf")
    for dp in df:
    ...
  - Public methods (6):
    - `clear_predictor(self) -> None`
    - `clone(self) -> TextExtractionService`
    - `get_meta_annotation(self) -> MetaAnnotation`
    - `get_predictor_input(
        self, text_roi: Union[Image, ImageAnnotation, list[ImageAnnotation]]
    ) -> Optional[Union[bytes, PixelValues, list[tuple[str, PixelValues]], int]]`
    - `get_text_rois(self, dp: Image) -> Sequence[Union[Image, ImageAnnotation, list[ImageAnnotation]]]`
    - `serve(self, dp: Image) -> None`
  - Private methods (2):
    - `__init__(
        self,
        text_extract_detector: Union[ObjectDetector, PdfMiner, TextRecognizer],
        extract_from_roi: Optional[Union[Sequence[TypeOrStr], TypeOrStr]] = None,
        run_time_ocr_language_selection: bool = False,
    )`
    - `_get_name(text_detector_name: str) -> str`

#### deepdoctection/pipe/transform.py

**`class SimpleTransformService`**
  - Location: line 32-113
  - Inherits: PipelineComponent
  - Pipeline component for transforming an image.
    The service is designed for applying transform predictors that take an image as numpy array as input and 
return
    the same. The service itself will change the underlying metadata like height and width of the returned 
transform.
    This component is meant to be used at the very first stage of a pipeline. If components have already 
returned image
    annotations then this component will currently not re-calculate bounding boxes in terms of the transformed
image.
    It will raise a warning (at runtime) if image annotations have already been appended.
  - Public methods (4):
    - `clear_predictor(self) -> None`
    - `clone(self) -> SimpleTransformService`
    - `get_meta_annotation(self) -> MetaAnnotation`
    - `serve(self, dp: Image) -> None`
  - Private methods (2):
    - `__init__(self, transform_predictor: ImageTransformer)`
    - `_get_name(transform_name: str) -> str`

#### deepdoctection/train/d2_frcnn_train.py

**`class WandbWriter`**
  - Location: line 100-137
  - Inherits: EventWriter
  - Write all scalars to a wandb tool.
  - Public methods (2):
    - `close(self) -> None`
    - `write(self) -> None`
  - Private methods (1):
    - `__init__(
        self,
        project: str,
        repo: str,
        config: Optional[Union[dict[str, Any], CfgNode]] = None,
        window_size: int = 20,
        **kwargs: Any,
    )`

**`class D2Trainer`**
  - Location: line 140-302
  - Inherits: DefaultTrainer
  - Detectron2 `DefaultTrainer` with some custom method for handling datasets and running evaluation.
    Info:
    The setting is made to train standard models in Detectron2.
  - Public methods (6):
    - `build_evaluator(cls, cfg, dataset_name)`
    - `build_hooks(self) -> list[HookBase]`
    - `build_train_loader(self, cfg: CfgNode) -> DataLoader[Any]`
    - `build_writers(self) -> list[EventWriter]`
    - `eval_with_dd_evaluator(self, **build_eval_kwargs: str) -> Union[list[dict[str, Any]], dict[str, Any]]`
    - `setup_evaluator(
        self,
        dataset_val: DatasetBase,
        pipeline_component: PipelineComponent,
        metric: Union[Type[MetricBase], MetricBase],
        build_val_dict: Optional[Mapping[str, str]] = None,
    ) -> None`
  - Private methods (1):
    - `__init__(self, cfg: CfgNode, torch_dataset: IterableDataset[Any], mapper: DatasetMapper) -> None`

#### deepdoctection/train/hf_detr_train.py

**`class DetrDerivedTrainer`**
  - Location: line 65-147
  - Inherits: Trainer
  - Huggingface Trainer for training Transformer models with a custom evaluate method in order
    to use dd Evaluator.
    Train setting is not defined in the trainer itself but in config setting as defined in 
`TrainingArguments`.
    Please check the Transformer documentation: https://huggingface.co/docs/transformers/main_classes/trainer 
for
    custom training setting.
  - Public methods (2):
    - `evaluate(
        self,
        eval_dataset: Optional[Dataset[Any]] = None,  # pylint: disable=W0613
        ignore_keys: Optional[list[str]] = None,  # pylint: disable=W0613
        metric_key_prefix: str = "eval",  # pylint: disable=W0613
    ) -> dict[str, float]`
    - `setup_evaluator(
        self,
        dataset_val: DatasetBase,
        pipeline_component: PipelineComponent,
        metric: Union[Type[MetricBase], MetricBase],
        run: Optional[wandb.sdk.wandb_run.Run] = None,
        **build_eval_kwargs: Union[str, int],
    ) -> None`
  - Private methods (1):
    - `__init__(
        self,
        model: Union[PreTrainedModel, nn.Module],
        args: TrainingArguments,
        data_collator: DetrDataCollator,
        train_dataset: DatasetAdapter,
        eval_dataset: Optional[DatasetBase] = None,
    )`

#### deepdoctection/train/hf_layoutlm_train.py

**`class LayoutLMTrainer`**
  - Location: line 162-255
  - Inherits: Trainer
  - Huggingface Trainer for training Transformer models with a custom evaluate method to use the 
Deepdoctection
    Evaluator.
    Train settings are not defined in the trainer itself but in the config setting as defined in 
`TrainingArguments`.
    Please check the Transformer documentation for custom training settings.
    Info:
    https://huggingface.co/docs/transformers/main_classes/trainer
  - Public methods (2):
    - `evaluate(
        self,
        eval_dataset: Optional[Dataset[Any]] = None,  # pylint: disable=W0613
        ignore_keys: Optional[list[str]] = None,  # pylint: disable=W0613
        metric_key_prefix: str = "eval",  # pylint: disable=W0613
    ) -> dict[str, float]`
    - `setup_evaluator(
        self,
        dataset_val: DatasetBase,
        pipeline_component: PipelineComponent,
        metric: Union[Type[ClassificationMetric], ClassificationMetric],
        run: Optional[wandb.sdk.wandb_run.Run] = None,
        **build_eval_kwargs: Union[str, int],
    ) -> None`
  - Private methods (1):
    - `__init__(
        self,
        model: Union[PreTrainedModel, nn.Module],
        args: TrainingArguments,
        data_collator: LayoutLMDataCollator,
        train_dataset: DatasetAdapter,
        eval_dataset: Optional[DatasetBase] = None,
    )`

#### deepdoctection/train/tp_frcnn_train.py

**`class LoadAugmentAddAnchors`**
  - Location: line 75-87
  - A helper class for default mapping `load_augment_add_anchors`.
    Args:
    config: An `AttrDict` configuration for TP FRCNN.
  - Private methods (2):
    - `__call__(self, dp: JsonDict) -> Optional[JsonDict]`
    - `__init__(self, config: AttrDict) -> None`

#### deepdoctection/utils/concurrency.py

**`class StoppableThread`**
  - Location: line 36-101
  - Inherits: threading.Thread
  - A thread that has a `stop` event.
    This class extends `threading.Thread` and provides a mechanism to stop the thread gracefully.
  - Public methods (4):
    - `queue_get_stoppable(self, q: QueueType) -> Any`
    - `queue_put_stoppable(self, q: QueueType, obj: Any) -> None`
    - `stop(self) -> None`
    - `stopped(self) -> bool`
  - Private methods (1):
    - `__init__(self, evt: Optional[threading.Event] = None) -> None`

#### deepdoctection/utils/error.py

**`class BoundingBoxError`**
  - Location: line 23-24
  - Inherits: BaseException
  - Special exception only for `datapoint.box.BoundingBox`

**`class AnnotationError`**
  - Location: line 27-28
  - Inherits: BaseException
  - Special exception only for `datapoint.annotation.Annotation`

**`class ImageError`**
  - Location: line 31-32
  - Inherits: BaseException
  - Special exception only for `datapoint.image.Image`

**`class UUIDError`**
  - Location: line 35-36
  - Inherits: BaseException
  - Special exception only for `utils.identifier`

**`class DependencyError`**
  - Location: line 39-41
  - Inherits: BaseException
  - Special exception only for missing dependencies. We do not use the internals `ImportError` or
    `ModuleNotFoundError`.

**`class DataFlowTerminatedError`**
  - Location: line 44-50
  - Inherits: BaseException
  - An exception indicating that the `DataFlow` is unable to produce any more data.
    This exception is raised when something wrong happens so that calling `__iter__` cannot give a valid 
iterator
    anymore. In most `DataFlow` this will never be raised.

**`class DataFlowResetStateNotCalledError`**
  - Location: line 53-64
  - Inherits: BaseException
  - An exception indicating that `reset_state()` has not been called before starting iteration.
    Example:
    ```python
    raise DataFlowResetStateNotCalledError()
    ```
  - Private methods (1):
    - `__init__(self) -> None`

**`class MalformedData`**
  - Location: line 67-72
  - Inherits: BaseException
  - Exception class for malformed data.
    Use this class if something does not look right with the data.

**`class FileExtensionError`**
  - Location: line 75-78
  - Inherits: BaseException
  - Exception class for wrong file extensions.

**`class TesseractError`**
  - Location: line 81-90
  - Inherits: RuntimeError
  - Tesseract Error
  - Private methods (1):
    - `__init__(self, status: int, message: str) -> None`

#### deepdoctection/utils/file_utils.py

**(private) `class _LazyModule`**
  - Location: line 904-970
  - Inherits: ModuleType
  - Module class that surfaces all objects but only performs associated imports when the objects are 
requested.
    Note:
    This class is needed for autocompletion in an IDE.
  - Private methods (5):
    - `__dir__(self)`
    - `__getattr__(self, name: str) -> Any`
    - `__init__(self, name, module_file, import_structure, module_spec=None, extra_objects=None)`
    - `__reduce__(self)`
    - `_get_module(self, module_name: str)`

#### deepdoctection/utils/fs.py

**`class LoadImageFunc`**
  - Location: line 251-260
  - Inherits: Protocol
  - Protocol for typing `load_image_from_file`.
    Info:
    This protocol defines the call signature for image loading functions.
  - Private methods (1):
    - `__call__(self, path: PathLikeOrStr) -> Optional[PixelValues]`

#### deepdoctection/utils/logger.py

**`class LoggingRecord`**
  - Location: line 51-74
  - `LoggingRecord` to pass to the logger in order to distinguish from third party libraries.
    Note:
    `log_dict` will be added to the log record as a dict.
    Args:
    msg: The log message.
    log_dict: Optional dictionary to add to the log record.
  - Private methods (2):
    - `__post_init__(self) -> None`
    - `__str__(self) -> str`

**`class CustomFilter`**
  - Location: line 77-87
  - Inherits: logging.Filter
  - A custom filter
  - Public methods (1):
    - `filter(self, record: logging.LogRecord) -> bool`

**`class StreamFormatter`**
  - Location: line 90-117
  - Inherits: logging.Formatter
  - A custom formatter to produce unified LogRecords
  - Public methods (1):
    - `format(self, record: logging.LogRecord) -> str`

**`class FileFormatter`**
  - Location: line 120-142
  - Inherits: logging.Formatter
  - A custom formatter to produce a loggings in json format
  - Public methods (1):
    - `format(self, record: logging.LogRecord) -> str`

#### deepdoctection/utils/metacfg.py

**`class AttrDict`**
  - Location: line 34-177
  - Class `AttrDict` for maintaining configs and some functions for generating and saving `AttrDict` instances
to
    `.yaml` files.
    Info:
    This module provides a class for storing key-value pairs as attributes and functions for serializing and
    deserializing configurations.
  - Public methods (5):
    - `freeze(self, freezed: bool = True) -> None`
    - `from_dict(self, d: dict[str, Any]) -> None`
    - `overwrite_config(self, other_config: AttrDict) -> None`
    - `to_dict(self) -> dict[str, Any]`
    - `update_args(self, args: list[str]) -> None`
  - Private methods (5):
    - `__eq__(self, _: Any) -> bool`
    - `__getattr__(self, name: str) -> Any`
    - `__ne__(self, _: Any) -> bool`
    - `__setattr__(self, name: str, value: Any) -> None`
    - `__str__(self) -> str`

#### deepdoctection/utils/mocks.py

**`class ModelDesc`**
  - Location: line 57-61
  - Mock ModelDesc class from tensorpack.
  - Private methods (1):
    - `__init__(self) -> None`

**`class ImageAugmentor`**
  - Location: line 64-68
  - Mock ImageAugmentor class from tensorpack.
  - Private methods (1):
    - `__init__(self) -> None`

**`class Callback`**
  - Location: line 71-75
  - Mock Callback class from tensor
  - Private methods (1):
    - `__init__(self) -> None`

**`class Config`**
  - Location: line 78-81
  - Mock class for Config

**`class Tree`**
  - Location: line 84-87
  - Mock class for Tree

**`class IterableDataset`**
  - Location: line 90-93
  - Mock class for IterableDataset

#### deepdoctection/utils/pdf_utils.py

**`class PDFStreamer`**
  - Location: line 181-241
  - A class for streaming PDF documents as bytes objects.
    Built as a generator, it is possible to load the document iteratively into memory. Uses `pypdf` 
`PdfReader` and
    `PdfWriter`.
    Example:
    ```python
    df = dataflow.DataFromIterable(PDFStreamer(path=path))
    df.reset_state()
    for page in df:
    ...
    streamer = PDFStreamer(path=path)
    pages = len(streamer)
    random_int = random.sample(range(0, pages), 2)
    for ran in random_int:
    pdf_bytes = streamer[ran]
    streamer.close()
    ```
    Note:
    Do not forget to close the streamer, otherwise the file will never be closed and might cause memory leaks 
if
    you open many files.
  - Public methods (1):
    - `close(self) -> None`
  - Private methods (4):
    - `__getitem__(self, index: int) -> bytes`
    - `__init__(self, path_or_bytes: Union[PathLikeOrStr, bytes]) -> None`
    - `__iter__(self) -> Generator[tuple[bytes, int], None, None]`
    - `__len__(self) -> int`

**`class PopplerError`**
  - Location: line 282-296
  - Inherits: RuntimeError
  - Poppler Error.
  - Private methods (1):
    - `__init__(self, status: int, message: str) -> None`

#### deepdoctection/utils/settings.py

**`class ObjectTypes`**
  - Location: line 31-47
  - Inherits: str, Enum
  - Base Class for describing objects as attributes of Enums
  - Public methods (1):
    - `from_value(cls, value: str) -> ObjectTypes`
  - Private methods (1):
    - `__repr__(self) -> str`

**`class DefaultType`**
  - Location: line 57-60
  - Inherits: ObjectTypes
  - Type for default member

**`class PageType`**
  - Location: line 64-74
  - Inherits: ObjectTypes
  - Type for document page properties

**`class SummaryType`**
  - Location: line 78-83
  - Inherits: ObjectTypes
  - Summary type member

**`class DocumentType`**
  - Location: line 87-111
  - Inherits: ObjectTypes
  - Document types

**`class LayoutType`**
  - Location: line 115-142
  - Inherits: ObjectTypes
  - Layout types

**`class TableType`**
  - Location: line 146-154
  - Inherits: ObjectTypes
  - Types for table properties

**`class CellType`**
  - Location: line 158-170
  - Inherits: ObjectTypes
  - Types for cell properties

**`class WordType`**
  - Location: line 174-185
  - Inherits: ObjectTypes
  - Types for word properties

**`class TokenClasses`**
  - Location: line 189-195
  - Inherits: ObjectTypes
  - Types for token classes

**`class BioTag`**
  - Location: line 199-206
  - Inherits: ObjectTypes
  - Types for tags

**`class TokenClassWithTag`**
  - Location: line 210-224
  - Inherits: ObjectTypes
  - Types for token classes with tags, e.g. B-answer

**`class Relationships`**
  - Location: line 228-235
  - Inherits: ObjectTypes
  - Types for describing relationships between types

**`class Languages`**
  - Location: line 239-301
  - Inherits: ObjectTypes
  - Language types

**`class DatasetType`**
  - Location: line 305-312
  - Inherits: ObjectTypes
  - Dataset types

#### deepdoctection/utils/transform.py

**`class BaseTransform`**
  - Location: line 78-138
  - Inherits: ABC
  - A deterministic image transformation. This class is also the place to provide a default implementation to 
any
    `apply_xxx` method. The current default is to raise `NotImplementedError` in any such methods.
    All subclasses should implement `apply_image`. The image should be of type `uint8` in range [0, 255], or
    floating point images in range [0, 1] or [0, 255]. Some subclasses may implement `apply_coords`, when 
applicable.
    It should take and return a numpy array of Nx2, where each row is the (x, y) coordinate.
    The implementation of each method may choose to modify its input data in-place for efficient 
transformation.
    Note:
    All subclasses should implement `apply_image`. Some may implement `apply_coords`.
  - Public methods (5):
    - `apply_coords(self, coords: npt.NDArray[float32]) -> npt.NDArray[float32]`
    - `apply_image(self, img: PixelValues) -> PixelValues`
    - `get_category_names(self) -> tuple[ObjectTypes, ...]`
    - `get_init_args(self) -> Set[str]`
    - `inverse_apply_coords(self, coords: npt.NDArray[float32]) -> npt.NDArray[float32]`

**`class ResizeTransform`**
  - Location: line 141-222
  - Inherits: BaseTransform
  - Resize the image.
  - Public methods (4):
    - `apply_coords(self, coords: npt.NDArray[float32]) -> npt.NDArray[float32]`
    - `apply_image(self, img: PixelValues) -> PixelValues`
    - `get_category_names(self) -> tuple[ObjectTypes, ...]`
    - `inverse_apply_coords(self, coords: npt.NDArray[float32]) -> npt.NDArray[float32]`
  - Private methods (1):
    - `__init__(
        self,
        h: Union[int, float],
        w: Union[int, float],
        new_h: Union[int, float],
        new_w: Union[int, float],
        interp: str,
    )`

**`class InferenceResize`**
  - Location: line 225-268
  - Try resizing the shortest edge to a certain number while avoiding the longest edge to exceed max_size. 
This is
    the inference version of `extern.tp.frcnn.common.CustomResize` .
  - Public methods (1):
    - `get_transform(self, img: PixelValues) -> ResizeTransform`
  - Private methods (1):
    - `__init__(self, short_edge_length: int, max_size: int, interp: str = "VIZ") -> None`

**`class PadTransform`**
  - Location: line 306-397
  - Inherits: BaseTransform
  - A transform for padding images left/right/top/bottom-wise.
  - Public methods (5):
    - `apply_coords(self, coords: npt.NDArray[float32]) -> npt.NDArray[float32]`
    - `apply_image(self, img: PixelValues) -> PixelValues`
    - `clone(self) -> PadTransform`
    - `get_category_names(self) -> tuple[ObjectTypes, ...]`
    - `inverse_apply_coords(self, coords: npt.NDArray[float32]) -> npt.NDArray[float32]`
  - Private methods (1):
    - `__init__(
        self,
        pad_top: int,
        pad_right: int,
        pad_bottom: int,
        pad_left: int,
    )`

**`class RotationTransform`**
  - Location: line 400-520
  - Inherits: BaseTransform
  - A transform for rotating images by 90, 180, 270, or 360 degrees.
  - Public methods (8):
    - `apply_coords(self, coords: npt.NDArray[float32]) -> npt.NDArray[float32]`
    - `apply_image(self, img: PixelValues) -> PixelValues`
    - `clone(self) -> RotationTransform`
    - `get_category_names(self) -> tuple[ObjectTypes, ...]`
    - `inverse_apply_coords(self, coords: npt.NDArray[float32]) -> npt.NDArray[float32]`
    - `set_angle(self, angle: Literal[90, 180, 270, 360]) -> None`
    - `set_image_height(self, image_height: Union[int, float]) -> None`
    - `set_image_width(self, image_width: Union[int, float]) -> None`
  - Private methods (1):
    - `__init__(self, angle: Literal[90, 180, 270, 360])`

#### deepdoctection/utils/types.py

**`class IsDataclass`**
  - Location: line 33-38
  - Inherits: Protocol
  - type hint for general dataclass

#### deepdoctection/utils/viz.py

**`class VizPackageHandler`**
  - Location: line 217-730
  - A handler for the image processing libraries PIL or OpenCV. Explicit use of the libraries is not intended.
    If the environ.ment variable USE_DD_OPENCV=True is set, only the CV2 functions will be used via the 
handler.
    The default library is PIL. Compared to OpenCV, PIL is somewhat slower (this applies to reading and 
writing
    image files), which can lead to a bottleneck during training, especially if the loading is not 
parallelized
  - Public methods (13):
    - `convert_b64_to_np(self, image: B64Str) -> PixelValues`
    - `convert_bytes_to_np(self, image_bytes: bytes) -> PixelValues`
    - `convert_np_to_b64(self, image: PixelValues) -> str`
    - `draw_rectangle(
        self, np_image: PixelValues, box: tuple[Any, Any, Any, Any], color: tuple[int, int, int], thickness: 
int
    ) -> PixelValues`
    - `draw_text(
        self,
        np_image: PixelValues,
        pos: tuple[Any, Any],
        text: str,
        color: tuple[int, int, int],
        font_scale: float,
        rectangle_thickness: int = 1,
    ) -> PixelValues`
    - `encode(self, np_image: PixelValues) -> bytes`
    - `get_text_size(self, text: str, font_scale: float) -> tuple[int, int]`
    - `interactive_imshow(self, np_image: PixelValues) -> None`
    - `read_image(self, path: PathLikeOrStr) -> PixelValues`
    - `refresh(self) -> None`
    - `resize(self, image: PixelValues, width: int, height: int, interpolation: str) -> PixelValues`
    - `rotate_image(self, np_image: PixelValues, angle: float) -> PixelValues`
    - `write_image(self, path: PathLikeOrStr, image: PixelValues) -> None`
  - Private methods (27):
    - `__init__(self) -> None`
    - `_cv2_convert_b64_to_np(image: B64Str) -> PixelValues`
    - `_cv2_convert_bytes_to_np(image_bytes: bytes) -> PixelValues`
    - `_cv2_convert_np_to_b64(image: PixelValues) -> str`
    - `_cv2_draw_rectangle(
        np_image: PixelValues, box: tuple[Any, Any, Any, Any], color: Sequence[int], thickness: int
    ) -> PixelValues`
    - `_cv2_draw_text(
        self,
        np_image: PixelValues,
        pos: tuple[Any, Any],
        text: str,
        color: tuple[int, int, int],
        font_scale: float,
        rectangle_thickness: int,
    ) -> PixelValues`
    - `_cv2_encode(np_image: PixelValues) -> bytes`
    - `_cv2_get_text_size(self, text: str, font_scale: float) -> tuple[int, int]`
    - `_cv2_interactive_imshow(self, np_image: PixelValues) -> None`
    - `_cv2_read_image(path: PathLikeOrStr) -> PixelValues`
    - `_cv2_resize(image: PixelValues, width: int, height: int, interpolation: str) -> PixelValues`
    - `_cv2_rotate_image(np_image: PixelValues, angle: float) -> PixelValues`
    - `_cv2_write_image(path: PathLikeOrStr, image: PixelValues) -> None`
    - `_pillow_convert_b64_to_np(image: B64Str) -> PixelValues`
    - `_pillow_convert_bytes_to_np(image_bytes: bytes) -> PixelValues`
    - `_pillow_convert_np_to_b64(np_image: PixelValues) -> str`
    - `_pillow_draw_rectangle(
        np_image: PixelValues, box: tuple[Any, Any, Any, Any], color: Sequence[int], thickness: int
    ) -> PixelValues`
    - `_pillow_draw_text(
        np_image: PixelValues,
        pos: tuple[Any, Any],
        text: str,
        color: tuple[int, int, int],  # pylint: disable=W0613
        font_scale: float,  # pylint: disable=W0613
        rectangle_thickness: int,  # pylint: disable=W0613
    ) -> PixelValues`
    - `_pillow_encode(np_image: PixelValues) -> bytes`
    - `_pillow_get_text_size(self, text: str, font_scale: float) -> tuple[int, int]`
    - `_pillow_interactive_imshow(np_image: PixelValues) -> None`
    - `_pillow_read_image(path: PathLikeOrStr) -> PixelValues`
    - `_pillow_resize(image: PixelValues, width: int, height: int, interpolation: str) -> PixelValues`
    - `_pillow_rotate_image(np_image: PixelValues, angle: float) -> PixelValues`
    - `_pillow_write_image(path: PathLikeOrStr, image: PixelValues) -> None`
    - `_select_package() -> str`
    - `_set_vars(self, package: str) -> None`

#### tests/data.py

**`class Annotations`**
  - Location: line 50-833
  - dataclass Annotations for building fixtures
  - Public methods (25):
    - `get_annotation_maps(self) -> dict[str, list[AnnotationMap]]`
    - `get_caption_annotation(self) -> List[ImageAnnotation]`
    - `get_cell_annotations(self) -> List[List[ImageAnnotation]]`
    - `get_cell_detect_results(self) -> List[List[DetectionResult]]`
    - `get_cell_sub_cats(
        self,
    ) -> List[Tuple[CategoryAnnotation, CategoryAnnotation, CategoryAnnotation, CategoryAnnotation]]`
    - `get_cell_sub_cats_when_table_fully_tiled(
        self,
    ) -> List[Tuple[CategoryAnnotation, CategoryAnnotation, CategoryAnnotation, CategoryAnnotation]]`
    - `get_col_box_tiling_table(self) -> List[BoundingBox]`
    - `get_col_sub_cats(self) -> List[CategoryAnnotation]`
    - `get_double_word_detect_results(self) -> List[List[DetectionResult]]`
    - `get_global_cell_boxes(self) -> List[List[BoundingBox]]`
    - `get_layout_ann_for_ordering(self) -> List[ImageAnnotation]`
    - `get_layout_annotation(self, segmentation: bool = False) -> List[ImageAnnotation]`
    - `get_layout_detect_results(self) -> List[DetectionResult]`
    - `get_row_box_tiling_table(self) -> List[BoundingBox]`
    - `get_row_sub_cats(self) -> List[CategoryAnnotation]`
    - `get_service_id_to_ann_id(self) -> dict[str, list[str]]`
    - `get_summary_htab_sub_cat(self) -> ContainerAnnotation`
    - `get_summary_sub_cats_when_table_fully_tiled(
        self,
    ) -> Tuple[CategoryAnnotation, CategoryAnnotation, CategoryAnnotation, CategoryAnnotation]`
    - `get_word_box_global(self) -> List[BoundingBox]`
    - `get_word_detect_results(self) -> List[DetectionResult]`
    - `get_word_layout_ann(self) -> List[ImageAnnotation]`
    - `get_word_layout_ann_for_matching(self) -> List[ImageAnnotation]`
    - `get_word_layout_annotations_for_ordering(self) -> List[ImageAnnotation]`
    - `get_word_sub_cats(self) -> List[List[Union[ContainerAnnotation, CategoryAnnotation, 
CategoryAnnotation]]]`
    - `get_word_sub_cats_for_ordering(self) -> List[List[CategoryAnnotation]]`
  - Private methods (1):
    - `__post_init__(self) -> None`

#### tests/dataflow/conftest.py

**`class DatasetThreeDim`**
  - Location: line 37-47
  - Dataset of shape (2,2,3)

#### tests/datapoint/conftest.py

**`class Box`**
  - Location: line 33-121
  - Coordinates for bounding box testing
  - Public methods (11):
    - `area(self) -> float`
    - `cx(self) -> float`
    - `cy(self) -> float`
    - `h(self) -> float`
    - `h_relative(self) -> float`
    - `lrx_relative(self) -> float`
    - `lry_relative(self) -> float`
    - `ulx_relative(self) -> float`
    - `uly_relative(self) -> float`
    - `w(self) -> float`
    - `w_relative(self) -> float`

**`class WhiteImage`**
  - Location: line 133-173
  - np_array, dummy location and file name and ids for testing
  - Public methods (4):
    - `get_bounding_box(self) -> BoundingBox`
    - `get_image_as_b64_string(self) -> str`
    - `get_image_as_np_array(self) -> PixelValues`
    - `get_image_id(cls, type_id: str) -> str`

**`class CatAnn`**
  - Location: line 185-204
  - Category and ids for testing
  - Public methods (1):
    - `get_annotation_id(cls, type_id: str) -> str`

#### tests/mapper/data.py

**`class DatapointCoco`**
  - Location: line 659-721
  - Class for datapoint in coco annotation format
  - Public methods (6):
    - `get_first_ann_box(self) -> Box`
    - `get_first_ann_category(self, as_index: bool = True) -> Union[int, LayoutType]`
    - `get_height(self, image_loaded: bool) -> float`
    - `get_number_anns(self) -> int`
    - `get_white_image(self, path: str, type_id: str = "np") -> Optional[Union[str, PixelValues]]`
    - `get_width(self, image_loaded: bool) -> float`

**`class DatapointPubtabnet`**
  - Location: line 725-901
  - Class for datapoint in pubtabnet annotation format
  - Public methods (24):
    - `get_first_ann_box(self) -> Box`
    - `get_first_ann_category(self, as_index: bool = True) -> Union[int, ObjectTypes]`
    - `get_first_ann_sub_category_col_number_id() -> int`
    - `get_first_ann_sub_category_col_span_id() -> int`
    - `get_first_ann_sub_category_header_name() -> ObjectTypes`
    - `get_first_ann_sub_category_row_number_id() -> int`
    - `get_first_ann_sub_category_row_span_id() -> int`
    - `get_height(self) -> float`
    - `get_html(self) -> str`
    - `get_last_ann_category_name(self) -> ObjectTypes`
    - `get_last_ann_sub_category_col_number_id() -> int`
    - `get_last_ann_sub_category_col_span_id() -> int`
    - `get_last_ann_sub_category_header_name() -> ObjectTypes`
    - `get_last_ann_sub_category_row_number_id() -> int`
    - `get_last_ann_sub_category_row_span_id() -> int`
    - `get_number_cell_anns(self) -> int`
    - `get_number_of_bodies() -> int`
    - `get_number_of_heads() -> int`
    - `get_summary_ann_sub_category_col_id() -> int`
    - `get_summary_ann_sub_category_col_span_id() -> int`
    - `get_summary_ann_sub_category_row_span_id() -> int`
    - `get_summary_ann_sub_category_rows_id() -> int`
    - `get_white_image(self, path: str, type_id: str = "np") -> Union[str, PixelValues]`
    - `get_width(self) -> float`

**`class DatapointProdigy`**
  - Location: line 905-954
  - Class for datapoint in coco annotation format
  - Public methods (5):
    - `get_first_ann_box(self) -> Box`
    - `get_first_ann_category(self, as_index: bool = True) -> Union[ObjectTypes, int]`
    - `get_height(self, image_loaded: bool) -> float`
    - `get_number_anns(self) -> int`
    - `get_width(self, image_loaded: bool) -> float`

**`class DatapointImage`**
  - Location: line 957-1123
  - Class for datapoint in standard Image format
  - Public methods (12):
    - `get_coco_anns(self) -> List[JsonDict]`
    - `get_coco_image(self) -> JsonDict`
    - `get_d2_frcnn_training_anns(self) -> JsonDict`
    - `get_dataset_categories(self) -> DatasetCategories`
    - `get_first_span(self) -> JsonDict`
    - `get_hf_detr_training_anns(self) -> JsonDict`
    - `get_image_str(self) -> str`
    - `get_image_with_summary(self) -> Image`
    - `get_len_spans(self) -> int`
    - `get_second_span(self) -> JsonDict`
    - `get_text(self) -> str`
    - `get_tp_frcnn_training_anns(self) -> JsonDict`
  - Private methods (1):
    - `__init__(self) -> None`

**`class DatapointPageDict`**
  - Location: line 1126-1784
  - Page object as dict
  - Public methods (1):
    - `get_page_dict(self) -> JsonDict`

**`class DatapointXfund`**
  - Location: line 1823-2087
  - Xfund datapoint sample
  - Public methods (12):
    - `get_categories_bio() -> List[ObjectTypes]`
    - `get_categories_dict(self) -> Mapping[LayoutType, str]`
    - `get_categories_dict_names_as_key(self) -> Dict[ObjectTypes, int]`
    - `get_categories_semantics() -> List[ObjectTypes]`
    - `get_category_names_mapping(self) -> Mapping[str, ObjectTypes]`
    - `get_layout_input(self) -> JsonDict`
    - `get_layout_v2_input(self) -> JsonDict`
    - `get_net_token_to_id_mapping(self) -> Dict[ObjectTypes, Any]`
    - `get_raw_layoutlm_features(self) -> JsonDict`
    - `get_sequence_class_results() -> SequenceClassResult`
    - `get_token_class_names() -> List[ObjectTypes]`
    - `get_token_class_results(self) -> List[TokenClassResult]`

**`class IIITar13KJson`**
  - Location: line 2091-2176
  - Xfund datapoint sample already converted to json format
  - Public methods (7):
    - `get_categories_name_as_keys(self) -> Mapping[ObjectTypes, int]`
    - `get_category_names_mapping(self) -> Mapping[str, ObjectTypes]`
    - `get_first_ann_box(self) -> Box`
    - `get_first_ann_category_name() -> str`
    - `get_height(self) -> float`
    - `get_number_anns(self) -> int`
    - `get_width(self) -> float`

#### tests/train/conftest.py

**`class Datapoint`**
  - Location: line 45-73
  - A dataclass for generating an Image datapoint with annotations
  - Public methods (1):
    - `get_datapoint(self) -> Image`

### Functions

#### deepdoctection/analyzer/config.py

**`te_cfg_from_defaults() ->  -> :
  `**
  - Location: line 951
  - Update the configuration with current values from IMAGE_DEFAULTS.
    """

#### deepdoctection/analyzer/dd.py

**`config_sanity_checks() -> None`**
  - Location: line 50
  - Some config sanity checks

**`get_dd_analyzer(
    reset_config_file: bool = True,
    load_default_config_file: bool = False,
    config_overwrite: Optional[list[str]] = None,
    path_config_file: Optional[PathLikeOrStr] = None,
) -> DoctectionPipe`**
  - Location: line 62
  - Factory function for creating the built-in **deep**doctection analyzer.
    Info:
    ...

#### deepdoctection/dataflow/parallel_map.py

**`del_weakref(x)`**
  - Location: line 42
  - delete weakref

#### deepdoctection/datapoint/annotation.py

**`ann_from_dict(cls, **kwargs: AnnotationDict)`**
  - Location: line 39
  - A factory function to create subclasses of annotations from a given dict

#### deepdoctection/datapoint/box.py

**`coco_iou(box_a: npt.NDArray[float32], box_b: npt.NDArray[float32]) -> npt.NDArray[float32]`**
  - Location: line 45
  - Calculate iou for two arrays of bounding boxes in `xyxy` format
    Args:
    ...

**`area(boxes: npt.NDArray[float32]) -> npt.NDArray[float32]`**
  - Location: line 71
  - Computes area of boxes.
    Args:
    ...

**`intersection(boxes1: npt.NDArray[float32], boxes2: npt.NDArray[float32]) -> npt.NDArray[float32]`**
  - Location: line 87
  - Compute pairwise intersection areas between boxes.
    Args:
    ...

**`np_iou(boxes1: npt.NDArray[float32], boxes2: npt.NDArray[float32]) -> npt.NDArray[float32]`**
  - Location: line 117
  - Computes pairwise intersection-over-union between box collections.
    Args:
    ...

**`iou(boxes1: npt.NDArray[float32], boxes2: npt.NDArray[float32]) -> npt.NDArray[float32]`**
  - Location: line 136
  - Computes pairwise intersection-over-union between box collections.
    Note:
    ...

**`intersection_box(
    box_1: BoundingBox, box_2: BoundingBox, width: Optional[float] = None, height: Optional[float] = None
) -> BoundingBox`**
  - Location: line 557
  - Returns the intersection bounding box of two boxes.
    If coords are absolute, it will floor the lower and ceil the upper coord to ensure the resulting box has 
same
    coordinates as the box induces from `crop_box_from_image`
    ...

**`crop_box_from_image(
    np_image: PixelValues, crop_box: BoundingBox, width: Optional[float] = None, height: Optional[float] = 
None
) -> PixelValues`**
  - Location: line 596
  - Crop a box (the crop_box) from a image given as `np.array`. Will floor the left  and ceil the right 
coordinate
    point.
    ...

**`local_to_global_coords(local_box: BoundingBox, embedding_box: BoundingBox) -> BoundingBox`**
  - Location: line 629
  - Transform coords in terms of a cropped image into global coords. The local box coords are given in terms 
of the
    embedding box. The global coords will be determined by transforming the upper left point (which is `(0,0)`
in
    local terms) into the upper left point given by the embedding box. This will shift the ul point of the
    ...

**`global_to_local_coords(global_box: BoundingBox, embedding_box: BoundingBox) -> BoundingBox`**
  - Location: line 665
  - Transforming global bounding box coords into the coordinate system given by the embedding box. The 
transformation
    requires that the global bounding box coordinates lie completely within the rectangle of the embedding 
box.
    The transformation results from a shift of all coordinates given by the shift of the upper left point of 
the
    ...

**`merge_boxes(*boxes: BoundingBox) -> BoundingBox`**
  - Location: line 695
  - Generating the smallest box containing an arbitrary tuple/list of boxes.
    Args:
    ...

**`rescale_coords(
    box: BoundingBox,
    current_total_width: float,
    current_total_height: float,
    scaled_total_width: float,
    scaled_total_height: float,
) -> BoundingBox`**
  - Location: line 713
  - Generating a bounding box with scaled coordinates. Will rescale `x` coordinate with factor
    `*(current_total_width/scaled_total_width)`, resp. `y` coordinate with factor
    `* (current_total_height/scaled_total_height)`,
    ...

**`intersection_boxes(boxes_1: Sequence[BoundingBox], boxes_2: Sequence[BoundingBox]) -> 
Sequence[BoundingBox]`**
  - Location: line 752
  - The multiple version of `intersection_box`: Given two lists of `m` and `n` bounding boxes, it will 
calculate the
    pairwise intersection of both groups. There will be at most `mxn` intersection boxes.
    ...

#### deepdoctection/datapoint/convert.py

**`as_dict(obj: Any, dict_factory) -> Union[Any]`**
  - Location: line 49
  - Args:
    custom func: as_dict to use instead of `dataclasses.asdict` . It also checks if a dataclass has a
    'remove_keys' and will remove all attributes that are returned. Ensures that private attributes
    ...

**`convert_b64_to_np_array(image: str) -> PixelValues`**
  - Location: line 82
  - Converts an image in base4 string encoding representation to a `np.array` of shape 
`(width,height,channel)`.
    Args:
    ...

**`convert_np_array_to_b64(np_image: PixelValues) -> str`**
  - Location: line 96
  - Converts an image from numpy array into a base64 string encoding representation
    Args:
    ...

**`convert_np_array_to_b64_b(np_image: PixelValues) -> bytes`**
  - Location: line 110
  - Converts an image from numpy array into a base64 bytes encoding representation
    Args:
    ...

**`convert_bytes_to_np_array(image_bytes: bytes) -> PixelValues`**
  - Location: line 123
  - Converts an image in `bytes` to a `np.array`
    Args:
    ...

**`convert_pdf_bytes_to_np_array(pdf_bytes: bytes, dpi: Optional[int] = None) -> PixelValues`**
  - Location: line 137
  - Converts a pdf passed as bytes into a `np.array`. Note, that this method expects poppler to be installed.
    Please check the installation guides at <https://poppler.freedesktop.org/> . If no value for `dpi` is 
provided
    the output size will be determined by the mediaBox of the pdf file ready.
    ...

**`convert_pdf_bytes_to_np_array_v2(
    pdf_bytes: bytes, dpi: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None
) -> PixelValues`**
  - Location: line 177
  - Converts a pdf passed as bytes into a numpy array. We use poppler or `pdfmium` to convert the pdf to an 
image.
    Note:
    ...

#### deepdoctection/datapoint/view.py

**`ann_obj_view_factory(annotation: ImageAnnotation, text_container: ObjectTypes) -> 
ImageAnnotationBaseView`**
  - Location: line 829
  - Create an `ImageAnnotationBaseView` subclass given the mapping `IMAGE_ANNOTATION_TO_LAYOUTS`.
    Args:
    ...

#### deepdoctection/datasets/info.py

**`get_merged_categories(*categories: DatasetCategories) -> DatasetCategories`**
  - Location: line 389
  - Given a set of `DatasetCategories`, a `DatasetCategories` instance will be returned that summarize the 
category
    properties of merged dataset. This means it will save the union of all possible categories as its init 
categories.
    Regarding sub categories, only those will be accessible if and only if they are a sub category of a 
category for all
    ...

#### deepdoctection/datasets/instances/funsd.py

**`nn: path
    Returns:
        dict ->  """
    `**
  - Location: line 53
  - load_json(path_ann)
    path, file_name = os.path.split(path_ann)
    base_path, _ = os.path

#### deepdoctection/datasets/registry.py

**`get_dataset(name: str) -> DatasetBase`**
  - Location: line 36
  - Returns an instance of a dataset with a given name. This instance can be used to customize the dataflow 
output
    Example:
    ...

**`print_dataset_infos(add_license: bool = True, add_info: bool = True) -> None`**
  - Location: line 63
  - Prints a table with all registered datasets and some basic information (name, license and optionally 
description)
    Args:
    ...

#### deepdoctection/datasets/save.py

**`dataflow_to_json(
    df: DataFlow,
    path: PathLikeOrStr,
    single_files: bool = False,
    file_name: Optional[str] = None,
    max_datapoints: Optional[int] = None,
    save_image_in_json: bool = True,
    highest_hierarchy_only: bool = False,
) -> None`**
  - Location: line 35
  - Save a dataflow consisting of `datapoint.Image` to a `jsonl` file. Each image will be dumped into a 
separate
    `JSON` object.
    ...

#### deepdoctection/eval/accmetric.py

**`accuracy(label_gt: Sequence[int], label_predictions: Sequence[int], masks: Optional[Sequence[int]] = None) 
-> float`**
  - Location: line 75
  - Calculates the accuracy given predictions and labels. Ignores masked indices.
    Uses `sklearn.metrics.accuracy_score`
    ...

**`confusion(
    label_gt: Sequence[int], label_predictions: Sequence[int], masks: Optional[Sequence[int]] = None
) -> NDArray[int32]`**
  - Location: line 104
  - Calculates the confusion matrix given the predictions and labels.
    Args:
    ...

**`precision(
    label_gt: Sequence[int],
    label_predictions: Sequence[int],
    masks: Optional[Sequence[int]] = None,
    micro: bool = False,
) -> NDArray[float32]`**
  - Location: line 127
  - Calculates the precision for a multi-classification problem using a confusion matrix.
    Args:
    ...

**`recall(
    label_gt: Sequence[int],
    label_predictions: Sequence[int],
    masks: Optional[Sequence[int]] = None,
    micro: bool = False,
) -> NDArray[float32]`**
  - Location: line 159
  - Calculates the recall for a multi-classification problem using a confusion matrix.
    Args:
    ...

**`f1_score(
    label_gt: Sequence[int],
    label_predictions: Sequence[int],
    masks: Optional[Sequence[int]] = None,
    micro: bool = False,
    per_label: bool = True,
) -> NDArray[float32]`**
  - Location: line 191
  - Calculates the `F1` score for a multi-classification problem.
    Args:
    ...

#### deepdoctection/eval/registry.py

**`get_metric(name: str) -> MetricBase`**
  - Location: line 29
  - Returns an instance of a metric with a given name.
    Args:
    ...

#### deepdoctection/eval/tedsmetric.py

**`teds_metric(gt_list: list[str], predict_list: list[str], structure_only: bool) -> tuple[float, int]`**
  - Location: line 202
  - Computes tree edit distance score (TEDS) between the prediction and the ground truth of a batch of 
samples. The
    approach to measure similarity of tables by means of their html representation has been advocated in
    <https://arxiv.org/abs/1911.10683>
    ...

#### deepdoctection/extern/d2detect.py

**`d2_predict_image(
    np_img: PixelValues,
    predictor: nn.Module,
    resizer: InferenceResize,
    nms_thresh_class_agnostic: float,
) -> list[DetectionResult]`**
  - Location: line 73
  - Run detection on one image. It will also handle the preprocessing internally which is using a custom 
resizing
    within some bounds.
    ...

**`d2_jit_predict_image(
    np_img: PixelValues, d2_predictor: nn.Module, resizer: InferenceResize, nms_thresh_class_agnostic: float
) -> list[DetectionResult]`**
  - Location: line 112
  - Run detection on an image using Torchscript. It will also handle the preprocessing internally which
    is using a custom resizing within some bounds. Moreover, and different from the setting where D2 is used
    it will also handle the resizing of the bounding box coords to the original image size.
    ...

#### deepdoctection/extern/doctrocr.py

**`auto_select_lib_for_doctr() -> Literal["PT", "TF"]`**
  - Location: line 99
  - Auto select the DL library from environment variables

**`doctr_predict_text_lines(
    np_img: PixelValues, predictor: DetectionPredictor, device: Union[torch.device, tf.device], lib: 
Literal["TF", "PT"]
) -> list[DetectionResult]`**
  - Location: line 108
  - Generating text line `DetectionResult` based on DocTr `DetectionPredictor`.
    Args:
    ...

**`doctr_predict_text(
    inputs: list[tuple[str, PixelValues]],
    predictor: RecognitionPredictor,
    device: Union[torch.device, tf.device],
    lib: Literal["TF", "PT"],
) -> list[DetectionResult]`**
  - Location: line 139
  - Calls DocTr text recognition model on a batch of `np.array`s (text lines predicted from a text line 
detector) and
    returns the recognized text as `DetectionResult`
    ...

#### deepdoctection/extern/hfdetr.py

**`detr_predict_image(
    np_img: PixelValues,
    predictor: EligibleDetrModel,
    feature_extractor: DetrImageProcessor,
    device: torch.device,
    threshold: float,
    nms_threshold: float,
) -> list[DetectionResult]`**
  - Location: line 61
  - Calling predictor. Before, tensors must be transferred to the device where the model is loaded.
    Args:
    ...

#### deepdoctection/extern/hflayoutlm.py

**`get_tokenizer_from_model_class(model_class: str, use_xlm_tokenizer: bool) -> Any`**
  - Location: line 85
  - We do not use the tokenizer for a particular model that the transformer library provides. Thie mapping 
therefore
    returns the tokenizer that should be used for a particular model.
    ...

**`predict_token_classes_from_layoutlm(
    uuids: list[list[str]],
    input_ids: torch.Tensor,
    attention_mask: torch.Tensor,
    token_type_ids: torch.Tensor,
    boxes: torch.Tensor,
    tokens: list[list[str]],
    model: HfLayoutTokenModels,
    images: Optional[torch.Tensor] = None,
) -> list[TokenClassResult]`**
  - Location: line 135
  - Args:
    uuids: A list of uuids that correspond to a word that induces the resulting token
    input_ids: Token converted to ids to be taken from `LayoutLMTokenizer`
    ...

**`predict_sequence_classes_from_layoutlm(
    input_ids: torch.Tensor,
    attention_mask: torch.Tensor,
    token_type_ids: torch.Tensor,
    boxes: torch.Tensor,
    model: HfLayoutSequenceModels,
    images: Optional[torch.Tensor] = None,
) -> SequenceClassResult`**
  - Location: line 198
  - Args:
    input_ids: Token converted to ids to be taken from `LayoutLMTokenizer`
    attention_mask: The associated attention masks from padded sequences taken from `LayoutLMTokenizer`
    ...

#### deepdoctection/extern/hflm.py

**`predict_token_classes_from_lm(
    uuids: list[list[str]],
    input_ids: torch.Tensor,
    attention_mask: torch.Tensor,
    token_type_ids: torch.Tensor,
    tokens: list[list[str]],
    model: XLMRobertaForTokenClassification,
) -> list[TokenClassResult]`**
  - Location: line 61
  - Args:
    uuids: A list of uuids that correspond to a word that induces the resulting token
    input_ids: Token converted to ids to be taken from `LayoutLMTokenizer`
    ...

**`predict_sequence_classes_from_lm(
    input_ids: torch.Tensor,
    attention_mask: torch.Tensor,
    token_type_ids: torch.Tensor,
    model: XLMRobertaForSequenceClassification,
) -> SequenceClassResult`**
  - Location: line 105
  - Args:
    input_ids: Token converted to ids to be taken from `XLMRobertaTokenizer`
    attention_mask: The associated attention masks from padded sequences taken from `XLMRobertaTokenizer`
    ...

#### deepdoctection/extern/model.py

**`get_tp_weight_names(name: str) -> list[str]`**
  - Location: line 316
  - Given a path to some model weights it will return all file names according to TP naming convention
    Args:
    ...

**`print_model_infos(add_description: bool = True, add_config: bool = True, add_categories: bool = True) -> 
None`**
  - Location: line 335
  - Prints a table with all registered model profiles and some of their attributes (name, description, config 
and
    categories)
    ...

#### deepdoctection/extern/pt/nms.py

**`batched_nms(boxes: torch.Tensor, scores: torch.Tensor, idxs: torch.Tensor, iou_threshold: float) -> 
torch.Tensor`**
  - Location: line 31
  - Same as `torchvision.ops.boxes.batched_nms`, but with `float()`.
    Args:
    ...

#### deepdoctection/extern/pt/ptutils.py

**`get_torch_device(device: Optional[Union[str, torch.device]] = None) -> torch.device`**
  - Location: line 34
  - Select a device on which to load a model. The selection follows a cascade of priorities:
    If a device string is provided, it is used. If the environment variable `USE_CUDA` is set, a GPU is used.
    ...

#### deepdoctection/extern/tessocr.py

**`get_tesseract_version() -> Version`**
  - Location: line 118
  - Returns:
    Version of the installed tesseract engine.

**`image_to_angle(image: PixelValues) -> Mapping[str, str]`**
  - Location: line 146
  - Generating a tmp file and running Tesseract to get the orientation of the image.
    Args:
    ...

**`image_to_dict(image: PixelValues, lang: str, config: str) -> dict[str, list[Union[str, int, float]]]`**
  - Location: line 165
  - This is more or less `pytesseract.image_to_data` with a dict as returned value.
    What happens under the hood is:
    ...

**`tesseract_line_to_detectresult(detect_result_list: list[DetectionResult]) -> list[DetectionResult]`**
  - Location: line 223
  - Generating text line `DetectionResult`s based on Tesseract word grouping. It generates line bounding boxes
from
    word bounding boxes.
    ...

**`predict_text(np_img: PixelValues, supported_languages: str, text_lines: bool, config: str) -> 
list[DetectionResult]`**
  - Location: line 261
  - Calls Tesseract directly with some given configs. Requires Tesseract to be installed.
    Args:
    ...

**`predict_rotation(np_img: PixelValues) -> Mapping[str, str]`**
  - Location: line 305
  - Predicts the rotation of an image using the Tesseract OCR engine.
    Args:
    ...

#### deepdoctection/extern/texocr.py

**`predict_text(np_img: PixelValues, client: boto3.client, text_lines: bool) -> list[DetectionResult]`**
  - Location: line 63
  - Calls AWS Textract client (`detect_document_text`) and returns plain OCR results.
    AWS account required.
    ...

#### deepdoctection/extern/tp/tfutils.py

**`is_tfv2() -> bool`**
  - Location: line 38
  - Returns whether TensorFlow is operating in V2 mode.
    Returns:
    ...

**`disable_tfv2() -> bool`**
  - Location: line 58
  - Disables TensorFlow V2 mode.
    Returns:
    ...

**`disable_tp_layer_logging() -> None`**
  - Location: line 79
  - Disables tensorpack layer logging, if not already set.
    Example:
    ...

**`get_tf_device(device: Optional[Union[str, tf.device]] = None) -> tf.device`**
  - Location: line 91
  - Selects a device on which to load a model. The selection follows a cascade of priorities:
    - If a `device` string is provided, it is used. If the string is "cuda" or "GPU", the first GPU is used.
    ...

#### deepdoctection/extern/tp/tpfrcnn/common.py

**`polygons_to_mask(polys, height, width, intersect=False)`**
  - Location: line 64
  - Convert polygons to binary masks.
    :param polys: a list of nx2 float array. Each array contains many (x, y) coordinates.#
    ...

**`clip_boxes(boxes, shape)`**
  - Location: line 83
  - :param boxes: (...)x4, float
    :param shape: h, w

**`filter_boxes_inside_shape(boxes, shape)`**
  - Location: line 98
  - :param boxes: (nx4), float
    :param shape: (h, w)
    ...

**`np_iou(box_a, box_b)`**
  - Location: line 115
  - np iou

#### deepdoctection/extern/tp/tpfrcnn/config/config.py

**`model_frcnn_config(config: AttrDict, categories: Mapping[int, TypeOrStr], print_summary: bool = True) -> 
None`**
  - Location: line 228
  - Sanity checks for Tensorpack Faster-RCNN config settings, where the focus lies on the model for 
predicting.
    It will update the config instance.
    ...

**`train_frcnn_config(config: AttrDict) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]], int]`**
  - Location: line 277
  - Enhances the config instance by some parameters which are necessary for setting up the training
    Run some sanity checks, and populate some configs from others
    ...

#### deepdoctection/extern/tp/tpfrcnn/modeling/backbone.py

**`GroupNorm(x, group=32, gamma_initializer=None)`**
  - Location: line 33
  - More code that reproduces the paper can be found at <https://github.com/ppwwyyxx/GroupNorm-reproduce/>.

**`freeze_affine_getter(getter, *args, **kwargs)`**
  - Location: line 65
  - Custom getter to freeze affine params inside bn

**`maybe_reverse_pad(cfg, topleft, bottomright)`**
  - Location: line 80
  - Returning chosen pad mode

**`backbone_scope(cfg, freeze)`**
  - Location: line 90
  - Context scope for setting up the backbone
    :param cfg: The configuration instance as an AttrDict
    ...

**`image_preprocess(image, cfg)`**
  - Location: line 125
  - Preprocessing image by rescaling.
    :param image: tf.Tensor
    ...

**`get_norm(cfg, zero_init=False)`**
  - Location: line 145
  - Return a norm with respect to config.
    :param cfg: config
    ...

**`resnet_shortcut(l, n_out, stride, activation=None)`**
  - Location: line 164
  - Defining the skip connection in bottleneck
    :param l: tf.Tensor
    ...

**`resnet_bottleneck(l, ch_out, stride, cfg)`**
  - Location: line 182
  - Defining the bottleneck for Resnet50/101 backbones
    :param l: tf.Tensor
    ...

**`resnext32x4d_bottleneck(l, ch_out, stride, cfg)`**
  - Location: line 208
  - Defining Resnext bottleneck <https://arxiv.org/abs/1611.05431>
    :param l: tf.Tensor
    ...

**`resnet_group(name, l, block_func, features, count, stride, cfg)`**
  - Location: line 226
  - Defining resnet groups
    :param name: name of group
    ...

**`resnet_fpn_backbone(image, cfg)`**
  - Location: line 246
  - Setup of the full FPN backbone.
    :param image: tf.Tensor
    ...

#### deepdoctection/extern/tp/tpfrcnn/modeling/model_box.py

**`clip_boxes(boxes, window, name=None)`**
  - Location: line 28
  - clip boxes
    :param boxes: nx4, xyxy
    ...

**`decode_bbox_target(box_predictions, anchors, preproc_max_size)`**
  - Location: line 44
  - Decode bbox target
    :param box_predictions: (..., 4), logits
    ...

**`encode_bbox_target(boxes, anchors)`**
  - Location: line 74
  - Encode bbox target
    :param boxes: (..., 4), float32
    ...

**`crop_and_resize(image, boxes, box_ind, crop_size, pad_border=True)`**
  - Location: line 101
  - Crop and resize
    :param image: NCHW
    ...

**`roi_align(feature_map, boxes, resolution)`**
  - Location: line 168
  - Roi align
    :param feature_map: 1xCxHxW
    ...

#### deepdoctection/extern/tp/tpfrcnn/modeling/model_fpn.py

**`fpn_model(features, fpn_num_channels, fpn_norm)`**
  - Location: line 40
  - Feature Pyramid Network model
    :param features: ResNet features c2-c5 [tf.Tensor]
    ...

**`fpn_map_rois_to_levels(boxes)`**
  - Location: line 102
  - Assign boxes to level 2~5. Be careful that the returned tensor could be empty.
    :param boxes: (nx4)
    ...

**`multilevel_roi_align(features, rcnn_boxes, resolution, fpn_anchor_strides)`**
  - Location: line 130
  - multilevel roi align
    ...

**`multilevel_rpn_losses(
    multilevel_anchors, multilevel_label_logits, multilevel_box_logits, rpn_batch_per_im, fpn_anchor_strides
)`**
  - Location: line 162
  - multilevel rpn losses
    :param multilevel_anchors: #lvl RPNAnchors
    ...

**`generate_fpn_proposals(
    multilevel_pred_boxes,
    multilevel_label_logits,
    image_shape2d,
    fpn_anchor_strides,
    fpn_proposal_mode,
    rpn_train_per_level_nms_topk,
    rpn_per_level_nms_topk,
    rpn_min_size,
    rpn_proposal_nms_thresh,
    rpn_train_pre_nms_top_k,
    rpn_test_pre_nms_top_k,
    rpn_train_post_nms_top_k,
    rpn_test_post_nms_top_k,
)`**
  - Location: line 202
  - generate fpn proposals
    :param multilevel_pred_boxes: #lvl HxWxAx4 boxes
    ...

**`get_all_anchors_fpn(*, strides, sizes, ratios, max_size)`**
  - Location: line 291
  - get all anchors for fpn
    :return: each anchors is a SxSx NUM_ANCHOR_RATIOS x4 array. [anchors]

#### deepdoctection/extern/tp/tpfrcnn/modeling/model_frcnn.py

**`proposal_metrics(iou)`**
  - Location: line 36
  - Add summaries for RPN proposals.
    :param iou: nxm, #proposal x #gt

**`sample_fast_rcnn_targets(boxes, gt_boxes, gt_labels, frcnn_fg_thresh, frcnn_batch_per_im, 
frcnn_fg_ratio)`**
  - Location: line 58
  - Sample some boxes from all proposals for training.
    #fg is guaranteed to be > 0, because ground truth boxes will be added as proposals.
    ...

**`fastrcnn_outputs(feature, num_categories, class_agnostic_regression=False)`**
  - Location: line 133
  - Fast RCNN outputs
    :param feature:(any shape)
    ...

**`fastrcnn_losses(labels, label_logits, fg_boxes, fg_box_logits)`**
  - Location: line 158
  - Fast RCNN losses
    :param labels: n,
    ...

**`fastrcnn_predictions(boxes, scores, output_result_score_thresh, output_results_per_im, 
output_frcnn_nms_thresh)`**
  - Location: line 206
  - Generate final results from predictions of all proposals.
    :param scores: nx#class
    ...

**`nms_post_processing(boxes, scores, labels, output_results_per_im, output_nms_thresh_class_agnostic)`**
  - Location: line 240
  - Final results from Fast RCNN are calculated from performing nms per class. For layout detection 
overlapping boxes
    with different categories are not possible, so this post-processing steps is doing a final nms calculation
over all
    classes.
    ...

**`fastrcnn_2fc_head(feature, cfg)`**
  - Location: line 267
  - FRCNN head with two fully connected heads
    :param feature: (any shape)
    ...

**`fastrcnn_Xconv1fc_head(feature, num_convs, norm=None, **kwargs)`**
  - Location: line 285
  - FRCNN head with x convolutional and one fully connected head
    :param  feature: The configuration instance as an AttrDict (NCHW)
    ...

**`fastrcnn_4conv1fc_head(*args, **kwargs)`**
  - Location: line 320
  - FRCNN head with four convolutional and one fully connected head

**`fastrcnn_4conv1fc_gn_head(*args, **kwargs)`**
  - Location: line 327
  - FRCNN head with four convolutional and one fully connected group normalized head

#### deepdoctection/extern/tp/tpfrcnn/modeling/model_mrcnn.py

**`maskrcnn_loss(mask_logits, fg_labels, fg_target_masks)`**
  - Location: line 32
  - :param mask_logits: #fg x #category xhxw
    :param fg_labels: #fg, in 1~#class, int64
    :param fg_target_masks: #fgxhxw, float32

**`maskrcnn_upXconv_head(feature, num_category, num_convs, norm=None, **kwargs)`**
  - Location: line 70
  - :param feature: size is 7 in C4 models and 14 in FPN models. (NxCx s x s)
    :param num_category: number of categories
    :param num_convs: number of convolution layers
    ...

**`maskrcnn_up4conv_head(*args, **kwargs)`**
  - Location: line 104
  - maskrcnn four up-sampled convolutional layers

**`maskrcnn_up4conv_gn_head(*args, **kwargs)`**
  - Location: line 111
  - maskrcnn four up-sampled group normalized convolutional layers

**`unpackbits_masks(masks)`**
  - Location: line 118
  - :param masks: (Tensor) uint8 Tensor of shape N, H, W. The last dimension is packed bits.
    :return: (Tensor) bool Tensor of shape N, H, 8*W.
    ...

#### deepdoctection/extern/tp/tpfrcnn/modeling/model_rpn.py

**`rpn_head(feature_map, channel, num_anchors)`**
  - Location: line 35
  - RPN head
    :return: label_logits: fHxfWxNA
    ...

**`rpn_losses(anchor_labels, anchor_boxes, label_logits, box_logits, rpn_batch_per_im)`**
  - Location: line 60
  - RPN losses
    :param anchor_labels: fHxfWxNA
    ...

**`generate_rpn_proposals(
    boxes, scores, img_shape, rpn_min_size, rpn_proposal_nms_thres, pre_nms_top_k, post_nms_top_k=None
)`**
  - Location: line 128
  - Sample RPN proposals by the following steps:
    1. Pick top k1 by scores
    2. NMS them
    ...

**`get_all_anchors(*, stride, sizes, ratios, max_size)`**
  - Location: line 179
  - Get all anchors in the largest possible image, shifted, float box
    :param stride: the stride of anchors.
    ...

#### deepdoctection/extern/tp/tpfrcnn/predict.py

**`tp_predict_image(
    np_img: np.ndarray,
    predictor: OfflinePredictor,
    preproc_short_edge_size: int,
    preproc_max_size: int,
    mrcnn_accurate_paste: bool,
) -> List[DetectionResult]`**
  - Location: line 94
  - Run detection on one image, using the TF callable. This function should handle the preprocessing 
internally.
    :param np_img: ndarray
    ...

#### deepdoctection/extern/tp/tpfrcnn/preproc.py

**`augment(dp: JsonDict, imgaug_list: List[ImageAugmentor], add_mask: bool) -> JsonDict`**
  - Location: line 35
  - Augment an image according to a list of augmentors.
    :param dp: A dict with "image","gt_boxes","gt_labels"
    ...

**`anchors_and_labels(
    dp: JsonDict,
    anchor_strides: Tuple[int],
    anchor_sizes: Tuple[int],
    anchor_ratios: Tuple[int],
    max_size: int,
    batch_per_image: int,
    front_ground_ratio: float,
    positive_anchor_threshold: float,
    negative_anchor_threshold: float,
    crowd_overlap_threshold: float,
) -> Optional[JsonDict]`**
  - Location: line 69
  - Generating anchors and labels.
    :param dp: datapoint image
    ...

**`get_multilevel_rpn_anchor_input(
    image: np.array,
    boxes: np.array,
    is_crowd: np.array,
    anchor_strides: Tuple[int],
    anchor_sizes: Tuple[int],
    anchor_ratios: Tuple[int],
    max_size: float,
    batch_per_image: int,
    front_ground_ratio: float,
    positive_anchor_threshold: float,
    negative_anchor_threshold: float,
    crowd_overlap_threshold: float,
) -> List[Tuple[Any, Any]]`**
  - Location: line 128
  - Generates multilevel rpn anchors
    :param image: an image
    ...

**`get_anchor_labels(
    anchors: PixelValues,
    gt_boxes: PixelValues,
    crowd_boxes: PixelValues,
    batch_per_image: int,
    front_ground_ratio: float,
    positive_anchor_threshold: float,
    negative_anchor_threshold: float,
    crowd_overlap_threshold: float,
) -> (PixelValues, PixelValues)`**
  - Location: line 216
  - Label each anchor as fg/bg/ignore.
    :param batch_per_image: total (across FPN levels) number of anchors that are marked valid
    ...

#### deepdoctection/extern/tp/tpfrcnn/utils/box_ops.py

**`area(boxes)`**
  - Location: line 33
  - :param boxes: nx4 floatbox
    :return: n

**`pairwise_intersection(boxlist1, boxlist2)`**
  - Location: line 45
  - Compute pairwise intersection areas between boxes.
    :param boxlist1: Nx4 floatbox
    ...

**`pairwise_iou(boxlist1, boxlist2)`**
  - Location: line 66
  - Computes pairwise intersection-over-union between box collections.
    :param boxlist1: Nx4 floatbox
    ...

#### deepdoctection/extern/tp/tpfrcnn/utils/np_box_ops.py

**`area(boxes)`**
  - Location: line 32
  - Computes area of boxes.
    :param boxes: Numpy array with shape [N, 4] holding N boxes
    ...

**`intersection(boxes1, boxes2)`**
  - Location: line 43
  - Compute pairwise intersection areas between boxes.
    :param boxes1: a numpy array with shape [N, 4] holding N boxes
    ...

**`iou(boxes1, boxes2)`**
  - Location: line 69
  - Computes pairwise intersection-over-union between box collections.
    :param boxes1: a numpy array with shape [N, 4] holding N boxes.
    ...

**`ioa(boxes1, boxes2)`**
  - Location: line 86
  - Computes pairwise intersection-over-area between box collections.
    Intersection-over-area (ioa) between two boxes box1 and box2 is defined as
    ...

#### deepdoctection/mapper/cats.py

**`cat_to_sub_cat(
    dp: Image,
    categories_dict_names_as_key: Optional[dict[TypeOrStr, int]] = None,
    cat_to_sub_cat_dict: Optional[dict[TypeOrStr, TypeOrStr]] = None,
) -> Image`**
  - Location: line 32
  - Replace some categories with sub categories.
    Example:
    ...

**`re_assign_cat_ids(
    dp: Image,
    categories_dict_name_as_key: Optional[dict[TypeOrStr, int]] = None,
    cat_to_sub_cat_mapping: Optional[Mapping[ObjectTypes, Any]] = None,
) -> Image`**
  - Location: line 85
  - Re-assigning `category_id`s is sometimes necessary to align with categories of the `DatasetCategories` .
    Example:
    ...

**`filter_cat(
    dp: Image, categories_as_list_filtered: list[TypeOrStr], categories_as_list_unfiltered: list[TypeOrStr]
) -> Image`**
  - Location: line 148
  - Filters category annotations based on the on a list of categories to be kept and a list of all possible
    category names that might be available in dp.
    ...

**`filter_summary(
    dp: Image,
    sub_cat_to_sub_cat_names_or_ids: Mapping[TypeOrStr, Sequence[TypeOrStr]],
    mode: Literal["name", "id", "value"] = "name",
) -> Optional[Image]`**
  - Location: line 180
  - Filters datapoints with given summary conditions. If several conditions are given, it will filter out 
datapoints
    that do not satisfy all conditions.
    ...

**`image_to_cat_id(
    dp: Image,
    category_names: Optional[Union[TypeOrStr, Sequence[TypeOrStr]]] = None,
    sub_categories: Optional[Union[Mapping[TypeOrStr, TypeOrStr], Mapping[TypeOrStr, Sequence[TypeOrStr]]]] = 
None,
    summary_sub_category_names: Optional[Union[TypeOrStr, Sequence[TypeOrStr]]] = None,
    id_name_or_value: Literal["id", "name", "value"] = "id",
) -> tuple[dict[TypeOrStr, list[int]], str]`**
  - Location: line 213
  - Extracts all category_ids, sub category information or summary sub category information with given names 
into a
    defaultdict. This mapping is useful when running evaluation with e.g. an accuracy metric.
    ...

**`remove_cats(
    dp: Image,
    category_names: Optional[Union[TypeOrStr, Sequence[TypeOrStr]]] = None,
    sub_categories: Optional[Union[Mapping[TypeOrStr, TypeOrStr], Mapping[TypeOrStr, Sequence[TypeOrStr]]]] = 
None,
    relationships: Optional[Union[Mapping[TypeOrStr, TypeOrStr], Mapping[TypeOrStr, Sequence[TypeOrStr]]]] = 
None,
    summary_sub_categories: Optional[Union[TypeOrStr, Sequence[TypeOrStr]]] = None,
) -> Image`**
  - Location: line 336
  - Remove categories according to given category names or sub category names. Note that these will change the
container
    in which the objects are stored.
    ...

**`add_summary(dp: Image, categories: Mapping[int, ObjectTypes]) -> Image`**
  - Location: line 401
  - Adding a summary with the number of categories in an image.
    Args:
    ...

#### deepdoctection/mapper/cocostruct.py

**`coco_to_image(
    dp: CocoDatapointDict,
    categories: dict[int, ObjectTypes],
    load_image: bool,
    filter_empty_image: bool,
    fake_score: bool,
    coarse_mapping: Optional[Mapping[int, int]] = None,
    coarse_sub_cat_name: Optional[ObjectTypes] = None,
) -> Optional[Image]`**
  - Location: line 35
  - Maps a dataset in `COCO` format that has been serialized to image format.
    This serialized input requirements hold when a `COCO` style sheet is loaded via `SerializerCoco.load`.
    ...

**`image_to_coco(dp: Image) -> tuple[JsonDict, list[JsonDict]]`**
  - Location: line 122
  - Converts an image back into the `COCO` format.
    As images and annotations are separated, it will return a dict with the image information and one for its
    ...

#### deepdoctection/mapper/d2struct.py

**`image_to_d2_frcnn_training(
    dp: Image,
    add_mask: bool = False,
    category_names: Optional[Union[TypeOrStr, Sequence[TypeOrStr]]] = None,
) -> Optional[Detectron2Dict]`**
  - Location: line 50
  - Maps an image to a standard dataset dict as described in
    <https://detectron2.readthedocs.io/en/latest/tutorials/datasets.html>. It further checks if the image is 
physically
    available, for otherwise the annotation will be filtered.
    ...

**`pt_nms_image_annotations_depr(
    anns: Sequence[ImageAnnotation], threshold: float, image_id: Optional[str] = None, prio: str = ""
) -> Sequence[str]`**
  - Location: line 109
  - Processing given image annotations through NMS. This is useful, if you want to supress some specific image
    annotation, e.g. given by name or returned through different predictors. This is the pt version, for tf 
check
    `mapper.tpstruct`
    ...

**`pt_nms_image_annotations(
    anns: Sequence[ImageAnnotation], threshold: float, image_id: Optional[str] = None, prio: str = ""
) -> Sequence[str]`**
  - Location: line 157
  - Processes given image annotations through NMS (Non-Maximum Suppression). Useful for suppressing specific 
image
    annotations, e.g., given by name or returned through different predictors. This is the pt version, for tf 
check
    `mapper.tpstruct`
    ...

**`to_wandb_image(
    dp: Image,
    categories: Mapping[int, TypeOrStr],
    sub_categories: Optional[Mapping[int, TypeOrStr]] = None,
    cat_to_sub_cat: Optional[Mapping[ObjectTypes, ObjectTypes]] = None,
) -> tuple[str, Wbimage]`**
  - Location: line 246
  - Converts a deepdoctection `Image` into a `W&B` image.
    Args:
    ...

#### deepdoctection/mapper/hfstruct.py

**`image_to_hf_detr_training(
    dp: Image,
    add_mask: bool = False,
    category_names: Optional[Union[TypeOrStr, Sequence[Union[TypeOrStr]]]] = None,
) -> Optional[JsonDict]`**
  - Location: line 43
  - Maps an `image` to a detr input datapoint `dict`, that, after collating, can be used for training.
    Args:
    ...

#### deepdoctection/mapper/laylmstruct.py

**`image_to_raw_layoutlm_features(
    dp: Image,
    dataset_type: Optional[Literal["sequence_classification", "token_classification"]] = None,
    input_width: int = 1000,
    input_height: int = 1000,
    image_width: int = 1000,
    image_height: int = 1000,
    color_mode: Literal["BGR", "RGB"] = "BGR",
    pixel_mean: Optional[npt.NDArray[np.float32]] = None,
    pixel_std: Optional[npt.NDArray[np.float32]] = None,
    use_token_tag: bool = True,
    segment_positions: Optional[Union[LayoutType, Sequence[LayoutType]]] = None,
) -> Optional[RawLayoutLMFeatures]`**
  - Location: line 78
  - Maps a datapoint into an intermediate format for LayoutLM. Features are provided in a dict and this 
mapping
    can be used for sequence or token classification as well as for inference. To generate input features for 
the model
    please use `raw_features_to_layoutlm_features`.
    ...

**`layoutlm_features_to_pt_tensors(features: LayoutLMFeatures) -> LayoutLMFeatures`**
  - Location: line 211
  - Converts a list of floats to PyTorch tensors.
    Args:
    ...

**`raw_features_to_layoutlm_features(
    raw_features: Union[RawLayoutLMFeatures, RawLMFeatures, list[Union[RawLayoutLMFeatures, RawLMFeatures]]],
    tokenizer: PreTrainedTokenizerFast,
    padding: Literal["max_length", "do_not_pad", "longest"] = "max_length",
    truncation: bool = True,
    return_overflowing_tokens: bool = False,
    return_tensors: Optional[Literal["pt"]] = None,
    remove_columns_for_training: bool = False,
    sliding_window_stride: int = 0,
    max_batch_size: int = 0,
    remove_bounding_boxes: bool = False,
) -> LayoutLMFeatures`**
  - Location: line 415
  - Maps raw features to tokenized input sequences for LayoutLM models.
    Args:
    ...

**`image_to_layoutlm_features(
    dp: Image,
    tokenizer: PreTrainedTokenizerFast,
    padding: Literal["max_length", "do_not_pad", "longest"] = "max_length",
    truncation: bool = True,
    return_overflowing_tokens: bool = False,
    return_tensors: Optional[Literal["pt"]] = "pt",
    input_width: int = 1000,
    input_height: int = 1000,
    image_width: int = 1000,
    image_height: int = 1000,
    color_mode: Literal["BGR", "RGB"] = "BGR",
    pixel_mean: Optional[npt.NDArray[np.float32]] = None,
    pixel_std: Optional[npt.NDArray[np.float32]] = None,
    segment_positions: Optional[Union[LayoutType, Sequence[LayoutType]]] = None,
    sliding_window_stride: int = 0,
) -> Optional[LayoutLMFeatures]`**
  - Location: line 666
  - Mapping function to generate LayoutLM features from `Image` to be used for inference in a pipeline 
component.
    `LanguageModelPipelineComponent` has a positional argument `mapping_to_lm_input_func` that must be chosen
    with respect to the language model chosen. This mapper is devoted to generating features for LayoutLM. It 
will be
    ...

**`image_to_raw_lm_features(
    dp: Image,
    dataset_type: Optional[Literal["sequence_classification", "token_classification"]] = None,
    use_token_tag: bool = True,
    text_container: Optional[LayoutType] = LayoutType.WORD,
    floating_text_block_categories: Optional[Sequence[LayoutType]] = None,
    include_residual_text_container: bool = False,
) -> Optional[RawLMFeatures]`**
  - Location: line 763
  - Maps a datapoint into an intermediate format for BERT-like models. Features are provided in a dict and
    this mapping can be used for sequence or token classification as well as for inference. To generate input 
features
    for the model, please use `raw_features_to_layoutlm_features`.
    ...

**`image_to_lm_features(
    dp: Image,
    tokenizer: PreTrainedTokenizerFast,
    padding: Literal["max_length", "do_not_pad", "longest"] = "max_length",
    truncation: bool = True,
    return_overflowing_tokens: bool = False,
    return_tensors: Optional[Literal["pt"]] = "pt",
    sliding_window_stride: int = 0,
    text_container: Optional[LayoutType] = LayoutType.WORD,
    floating_text_block_categories: Optional[Sequence[LayoutType]] = None,
    include_residual_text_container: bool = False,
) -> Optional[LayoutLMFeatures]`**
  - Location: line 830
  - Mapping function to generate LayoutLM features from `Image` to be used for inference in a pipeline 
component.
    `LanguageModelPipelineComponent` has a positional argument `mapping_to_lm_input_func` that must be chosen
    with respect to the language model chosen. This mapper is devoted to generating features for LayoutLM. It 
will be
    ...

#### deepdoctection/mapper/maputils.py

**`curry(func: Callable[..., T]) -> Callable[..., Callable[[DP], T]]`**
  - Location: line 161
  - Decorator for converting functions that map
    ```python
    ...

**`maybe_get_fake_score(add_fake_score: bool) -> Optional[float]`**
  - Location: line 195
  - Returns a fake score, if `add_fake_score` is `True`. Will otherwise return `None`.
    Args:
    ...

#### deepdoctection/mapper/match.py

**`match_anns_by_intersection(
    dp: Image,
    matching_rule: Literal["iou", "ioa"],
    threshold: float,
    use_weighted_intersections: bool = False,
    parent_ann_category_names: Optional[Union[TypeOrStr, Sequence[TypeOrStr]]] = None,
    child_ann_category_names: Optional[Union[TypeOrStr, Sequence[TypeOrStr]]] = None,
    parent_ann_ids: Optional[Union[Sequence[str], str]] = None,
    child_ann_ids: Optional[Union[str, Sequence[str]]] = None,
    parent_ann_service_ids: Optional[Union[str, Sequence[str]]] = None,
    child_ann_service_ids: Optional[Union[str, Sequence[str]]] = None,
    max_parent_only: bool = False,
) -> tuple[Any, Any, Sequence[ImageAnnotation], Sequence[ImageAnnotation]]`**
  - Location: line 35
  - Generates an iou/ioa-matrix for `parent_ann_categories` and `child_ann_categories` and returns pairs of 
child/parent
    indices that are above some intersection threshold. It will also return a list of all pre-selected parent 
and child
    annotations.
    ...

**`match_anns_by_distance(
    dp: Image,
    parent_ann_category_names: Optional[Union[TypeOrStr, Sequence[TypeOrStr]]] = None,
    child_ann_category_names: Optional[Union[TypeOrStr, Sequence[TypeOrStr]]] = None,
    parent_ann_ids: Optional[Union[Sequence[str], str]] = None,
    child_ann_ids: Optional[Union[str, Sequence[str]]] = None,
    parent_ann_service_ids: Optional[Union[str, Sequence[str]]] = None,
    child_ann_service_ids: Optional[Union[str, Sequence[str]]] = None,
) -> list[tuple[ImageAnnotation, ImageAnnotation]]`**
  - Location: line 167
  - Generates pairs of parent and child annotations by calculating the euclidean distance between the centers 
of the
    parent and child bounding boxes. It will return the closest child for each parent.
    ...

#### deepdoctection/mapper/misc.py

**`to_image(
    dp: Union[str, Mapping[str, Union[str, bytes]]],
    dpi: Optional[int] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> Optional[Image]`**
  - Location: line 41
  - Maps an input from `dataflow.SerializerFiles` or similar to an `Image`.
    Args:
    ...

**`maybe_load_image(dp: Image) -> Image`**
  - Location: line 107
  - If `image` is `None`, loads the image.
    Args:
    ...

**`maybe_remove_image(dp: Image) -> Image`**
  - Location: line 125
  - Removes `image` if a location is provided.
    Args:
    ...

**`maybe_remove_image_from_category(dp: Image, category_names: Optional[Union[str, Sequence[str]]] = None) -> 
Image`**
  - Location: line 142
  - Removes `image` from image annotation for some `category_name`s.
    Args:
    ...

**`image_ann_to_image(dp: Image, category_names: Union[str, list[str]], crop_image: bool = True) -> Image`**
  - Location: line 166
  - Adds `image` to annotations with given category names.
    Args:
    ...

**`maybe_ann_to_sub_image(
    dp: Image, category_names_sub_image: Union[str, list[str]], category_names: Union[str, list[str]], 
add_summary: bool
) -> Image`**
  - Location: line 187
  - Assigns to sub image with given category names all annotations with given category names whose bounding 
box lies
    within the bounding box of the sub image.
    ...

**`xml_to_dict(dp: JsonDict, xslt_obj: etree.XSLT) -> JsonDict`**
  - Location: line 215
  - Converts an XML object into a dict using an XSL style sheet.
    Example:
    ...

#### deepdoctection/mapper/pascalstruct.py

**`pascal_voc_dict_to_image(
    dp: JsonDict,
    categories_name_as_key: dict[str, int],
    load_image: bool,
    filter_empty_image: bool,
    fake_score: bool,
    category_name_mapping: Optional[dict[str, str]] = None,
) -> Optional[Image]`**
  - Location: line 35
  - Maps a dataset in a structure equivalent to the PASCAL VOC annotation style to the `Image` format.
    Args:
    ...

#### deepdoctection/mapper/prodigystruct.py

**`prodigy_to_image(
    dp: JsonDict,
    categories_name_as_key: Mapping[ObjectTypes, int],
    load_image: bool,
    fake_score: bool,
    path_reference_ds: Optional[PathLikeOrStr] = None,
    accept_only_answer: bool = False,
    category_name_mapping: Optional[Mapping[str, str]] = None,
) -> Optional[Image]`**
  - Location: line 34
  - Maps a datapoint of annotation structure from Prodigy database to an `Image` structure.
    Args:
    ...

**`image_to_prodigy(dp: Image, category_names: Optional[Sequence[ObjectTypes]] = None) -> JsonDict`**
  - Location: line 153
  - Transforms the normalized image representation of datasets into the format for visualizing the annotation
    components in Prodigy.
    ...

#### deepdoctection/mapper/pubstruct.py

**`tile_table(row_spans: Sequence[Sequence[int]], col_spans: Sequence[Sequence[int]]) -> list[list[int]]`**
  - Location: line 104
  - Tiles a table according to the row and column span scheme. A table can be represented as a list of lists, 
where
    each inner list has the same length. Each cell with a cell id can be located according to their row and 
column
    spans in that scheme.
    ...

**`row_col_cell_ids(tiling: list[list[int]]) -> list[tuple[int, int, int]]`**
  - Location: line 257
  - Infers absolute rows and columns for every cell from the tiling of a table.
    Args:
    ...

**`embedding_in_image(dp: Image, html: list[str], categories_name_as_key: dict[ObjectTypes, int]) -> Image`**
  - Location: line 276
  - Generating an image that resembles the output of an analyzer. The layout of the image is a table spanning 
the full
    page, i.e. there is one table image annotation. Moreover, the table annotation has an image, with cells as
image
    annotations.
    ...

**`nth_index(iterable: Iterable[str], value: str, n: int) -> Optional[int]`**
  - Location: line 321
  - Returns the position of the n-th string value in an iterable, e.g. a list.
    Args:
    ...

**`pub_to_image_uncur(  # pylint: disable=R0914
    dp: PubtabnetDict,
    categories_name_as_key: dict[ObjectTypes, int],
    load_image: bool,
    fake_score: bool,
    rows_and_cols: bool,
    dd_pipe_like: bool,
    is_fintabnet: bool,
    pubtables_like: bool,
) -> Optional[Image]`**
  - Location: line 335
  - Map a datapoint of annotation structure as given in the Pubtabnet dataset to an Image structure.
    <https://github.com/ibm-aur-nlp/PubTabNet>
    ...

#### deepdoctection/mapper/tpstruct.py

**`image_to_tp_frcnn_training(
    dp: Image,
    add_mask: bool = False,
    category_names: Optional[Union[TypeOrStr, Sequence[TypeOrStr]]] = None,
) -> Optional[JsonDict]`**
  - Location: line 39
  - Maps an `Image` to a dict to be consumed by Tensorpack Faster-RCNN bounding box detection.
    Note:
    ...

**`tf_nms_image_annotations(
    anns: Sequence[ImageAnnotation], threshold: float, image_id: Optional[str] = None, prio: str = ""
) -> Sequence[str]`**
  - Location: line 92
  - Processes given `ImageAnnotation` through `NMS`.
    This is useful if you want to suppress some specific image annotation, e.g., given by name or returned 
through
    ...

#### deepdoctection/mapper/xfundstruct.py

**`xfund_to_image(
    dp: FunsdDict,
    load_image: bool,
    fake_score: bool,
    categories_dict_name_as_key: Mapping[ObjectTypes, int],
    token_class_names_mapping: Mapping[str, str],
    ner_token_to_id_mapping: Mapping[ObjectTypes, Mapping[ObjectTypes, Mapping[ObjectTypes, int]]],
) -> Optional[Image]`**
  - Location: line 44
  - Maps a datapoint of annotation structure as given from Xfund or Funsd dataset into an `Image` structure.
    Args:
    ...

#### deepdoctection/pipe/layout.py

**`skip_if_category_or_service_extracted(
    dp: Image,
    category_names: Optional[Union[str, Sequence[ObjectTypes]]] = None,
    service_ids: Optional[Union[str, Sequence[str]]] = None,
) -> bool`**
  - Location: line 38
  - Skip the processing of the pipeline component if the category or service is already extracted.
    Example:
    ...

#### deepdoctection/pipe/refine.py

**`tiles_to_cells(dp: Image, table: ImageAnnotation) -> list[tuple[tuple[int, int], str]]`**
  - Location: line 50
  - Creates a table parquet by dividing a table into a tile parquet with the number of rows x number of 
columns tiles.
    Each tile is assigned a list of cell ids that are occupied by the cell. No cells but one or more cells can
be
    assigned per tile.
    ...

**`connected_component_tiles(
    tile_to_cell_list: list[tuple[tuple[int, int], str]]
) -> tuple[list[set[tuple[int, int]]], DefaultDict[tuple[int, int], list[str]]]`**
  - Location: line 83
  - Assigns bricks to their cell occupancy, inducing a graph with bricks as nodes and cell edges. Cells that 
lie on
    top of several bricks connect the underlying bricks. The graph generated is usually multiple connected. 
Determines
    the related components and the tile/cell ids assignment.
    ...

**`generate_rectangle_tiling(connected_components_tiles: list[set[tuple[int, int]]]) -> list[set[tuple[int, 
int]]]`**
  - Location: line 175
  - Combines connected components so that all cells above them form a rectangular scheme. Ensures that all 
tiles are
    combined in such a way that all cells above them combine to form a rectangular tiling.
    ...

**`rectangle_cells(
    rectangle_tiling: list[set[tuple[int, int]]], tile_to_cell_dict: DefaultDict[tuple[int, int], list[str]]
) -> list[set[str]]`**
  - Location: line 197
  - Determines all cells that are located above combined connected components and form a rectangular scheme.
    Args:
    ...

**`generate_html_string(table: ImageAnnotation, cell_names: Sequence[ObjectTypes]) -> list[str]`**
  - Location: line 338
  - Generates an HTML representation of a table using table segmentation by row number, column number, etc.
    Note:
    ...

#### deepdoctection/pipe/segment.py

**`choose_items_by_iou(
    dp: Image,
    item_proposals: list[ImageAnnotation],
    iou_threshold: float,
    above_threshold: bool = True,
    reference_item_proposals: Optional[list[ImageAnnotation]] = None,
) -> Image`**
  - Location: line 74
  - Deactivate image annotations that have `ious` with each other above some threshold. It will deactivate an 
annotation
    that has `iou` above some threshold with another annotation and that has a lesser score.
    ...

**`stretch_item_per_table(
    dp: Image,
    table: ImageAnnotation,
    row_name: str,
    col_name: str,
    remove_iou_threshold_rows: float,
    remove_iou_threshold_cols: float,
) -> Image`**
  - Location: line 133
  - Stretch rows horizontally and stretch columns vertically. Since the predictor usually does not predict a 
box for
    lines across the entire width of the table, lines are stretched from the left to the right edge of the 
table if the
    y coordinates remain the same. Columns between the top and bottom of the table can be stretched in an 
analogous way.
    ...

**`tile_tables_with_items_per_table(
    dp: Image, table: ImageAnnotation, item_name: ObjectTypes, stretch_rule: Literal["left", "equal"] = "left"
) -> Image`**
  - Location: line 337
  - Tiling a table with items (i.e. rows or columns). To ensure that every position in a table can be assigned
to a row
    or column, rows are stretched vertically and columns horizontally. The stretching takes place according to
ascending
    coordinate axes. The first item is stretched to the top or right-hand edge of the table. The next item 
down or to
    ...

**`stretch_items(
    dp: Image,
    table_name: ObjectTypes,
    row_name: ObjectTypes,
    col_name: ObjectTypes,
    remove_iou_threshold_rows: float,
    remove_iou_threshold_cols: float,
) -> Image`**
  - Location: line 379
  - Stretch rows and columns from item detector to full table length and width. See `stretch_item_per_table`.
    Args:
    ...

**`segment_table(
    dp: Image,
    table: ImageAnnotation,
    item_names: Union[ObjectTypes, Sequence[ObjectTypes]],
    cell_names: Union[ObjectTypes, Sequence[ObjectTypes]],
    segment_rule: Literal["iou", "ioa"],
    threshold_rows: float,
    threshold_cols: float,
) -> list[SegmentationResult]`**
  - Location: line 428
  - Segments a table, i.e. produces for each cell a `SegmentationResult`. It uses numbered rows and columns 
that have
    to be predicted by an appropriate detector. For calculating row and row spans it first infers the `iou` of
a cell
    with all rows. All `ious` with rows above `iou_threshold_rows` will induce the cell to have that row 
number. As
    ...

**`create_intersection_cells(
    rows: Sequence[ImageAnnotation],
    cols: Sequence[ImageAnnotation],
    table_annotation_id: str,
    sub_item_names: Sequence[ObjectTypes],
) -> tuple[Sequence[DetectionResult], Sequence[SegmentationResult]]`**
  - Location: line 523
  - Given rows and columns with row- and column number sub categories, create a list of `DetectionResult` and
    `SegmentationResult` as intersection of all their intersection rectangles.
    ...

**`header_cell_to_item_detect_result(
    dp: Image,
    table: ImageAnnotation,
    item_name: ObjectTypes,
    item_header_name: ObjectTypes,
    segment_rule: Literal["iou", "ioa"],
    threshold: float,
) -> list[ItemHeaderResult]`**
  - Location: line 579
  - Match header cells to items (rows or columns) based on intersection-over-union (`iou`) or
    intersection-over-area (`ioa`) and return a list of `ItemHeaderResult`.
    ...

**`segment_pubtables(
    dp: Image,
    table: ImageAnnotation,
    item_names: Sequence[ObjectTypes],
    spanning_cell_names: Sequence[ObjectTypes],
    segment_rule: Literal["iou", "ioa"],
    threshold_rows: float,
    threshold_cols: float,
) -> list[SegmentationResult]`**
  - Location: line 620
  - Segment a table based on the results of `table-transformer-structure-recognition`. The processing assumes 
that cells
    have already been generated from the intersection of columns and rows and that column and row numbers have
been
    inferred for rows and columns.
    ...

#### deepdoctection/train/d2_frcnn_train.py

**`train_d2_faster_rcnn(
    path_config_yaml: PathLikeOrStr,
    dataset_train: Union[str, DatasetBase],
    path_weights: PathLikeOrStr,
    config_overwrite: Optional[list[str]] = None,
    log_dir: PathLikeOrStr = "train_log/frcnn",
    build_train_config: Optional[Sequence[str]] = None,
    dataset_val: Optional[DatasetBase] = None,
    build_val_config: Optional[Sequence[str]] = None,
    metric_name: Optional[str] = None,
    metric: Optional[Union[Type[MetricBase], MetricBase]] = None,
    pipeline_component_name: Optional[str] = None,
) -> None`**
  - Location: line 305
  - Adaptation of https://github.com/facebookresearch/detectron2/blob/main/tools/train_net.py for training 
Detectron2
    standard models.
    ...

#### deepdoctection/train/hf_detr_train.py

**`train_hf_detr(
    path_config_json: PathLikeOrStr,
    dataset_train: Union[str, DatasetBase],
    path_weights: PathLikeOrStr,
    path_feature_extractor_config_json: str,
    config_overwrite: Optional[list[str]] = None,
    log_dir: PathLikeOrStr = "train_log/detr",
    build_train_config: Optional[Sequence[str]] = None,
    dataset_val: Optional[DatasetBase] = None,
    build_val_config: Optional[Sequence[str]] = None,
    metric_name: Optional[str] = None,
    metric: Optional[Union[Type[MetricBase], MetricBase]] = None,
    pipeline_component_name: Optional[str] = None,
) -> None`**
  - Location: line 150
  - Train Tabletransformer from scratch or fine-tune using an adaptation of the transformer trainer.
    Allowing experiments by using different config settings.
    ...

#### deepdoctection/train/hf_layoutlm_train.py

**`get_model_architectures_and_configs(model_type: str, dataset_type: DatasetType) -> tuple[Any, Any, Any]`**
  - Location: line 89
  - Gets the model architecture, model wrapper, and config class for a given `model_type` and `dataset_type`.
    Args:
    ...

**`maybe_remove_bounding_box_features(model_type: str) -> bool`**
  - Location: line 149
  - Lists models that do not need bounding box features.
    Args:
    ...

**`get_image_to_raw_features_mapping(input_str: str) -> Any`**
  - Location: line 274
  - Replacing eval functions

**`train_hf_layoutlm(
    path_config_json: PathLikeOrStr,
    dataset_train: Union[str, DatasetBase],
    path_weights: PathLikeOrStr,
    config_overwrite: Optional[list[str]] = None,
    log_dir: PathLikeOrStr = "train_log/layoutlm",
    build_train_config: Optional[Sequence[str]] = None,
    dataset_val: Optional[DatasetBase] = None,
    build_val_config: Optional[Sequence[str]] = None,
    metric: Optional[Union[Type[ClassificationMetric], ClassificationMetric]] = None,
    pipeline_component_name: Optional[str] = None,
    use_xlm_tokenizer: bool = False,
    use_token_tag: bool = True,
    segment_positions: Optional[Union[LayoutType, Sequence[LayoutType]]] = None,
) -> None`**
  - Location: line 282
  - Script for fine-tuning LayoutLM models either for sequence classification (e.g. classifying documents) or 
token
    classification using HF Trainer and custom evaluation. It currently supports LayoutLM, LayoutLMv2, 
LayoutLMv3 and
    LayoutXLM. Training similar but different models like LILT <https://arxiv.org/abs/2202.13669> can be done 
by
    ...

#### deepdoctection/train/tp_frcnn_train.py

**`load_augment_add_anchors(dp: JsonDict, config: AttrDict) -> Optional[JsonDict]`**
  - Location: line 90
  - Transforming an image before entering the graph. This function bundles all the necessary steps to feed
    the network for training.
    ...

**`get_train_dataflow(
    dataset: DatasetBase, config: AttrDict, use_multi_proc_for_train: bool, **build_train_kwargs: str
) -> DataFlow`**
  - Location: line 132
  - Return a dataflow for training TP FRCNN. The returned dataflow depends on the dataset and the 
configuration of
    the model, as the augmentation is part of the data preparation.
    ...

**`train_faster_rcnn(
    path_config_yaml: PathLikeOrStr,
    dataset_train: DatasetBase,
    path_weights: PathLikeOrStr,
    config_overwrite: Optional[list[str]] = None,
    log_dir: PathLikeOrStr = "train_log/frcnn",
    build_train_config: Optional[Sequence[str]] = None,
    dataset_val: Optional[DatasetBase] = None,
    build_val_config: Optional[Sequence[str]] = None,
    metric_name: Optional[str] = None,
    metric: Optional[Union[Type[MetricBase], MetricBase]] = None,
    pipeline_component_name: Optional[str] = None,
) -> None`**
  - Location: line 201
  - Easy adaptation of the training script for Tensorpack Faster-RCNN.
    Train Faster-RCNN from Scratch or fine-tune a model using Tensorpack's training API. Observe the training 
with
    ...

#### deepdoctection/utils/concurrency.py

**`mask_sigint() -> Generator[Any, None, None]`**
  - Location: line 105
  - Context manager to mask `SIGINT`.
    If called in the main thread, returns a context where `SIGINT` is ignored, and yields `True`. Otherwise, 
yields
    ...

**`enable_death_signal(_warn: bool = True) -> None`**
  - Location: line 123
  - Set the "death signal" of the current process.
    Ensures that the current process will be cleaned up if the parent process dies accidentally.
    ...

**`start_proc_mask_signal(proc)`**
  - Location: line 156
  - Start process(es) with `SIGINT` ignored.
    The signal mask is only applied when called from the main thread.
    ...

#### deepdoctection/utils/context.py

**`timeout_manager(proc: Any, seconds: Optional[int] = None) -> Iterator[str]`**
  - Location: line 41
  - Manager for time handling while some process is being called.
    Example:
    ...

**`save_tmp_file(image: Union[B64Str, PixelValues, B64], prefix: str) -> Iterator[tuple[str, str]]`**
  - Location: line 86
  - Save image temporarily and handle the clean-up once not necessary anymore.
    Args:
    ...

**`timed_operation(message: str, log_start: bool = False) -> Generator[Any, None, None]`**
  - Location: line 131
  - Context manager with a timer.
    Example:
    ...

#### deepdoctection/utils/develop.py

**`log_deprecated(name: str, text: str, eos: str = "", max_num_warnings: Optional[int] = None) -> None`**
  - Location: line 41
  - Logs a deprecation warning.
    Args:
    ...

**`deprecated(
    text: str = "", eos: str = "", max_num_warnings: Optional[int] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]`**
  - Location: line 74
  - Decorator to deprecate a function.
    Example:
    ...

#### deepdoctection/utils/env_info.py

**`collect_torch_env() -> str`**
  - Location: line 122
  - Wrapper for `torch.utils.collect_env.get_pretty_env_info`.
    Returns:
    ...

**`collect_installed_dependencies(data: KeyValEnvInfos) -> KeyValEnvInfos`**
  - Location: line 140
  - Collect installed dependencies for all third party libraries.
    Args:
    ...

**`detect_compute_compatibility(cuda_home: Optional[PathLikeOrStr], so_file: Optional[PathLikeOrStr]) -> 
str`**
  - Location: line 269
  - Detect the compute compatibility of a CUDA library.
    Args:
    ...

**`tf_info(data: KeyValEnvInfos) -> KeyValEnvInfos`**
  - Location: line 298
  - Returns a list of (key, value) pairs containing TensorFlow information.
    Args:
    ...

**`pt_info(data: KeyValEnvInfos) -> KeyValEnvInfos`**
  - Location: line 359
  - Returns a list of (key, value) pairs containing PyTorch information.
    Args:
    ...

**`set_dl_env_vars() -> None`**
  - Location: line 471
  - Set the environment variables that steer the selection of the DL framework.
    If both PyTorch and TensorFlow are available, PyTorch will be selected by default. For testing purposes, 
e.g. on
    ...

**`collect_env_info() -> str`**
  - Location: line 509
  - Collects and returns environment information.
    Returns:
    ...

**`auto_select_viz_library() -> None`**
  - Location: line 569
  - Sets PIL as the default image library if OpenCV is not installed.
    Note:
    ...

**`auto_select_pdf_render_framework() -> None`**
  - Location: line 588
  - Sets `pdf2image` as the default PDF rendering library if pdfium is not installed.
    Note:
    ...

#### deepdoctection/utils/file_utils.py

**`tf_available() -> bool`**
  - Location: line 41
  - Returns whether TensorFlow is installed.
    Returns:
    ...

**`get_tf_version() -> str`**
  - Location: line 51
  - Determines the installed TensorFlow version.
    Returns:
    ...

**`get_tensorflow_requirement() -> Requirement`**
  - Location: line 82
  - Returns the TensorFlow requirement.
    Returns:
    ...

**`tf_addons_available() -> bool`**
  - Location: line 109
  - Returns whether `tensorflow_addons` is installed.
    Returns:
    ...

**`get_tf_addons_requirements() -> Requirement`**
  - Location: line 119
  - Returns the `tensorflow_addons` requirement.
    Returns:
    ...

**`tensorpack_available() -> bool`**
  - Location: line 133
  - Returns whether `tensorpack` is installed.
    Returns:
    ...

**`get_tensorpack_requirement() -> Requirement`**
  - Location: line 143
  - Returns the `tensorpack` requirement.
    Returns:
    ...

**`pytorch_available() -> bool`**
  - Location: line 158
  - Returns whether PyTorch is installed.
    Returns:
    ...

**`get_pytorch_requirement() -> Requirement`**
  - Location: line 168
  - Returns the PyTorch requirement.
    Returns:
    ...

**`pyzmq_available() -> bool`**
  - Location: line 181
  - Returns whether pyzmq is installed.
    Returns:
    ...

**`lxml_available() -> bool`**
  - Location: line 196
  - Returns whether `lxml` is installed.
    Returns:
    ...

**`get_lxml_requirement() -> Requirement`**
  - Location: line 206
  - Returns the `lxml` requirement.
    Returns:
    ...

**`apted_available() -> bool`**
  - Location: line 221
  - Returns whether `apted` is available.
    Returns:
    ...

**`get_apted_requirement() -> Requirement`**
  - Location: line 231
  - Returns the `apted` requirement.
    Returns:
    ...

**`distance_available() -> bool`**
  - Location: line 246
  - Returns True if `distance` is available.
    Returns:
    ...

**`get_distance_requirement() -> Requirement`**
  - Location: line 256
  - Returns the `distance` requirement.
    Returns:
    ...

**`networkx_available() -> bool`**
  - Location: line 270
  - Checks if networkx is installed.
    Returns:
    ...

**`numpy_v1_available() -> bool`**
  - Location: line 285
  - Check if the installed NumPy version is version 1.
    This helper function determines whether the currently installed version
    ...

**`get_numpy_v1_requirement() -> Requirement`**
  - Location: line 302
  - Retrieves the requirement details for numpy version 1.
    Returns:
    ...

**`transformers_available() -> bool`**
  - Location: line 320
  - Returns whether HuggingFace Transformers is installed.
    Returns:
    ...

**`get_transformers_requirement() -> Requirement`**
  - Location: line 330
  - Returns the HuggingFace Transformers requirement.
    Returns:
    ...

**`detectron2_available() -> bool`**
  - Location: line 348
  - Returns whether `detectron2` is installed.
    Returns:
    ...

**`get_detectron2_requirement() -> Requirement`**
  - Location: line 358
  - Returns the `detectron2` requirement.
    Returns:
    ...

**`set_tesseract_path(tesseract_path: PathLikeOrStr) -> None`**
  - Location: line 378
  - Sets the Tesseract path.
    Note:
    ...

**`tesseract_available() -> bool`**
  - Location: line 399
  - Returns True if Tesseract is installed

**`get_tesseract_version() -> Union[int, version.Version]`**
  - Location: line 409
  - Returns the version of the installed Tesseract.
    Returns:
    ...

**`get_tesseract_requirement() -> Requirement`**
  - Location: line 440
  - Returns the Tesseract requirement.
    Returns:
    ...

**`pdf_to_ppm_available() -> bool`**
  - Location: line 461
  - Returns whether `pdftoppm` is installed.
    Returns:
    ...

**`pdf_to_cairo_available() -> bool`**
  - Location: line 471
  - Returns whether `pdftocairo` is installed.
    Returns:
    ...

**`get_poppler_version() -> Union[int, version.Version]`**
  - Location: line 481
  - Returns the version of the installed Poppler utility.
    Returns:
    ...

**`get_poppler_requirement() -> Requirement`**
  - Location: line 511
  - Returns the Poppler requirement.
    Returns:
    ...

**`pdfplumber_available() -> bool`**
  - Location: line 528
  - Returns whether `pdfplumber` is installed.
    Returns:
    ...

**`get_pdfplumber_requirement() -> Requirement`**
  - Location: line 538
  - Returns the `pdfplumber` requirement.
    Returns:
    ...

**`cocotools_available() -> bool`**
  - Location: line 553
  - Returns whether `pycocotools` is installed.
    Returns:
    ...

**`get_cocotools_requirement() -> Requirement`**
  - Location: line 563
  - Returns the `pycocotools` requirement.
    Returns:
    ...

**`scipy_available() -> bool`**
  - Location: line 577
  - Returns whether `scipy` is installed.
    Returns:
    ...

**`jdeskew_available() -> bool`**
  - Location: line 592
  - Returns whether `jdeskew` is installed.
    Returns:
    ...

**`get_jdeskew_requirement() -> Requirement`**
  - Location: line 602
  - Returns the `jdeskew` requirement.
    Returns:
    ...

**`sklearn_available() -> bool`**
  - Location: line 617
  - Returns whether `sklearn` is installed.
    Returns:
    ...

**`get_sklearn_requirement() -> Requirement`**
  - Location: line 627
  - Returns the `sklearn` requirement.
    Returns:
    ...

**`qpdf_available() -> bool`**
  - Location: line 641
  - Returns whether `qpdf` is installed.
    Returns:
    ...

**`boto3_available() -> bool`**
  - Location: line 659
  - Returns whether `boto3` is installed.
    Returns:
    ...

**`get_boto3_requirement() -> Requirement`**
  - Location: line 670
  - Returns the `boto3` requirement.
    Returns:
    ...

**`aws_available() -> bool`**
  - Location: line 680
  - Returns whether AWS CLI is installed.
    Returns:
    ...

**`get_aws_requirement() -> Requirement`**
  - Location: line 690
  - Returns the AWS CLI requirement.
    Returns:
    ...

**`doctr_available() -> bool`**
  - Location: line 705
  - Returns whether `doctr` is installed.
    Returns:
    ...

**`get_doctr_requirement() -> Requirement`**
  - Location: line 715
  - Returns the `doctr` requirement.
    Returns:
    ...

**`fasttext_available() -> bool`**
  - Location: line 734
  - Returns whether `fasttext` is installed.
    Returns:
    ...

**`get_fasttext_requirement() -> Requirement`**
  - Location: line 744
  - Returns the `fasttext` requirement.
    Returns:
    ...

**`wandb_available() -> bool`**
  - Location: line 759
  - Returns whether the W&B package `wandb` is installed.
    Returns:
    ...

**`get_wandb_requirement() -> Requirement`**
  - Location: line 769
  - Returns the W&B requirement.
    Returns:
    ...

**`opencv_available() -> bool`**
  - Location: line 789
  - Returns whether OpenCV is installed.
    Returns:
    ...

**`get_opencv_requirement() -> Requirement`**
  - Location: line 799
  - Returns the OpenCV requirement.
    Returns:
    ...

**`pillow_available() -> bool`**
  - Location: line 814
  - Returns whether Pillow is installed.
    Returns:
    ...

**`get_pillow_requirement() -> Requirement`**
  - Location: line 824
  - Returns the Pillow requirement.
    Returns:
    ...

**`pypdfium2_available() -> bool`**
  - Location: line 839
  - Returns whether `pypdfium2` is installed.
    Returns:
    ...

**`get_pypdfium2_requirement() -> Requirement`**
  - Location: line 849
  - Returns the `pypdfium2` requirement.
    Returns:
    ...

**`spacy_available() -> bool`**
  - Location: line 864
  - Returns whether SpaCy is installed.
    Returns:
    ...

**`get_spacy_requirement() -> Requirement`**
  - Location: line 875
  - Returns the SpaCy requirement.
    Returns:
    ...

**`set_mp_spawn() -> None`**
  - Location: line 885
  - Sets the multiprocessing method to "spawn".
    Note:
    ...

#### deepdoctection/utils/fs.py

**`sizeof_fmt(num: float, suffix: str = "B") -> str`**
  - Location: line 59
  - Converts a number of bytes into a human-readable string.
    Example:
    ...

**`mkdir_p(dir_name: PathLikeOrStr) -> None`**
  - Location: line 84
  - Creates a directory recursively, similar to `mkdir -p`. Does nothing if the directory already exists.
    Example:
    ...

**`download(
    url: str, directory: PathLikeOrStr, file_name: Optional[str] = None, expect_size: Optional[int] = None
) -> str`**
  - Location: line 111
  - Downloads a file from a URL to a directory. Determines the filename from the URL if not provided.
    Example:
    ...

**`load_image_from_file(path: PathLikeOrStr, type_id: Literal["np"] = "np") -> Optional[PixelValues]`**
  - Location: line 176

**`load_image_from_file(path: PathLikeOrStr, type_id: Literal["b64"]) -> Optional[B64Str]`**
  - Location: line 181

**`load_image_from_file(
    path: PathLikeOrStr, type_id: Literal["np", "b64"] = "np"
) -> Optional[Union[B64Str, PixelValues]]`**
  - Location: line 185
  - Loads an image from a file and returns either a base64-encoded string, a numpy array, or `None` if the 
file is not
    found or a conversion error occurs.
    ...

**`load_bytes_from_pdf_file(path: PathLikeOrStr, page_number: int = 0) -> B64`**
  - Location: line 222
  - Loads a PDF file with a single page and returns a bytes representation of this file. Can be converted into
a numpy
    array or passed directly to the `image` attribute of `Image`.
    ...

**`get_load_image_func(
    path: PathLikeOrStr,
) -> Union[LoadImageFunc, Callable[[PathLikeOrStr], B64]]`**
  - Location: line 263
  - Returns the loading function according to the file extension.
    Example:
    ...

**`maybe_path_or_pdf(path: PathLikeOrStr) -> int`**
  - Location: line 295
  - Checks if the path points to a directory, a PDF document, or a single image.
    Example:
    ...

**`load_json(path_ann: PathLikeOrStr) -> JsonDict`**
  - Location: line 322
  - Loads a JSON file.
    Example:
    ...

**`get_package_path() -> Path`**
  - Location: line 342
  - Returns the full base path of this package.
    Returns:
    ...

**`get_cache_dir_path() -> Path`**
  - Location: line 352
  - Returns the full base path to the cache directory.
    Returns:
    ...

**`get_weights_dir_path() -> Path`**
  - Location: line 362
  - Returns the full base path to the model directory.
    Returns:
    ...

**`get_configs_dir_path() -> Path`**
  - Location: line 372
  - Returns the full base path to the configs directory.
    Returns:
    ...

**`get_dataset_dir_path() -> Path`**
  - Location: line 382
  - Returns the full base path to the dataset directory.
    Returns:
    ...

**`maybe_copy_config_to_cache(
    package_path: PathLikeOrStr, configs_dir_path: PathLikeOrStr, file_name: str, force_copy: bool = True
) -> str`**
  - Location: line 392
  - Copies a file from the source directory to the target directory.
    Example:
    ...

**`sub_path(anchor_dir: PathLikeOrStr, *paths: PathLikeOrStr) -> PathLikeOrStr`**
  - Location: line 422
  - Generates a path from the anchor directory and additional path arguments.
    Example:
    ...

#### deepdoctection/utils/identifier.py

**`is_uuid_like(input_id: str) -> bool`**
  - Location: line 29
  - Check if the input string has a UUID3 string representation format.
    Example:
    ...

**`get_uuid_from_str(input_id: str) -> str`**
  - Location: line 51
  - Return a UUID3 string representation generated from an input string.
    Args:
    ...

**`get_uuid(*inputs: str) -> str`**
  - Location: line 64
  - Set a UUID generated by the concatenation of string inputs.
    Args:
    ...

**`get_md5_hash(path: PathLikeOrStr, buffer_size: int = 65536) -> str`**
  - Location: line 78
  - Calculate an MD5 hash for a given file.
    Args:
    ...

#### deepdoctection/utils/logger.py

**`set_logger_dir(dir_name: PathLikeOrStr, action: Optional[str] = None) -> None`**
  - Location: line 238
  - Set the directory for global logging.
    Args:
    ...

**`auto_set_dir(action: Optional[str] = None, name: Optional[str] = None) -> None`**
  - Location: line 299
  - Will set the log directory to './train_log/{script_name}:{name}'.
    `script_name` is the name of the main python file currently running.
    ...

**`get_logger_dir() -> Optional[PathLikeOrStr]`**
  - Location: line 317
  - The logger directory, or `None` if not set.
    Returns:
    ...

**`log_once(message: str, function: str = "info") -> None`**
  - Location: line 328
  - Log certain message only once. Calling this function more than once with
    the same message will result in no operation.
    ...

#### deepdoctection/utils/metacfg.py

**`set_config_by_yaml(path_yaml: PathLikeOrStr) -> AttrDict`**
  - Location: line 180
  - Initialize the config class from a YAML file.
    Args:
    ...

**`save_config_to_yaml(config: AttrDict, path_yaml: PathLikeOrStr) -> None`**
  - Location: line 201
  - Save the configuration instance as a YAML file.
    Example:
    ...

**`config_to_cli_str(config: AttrDict, *exclude: str) -> str`**
  - Location: line 220
  - Transform an `AttrDict` to a string that can be passed to a CLI. Optionally exclude keys from the string.
    Example:
    ...

#### deepdoctection/utils/mocks.py

**`layer_register(log_shape)`**
  - Location: line 25
  - Mock layer_register function from tensorpack.

**`under_name_scope()`**
  - Location: line 34
  - Mock under_name_scope function from tensorpack.

**`memoized(func)`**
  - Location: line 43
  - Mock memoized function from tensorpack.

**`memoized_method(func)`**
  - Location: line 48
  - Mock memoized_method function from tensorpack.

**`auto_reuse_variable_scope(inputs)`**
  - Location: line 53
  - Mock auto_reuse_variable_scope function from tensorpack.

#### deepdoctection/utils/pdf_utils.py

**`decrypt_pdf_document(path: PathLikeOrStr) -> bool`**
  - Location: line 59
  - Decrypt a PDF file.
    As copying a PDF document removes the password that protects the PDF, this method generates a copy and 
decrypts the
    ...

**`decrypt_pdf_document_from_bytes(input_bytes: bytes) -> bytes`**
  - Location: line 93
  - Decrypt a PDF given as bytes.
    Under the hood, it saves the bytes to a temporary file and then calls `decrypt_pdf_document`.
    ...

**`get_pdf_file_reader(path_or_bytes: Union[PathLikeOrStr, bytes]) -> PdfReader`**
  - Location: line 120
  - Create a file reader object from a PDF document.
    Will try to decrypt the document if it is encrypted. (See `decrypt_pdf_document` to understand what is 
meant with
    ...

**`get_pdf_file_writer() -> PdfWriter`**
  - Location: line 171
  - `PdfWriter` instance.
    Returns:
    ...

**`pdf_to_np_array_poppler(
    pdf_bytes: bytes, size: Optional[tuple[int, int]] = None, dpi: Optional[int] = None
) -> PixelValues`**
  - Location: line 312
  - Convert a single PDF page from its byte representation to a numpy array using Poppler.
    This function will save the PDF as a temporary file and then call Poppler via `pdftoppm` or `pdftocairo`.
    ...

**`pdf_to_np_array_pdfmium(pdf_bytes: bytes, dpi: Optional[int] = None) -> PixelValues`**
  - Location: line 340
  - Convert a single PDF page from its byte representation to a numpy array using pdfium.
    Args:
    ...

**`pdf_to_np_array(pdf_bytes: bytes, size: Optional[tuple[int, int]] = None, dpi: Optional[int] = None) -> 
PixelValues`**
  - Location: line 360
  - Convert a single PDF page from its byte representation to a `np.array`.
    This function will either use Poppler or pdfium to render the PDF.
    ...

**`split_pdf(
    pdf_path: PathLikeOrStr, output_dir: PathLikeOrStr, file_type: Literal["image", "pdf"], dpi: int = 200
) -> None`**
  - Location: line 389
  - Split a PDF into single pages.
    The pages are saved as single PDF or PNG files in a subfolder of the output directory.
    ...

#### deepdoctection/utils/settings.py

**`token_class_tag_to_token_class_with_tag(token: ObjectTypes, tag: ObjectTypes) -> ObjectTypes`**
  - Location: line 335
  - Maps a `TokenClassWithTag` enum member from a token class and tag, e.g. `TokenClasses.header` and 
`BioTag.inside`
    maps to `TokenClassWithTag.i_header`.
    ...

**`token_class_with_tag_to_token_class_and_tag(
    token_class_with_tag: ObjectTypes,
) -> Optional[tuple[ObjectTypes, ObjectTypes]]`**
  - Location: line 357
  - This is the reverse mapping from TokenClassWithTag members to TokenClasses and BioTag
    Args:
    ...

**`update_all_types_dict() -> None`**
  - Location: line 378
  - Updates subsequently registered object types. Useful for defining additional ObjectTypes in tests

**`update_black_list(item: str) -> None`**
  - Location: line 416
  - Updates the black list, i.e. set of elements that must not be lowered

**`get_type(obj_type: Union[str, ObjectTypes]) -> ObjectTypes`**
  - Location: line 421
  - Get an object type property from a given string. Does nothing if an `ObjectType` is passed
    Args:
    ...

#### deepdoctection/utils/tqdm.py

**`get_tqdm_default_kwargs(
    **kwargs: Optional[Union[str, int, float]]
) -> Dict[str, Union[str, float, bool, int, None]]`**
  - Location: line 31
  - Return default arguments to be used with `tqdm`.
    Args:
    ...

**`get_tqdm(total: Optional[Union[int, float]] = None, **kwargs: Union[str, int, float]) -> TqdmType`**
  - Location: line 52
  - Get `tqdm` progress bar with some default options to have consistent style.
    Args:
    ...

#### deepdoctection/utils/transform.py

**`box_to_point4(boxes: npt.NDArray[np.float32]) -> npt.NDArray[np.float32]`**
  - Location: line 51
  - Args:
    boxes: nx4
    ...

**`point4_to_box(points: npt.NDArray[np.float32]) -> npt.NDArray[np.float32]`**
  - Location: line 64
  - Args:
    points: (nx4)x2
    ...

**`normalize_image(
    image: PixelValues, pixel_mean: npt.NDArray[float32], pixel_std: npt.NDArray[float32]
) -> PixelValues`**
  - Location: line 271
  - Preprocess pixel values of an image by rescaling.
    Args:
    ...

**`pad_image(image: PixelValues, top: int, right: int, bottom: int, left: int) -> PixelValues`**
  - Location: line 288
  - Pad an image with white color and with given top/bottom/right/left pixel values. Only white padding is
    currently supported.
    ...

#### deepdoctection/utils/utils.py

**`delete_keys_from_dict(
    dictionary: Union[dict[Any, Any], MutableMapping], keys: Union[str, list[str], set[str]]  # type: ignore
) -> dict[Any, Any]`**
  - Location: line 33
  - Removes key/value pairs from a `dictionary`. Works for nested dictionaries as well.
    Args:
    ...

**`split_string(input_string: str) -> list[str]`**
  - Location: line 68
  - Splits an `input_string` by commas and returns a list of the split components.
    Args:
    ...

**`string_to_dict(input_string: str) -> dict[str, str]`**
  - Location: line 81
  - Converts an `input_string` of the form `key1=val1,key2=val2` into a dictionary.
    Args:
    ...

**`to_bool(inputs: Union[str, bool, int]) -> bool`**
  - Location: line 99
  - Converts a string "True" or "False" to its boolean value.
    Args:
    ...

**`call_only_once(func: Callable[..., Any]) -> Callable[..., Any]`**
  - Location: line 120
  - Decorates a method or property of a class so that it can only be called once for every instance.
    Calling it more than once will result in an exception.
    ...

**`get_rng(obj: Any = None) -> np.random.RandomState`**
  - Location: line 160
  - Gets a good random number generator seeded with time, process id, and the object.
    Args:
    ...

**`is_file_extension(file_name: PathLikeOrStr, extension: Union[str, Sequence[str]]) -> bool`**
  - Location: line 174
  - Checks if a given `file_name` has a given `extension`.
    Args:
    ...

**`partition_list(base_list: list[str], stop_value: str) -> list[list[str]]`**
  - Location: line 190
  - Partitions a list of strings into sublists, where each sublist starts with the first occurrence of the 
`stop_value`.
    Consecutive `stop_value` elements are grouped together in the same sublist.
    ...

#### deepdoctection/utils/viz.py

**`random_color(
    rgb: bool = True, maximum: int = 255, deterministic_input_str: Optional[str] = None
) -> tuple[int, int, int]`**
  - Location: line 85
  - Args:
    rgb: Whether to return RGB colors or BGR colors.
    maximum: Either 255 or 1.
    ...

**`draw_boxes(
    np_image: PixelValues,
    boxes: npt.NDArray[float32],
    category_names_list: Optional[list[Tuple[Union[str, None], Union[str, None]]]] = None,
    color: Optional[BGR] = None,
    font_scale: float = 1.0,
    rectangle_thickness: int = 4,
    box_color_by_category: bool = True,
    show_palette: bool = True,
) -> PixelValues`**
  - Location: line 108
  - Draw bounding boxes with category names into image.
    Args:
    ...

**`interactive_imshow(img: PixelValues) -> None`**
  - Location: line 202
  - Display an image in a pop-up window.
    Args:
    ...

#### scripts/export_tracing_d2.py

**`setup_cfg(path_config_yaml, device)`**
  - Location: line 21

**`export_tracing(torch_model, image, path_output)`**
  - Location: line 32

#### scripts/reduce_d2.py

**`get_state_dict(path_yaml, path_weights)`**
  - Location: line 32

#### scripts/reduce_tp.py

**`reduce_model(weights)`**
  - Location: line 29

#### scripts/tp2d2.py

**`convert_weights_tp_to_d2(weights, cfg)`**
  - Location: line 32

#### setup.py

**`get_version()`**
  - Location: line 30

**`deps_list(*pkgs: str)`**
  - Location: line 119

#### tests/conftest.py

**`get_image_results() -> DatapointImage`**
  - Location: line 66
  - DatapointImage

**`fixture_image_results() -> DatapointImage`**
  - Location: line 74
  - DatapointImage

**`fixture_path_to_tp_frcnn_yaml() -> PathLikeOrStr`**
  - Location: line 82
  - path to tp frcnn yaml file

**`fixture_path_to_d2_frcnn_yaml() -> PathLikeOrStr`**
  - Location: line 90
  - path to d2 frcnn yaml file

**`fixture_categories() -> Dict[int, LayoutType]`**
  - Location: line 98
  - Categories as Dict

**`fixture_dataset_categories() -> DatasetCategories`**
  - Location: line 112
  - fixture categories

**`fixture_np_image() -> PixelValues`**
  - Location: line 131
  - np_array image

**`fixture_np_image_large() -> PixelValues`**
  - Location: line 139
  - np_array image large

**`fixture_path_to_tesseract_yaml() -> PathLikeOrStr`**
  - Location: line 147
  - path to tesseract yaml file

**`fixture_dp_image() -> Image`**
  - Location: line 155
  - fixture Image datapoint

**`fixture_layout_detect_results() -> List[DetectionResult]`**
  - Location: line 163
  - fixture layout_detect_results

**`fixture_layout_annotations() -> List[ImageAnnotation]`**
  - Location: line 169
  - fixture layout_annotations

**`fixture_caption_annotations() -> List[ImageAnnotation]`**
  - Location: line 175
  - fixture caption_annotations

**`fixture_layout_annotations_for_ordering() -> List[ImageAnnotation]`**
  - Location: line 181
  - fixture layout_annotations

**`fixture_cell_detect_results() -> List[List[DetectionResult]]`**
  - Location: line 187
  - fixture cell_detect_results

**`fixture_cell_annotations() -> List[List[ImageAnnotation]]`**
  - Location: line 193
  - fixture cell_annotation

**`fixture_dp_image_with_layout_anns(dp_image: Image, layout_annotations: List[ImageAnnotation]) -> Image`**
  - Location: line 199
  - fixture dp_image_with_anns

**`fixture_dp_image_with_layout_and_caption_anns(
    dp_image: Image, layout_annotations: List[ImageAnnotation], caption_annotations: List[ImageAnnotation]
) -> Image`**
  - Location: line 208
  - fixture dp_image_with_anns

**`fixture_global_cell_boxes() -> List[List[BoundingBox]]`**
  - Location: line 222
  - fixture global_cell_boxes

**`fixture_dp_image_tab_cell_item(dp_image: Image) -> Image`**
  - Location: line 228
  - fixture dp_image_tab_cell_item

**`fixture_dp_image_item_stretched(dp_image_tab_cell_item: Image) -> Image`**
  - Location: line 251
  - fixture dp_image_tab_cell_item

**`fixture_row_sub_cats() -> List[CategoryAnnotation]`**
  - Location: line 275
  - fixture row_sub_cats

**`fixture_col_sub_cats() -> List[CategoryAnnotation]`**
  - Location: line 281
  - fixture col_sub_cats

**`fixture_cell_sub_cats() -> (
    List[Tuple[CategoryAnnotation, CategoryAnnotation, CategoryAnnotation, CategoryAnnotation]]
)`**
  - Location: line 287
  - fixture cell_sub_cats

**`fixture_word_layout_annotations_for_ordering() -> List[ImageAnnotation]`**
  - Location: line 295
  - fixture word_layout_annotations_for_ordering

**`fixture_word_sub_cats_for_ordering() -> List[List[CategoryAnnotation]]`**
  - Location: line 301
  - fixture word_sub_cats_for_ordering

**`fixture_words_annotations_with_sub_cats(
    word_layout_annotations_for_ordering: List[ImageAnnotation],
    word_sub_cats_for_ordering: List[List[CategoryAnnotation]],
) -> List[ImageAnnotation]`**
  - Location: line 307
  - fixture words_annotations_with_sub_cats

**`fixture_dp_image_with_layout_and_word_annotations(
    dp_image: Image,
    layout_annotations_for_ordering: List[ImageAnnotation],
    words_annotations_with_sub_cats: List[ImageAnnotation],
) -> Image`**
  - Location: line 320
  - fixture dp_image_with_layout_and_word_annotations

**`fixture_dp_image_fully_segmented(
    dp_image_item_stretched: Image,
    row_sub_cats: List[CategoryAnnotation],
    col_sub_cats: List[CategoryAnnotation],
    cell_sub_cats: List[Tuple[CategoryAnnotation, CategoryAnnotation, CategoryAnnotation, 
CategoryAnnotation]],
) -> Image`**
  - Location: line 345
  - fixture dp_image_fully_segmented

**`fixture_cell_sub_cats_when_table_fully_tiled() -> (
    List[Tuple[CategoryAnnotation, CategoryAnnotation, CategoryAnnotation, CategoryAnnotation]]
)`**
  - Location: line 372
  - fixture cell_sub_cats_when_table_fully_tiled

**`fixture_summary_sub_cats_when_table_fully_tiled() -> (
    Tuple[CategoryAnnotation, CategoryAnnotation, CategoryAnnotation, CategoryAnnotation]
)`**
  - Location: line 380
  - fixture summary_sub_cats_when_table_fully_tiled

**`fixture_summary_htab_sub_cat() -> ContainerAnnotation`**
  - Location: line 388
  - fixture summary_htab_sub_cat

**`fixture_dp_image_fully_segmented_fully_tiled(
    dp_image_item_stretched: Image,
    row_sub_cats: List[CategoryAnnotation],
    col_sub_cats: List[CategoryAnnotation],
    cell_sub_cats_when_table_fully_tiled: List[
        Tuple[CategoryAnnotation, CategoryAnnotation, CategoryAnnotation, CategoryAnnotation]
    ],
) -> Image`**
  - Location: line 394
  - fixture datapoint_fully_segmented_when_table_fully_tiled. Note that bounding boxes of row and cols are not
adjusted

**`fixture_word_detect_result() -> List[DetectionResult]`**
  - Location: line 426
  - fixture word_detect_result

**`fixture_double_word_detect_results() -> List[List[DetectionResult]]`**
  - Location: line 432
  - fixture double_word_detect_results

**`fixture_word_layout_annotation() -> List[ImageAnnotation]`**
  - Location: line 438
  - fixture word_layout_annotation

**`fixture_word_layout_annotation_for_matching() -> List[ImageAnnotation]`**
  - Location: line 444
  - fixture word_layout_annotation_for_matching

**`fixture_word_box_global() -> List[BoundingBox]`**
  - Location: line 450
  - fixture word_box_global

**`fixture_dp_image_fully_segmented_unrelated_words(
    dp_image_fully_segmented_fully_tiled: Image, word_layout_annotation_for_matching: List[ImageAnnotation]
) -> Image`**
  - Location: line 456
  - fixture dp_image_fully_segmented_unrelated_words. Word annotations are not related to layout detections

**`fixture_row_box_tiling_table() -> List[BoundingBox]`**
  - Location: line 472
  - fixture row_box_tiling_table

**`fixture_col_box_tiling_table() -> List[BoundingBox]`**
  - Location: line 478
  - fixture col_box_tiling_table

**`fixture_layoutlm_input() -> JsonDict`**
  - Location: line 484
  - fixture layoutlm_input

**`fixture_layoutlm_features() -> JsonDict`**
  - Location: line 490
  - fixture layoutlm_features

**`fixture_token_class_result() -> List[TokenClassResult]`**
  - Location: line 496
  - fixture token_class_result

**`fixture_sequence_class_result() -> SequenceClassResult`**
  - Location: line 502
  - fixture sequence_class_result

**`fixture_text_lines() -> List[Tuple[str, PixelValues]]`**
  - Location: line 508
  - fixture text_lines

**`fixture_language_detect_result() -> DetectionResult`**
  - Location: line 517
  - fixture language_detect_result

**`fixture_get_annotation_maps() -> dict[str, list[AnnotationMap]]`**
  - Location: line 523
  - fixture annotation_maps

**`fixture_service_id_to_ann_id() -> dict[str, list[str]]`**
  - Location: line 529
  - fixture service_id_to_ann_id

**`pytest_sessionstart() -> None`**
  - Location: line 534
  - Pre configuration before testing starts

#### tests/data.py

**`get_textract_response() -> JsonDict`**
  - Location: line 1686
  - sample aws textract response

**`get_layoutlm_input() -> JsonDict`**
  - Location: line 1748
  - layout lm model input from tokenizer

**`get_layoutlm_features() -> JsonDict`**
  - Location: line 1755
  - layoutlm features

**`get_token_class_result() -> List[TokenClassResult]`**
  - Location: line 1762
  - token class result

**`get_sequence_class_result() -> SequenceClassResult`**
  - Location: line 1803
  - sequence class result

#### tests/dataflow/conftest.py

**`fixture_datapoint_list() -> List[str]`**
  - Location: line 29
  - List fixture

**`fixture_dataset_three_dim() -> List[List[List[float]]]`**
  - Location: line 51
  - Dataset fixture

**`fixture_mean_axis_zero() -> List[List[float]]`**
  - Location: line 59
  - Mean fixture

**`fixture_mean_all_axes() -> float`**
  - Location: line 67
  - Mean fixture

**`fixture_std_axis_zero() -> List[List[float]]`**
  - Location: line 75
  - Std fixture

**`fixture_std_all_axes() -> float`**
  - Location: line 83
  - Std fixture

**`fixture_dataset_flatten() -> List[List[List[float]]]`**
  - Location: line 91
  - Dataset flatten

#### tests/datapoint/conftest.py

**`fixture_box() -> Box`**
  - Location: line 125
  - Box fixture

**`fixture_image() -> WhiteImage`**
  - Location: line 177
  - TestWhiteImage

**`fixture_category_ann() -> CatAnn`**
  - Location: line 208
  - TestCatAnn

**`fixture_pdf_page() -> TestPdfPage`**
  - Location: line 258
  - TestPdfPage

#### tests/datasets/instances/conftest.py

**`get_white_image(path: str) -> Optional[PixelValues]`**
  - Location: line 29
  - white image

**`get_white_image_pdf(path: str, dpi: int) -> Optional[PixelValues]`**
  - Location: line 38
  - white image

#### tests/eval/conftest.py

**`fixture_datapoint_image() -> Image`**
  - Location: line 35
  - fixture Image datapoint

**`fixture_annotation() -> List[ImageAnnotation]`**
  - Location: line 45
  - annotations

**`fixture_image_with_anns(datapoint_image: Image, annotations: List[ImageAnnotation]) -> Image`**
  - Location: line 78
  - image with annotations

**`fixture_categories() -> DatasetCategories`**
  - Location: line 89
  - categories

**`fixture_detection_results() -> List[DetectionResult]`**
  - Location: line 97
  - detection results

#### tests/extern/conftest.py

**`fixture_layoutlm_input_for_predictor() -> JsonDict`**
  - Location: line 35
  - Layoutlm input

**`fixture_layoutlm_input() -> JsonDict`**
  - Location: line 43
  - Layoutlm_v2 input

**`fixture_categories_semantics() -> Sequence[str]`**
  - Location: line 51
  - Categories semantics

**`fixture_categories_bio() -> Sequence[str]`**
  - Location: line 59
  - Categories semantics

**`fixture_token_class_names() -> Sequence[str]`**
  - Location: line 67
  - Categories semantics

**`fixture_textract_response() -> JsonDict`**
  - Location: line 75
  - fixture textract_response

**`fixture_pdf_bytes() -> bytes`**
  - Location: line 81
  - fixture pdf bytes

**`fixture_pdf_bytes_page_2() -> bytes`**
  - Location: line 89
  - fixture pdf bytes

**`fixture_angle_detection_result() -> DetectionResult`**
  - Location: line 97
  - fixture detection result for running rotation image transformation

**`fixture_detr_categories() -> Mapping[int, ObjectTypes]`**
  - Location: line 105
  - fixture object types

#### tests/extern/data.py

**`get_detr_categories() -> Mapping[int, ObjectTypes]`**
  - Location: line 95
  - detr_categories

#### tests/mapper/conftest.py

**`fixture_datapoint_coco() -> Dict[str, Any]`**
  - Location: line 42
  - Datapoint as received from SerializerCoco

**`fixture_categories_coco() -> Mapping[int, ObjectTypes]`**
  - Location: line 51
  - Categories as Dict

**`get_coco_white_image(path: str, type_id: str = "np") -> Optional[Union[str, PixelValues]]`**
  - Location: line 58
  - Returns a white image
    :param path: An image path
    :param type_id: "np" or "b64"
    ...

**`fixture_coco_results() -> DatapointCoco`**
  - Location: line 69
  - DatapointCoco

**`fixture_datapoint_pubtabnet() -> Dict[str, Any]`**
  - Location: line 77
  - Datapoint as received from SerializerCoco

**`fixture_categories_name_as_key_pubtabnet() -> Mapping[ObjectTypes, int]`**
  - Location: line 86
  - Categories as Dict

**`fixture_pubtabnet_results() -> DatapointPubtabnet`**
  - Location: line 94
  - DatapointPubtabnet

**`get_pubtabnet_white_image(path: str, type_id: str = "np") -> Optional[Union[str, PixelValues]]`**
  - Location: line 101
  - Returns a white image
    :param path: An image path
    :param type_id: "np" or "b64"

**`get_always_pubtabnet_white_image(path: str, type_id: str = "np") -> Optional[Union[str, PixelValues]]`**
  - Location: line 113
  - Returns a white image
    :param path: An image path
    :param type_id: "np" or "b64"

**`get_always_pubtabnet_white_image_from_bytes(
    pdf_bytes: str, dpi: Optional[int] = None
) -> Optional[Union[str, PixelValues]]`**
  - Location: line 123
  - Returns a white image

**`get_always_bytes(path: str) -> bytes`**
  - Location: line 134
  - Returns bytes

**`fixture_datapoint_prodigy() -> JsonDict`**
  - Location: line 144
  - Datapoint as received from Prodigy db

**`fixture_categories_prodigy() -> Mapping[ObjectTypes, str]`**
  - Location: line 153
  - Categories as Dict

**`get_datapoint_prodigy() -> DatapointProdigy`**
  - Location: line 160
  - DatapointProdigy

**`fixture_prodigy_results() -> DatapointProdigy`**
  - Location: line 168
  - DatapointProdigy

**`fixture_datapoint_image() -> Image`**
  - Location: line 176
  - Image

**`fixture_datapoint_image_with_summary() -> Image`**
  - Location: line 184
  - Image with summary annotation

**`fixture_page_dict() -> JsonDict`**
  - Location: line 192
  - page file

**`fixture_datapoint_xfund() -> Dict[str, Any]`**
  - Location: line 200
  - Datapoint as received from Xfund dataset

**`fixture_xfund_category_names() -> Mapping[str, ObjectTypes]`**
  - Location: line 209
  - Xfund category names mapping

**`fixture_xfund_category_dict_name_as_key() -> Mapping[LayoutType, str]`**
  - Location: line 218
  - Xfund category dict name as key

**`fixture_layoutlm_input() -> JsonDict`**
  - Location: line 226
  - Layoutlm input

**`fixture_layoutlm_v2_input() -> JsonDict`**
  - Location: line 234
  - Layoutlm_v2 input

**`fixture_raw_layoutlm_featurest() -> JsonDict`**
  - Location: line 242
  - Layoutlm input

**`fixture_xfund_categories_dict_name_as_key() -> Mapping[ObjectTypes, int]`**
  - Location: line 250
  - categories_dict_name_as_key

**`fixture_ner_token_to_id_mapping() -> Mapping[ObjectTypes, Any]`**
  - Location: line 258
  - ner_token_to_id_mapping

**`fixture_datapoint_iiitar13kjson() -> Dict[str, Any]`**
  - Location: line 266
  - Datapoint as received from iiitar13k dataset already converted into json format

**`fixture_iiitar13k_categories_name_as_keys() -> Mapping[ObjectTypes, int]`**
  - Location: line 275
  - iiitar13k category names dict

**`fixture_xfund_category_names_mapping() -> Mapping[str, ObjectTypes]`**
  - Location: line 284
  - iiitar13k category names mapping

**`fixture_iiitar13k_results() -> IIITar13KJson`**
  - Location: line 293
  - iiitar13k results

#### tests/train/conftest.py

**`fixture_test_dataset() -> DatasetBase`**
  - Location: line 114
  - fixture for test dataset

#### tests_d2/conftest.py

**`fixture_path_to_d2_frcnn_yaml() -> Path`**
  - Location: line 35
  - path to d2 frcnn yaml file

**`fixture_categories() -> Dict[int, ObjectTypes]`**
  - Location: line 43
  - Categories as Dict

**`fixture_np_image() -> PixelValues`**
  - Location: line 52
  - np_array image

### Class Hierarchy Diagram

```mermaid
classDiagram
    class ABC
    class BaseException
    class DefaultTrainer
    class Enum
    class EventWriter
    class Filter
    class Formatter
    class ModuleType
    class Process
    class Protocol
    class RuntimeError
    class Thread
    class Trainer
    class TypedDict
    class str
    class DetrDataCollator {
        +maybe_pad_image_and_transform()
    }
    class MappingContextManager
    class DefaultMapper
    class LabelSummarizer {
        +dump()
        +get_summary()
        +print_summary_histogram()
    }
    class LayoutLMDataCollator
    class Evaluator {
        +run()
        +run()
        +run()
        +compare()
    }
    class WandbTableAgent {
        +dump()
        +reset()
        +log()
    }
    class TableTree {
        +bracket()
    }
    class CustomConfig {
        +maximum()
        +normalized_distance()
        +rename()
    }
    class TEDS {
        +tokenize()
        +load_html_tree()
        +evaluate()
    }
    class TedsMetric {
        +dump()
        +get_distance()
        +get_requirements()
    }
    class EvalCallback
    class ClassificationMetric {
        +dump()
        +get_distance()
        +set_categories()
        +get_requirements()
        +sub_cats()
        +... 2 more
    }
    class AccuracyMetric
    class ConfusionMetric {
        +get_distance()
        +print_result()
    }
    class PrecisionMetric {
        +get_distance()
    }
    class RecallMetric
    class F1Metric
    class PrecisionMetricMicro {
        +get_distance()
    }
    class RecallMetricMicro
    class F1MetricMicro
    class MetricBase {
        +get_requirements()
        +get_distance()
        +dump()
        +result_list_to_dict()
        +print_result()
    }
    class CocoMetric {
        +dump()
        +get_distance()
        +get_summary_default_parameters()
        +set_params()
        +get_requirements()
    }
    class ServiceFactory {
        +build_layout_detector()
        +build_rotation_detector()
        +build_transform_service()
        +build_padder()
        +build_layout_service()
        +... 20 more
    }
    class LMTokenClassifierService {
        +serve()
        +clone()
        +get_meta_annotation()
        +image_to_features_func()
        +clear_predictor()
    }
    class LMSequenceClassifierService {
        +serve()
        +clone()
        +get_meta_annotation()
        +image_to_features_func()
        +clear_predictor()
    }
    class ImageLayoutService {
        +serve()
        +get_meta_annotation()
        +clone()
        +clear_predictor()
    }
    class SegmentationResult
    class ItemHeaderResult
    class TableSegmentationService {
        +serve()
        +clone()
        +get_meta_annotation()
        +clear_predictor()
    }
    class PubtablesSegmentationService {
        +serve()
        +clone()
        +get_meta_annotation()
    }
    class TextExtractionService {
        +serve()
        +get_text_rois()
        +get_predictor_input()
        +get_meta_annotation()
        +clone()
        +... 1 more
    }
    class OrderGenerator {
        +group_words_into_lines()
        +group_lines_into_lines()
        +order_blocks()
    }
    class TextLineGenerator {
        +create_detection_result()
    }
    class TextLineServiceMixin
    class TextLineService {
        +clone()
        +serve()
        +get_meta_annotation()
    }
    class TextOrderService {
        +serve()
        +order_text_in_text_block()
        +order_blocks()
        +get_meta_annotation()
        +clone()
        +... 1 more
    }
    class DatapointManager {
        +datapoint()
        +datapoint()
        +assert_datapoint_passed()
        +set_image_annotation()
        +set_category_annotation()
        +... 6 more
    }
    class ImageCroppingService {
        +serve()
        +clone()
        +get_meta_annotation()
        +clear_predictor()
    }
    class IntersectionMatcher {
        +match()
    }
    class NeighbourMatcher {
        +match()
    }
    class FamilyCompound
    class MatchingService {
        +serve()
        +clone()
        +get_meta_annotation()
        +clear_predictor()
    }
    class PageParsingService {
        +serve()
        +pass_datapoint()
        +get_meta_annotation()
        +clone()
        +clear_predictor()
    }
    class AnnotationNmsService {
        +serve()
        +clone()
        +get_meta_annotation()
        +clear_predictor()
    }
    class ImageParsingService {
        +pass_datapoint()
        +predict_dataflow()
        +clone()
        +get_meta_annotation()
        +clear_predictor()
    }
    class TableSegmentationRefinementService {
        +serve()
        +clone()
        +get_meta_annotation()
        +clear_predictor()
    }
    class MultiThreadPipelineComponent {
        +put_task()
        +start()
        +pass_datapoints()
        +predict_dataflow()
        +serve()
        +... 3 more
    }
    class SimpleTransformService {
        +serve()
        +clone()
        +get_meta_annotation()
        +clear_predictor()
    }
    class DoctectionPipe {
        +path_to_dataflow()
        +doc_to_dataflow()
        +bytes_to_dataflow()
        +dataflow_to_page()
        +analyze()
    }
    class DetectResultGenerator {
        +create_detection_result()
    }
    class SubImageLayoutService {
        +serve()
        +get_meta_annotation()
        +clone()
        +prepare_np_image()
        +clear_predictor()
    }
    class PipelineComponent {
        +set_inbound_filter()
        +serve()
        +pass_datapoint()
        +predict_dataflow()
        +clone()
        +... 5 more
    }
    class Pipeline {
        +undo()
        +analyze()
        +get_meta_annotation()
        +get_service_id_to_meta_annotation()
        +get_pipeline_info()
        +... 2 more
    }
    class LanguageDetectionService {
        +serve()
        +clone()
        +get_meta_annotation()
        +clear_predictor()
    }
    class LoadAugmentAddAnchors
    class WandbWriter {
        +write()
        +close()
    }
    class D2Trainer {
        +build_hooks()
        +build_writers()
        +build_train_loader()
        +eval_with_dd_evaluator()
        +setup_evaluator()
        +... 1 more
    }
    class DetrDerivedTrainer {
        +setup_evaluator()
        +evaluate()
    }
    class LayoutLMTrainer {
        +setup_evaluator()
        +evaluate()
    }
    class DatasetInfo {
        +get_split()
    }
    class DatasetCategories {
        +get_categories()
        +get_categories()
        +get_categories()
        +get_categories()
        +get_categories()
        +... 6 more
    }
    class DatasetBase {
        +dataset_info()
        +dataflow()
        +dataset_available()
        +is_built_in()
    }
    class _BuiltInDataset {
        +is_built_in()
    }
    class SplitDataFlow {
        +build()
    }
    class MergeDataset {
        +explicit_dataflows()
        +buffer_datasets()
        +split_datasets()
        +get_ids_by_split()
        +create_split_by_id()
    }
    class DatasetCardDict
    class DatasetCard {
        +save_dataset_card()
        +load_dataset_card()
        +as_dict()
        +update_from_pipeline()
    }
    class CustomDataset {
        +from_dataset_card()
    }
    class DatasetAdapter
    class DataFlowBaseBuilder {
        +categories()
        +categories()
        +get_split()
        +splits()
        +splits()
        +... 3 more
    }
    class AnnotationMap
    class Annotation {
        +annotation_id()
        +annotation_id()
        +get_defining_attributes()
        +set_annotation_id()
        +as_dict()
        +... 4 more
    }
    class CategoryAnnotation {
        +category_name()
        +category_name()
        +dump_sub_category()
        +get_sub_category()
        +remove_sub_category()
        +... 7 more
    }
    class ImageAnnotation {
        +get_defining_attributes()
        +from_dict()
        +get_state_attributes()
        +get_bounding_box()
        +get_summary()
        +... 1 more
    }
    class ContainerAnnotation {
        +get_defining_attributes()
        +from_dict()
    }
    class BoundingBox {
        +ulx()
        +ulx()
        +uly()
        +uly()
        +lrx()
        +... 18 more
    }
    class MetaAnnotationDict
    class MetaAnnotation {
        +as_dict()
    }
    class Image {
        +image_id()
        +image_id()
        +image()
        +image()
        +summary()
        +... 29 more
    }
    class Text_ {
        +as_dict()
    }
    class ImageAnnotationBaseView {
        +b64_image()
        +bbox()
        +viz()
        +get_attribute_names()
        +from_dict()
    }
    class Word {
        +get_attribute_names()
    }
    class Layout {
        +words()
        +text()
        +get_ordered_words()
        +text_()
        +get_attribute_names()
    }
    class Cell {
        +get_attribute_names()
    }
    class List {
        +words()
        +get_ordered_words()
        +list_items()
    }
    class Table {
        +cells()
        +column_header_cells()
        +row_header_cells()
        +kv_header_rows()
        +rows()
        +... 11 more
    }
    class ImageDefaults
    class Page {
        +get_annotation()
        +layouts()
        +words()
        +tables()
        +figures()
        +... 14 more
    }
    class FileClosingIterator
    class SerializerJsonlines {
        +load()
        +save()
    }
    class SerializerTabsepFiles {
        +load()
        +save()
    }
    class SerializerFiles {
        +load()
        +save()
    }
    class CocoParser {
        +info()
        +get_ann_ids()
        +get_cat_ids()
        +get_image_ids()
        +load_anns()
        +... 2 more
    }
    class SerializerCoco
    class DataFromList
    class DataFromIterable {
        +reset_state()
    }
    class FakeData
    class PickleSerializer {
        +dumps()
        +loads()
    }
    class MeanFromDataFlow {
        +reset_state()
        +start()
    }
    class StdFromDataFlow {
        +reset_state()
        +start()
    }
    class FlattenData
    class MapData
    class MapDataComponent
    class RepeatedData
    class ConcatData {
        +reset_state()
    }
    class JoinData {
        +reset_state()
    }
    class BatchData
    class _ParallelMapData {
        +reset_state()
        +get_data_non_strict()
        +get_data_strict()
    }
    class MultiThreadMapData {
        +reset_state()
    }
    class _Worker
    class _MultiProcessZMQDataFlow {
        +reset_state()
    }
    class MultiProcessMapData {
        +reset_state()
    }
    class _Worker
    class DataFlowReentrantGuard
    class DataFlow {
        +reset_state()
    }
    class RNGDataFlow {
        +reset_state()
    }
    class ProxyDataFlow {
        +reset_state()
    }
    class CacheData {
        +reset_state()
        +get_cache()
    }
    class CustomDataFromList
    class CustomDataFromIterable
    class HFLmTokenClassifierBase {
        +get_requirements()
        +clone()
        +get_name()
        +get_tokenizer_class_name()
        +image_to_raw_features_mapping()
        +... 1 more
    }
    class HFLmTokenClassifier {
        +predict()
        +get_wrapped_model()
        +clear_model()
    }
    class HFLmSequenceClassifierBase {
        +get_requirements()
        +clone()
        +get_name()
        +get_tokenizer_class_name()
        +image_to_raw_features_mapping()
        +... 1 more
    }
    class HFLmSequenceClassifier {
        +predict()
        +get_wrapped_model()
        +default_kwargs_for_image_to_features_mapping()
        +clear_model()
    }
    class HFLmLanguageDetector {
        +predict()
        +clear_model()
        +get_requirements()
        +get_wrapped_model()
        +clone()
        +... 1 more
    }
    class D2FrcnnDetectorMixin {
        +get_category_names()
        +get_inference_resizer()
        +get_name()
    }
    class D2FrcnnDetector {
        +predict()
        +get_requirements()
        +clone()
        +get_wrapped_model()
        +clear_model()
    }
    class D2FrcnnTracingDetector {
        +predict()
        +get_requirements()
        +clone()
        +get_category_names()
        +get_wrapped_model()
        +... 1 more
    }
    class TextractOcrDetector {
        +predict()
        +get_requirements()
        +clone()
        +get_category_names()
    }
    class ModelProfile {
        +as_dict()
    }
    class ModelCatalog {
        +get_full_path_weights()
        +get_full_path_configs()
        +get_full_path_preprocessor_configs()
        +get_model_list()
        +get_profile_list()
        +... 5 more
    }
    class ModelDownloadManager {
        +maybe_download_weights_and_configs()
        +load_model_from_hf_hub()
        +load_configs_from_hf_hub()
    }
    class HFDetrDerivedDetectorMixin {
        +get_name()
        +get_category_names()
    }
    class HFDetrDerivedDetector {
        +predict()
        +get_model()
        +get_pre_processor()
        +get_config()
        +get_requirements()
        +... 3 more
    }
    class DoctrTextlineDetectorMixin {
        +get_category_names()
        +get_name()
        +auto_select_lib()
    }
    class DoctrTextlineDetector
    class TPFrcnnDetectorMixin {
        +get_name()
        +get_category_names()
    }
    class TPFrcnnDetector {
        +get_wrapped_model()
        +predict()
        +get_requirements()
        +clone()
        +clear_model()
    }
    class Jdeskewer {
        +transform_image()
        +predict()
        +get_requirements()
        +clone()
        +get_category_names()
    }
    class FasttextLangDetectorMixin {
        +output_to_detection_result()
        +get_name()
    }
    class FasttextLangDetector
    class HFLayoutLmTokenClassifierBase {
        +get_requirements()
        +clone()
        +get_name()
        +get_tokenizer_class_name()
        +image_to_raw_features_mapping()
        +... 1 more
    }
    class HFLayoutLmTokenClassifier {
        +predict()
        +get_wrapped_model()
        +clear_model()
    }
    class HFLayoutLmv2TokenClassifier {
        +predict()
        +default_kwargs_for_image_to_features_mapping()
        +get_wrapped_model()
        +clear_model()
    }
    class HFLayoutLmv3TokenClassifier {
        +predict()
        +default_kwargs_for_image_to_features_mapping()
        +get_wrapped_model()
        +clear_model()
    }
    class HFLayoutLmSequenceClassifierBase {
        +get_requirements()
        +clone()
        +get_name()
        +get_tokenizer_class_name()
        +image_to_raw_features_mapping()
        +... 1 more
    }
    class HFLayoutLmSequenceClassifier {
        +predict()
        +get_wrapped_model()
        +clear_model()
    }
    class HFLayoutLmv2SequenceClassifier {
        +predict()
        +default_kwargs_for_image_to_features_mapping()
        +get_wrapped_model()
        +clear_model()
    }
    class HFLayoutLmv3SequenceClassifier {
        +predict()
        +default_kwargs_for_image_to_features_mapping()
        +get_wrapped_model()
        +clear_model()
    }
    class HFLiltTokenClassifier {
        +predict()
        +get_wrapped_model()
        +clear_model()
    }
    class HFLiltSequenceClassifier {
        +predict()
        +get_wrapped_model()
        +clear_model()
    }
    class ModelCategories {
        +get_categories()
        +get_categories()
        +get_categories()
        +get_categories()
        +filter_categories()
        +... 2 more
    }
    class NerModelCategories {
        +merge_bio_semantics_categories()
        +disentangle_token_class_and_tag()
    }
    class PredictorBase {
        +get_requirements()
        +clone()
        +get_model_id()
        +clear_model()
    }
    class DetectionResult
    class ObjectDetector {
        +predict()
        +accepts_batch()
        +get_category_names()
        +clone()
    }
    class PdfMiner {
        +predict()
        +get_width_height()
        +clone()
        +accepts_batch()
        +get_category_names()
    }
    class TextRecognizer {
        +predict()
        +accepts_batch()
        +get_category_names()
    }
    class TokenClassResult
    class SequenceClassResult
    class LMTokenClassifier {
        +predict()
        +default_kwargs_for_image_to_features_mapping()
        +image_to_raw_features_mapping()
        +image_to_features_mapping()
    }
    class LMSequenceClassifier {
        +predict()
        +default_kwargs_for_image_to_features_mapping()
        +image_to_raw_features_mapping()
        +image_to_features_mapping()
    }
    class LanguageDetector {
        +predict()
    }
    class ImageTransformer {
        +transform_image()
        +predict()
        +clone()
        +get_category_names()
        +transform_coords()
        +... 1 more
    }
    class DeterministicImageTransformer {
        +transform_image()
        +transform_coords()
        +inverse_transform_coords()
        +clone()
        +predict()
        +... 2 more
    }
    class PdfPlumberTextDetector {
        +predict()
        +get_requirements()
        +get_width_height()
        +get_category_names()
    }
    class Pdfmium2TextDetector {
        +predict()
        +get_requirements()
        +get_width_height()
        +get_category_names()
    }
    class TesseractOcrDetector {
        +predict()
        +get_requirements()
        +clone()
        +get_category_names()
        +set_language()
        +... 1 more
    }
    class TesseractRotationTransformer {
        +transform_image()
        +transform_coords()
        +predict()
        +get_requirements()
        +clone()
        +... 1 more
    }
    class ModelDescWithConfig {
        +get_inference_tensor_names()
    }
    class TensorpackPredictor {
        +get_predictor()
        +get_wrapped_model()
        +predict()
        +model()
    }
    class CustomResize {
        +get_transform()
    }
    class BoxProposals {
        +fg_inds()
        +fg_boxes()
        +fg_labels()
    }
    class FastRCNNHead {
        +fg_box_logits()
        +losses()
        +decoded_output_boxes()
        +decoded_output_boxes_for_true_label()
        +decoded_output_boxes_for_predicted_label()
        +... 4 more
    }
    class GeneralizedRCNN {
        +preprocess()
        +optimizer()
        +get_inference_tensor_names()
        +build_graph()
    }
    class ResNetFPNModel {
        +inputs()
        +slice_feature_and_anchors()
        +backbone()
        +rpn()
        +roi_heads()
    }
    class RPNAnchors {
        +encoded_gt_boxes()
        +decode_logits()
        +narrow_to()
    }
    class CascadeRCNNHead {
        +run_head()
        +match_box_with_gt()
        +losses()
        +decoded_output_boxes()
        +output_scores()
    }
    class LoadImageFunc
    class IsDataclass
    class StoppableThread {
        +stop()
        +stopped()
        +queue_put_stoppable()
        +queue_get_stoppable()
    }
    class ModelDesc
    class ImageAugmentor
    class Callback
    class Config
    class Tree
    class IterableDataset
    class BaseTransform {
        +apply_image()
        +apply_coords()
        +inverse_apply_coords()
        +get_category_names()
        +get_init_args()
    }
    class ResizeTransform {
        +apply_image()
        +apply_coords()
        +inverse_apply_coords()
        +get_category_names()
    }
    class InferenceResize {
        +get_transform()
    }
    class PadTransform {
        +apply_image()
        +apply_coords()
        +inverse_apply_coords()
        +clone()
        +get_category_names()
    }
    class RotationTransform {
        +set_angle()
        +set_image_width()
        +set_image_height()
        +apply_image()
        +apply_coords()
        +... 3 more
    }
    class _LazyModule
    class AttrDict {
        +to_dict()
        +from_dict()
        +update_args()
        +overwrite_config()
        +freeze()
    }
    class PDFStreamer {
        +close()
    }
    class PopplerError
    class ObjectTypes {
        +from_value()
    }
    class DefaultType
    class PageType
    class SummaryType
    class DocumentType
    class LayoutType
    class TableType
    class CellType
    class WordType
    class TokenClasses
    class BioTag
    class TokenClassWithTag
    class Relationships
    class Languages
    class DatasetType
    class LoggingRecord
    class CustomFilter {
        +filter()
    }
    class StreamFormatter {
        +format()
    }
    class FileFormatter {
        +format()
    }
    class BoundingBoxError
    class AnnotationError
    class ImageError
    class UUIDError
    class DependencyError
    class DataFlowTerminatedError
    class DataFlowResetStateNotCalledError
    class MalformedData
    class FileExtensionError
    class TesseractError
    class VizPackageHandler {
        +refresh()
        +read_image()
        +write_image()
        +encode()
        +convert_np_to_b64()
        +... 8 more
    }
    class Annotations {
        +get_layout_detect_results()
        +get_layout_annotation()
        +get_caption_annotation()
        +get_layout_ann_for_ordering()
        +get_cell_detect_results()
        +... 20 more
    }
    class DatapointCoco {
        +get_white_image()
        +get_number_anns()
        +get_width()
        +get_height()
        +get_first_ann_box()
        +... 1 more
    }
    class DatapointPubtabnet {
        +get_white_image()
        +get_width()
        +get_height()
        +get_number_cell_anns()
        +get_first_ann_box()
        +... 19 more
    }
    class DatapointProdigy {
        +get_width()
        +get_height()
        +get_number_anns()
        +get_first_ann_box()
        +get_first_ann_category()
    }
    class DatapointImage {
        +get_image_str()
        +get_text()
        +get_len_spans()
        +get_first_span()
        +get_second_span()
        +... 7 more
    }
    class DatapointPageDict {
        +get_page_dict()
    }
    class DatapointXfund {
        +get_category_names_mapping()
        +get_categories_dict()
        +get_layout_input()
        +get_layout_v2_input()
        +get_raw_layoutlm_features()
        +... 7 more
    }
    class IIITar13KJson {
        +get_category_names_mapping()
        +get_number_anns()
        +get_width()
        +get_height()
        +get_first_ann_box()
        +... 2 more
    }
    class Datapoint {
        +get_datapoint()
    }
    class Box {
        +w()
        +h()
        +cx()
        +cy()
        +area()
        +... 6 more
    }
    class WhiteImage {
        +get_bounding_box()
        +get_image_id()
        +get_image_as_b64_string()
        +get_image_as_np_array()
    }
    class CatAnn {
        +get_annotation_id()
    }
    class DatasetThreeDim
    ABC <|-- Annotation
    ABC <|-- BaseTransform
    ABC <|-- D2FrcnnDetectorMixin
    ABC <|-- DataFlowBaseBuilder
    ABC <|-- DatasetBase
    ABC <|-- DoctrTextlineDetectorMixin
    ABC <|-- FasttextLangDetectorMixin
    ABC <|-- HFDetrDerivedDetectorMixin
    ABC <|-- HFLayoutLmSequenceClassifierBase
    ABC <|-- HFLayoutLmTokenClassifierBase
    ABC <|-- HFLmSequenceClassifierBase
    ABC <|-- HFLmTokenClassifierBase
    ABC <|-- ImageTransformer
    ABC <|-- LMSequenceClassifier
    ABC <|-- LMTokenClassifier
    ABC <|-- LanguageDetector
    ABC <|-- MetricBase
    ABC <|-- ModelDescWithConfig
    ABC <|-- ObjectDetector
    ABC <|-- PdfMiner
    ABC <|-- Pipeline
    ABC <|-- PipelineComponent
    ABC <|-- PredictorBase
    ABC <|-- RNGDataFlow
    ABC <|-- TPFrcnnDetectorMixin
    ABC <|-- TensorpackPredictor
    ABC <|-- TextLineServiceMixin
    ABC <|-- TextRecognizer
    ABC <|-- _BuiltInDataset
    ABC <|-- _MultiProcessZMQDataFlow
    ABC <|-- _ParallelMapData
    Annotation <|-- CategoryAnnotation
    BaseException <|-- AnnotationError
    BaseException <|-- BoundingBoxError
    BaseException <|-- DataFlowResetStateNotCalledError
    BaseException <|-- DataFlowTerminatedError
    BaseException <|-- DependencyError
    BaseException <|-- FileExtensionError
    BaseException <|-- ImageError
    BaseException <|-- MalformedData
    BaseException <|-- UUIDError
    BaseTransform <|-- PadTransform
    BaseTransform <|-- ResizeTransform
    BaseTransform <|-- RotationTransform
    Callback <|-- EvalCallback
    CategoryAnnotation <|-- ContainerAnnotation
    CategoryAnnotation <|-- ImageAnnotation
    ClassificationMetric <|-- AccuracyMetric
    ClassificationMetric <|-- ConfusionMetric
    ClassificationMetric <|-- PrecisionMetric
    ClassificationMetric <|-- PrecisionMetricMicro
    Config <|-- CustomConfig
    D2FrcnnDetectorMixin <|-- D2FrcnnDetector
    D2FrcnnDetectorMixin <|-- D2FrcnnTracingDetector
    DataFlow <|-- ConcatData
    DataFlow <|-- DataFromIterable
    DataFlow <|-- JoinData
    DataFlow <|-- ProxyDataFlow
    DataFlow <|-- RNGDataFlow
    DataFlow <|-- _MultiProcessZMQDataFlow
    DataFlowBaseBuilder <|-- SplitDataFlow
    DataFromIterable <|-- CustomDataFromIterable
    DataFromList <|-- CustomDataFromList
    DatasetBase <|-- CustomDataset
    DatasetBase <|-- MergeDataset
    DatasetBase <|-- _BuiltInDataset
    DefaultTrainer <|-- D2Trainer
    DoctrTextlineDetectorMixin <|-- DoctrTextlineDetector
    Enum <|-- ObjectTypes
    EventWriter <|-- WandbWriter
    FasttextLangDetectorMixin <|-- FasttextLangDetector
    Filter <|-- CustomFilter
    Formatter <|-- FileFormatter
    Formatter <|-- StreamFormatter
    GeneralizedRCNN <|-- ResNetFPNModel
    HFDetrDerivedDetectorMixin <|-- HFDetrDerivedDetector
    HFLayoutLmSequenceClassifierBase <|-- HFLayoutLmSequenceClassifier
    HFLayoutLmSequenceClassifierBase <|-- HFLayoutLmv2SequenceClassifier
    HFLayoutLmSequenceClassifierBase <|-- HFLayoutLmv3SequenceClassifier
    HFLayoutLmSequenceClassifierBase <|-- HFLiltSequenceClassifier
    HFLayoutLmTokenClassifierBase <|-- HFLayoutLmTokenClassifier
    HFLayoutLmTokenClassifierBase <|-- HFLayoutLmv2TokenClassifier
    HFLayoutLmTokenClassifierBase <|-- HFLayoutLmv3TokenClassifier
    HFLayoutLmTokenClassifierBase <|-- HFLiltTokenClassifier
    HFLmSequenceClassifierBase <|-- HFLmSequenceClassifier
    HFLmTokenClassifierBase <|-- HFLmTokenClassifier
    Image <|-- Page
    ImageAnnotation <|-- ImageAnnotationBaseView
    ImageAnnotationBaseView <|-- Layout
    ImageAnnotationBaseView <|-- Word
    ImageAugmentor <|-- CustomResize
    ImageTransformer <|-- DeterministicImageTransformer
    ImageTransformer <|-- Jdeskewer
    ImageTransformer <|-- TesseractRotationTransformer
    IterableDataset <|-- DatasetAdapter
    LMSequenceClassifier <|-- HFLayoutLmSequenceClassifierBase
    LMSequenceClassifier <|-- HFLmSequenceClassifierBase
    LMTokenClassifier <|-- HFLayoutLmTokenClassifierBase
    LMTokenClassifier <|-- HFLmTokenClassifierBase
    LanguageDetector <|-- FasttextLangDetectorMixin
    LanguageDetector <|-- HFLmLanguageDetector
    Layout <|-- Cell
    Layout <|-- List
    Layout <|-- Table
    MapData <|-- MapDataComponent
    MetricBase <|-- ClassificationMetric
    MetricBase <|-- CocoMetric
    MetricBase <|-- TedsMetric
    ModelCategories <|-- NerModelCategories
    ModelDesc <|-- ModelDescWithConfig
    ModelDescWithConfig <|-- GeneralizedRCNN
    ModuleType <|-- _LazyModule
    ObjectDetector <|-- D2FrcnnDetectorMixin
    ObjectDetector <|-- DoctrTextlineDetectorMixin
    ObjectDetector <|-- HFDetrDerivedDetectorMixin
    ObjectDetector <|-- TPFrcnnDetectorMixin
    ObjectDetector <|-- TesseractOcrDetector
    ObjectDetector <|-- TextractOcrDetector
    ObjectTypes <|-- BioTag
    ObjectTypes <|-- CellType
    ObjectTypes <|-- DatasetType
    ObjectTypes <|-- DefaultType
    ObjectTypes <|-- DocumentType
    ObjectTypes <|-- Languages
    ObjectTypes <|-- LayoutType
    ObjectTypes <|-- PageType
    ObjectTypes <|-- Relationships
    ObjectTypes <|-- SummaryType
    ObjectTypes <|-- TableType
    ObjectTypes <|-- TokenClassWithTag
    ObjectTypes <|-- TokenClasses
    ObjectTypes <|-- WordType
    PdfMiner <|-- PdfPlumberTextDetector
    PdfMiner <|-- Pdfmium2TextDetector
    Pipeline <|-- DoctectionPipe
    PipelineComponent <|-- AnnotationNmsService
    PipelineComponent <|-- ImageCroppingService
    PipelineComponent <|-- ImageLayoutService
    PipelineComponent <|-- LMSequenceClassifierService
    PipelineComponent <|-- LMTokenClassifierService
    PipelineComponent <|-- LanguageDetectionService
    PipelineComponent <|-- MatchingService
    PipelineComponent <|-- MultiThreadPipelineComponent
    PipelineComponent <|-- PageParsingService
    PipelineComponent <|-- PubtablesSegmentationService
    PipelineComponent <|-- SimpleTransformService
    PipelineComponent <|-- SubImageLayoutService
    PipelineComponent <|-- TableSegmentationRefinementService
    PipelineComponent <|-- TableSegmentationService
    PipelineComponent <|-- TextExtractionService
    PipelineComponent <|-- TextLineServiceMixin
    PrecisionMetric <|-- F1Metric
    PrecisionMetric <|-- RecallMetric
    PrecisionMetricMicro <|-- F1MetricMicro
    PrecisionMetricMicro <|-- RecallMetricMicro
    PredictorBase <|-- ImageTransformer
    PredictorBase <|-- LMSequenceClassifier
    PredictorBase <|-- LMTokenClassifier
    PredictorBase <|-- LanguageDetector
    PredictorBase <|-- ObjectDetector
    PredictorBase <|-- PdfMiner
    PredictorBase <|-- TextRecognizer
    Process <|-- _Worker
    Protocol <|-- IsDataclass
    Protocol <|-- LoadImageFunc
    ProxyDataFlow <|-- BatchData
    ProxyDataFlow <|-- CacheData
    ProxyDataFlow <|-- FlattenData
    ProxyDataFlow <|-- MapData
    ProxyDataFlow <|-- MeanFromDataFlow
    ProxyDataFlow <|-- RepeatedData
    ProxyDataFlow <|-- StdFromDataFlow
    ProxyDataFlow <|-- _ParallelMapData
    RNGDataFlow <|-- DataFromList
    RNGDataFlow <|-- FakeData
    RuntimeError <|-- PopplerError
    RuntimeError <|-- TesseractError
    StoppableThread <|-- _Worker
    TPFrcnnDetectorMixin <|-- TPFrcnnDetector
    TensorpackPredictor <|-- TPFrcnnDetector
    TextLineServiceMixin <|-- TextLineService
    TextLineServiceMixin <|-- TextOrderService
    Thread <|-- StoppableThread
    Trainer <|-- DetrDerivedTrainer
    Trainer <|-- LayoutLMTrainer
    Tree <|-- TableTree
    TypedDict <|-- DatasetCardDict
    TypedDict <|-- MetaAnnotationDict
    _MultiProcessZMQDataFlow <|-- MultiProcessMapData
    _ParallelMapData <|-- MultiProcessMapData
    _ParallelMapData <|-- MultiThreadMapData
    str <|-- ObjectTypes
```

### File Structure

| File | Classes | Functions | Methods | Interfaces | Enums |
|------|---------|-----------|---------|------------|-------|
| deepdoctection/analyzer/config.py | 0 | 1 | 0 | 0 | 0 |
| deepdoctection/analyzer/dd.py | 0 | 2 | 0 | 0 | 0 |
| deepdoctection/analyzer/factory.py | 1 | 0 | 69 | 0 | 0 |
| deepdoctection/dataflow/base.py | 4 | 0 | 11 | 0 | 0 |
| deepdoctection/dataflow/common.py | 7 | 0 | 23 | 0 | 0 |
| deepdoctection/dataflow/custom.py | 3 | 0 | 9 | 0 | 0 |
| deepdoctection/dataflow/custom_serialize.py | 7 | 1 | 23 | 0 | 0 |
| deepdoctection/dataflow/parallel_map.py | 6 | 4 | 29 | 0 | 0 |
| deepdoctection/dataflow/serialize.py | 4 | 0 | 12 | 0 | 0 |
| deepdoctection/dataflow/stats.py | 2 | 0 | 8 | 0 | 0 |
| deepdoctection/datapoint/annotation.py | 5 | 1 | 32 | 0 | 0 |
| deepdoctection/datapoint/box.py | 1 | 12 | 27 | 0 | 0 |
| deepdoctection/datapoint/convert.py | 0 | 7 | 0 | 0 | 0 |
| deepdoctection/datapoint/image.py | 3 | 0 | 38 | 0 | 0 |
| deepdoctection/datapoint/view.py | 9 | 1 | 59 | 0 | 0 |
| deepdoctection/datasets/adapter.py | 1 | 0 | 4 | 0 | 0 |
| deepdoctection/datasets/base.py | 7 | 0 | 30 | 0 | 0 |
| deepdoctection/datasets/dataflow_builder.py | 1 | 0 | 9 | 0 | 0 |
| deepdoctection/datasets/info.py | 2 | 5 | 14 | 0 | 0 |
| deepdoctection/datasets/instances/doclaynet.py | 4 | 0 | 8 | 0 | 0 |
| deepdoctection/datasets/instances/fintabnet.py | 2 | 0 | 4 | 0 | 0 |
| deepdoctection/datasets/instances/funsd.py | 2 | 1 | 4 | 0 | 0 |
| deepdoctection/datasets/instances/iiitar13k.py | 2 | 0 | 4 | 0 | 0 |
| deepdoctection/datasets/instances/layouttest.py | 2 | 0 | 4 | 0 | 0 |
| deepdoctection/datasets/instances/publaynet.py | 2 | 0 | 4 | 0 | 0 |
| deepdoctection/datasets/instances/pubtables1m.py | 4 | 0 | 8 | 0 | 0 |
| deepdoctection/datasets/instances/pubtabnet.py | 2 | 0 | 4 | 0 | 0 |
| deepdoctection/datasets/instances/rvlcdip.py | 2 | 0 | 4 | 0 | 0 |
| deepdoctection/datasets/instances/xfund.py | 2 | 0 | 4 | 0 | 0 |
| deepdoctection/datasets/registry.py | 0 | 2 | 0 | 0 | 0 |
| deepdoctection/datasets/save.py | 0 | 1 | 0 | 0 | 0 |
| deepdoctection/eval/accmetric.py | 9 | 7 | 12 | 0 | 0 |
| deepdoctection/eval/base.py | 1 | 0 | 6 | 0 | 0 |
| deepdoctection/eval/cocometric.py | 1 | 1 | 5 | 0 | 0 |
| deepdoctection/eval/eval.py | 2 | 0 | 14 | 0 | 0 |
| deepdoctection/eval/registry.py | 0 | 1 | 0 | 0 | 0 |
| deepdoctection/eval/tedsmetric.py | 4 | 1 | 12 | 0 | 0 |
| deepdoctection/eval/tp_eval_callback.py | 1 | 1 | 6 | 0 | 0 |
| deepdoctection/extern/base.py | 14 | 0 | 51 | 0 | 0 |
| deepdoctection/extern/d2detect.py | 3 | 3 | 23 | 0 | 0 |
| deepdoctection/extern/deskew.py | 1 | 0 | 6 | 0 | 0 |
| deepdoctection/extern/doctrocr.py | 4 | 5 | 28 | 0 | 0 |
| deepdoctection/extern/fastlang.py | 2 | 0 | 8 | 0 | 0 |
| deepdoctection/extern/hfdetr.py | 2 | 2 | 13 | 0 | 0 |
| deepdoctection/extern/hflayoutlm.py | 10 | 3 | 53 | 0 | 0 |
| deepdoctection/extern/hflm.py | 5 | 2 | 33 | 0 | 0 |
| deepdoctection/extern/model.py | 3 | 2 | 16 | 0 | 0 |
| deepdoctection/extern/pdftext.py | 2 | 1 | 10 | 0 | 0 |
| deepdoctection/extern/pt/nms.py | 0 | 1 | 0 | 0 | 0 |
| deepdoctection/extern/pt/ptutils.py | 0 | 1 | 0 | 0 | 0 |
| deepdoctection/extern/tessocr.py | 2 | 9 | 14 | 0 | 0 |
| deepdoctection/extern/texocr.py | 1 | 2 | 5 | 0 | 0 |
| deepdoctection/extern/tp/tfutils.py | 0 | 4 | 0 | 0 | 0 |
| deepdoctection/extern/tp/tpcompat.py | 2 | 0 | 8 | 0 | 0 |
| deepdoctection/extern/tp/tpfrcnn/common.py | 1 | 4 | 2 | 0 | 0 |
| deepdoctection/extern/tp/tpfrcnn/config/config.py | 0 | 2 | 0 | 0 | 0 |
| deepdoctection/extern/tp/tpfrcnn/modeling/backbone.py | 0 | 11 | 0 | 0 | 0 |
| deepdoctection/extern/tp/tpfrcnn/modeling/generalized_rcnn.py | 2 | 0 | 9 | 0 | 0 |
| deepdoctection/extern/tp/tpfrcnn/modeling/model_box.py | 1 | 5 | 3 | 0 | 0 |
| deepdoctection/extern/tp/tpfrcnn/modeling/model_cascade.py | 1 | 0 | 6 | 0 | 0 |
| deepdoctection/extern/tp/tpfrcnn/modeling/model_fpn.py | 0 | 6 | 0 | 0 | 0 |
| deepdoctection/extern/tp/tpfrcnn/modeling/model_frcnn.py | 2 | 10 | 14 | 0 | 0 |
| deepdoctection/extern/tp/tpfrcnn/modeling/model_mrcnn.py | 0 | 5 | 0 | 0 | 0 |
| deepdoctection/extern/tp/tpfrcnn/modeling/model_rpn.py | 0 | 4 | 0 | 0 | 0 |
| deepdoctection/extern/tp/tpfrcnn/predict.py | 0 | 3 | 0 | 0 | 0 |
| deepdoctection/extern/tp/tpfrcnn/preproc.py | 0 | 4 | 0 | 0 | 0 |
| deepdoctection/extern/tp/tpfrcnn/utils/box_ops.py | 0 | 3 | 0 | 0 | 0 |
| deepdoctection/extern/tp/tpfrcnn/utils/np_box_ops.py | 0 | 4 | 0 | 0 | 0 |
| deepdoctection/extern/tpdetect.py | 2 | 0 | 10 | 0 | 0 |
| deepdoctection/mapper/cats.py | 0 | 7 | 0 | 0 | 0 |
| deepdoctection/mapper/cocostruct.py | 0 | 2 | 0 | 0 | 0 |
| deepdoctection/mapper/d2struct.py | 0 | 5 | 0 | 0 | 0 |
| deepdoctection/mapper/hfstruct.py | 1 | 1 | 2 | 0 | 0 |
| deepdoctection/mapper/laylmstruct.py | 1 | 7 | 2 | 0 | 0 |
| deepdoctection/mapper/maputils.py | 3 | 2 | 9 | 0 | 0 |
| deepdoctection/mapper/match.py | 0 | 2 | 0 | 0 | 0 |
| deepdoctection/mapper/misc.py | 0 | 7 | 0 | 0 | 0 |
| deepdoctection/mapper/pascalstruct.py | 0 | 1 | 0 | 0 | 0 |
| deepdoctection/mapper/prodigystruct.py | 0 | 2 | 0 | 0 | 0 |
| deepdoctection/mapper/pubstruct.py | 0 | 11 | 0 | 0 | 0 |
| deepdoctection/mapper/tpstruct.py | 0 | 2 | 0 | 0 | 0 |
| deepdoctection/mapper/xfundstruct.py | 0 | 1 | 0 | 0 | 0 |
| deepdoctection/pipe/anngen.py | 1 | 0 | 12 | 0 | 0 |
| deepdoctection/pipe/base.py | 2 | 0 | 24 | 0 | 0 |
| deepdoctection/pipe/common.py | 8 | 0 | 32 | 0 | 0 |
| deepdoctection/pipe/concurrency.py | 1 | 0 | 11 | 0 | 0 |
| deepdoctection/pipe/doctectionpipe.py | 1 | 4 | 7 | 0 | 0 |
| deepdoctection/pipe/language.py | 1 | 0 | 6 | 0 | 0 |
| deepdoctection/pipe/layout.py | 1 | 1 | 6 | 0 | 0 |
| deepdoctection/pipe/lm.py | 2 | 0 | 16 | 0 | 0 |
| deepdoctection/pipe/order.py | 5 | 0 | 26 | 0 | 0 |
| deepdoctection/pipe/refine.py | 1 | 12 | 5 | 0 | 0 |
| deepdoctection/pipe/segment.py | 4 | 11 | 9 | 0 | 0 |
| deepdoctection/pipe/sub_layout.py | 2 | 0 | 13 | 0 | 0 |
| deepdoctection/pipe/text.py | 1 | 0 | 8 | 0 | 0 |
| deepdoctection/pipe/transform.py | 1 | 0 | 6 | 0 | 0 |
| deepdoctection/train/d2_frcnn_train.py | 2 | 3 | 10 | 0 | 0 |
| deepdoctection/train/hf_detr_train.py | 1 | 1 | 3 | 0 | 0 |
| deepdoctection/train/hf_layoutlm_train.py | 1 | 5 | 3 | 0 | 0 |
| deepdoctection/train/tp_frcnn_train.py | 1 | 3 | 2 | 0 | 0 |
| deepdoctection/utils/__init__.py | 0 | 1 | 0 | 0 | 0 |
| deepdoctection/utils/concurrency.py | 1 | 3 | 5 | 0 | 0 |
| deepdoctection/utils/context.py | 0 | 3 | 0 | 0 | 0 |
| deepdoctection/utils/develop.py | 0 | 2 | 0 | 0 | 0 |
| deepdoctection/utils/env_info.py | 0 | 9 | 0 | 0 | 0 |
| deepdoctection/utils/error.py | 10 | 0 | 2 | 0 | 0 |
| deepdoctection/utils/file_utils.py | 1 | 60 | 5 | 0 | 0 |
| deepdoctection/utils/fs.py | 1 | 17 | 1 | 0 | 0 |
| deepdoctection/utils/identifier.py | 0 | 4 | 0 | 0 | 0 |
| deepdoctection/utils/logger.py | 4 | 8 | 5 | 0 | 0 |
| deepdoctection/utils/metacfg.py | 1 | 3 | 10 | 0 | 0 |
| deepdoctection/utils/mocks.py | 6 | 5 | 3 | 0 | 0 |
| deepdoctection/utils/pdf_utils.py | 2 | 10 | 6 | 0 | 0 |
| deepdoctection/utils/settings.py | 15 | 7 | 2 | 0 | 0 |
| deepdoctection/utils/tqdm.py | 0 | 2 | 0 | 0 | 0 |
| deepdoctection/utils/transform.py | 5 | 4 | 27 | 0 | 0 |
| deepdoctection/utils/types.py | 1 | 0 | 0 | 0 | 0 |
| deepdoctection/utils/utils.py | 0 | 8 | 0 | 0 | 0 |
| deepdoctection/utils/viz.py | 1 | 3 | 40 | 0 | 0 |
| scripts/export_tracing_d2.py | 0 | 2 | 0 | 0 | 0 |
| scripts/reduce_d2.py | 0 | 1 | 0 | 0 | 0 |
| scripts/reduce_tp.py | 0 | 1 | 0 | 0 | 0 |
| scripts/tp2d2.py | 0 | 1 | 0 | 0 | 0 |
| setup.py | 0 | 2 | 0 | 0 | 0 |
| tests/conftest.py | 0 | 50 | 0 | 0 | 0 |
| tests/data.py | 1 | 5 | 26 | 0 | 0 |
| tests/dataflow/conftest.py | 1 | 7 | 0 | 0 | 0 |
| tests/datapoint/conftest.py | 3 | 4 | 17 | 0 | 0 |
| tests/datasets/instances/conftest.py | 0 | 2 | 0 | 0 | 0 |
| tests/eval/conftest.py | 0 | 5 | 0 | 0 | 0 |
| tests/extern/conftest.py | 0 | 10 | 0 | 0 | 0 |
| tests/extern/data.py | 0 | 1 | 0 | 0 | 0 |
| tests/mapper/conftest.py | 0 | 30 | 0 | 0 | 0 |
| tests/mapper/data.py | 7 | 0 | 68 | 0 | 0 |
| tests/train/conftest.py | 1 | 1 | 5 | 0 | 0 |
| tests_d2/conftest.py | 0 | 3 | 0 | 0 | 0 |

