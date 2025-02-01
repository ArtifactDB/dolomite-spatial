import json
import os

import dolomite_base as dl
import dolomite_se as dlse
import h5py
import numpy as np
from PIL import Image
from spatialexperiment import RemoteSpatialImage, SpatialExperiment, StoredSpatialImage

from .save_image import save_image


@dl.save_object.register
@dl.validate_saves
def save_spatial_experiment(
    x: SpatialExperiment,
    path: str,
    img_data_args: dict = None,
    **kwargs,
):
    """Method for saving
    :py:class:`~spatialexperiment.SpatialExperiment.SpatialExperiment`
    objects to their corresponding file representations, see
    :py:meth:`~dolomite_base.save_object.save_object` for details.

    Args:
        x:
            Object to be staged.

        path:
            Path to a directory in which to save ``x``.

        img_data_args:
            Further arguments to pass to the ``save_object`` method for the
            image data.

        kwargs:
            Further arguments.

    Returns:
        ``x`` is saved to path.
    """
    if img_data_args is None:
        img_data_args = {}

    dlse.save_single_cell_experiment(x, path, **kwargs)

    # Modify OBJECT
    _info = dl.read_object_file(path)
    _info["spatial_experiment"] = {"version": "1.2"}
    dl.save_object_file(path, "spatial_experiment", _info)

    # save spatial_coordinates
    _scoords = x.get_spatial_coordinates()
    _scoords_path = os.path.join(path, "coordinates")
    os.mkdir(_scoords_path)
    dl.alt_save_object(_scoords, path=_scoords_path, **kwargs)

    # save image data
    _imgdata = x.get_image_data()
    if len(_imgdata) > 0:
        _imgdata_path = os.path.join(path, "images")
        os.mkdir(_imgdata_path)

        with h5py.File(os.path.join(path, "mapping.h5"), "w") as handle:
            ghandle = handle.create_group("spatial_experiment")

            sample_names = list(set(_imgdata.get_column("sample_ids")))
            dl.write_string_vector_to_hdf5(ghandle, name="sample_names", x=sample_names)

            column_samples = [sample_names.index(z) for z in x.get_column_data().get_column("sample_ids")]
            dl.write_integer_vector_to_hdf5(ghandle, name="column_samples", x=column_samples, h5type="u4")

            image_samples = [sample_names.index(z) for z in _imgdata.get_column("sample_ids")]
            dl.write_integer_vector_to_hdf5(ghandle, name="image_samples", x=image_samples, h5type="u4")

            dl.write_boolean_vector_to_hdf5(ghandle, name="image_ids", x=_imgdata.get_column("image_ids"))
            dl.write_float_vector_to_hdf5(ghandle, name="image_scale_factors", x=_imgdata.get_column("scale_factor"))

            # write images themselves
            # assuming easy formats for now
            _images = _imgdata.get_column("data")
            formats = [None] * len(_images)

            for i, cur_img in enumerate(_images):
                format = None

                # Check if the object has a custom `save_object` method
                if hasattr(cur_img, "save_object"):
                    cur_img.save_object(os.path.join(_imgdata_path, str(i)))
                    format = "OTHER"
                else:
                    if isinstance(cur_img, StoredSpatialImage):
                        format = save_image(cur_img.img_source(), _imgdata_path, i)
                    elif isinstance(cur_img, RemoteSpatialImage):
                        format = save_image(cur_img.img_source(path=True), _imgdata_path, i)

                    # If format is still None, fall back to raster processing
                    if format is None:
                        raster = cur_img.img_raster()
                        # Convert raster to RGB array
                        rgb_array = np.array(raster)
                        if rgb_array.ndim == 2:  # If grayscale, convert to RGB
                            rgb_array = np.stack([rgb_array] * 3, axis=-1)

                        # Normalize values to [0, 1]
                        rgb_array = rgb_array.astype(float) / 255.0

                        # Save as PNG
                        dest = os.path.join(_imgdata_path, f"{i}.png")

                        # Convert back to 8-bit RGB and save
                        img = Image.fromarray((rgb_array * 255).astype(np.uint8))
                        img.save(dest, format="PNG")
                        format = "PNG"

                formats[i] = format
            
            dl.write_string_vector_to_hdf5(ghandle, name="image_formats", x=formats)

    return
