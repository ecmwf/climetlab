Machine learning tools
======================

.. warning::

     This part of CliMetLab is still a work in progress. Documentation and code behaviour will change.

.. todo::

     TODO: Develop and document machine learning related tools


to_tfdataset()
--------------

To use a CliMetLab dataset with tensorflow,
use the ``_to_tfdataset()`` method.

    .. code-block:: python

        >>> import climetlab as cml
        >>> ds = cml.load_dataset(x)
        >>> x = ds.to_tfdataset(options)
        >>> model.fit(x, ....)

The discussion is still open to decide whether ``to_dataset()`` returns:

 - ``tf.keras.utils.experimental.DatasetCreator``
 - ``tf.data.Dataset``
 - ``tf.keras.utils.Sequence``
 - A custom CliMetLab class

PyTorch support
---------------

.. todo::

     A long-term goal of CliMetLab is to provide a easy way to use a dataset with Pytorch.
     A merge request within this respect would be welcome.
     The CliMetLab API (exposed to the end-user) should be mostly identical for Tensorflow or Pytorch.
