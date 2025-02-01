[![PyPI-Server](https://img.shields.io/pypi/v/dolomite-spatial.svg)](https://pypi.org/project/dolomite-spatial/)
![Unit tests](https://github.com/BiocPy/dolomite-spatial/actions/workflows/run-tests.yml/badge.svg)

# Save and write `SpatialExperiment`'s in Python

## Introduction

The **dolomite-spatial** package is the Python counterpart to the [**alabaster.spatial**](https://github.com/ArtifactDB/alabaster.spatial) R package,
providing methods for saving/reading `SpatialExperiment` objects within the [**dolomite** framework](https://github.com/ArtifactDB/dolomite-base).

## Quick start

Let's mock up a `SpatialExperiment` that contains reduced dimensions and alternative experiments,

```python
from spatialexperiment import SpatialExperiment, construct_spatial_image_class

import biocframe
import numpy as np

spe = SpatialExperiment(
    assays={"counts": np.random.rand(1000, 200)},
    row_data=biocframe.BiocFrame(
        {"foo": np.random.rand(1000), "bar": np.random.rand(1000)}
    ),
    column_data=biocframe.BiocFrame(
        {"whee": np.random.rand(200), "stuff": np.random.rand(200), "sample_id": ["sample_1", "sample_2"] * 100}
    ),
    reduced_dims={"tsnooch": np.random.rand(200, 4)},
    spatial_coords = np.array(
        [
            np.random.uniform(low=0.0, high=100.0, size=200),
            np.random.uniform(low=0.0, high=100.0, size=200)
        ]
    ).transpose(),
    img_data = biocframe.BiocFrame({
        "sample_id": ["sample_1", "sample_1", "sample_2"],
        "image_id": ["aurora", "dice", "desert"],
        "data": [
            construct_spatial_image_class("biocpy/spatialexperiment/tests/images/sample_image1.jpg"),
            construct_spatial_image_class("biocpy/spatialexperiment/tests/images/sample_image2.png"),
            construct_spatial_image_class("biocpy/spatialexperiment/tests/images/sample_image3.jpg"),
        ],
        "scale_factor": [1, 1, 1],
    })
)

print(spe)
```

Now we can save it:

```python
from dolomite_base import save_object
import dolomite_spatial
import os
from tempfile import mkdtemp

path = os.path.join(mkdtemp(), "test")
save_object(spe, path)
```

And load it again, e,g., in a new session:

```python
from dolomite_base import read_object

roundtrip = read_object(path)
print(roundtrip)
```
    ## output
    class: SpatialExperiment
    dimensions: (1000, 200)
    assays(1): ['counts']
    row_data columns(2): ['foo', 'bar']
    row_names(0):  
    column_data columns(3): ['whee', 'stuff', 'sample_id']
    column_names(0):  
    main_experiment_name:  
    reduced_dims(1): ['tsnooch']
    alternative_experiments(0): []
    row_pairs(0): []
    column_pairs(0): []
    metadata(0): 
    spatial_coords columns(0): []
    img_data columns(4): ['sample_id', 'image_id', 'data', 'scale_factor']

## Note

This project has been set up using [BiocSetup](https://github.com/biocpy/biocsetup)
and [PyScaffold](https://pyscaffold.org/).
