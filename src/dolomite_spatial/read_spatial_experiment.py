import json
import os

import dolomite_base as dl
import dolomite_sce as dlsce
import h5py
from biocframe import BiocFrame
from dolomite_base.read_object import read_object_registry
from spatialexperiment import SpatialExperiment, construct_spatial_image_class

read_object_registry["spatial_experiment"] = "dolomite_spatial.read_spatial_experiment"


def read_spatial_experiment(path: str, metadata: dict, **kwargs) -> SpatialExperiment:
    """Load a
    :py:class:`~spatialexperiment.SpatialExperiment.SpatialExperiment`
    from its on-disk representation.

    This method should generally not be called directly but instead be invoked by
    :py:meth:`~dolomite_base.read_object.read_object`.

    Args:
        path:
            Path to the directory containing the object.

        metadata:
            Metadata for the object.

        kwargs:
            Further arguments.

    Returns:
        A
        :py:class:`~spatialexperiment.SpatialExperiment.SpatialExperiment`
        with file-backed arrays in the assays.
    """
    print("in spatial")
    sce = dlsce.read_single_cell_experiment(path, metadata=metadata, **kwargs)

    spe = SpatialExperiment(
        assays=sce.get_assays(),
        row_data=sce.get_row_data(),
        column_data=sce.get_column_data(),
        row_ranges=sce.get_row_ranges(),
        metadata=sce.get_metadata(),
        main_experiment_name=sce.get_main_experiment_name(),
        reduced_dims=sce.get_reduced_dims(),
        alternative_experiments=sce.get_alternative_experiments(),
    )

    _sp_coords_path = os.path.join(path, "coordinates")
    if os.path.exists(_sp_coords_path):
        _coords = dl.alt_read_object(_sp_coords_path, **kwargs)
        spe = spe.set_spatial_coordinates(_coords)
    else:
        raise FileNotFoundError(f"cannot find spatial coordinates at {path}.")

    _img_path = os.path.join(path, "images")
    if os.path.exists(_img_path):
        with h5py.File(os.path.join(_img_path, "mapping.h5"), "r") as handle:
            ghandle = handle["spatial_experiment"]

            sample_names = dl.load_vector_from_hdf5(ghandle["sample_names"], expected_type=str, report_1darray=True)
            column_samples = dl.load_vector_from_hdf5(ghandle["column_samples"], expected_type=int, report_1darray=True)

            image_samples = dl.load_vector_from_hdf5(ghandle["image_samples"], expected_type=int, report_1darray=True)

            image_ids = dl.load_vector_from_hdf5(ghandle["image_ids"], expected_type=str, report_1darray=True)
            image_formats = dl.load_vector_from_hdf5(ghandle["image_formats"], expected_type=str, report_1darray=True)

            image_scale_factors = dl.load_vector_from_hdf5(
                ghandle["image_scale_factors"], expected_type=float, report_1darray=True
            )

        # replace column names; just in case
        spe = spe.set_column_data(spe.get_column_data().set_column("sample_id", sample_names[column_samples]))

        image_data = []
        if len(image_samples) > 0:
            for i, _ in enumerate(image_samples):
                # TODO: write reader for SpatialImage class
                image_data.append(construct_spatial_image_class(os.path.join(_img_path, f"{i}.{image_formats[i].tolower()}")))

        _image_frame = BiocFrame(
            {
                "sample_id": sample_names[image_samples],
                "image_id": image_ids,
                "data": image_data,
                "scale_factor": image_scale_factors,
            }
        )

        # add image data
        spe = spe.set_image_data(_image_frame)

    return spe
