Output
======

The output of a cibyl command is the result of the query made by the user.
Cibyl provides a great amount of control on the format of this output. By
default, cibyl will print the output to the terminal, using colored text.

The user can choose to print to a file using the ``-o`` or ``--output`` flag. This
flag takes a file path as its value and will write there the query result.

.. note:: If the file specified exists, it will be overwritten.

The user can choose the format of the output. Currently three formats are
supported:

    * ``colorized``, colored text, is the default mode, well suited for printing to
      a terminal, but not very useful if printing to a file
    * ``text``, plain text, ideal to use when writing to a file
    * ``json``, output in json format, useful if the output of cibyl has to be
      passed to another piece of software

The user can also control the level of detail of the output, using the ``-v`` or
``--verbose`` flag. This flag is cumulative, so ``-vv`` will produce more output
than ``-v``. As an example, `Job` models will have a url field, but it will only
be printed in verbose mode. Similarly, `Test` models have a duration field that
is only shown in verbose mode.

Additionally, cibyl also has a stream of logging output. Normally, cibyl will log the duration
of the query, the system queried and where is the output written. If debug mode
is used with ``-d`` or ``--debug``, then additional information will be printed.
