.. automodule:: perfsprocket

Interacting with Files
======================

FileABC (Abstract Base Class)
-----------------------------

Protocol defining the interface for a file and supplying some base implementations.
File ABC is a pure Protocol class, only defining inputs and returns. All methods are
required when subclassing this protocol.

:class:`FileBase` offers partial implementation with sane defaults that both
:class:`File` and :class:`FileSequence` build off of.

.. autoclass:: FileABC
   :special-members: __init__, __iter__, __len__, __repr__
   :members:

   The following is a table of required / optional overrides

FileBase
--------

Offers sane base implementations of most :class:`FileABC`.

.. autoclass:: FileBase
   :members: init_new, move_iter, move, copy_iter, copy, rename, delete_iter, delete, chmod_iter,
       chmod

   The base implementations rely on some *additional*, simpler methods annotated below.
   Only these and implemented base methods are detailed

   ============================  ===============
   method                        required?
   ============================  ===============
   :func:`FileBase.init_new`     NEW - required
   :func:`FileABC.__iter__`      required
   :func:`FileABC.__len__`       required
   :func:`FileABC.path`          required
   :func:`FileABC.name`          required
   :func:`FileABC.rename_iter`   required
   :func:`FileBase.__repr__`     has default
   :func:`FileBase.move_iter`    has default
   :func:`FileBase.move`         has default
   :func:`FileBase.copy_iter`    has default
   :func:`FileBase.copy`         has default
   :func:`FileBase.rename`       has default
   :func:`FileBase.delete_iter`  has default
   :func:`FileBase.delete`       has default
   :func:`FileBase.chmod_iter`   has default
   :func:`FileBase.chmod`        has default
   ============================  ===============

File
----

The :class:`File` class is an implementation of :class:`FileABC` meant for interacting
with single files.

.. autoclass:: File
   :special-members: __init__,
   :members:

   ============   ===============================
   Magic Method   return
   ============   ===============================
   ``__iter__``   yields single file path
   ``__len__``    always ``1``
   ============   ===============================

FileSequence
------------

The :class:`File` class is an implementation of :class:`FileABC` meant for interacting
with file sequences.

File sequences are not arbitrary lists of files. They are numbered files in the same
directory, named in a way :class:`SeqName` can parse. Ex: `photo_0030.jpg`

Getting a Specific File Path.

.. autoclass:: FileSequence
   :special-members: __init__
   :members:

   ===============   ==============================================================
   Magic Method      return
   ===============   ==============================================================
   ``__iter__``      yields each path in file num order
   ``__len__``       number of files in sequence (theoretical, does not check disk)
   ``__getitem__``   returns path by index (not file num, 0 is first)
   ===============   ==============================================================

   Getting a Specific File
   -----------------------

   Specific file paths can be accessed via index:

   >>> sequence[0]
   PosixPath('/Volumes/disk/folder/photo_100.jpeg')
   >>> sequence[-1]
   PosixPath('/Volumes/disk/folder/photo_200.jpeg')

   If you wish to return by file number instead of a 0-based index, use
   :func:`FileSequence.files`:

   >>> sequence.files[150]
   PosixPath('/Volumes/disk/folder/photo_150.jpeg')
   >>> sequence.files[120]
   PosixPath('/Volumes/disk/folder/photo_120.jpeg')
   >>> sequence.files[201]
   Traceback (most recent call last):
      ...
   IndexError

   Getting a Sub-sequence
   ----------------------

   Both ways can be sliced. A slice returns a new :class:`FileSequence` of the desired
   bounds. As such, the slice ``step`` is always assumed to be ``None``.

   >>> sequence[20:51]
   <FileSequence: '/Volumes/disk/folder/photo_[120-150].jpeg'>
   >>> sequence.files[120:151]
   <FileSequence: '/Volumes/disk/folder/photo_[120-150].jpeg'>
