# ZS4IE: A Toolkit for Zero-Shot Information Extraction with Simple Verbalizations

Please cite the following paper if you use ZS4IE in your research. Bibtex Citation coming soon.

## Prepare conda environment

You'll need a Linux machine with CUDA enabled.

Please install conda (e.g., https://docs.conda.io/en/latest/miniconda.html) and activate it.

First, create a conda environment from `a2t_env.yml` by running the commands below. It will install pytorch/python/cuda and the dependencies. 

```
conda env create -f a2t_env.yml
conda activate a2t_env
```

Second, install stanza from the dev branch by running the following:

```
git clone https://github.com/stanfordnlp/stanza.git
cd stanza
git checkout dev
pip install .
cd ..
```

Third, you'll need to download stanza's current model.

```
python3
import stanza
stanza.download('en')
```

Typically the file will be saved to `~/stanza_resources`, we'll need it later.

Last, you need to change the configuration file `backend/config_a2t_basic_nlp.yml`. You'll only need to change 3 lines:

1. Change `/home/ubuntu/zs4ie/serif/model/impl/stanza_adapter2/a2t_compound_basic_nlp.py` to the absolute path of the same file (`a2t_compound_basic_nlp.py`) in your local copy of zs4ie. 
2. Change `/home/ubuntu/stanza_resources` to the absolute path to your local `stanza_resources` directory.
3. Change `/home/ubuntu/coref-spanbert-large-2021.03.10.tar.gz` to the absolute path of this file (your local copy). This file can be downloaded from [https://storage.googleapis.com/allennlp-public-models/coref-spanbert-large-2021.03.10.tar.gz](https://storage.googleapis.com/allennlp-public-models/coref-spanbert-large-2021.03.10.tar.gz)

Then you are good to go.

## Start ZS4IE service

Run the following command to start the ZS4IE web server:

```
env TOKENIZERS_PARALLELISM=false python3 backend/a2t_service_backend.py
```

Now you can access the service either locally (from the same machine where the service is started) or remotely via a web browser. Locally you need to open your browser and go to

[http://localhost:5008/index.html](http://localhost:5008/index.html)

Please do include `index.html` in the URL. When open the page in your browser for the first time, it will take about 1 minute for the page to show up. This is because the server will need to download pre-trained models from the web and then load all models into memory/GPU.


## Acknowledgments

This work was supported by the Office of the Director of National Intelligence (ODNI), Intelligence Advanced Research Projects Activity (IARPA), via IARPA Contract No. 2019-19051600006 under the BETTER program. The views, opinions, and/or findings expressed are those of the author(s) and should not be interpreted as representing the official views or policies, either expressed or implied, of ODNI, IARPA, or the U.S. Government. The U.S. Government is authorized to reproduce and distribute reprints for governmental purposes notwithstanding any copyright annotation therein.
