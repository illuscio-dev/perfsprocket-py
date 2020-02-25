.. automodule:: perfsprocket

Basic Usage
===========

- Copy files and file sequences with a unified interface!

   >>> from perfsprocket import File, FileSequence
   >>>
   >>> single = File("~/Desktop/test/source/movie.mp4")
   >>> single
   <File: '/Users/dev/Desktop/test/source/movie.mp4'>
   >>> copied_single = single.copy(dst_folder="~/Desktop/test/destination")
   >>> for path in copied_single:
   ...     print(path)
   ...
   /Users/dev/Desktop/test/destination/movie.mp4
   >>>
   >>> sequence = FileSequence("~/Desktop/test/source/photo_###.jpeg", start=1, end=5)
   >>> sequence
   <FileSequence: '/Users/dev/Desktop/test/source/photo_[001-005].jpeg'>
   >>> copied_sequence = sequence.copy(dst_folder="~/Desktop/test/destination")
   >>> for path in copied_sequence:
   ...     print(path)
   ...
   /Users/dev/Desktop/test/destination/photo_001.jpeg
   /Users/dev/Desktop/test/destination/photo_002.jpeg
   /Users/dev/Desktop/test/destination/photo_003.jpeg
   /Users/dev/Desktop/test/destination/photo_004.jpeg
   /Users/dev/Desktop/test/destination/photo_005.jpeg

   Both :class:`File` and :class:`FileSequence` are iterable. All operations are built to
   have a common interface, so you can mix single files and file sequences without thought.

- Both classes also supports move, rename, delete, and chmod commands:

   >>> single.rename("favorite_movie.mp4")
   <File: '/Users/dev/Desktop/test/source/favorite_movie.mp4'>
   >>>
   >>> sequence.rename("family_photo_###.jpeg")
   <FileSequence: '/Users/dev/Desktop/test/source/family_photo_[001-005].jpeg'>

- Each operation has an iterator equivalent, allowing you to track progress.

   >>> for path in copied_single.chmod_iter(0o777):
   ...     print(f"updated: {path}")
   ...
   updated: /Users/dev/Desktop/test/destination/movie.mp4
   >>>
   >>> for path in copied_sequence.chmod_iter(0o777):
   ...     print(f"updated: {path}")
   ...
   updated: /Users/dev/Desktop/test/destination/photo_001.jpeg
   updated: /Users/dev/Desktop/test/destination/photo_002.jpeg
   updated: /Users/dev/Desktop/test/destination/photo_003.jpeg
   updated: /Users/dev/Desktop/test/destination/photo_004.jpeg
   updated: /Users/dev/Desktop/test/destination/photo_005.jpeg

- Easily parse filenames:

   >>> file_name = FileName(name="movie", extension="mp4")
   >>> file_name
   FileName(name='movie', extension='.mp4')
   >>> str(file_name)
   'movie.mp4'
   >>>
   >>> seq_name
   SeqName(name='photo', extension='.jpeg', delim='_', start=1, end=None, pad=4, brackets=None)
   >>> str(seq_name)
   'photo_0001.jpeg'

- Manipulate :class:`NameABC` objects during rename operations:

   >>> single = File("~/Desktop/test/source/movie.mp4")
   >>> single.rename(single.name.alter(base="favorite"))
   <File: '/Users/dev/Desktop/test/source/favorite.mp4'>

   >>> sequence = FileSequence("~/Desktop/test/source/photo_###.jpeg", start=1, end=5)
   >>> sequence.rename(sequence.name.alter(base="favorite"))
   <FileSequence: '/Users/dev/Desktop/test/source/favorite_[001-005].jpeg'>