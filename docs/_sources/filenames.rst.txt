.. automodule:: perfsprocket

Parsing File Names
==================

NameABC
-------

Protocol defining methods / fields that should be available on an Implementation.

Concrete implementations should be FROZEN dataclasses, alterations are expected to be
made with :func:`NameABC.alter`

.. autoclass:: NameABC
   :members:

   ========================================= ===========
   method                                    required?
   ========================================= ===========
   name (attribute)                          required
   extension (attribute)                     required
   :func:`NameABC.from_path` (class method)  required
   :func:`NameABC.alter`                     required
   :func:`NameABC.formatted`                 required
   :finc:`NameABC.__str__`                   has default
   ========================================= ===========

   Implementation Notes:
      - :func:`NameABC.__str__` should give the same result as :func:`NameABC.formatted`

   Attributes:
      - **name** (str): The "name" of a file as a human would read it without data chaff
        like extensions.

      - **extension** (``Optional[str]``): The extension of an object *with* a period
        (ex: `.mov`).

FileName
--------

Implementation of :class:`FileABC`.

.. autoclass:: FileName
   :members:

   Attributes:
      - **base** (str): The "name" of a file as a human would read it without data chaff
        like extensions. Ex: ``'movie.mp4'`` has a "base" of ``'movie'``

      - **extension** (``Optional[str]``): The extension of an object *with* a period
        (ex: ``'.mp4'``).

   :class:`FileName` will automatically add a period to extensions that are missing it.

   Examples:
      - Basic init

         >>> name = FileName("movie", ".mp4")
         >>> name
         FileName(base='movie', extension='.mp4')
         >>> str(name)
         'movie.mp4'

      - Missing extension period

         >>> name = FileName("movie", "mp4")
         >>> name
         FileName(base='movie', extension='.mp4')
         >>> str(name)
         'movie.mp4'

      - :func:`Filename.from_path`:

         >>> name = FileName.from_path("/Volumes/disk/folder/movie.mp4")
         >>> name
         FileName(base='movie', extension='.mp4')
         >>> str(name)
         'movie.mp4'

      - :func:`FileName.from_path` works with just a name:

         >>> name = FileName.from_path("movie.mp4")
         >>> name
         FileName(base='movie', extension='.mp4')
         >>> str(name)
         'movie.mp4'

      - Make changes to name

         :class:`FileName` is a frozen dataclass, and treated as immutable. You can get
         a new name with different values using :func:`FileName.alter`

         >>> name = FileName.from_path("movie.mp4")
         >>> name
         FileName(base='movie', extension='.mp4')
         >>> str(name)
         'movie.mp4'


SeqName
-------

Implementation of :class:`FileABC`, describes sequence filenames, including naming
conventions for full sequences.

Examples:
   - ``'photo.0100.exr'``
   - ``'photo.####.exr'``
   - ``'photo_0100.exr'``
   - ``'photo_0100'``
   - ``'photo_0100-0200.exr'``
   - ``'photo_####-####.exr'``
   - ``'photo_[0100-0200].exr'``
   - ``'photo_{0100-0200}.exr'``
   - ``'photo_{0100-0200}'``

SeqName understands the following braces when representing file number ranges, and
transforms them to an :class:`Braces` object:

   ==========  =========   ========================
   Convention  Example     :class:`Braces` object
   ==========  =========   ========================
   <>          <010-020>   ``perfsprocket.ARROW``
   []          [010-020]   ``perfsprocket.BRACKET``
   {}          {010-020}   ``perfsprocket.CURLY``
   ()          (010-020)   ``perfsprocket.PAREN``
   ==========  =========   ========================

.. autoclass:: SeqName
   :members:

   Attributes:
      - **base** (str): The "name" of a file as a human would read it without data chaff
        like extensions.

         Ex: ``'photo'`` in ``'photo_0100.jpg'``
         Ex: ``'movie'`` in ```movie.[0143-0200].exr'``

      - **extension** (``Optional[str]``): The extension of an object *with* a period

         Default: ``None``

         Ex: ``'.jpg'`` in ``'photo_0100.jpg'``

         Ex: ``'.exr'`` in ```movie.[0143-0200].exr'``

         Ex: ``None`` in ```scan_0100'``

      - **delim** (``str``) - delimiter separating ``base`` from the file number or
        range. Must be ``'_'`` or ``'.'``

         Default: ``'.'``

         Ex: ``'_'`` in ``'photo_0100.jpg'``

         Ex: ``'.'`` in ``'movie.[0143-0200].exr'``

      - **start** (``Union[int, str]``) - first file number in range. Can be ``'#'`` for
        generic number. ``'#'`` is the only valid string value

         Default: ``'#'``

         Ex: ``100`` in ``'photo_0100.jpg'``

         Ex: ``143`` in ``'movie.[0143-0200].exr'``

         Ex: ``'#'`` in ``'photo_###.jpg'``

         Ex: ``'#'`` in ``'movie.[####-####].exr'``

      - **end** (``Optional[Union[int, str]]``) - second file number in range. Can be
        ``'#'`` for generic number. ``'#'`` is the only valid string value. ``None``
        when no end number is given.

         Default: ``None``

         Ex: ``None`` in ``'photo_0100.jpg'``

         Ex: ``200`` in ``'movie.[0143-0200].exr'``

         Ex: ``None`` in ``'photo_###.jpg'``

         Ex: ``'#'`` in ``'movie.[####-####].exr'``

      - **pad** (``int``) - padding for ``start`` and ``end`` values when printed to
        strings.

         Default: ``0``

         Ex: ``3`` in ``'photo_100.jpg'``

         Ex: ``4`` in ``'photo_0100.jpg'``

         Ex: ``4`` in ``'movie.[0143-0200].exr'``

         Ex: ``3`` in ``'photo_###.jpg'``

         Ex: ``4`` in ``'movie.[####-####].exr'``

      - **brackets** (``Optional[``:class:`Brackets```]``) - type of brackets
        surrounding range.

         Default: ``perfsprocket.BRACE``

         Ex: ``None`` in ``'photo_0100.jpg'``

         Ex: ``None`` in ``'movie.0143-0200.exr'``

         Ex: ``perfsprocket.BRACE`` in ``'movie.[0143-0200].exr'``

         Ex: ``perfsprocket.PAREN`` in ``'movie.(0143-0200).exr'``

   :class:`SeqName` will automatically add a period to extensions that are missing it.

   Examples:
      - Basic init

         >>> from perfsprocket import SeqName
         >>>
         >>> name = SeqName(base="movie", extension=".exr")
         >>> str(name)
         'movie.#.exr'

      - Non-default options:

         >>> name = SeqName(base="movie", extension=".exr", start=100, end=200, pad=4)
         >>> str(name)
         'movie.0100-0200.exr'

      - :func:`SeqName.from_path`:

         >>> name = SeqName.from_path("/Volumes/disk/folder/movie.0143.exr")
         >>> name
         SeqName(base='movie', extension='.exr', delim='.', start=143, end=None, ...)
         >>> str(name)
         'movie.0143.exr'

      - :func:`SeqName.from_path` works with just a name:

         >>> name = SeqName.from_path("movie.0143.exr")
         >>> name
         SeqName(base='movie', extension='.exr', delim='.', start=143, end=None, ...)
         >>> str(name)
         'movie.0143.exr'

      - Make changes to name:

         :class:`SeqName` is a frozen dataclass, and treated as immutable. You can get
         a new name with different values using :func:`FileName.alter`

         >>> name = SeqName.from_path("movie.0143.exr")
         >>> name = name.alter(start=243, pad=5)
         >>> str(name)
         'movie.00243.exr'


Braces
------

The class below is used to describe braces. Certain pre-loaded :class:`Braces` instances
are used to signal that a :class:`SeqName` uses a certain convention:

>>> from perfsprocket import SeqName, BRACKET, PAREN
>>>
>>> name = SeqName.from_path("movie.[0143-0327].exr")
>>> name.brackets is BRACKET
True
>>> name.brackets is PAREN
False
>>> BRACKET.open
'['
>>> BRACKET.close
']'
>>> str(BRACKET)
'[]'
>>> BRACKET.enclose("text")
'[text]'

.. autoclass:: Braces
   :special-members: __init__
   :members: