from typing import Optional

import esprima
from esprima.error_handler import Error as ParseError

from highcharts_gantt.options import HighchartsGanttOptions

from highcharts_gantt import errors
from highcharts_gantt.decorators import validate_types
from highcharts_stock.global_options.shared_options import SharedOptions, SharedStockOptions


class SharedGanttOptions(HighchartsGanttOptions):
    """Python object which can be used to configure global settings that can apply to
    multiple Highcharts charts when serialized to JavaScript."""

    def to_js_literal(self,
                      filename = None,
                      encoding = 'utf-8') -> Optional[str]:
        """Return the object represented as a :class:`str <python:str>` containing the
        JavaScript object literal.

        :param filename: The name of a file to which the JavaScript object literal should
          be persisted. Defaults to :obj:`None <python:None>`
        :type filename: Path-like

        :param encoding: The character encoding to apply to the resulting object. Defaults
          to ``'utf-8'``.
        :type encoding: :class:`str <python:str>`

        .. note::

          Returns a JavaScript string which applies the Highcharts global options. The
          JavaScript returned by this method takes the (pseudo-code) form:

          .. code-block:: javascript

            Highcharts.setOptions({... configuration options ... });

        :rtype: :class:`str <python:str>`
        """
        prefix = 'Highcharts.setOptions('
        options_body = super().to_js_literal(encoding = encoding)

        as_str = prefix + options_body + ');'

        if filename:
            with open(filename, 'w', encoding = encoding) as file_:
                file_.write(as_str)

        return as_str

    @classmethod
    def _validate_js_literal(cls,
                             as_str,
                             range = True,
                             _break_loop_on_failure = False):
        """Parse ``as_str`` as a valid JavaScript literal object.

        :param as_str: The string to parse as a JavaScript literal object.
        :type as_str: :class:`str <python:str>`

        :param range: If ``True``, includes location and range data for each node in the
          AST returned. Defaults to ``False``.
        :type range: :class:`bool <python:bool>`

        :param _break_loop_on_failure: If ``True``, will not loop if the method fails to
          parse/validate ``as_str``. Defaults to ``False``.
        :type _break_loop_on_failure: :class:`bool <python:bool>`

        :returns: The parsed AST representation of ``as_str`` and the updated string.
        :rtype: 2-member :class:`tuple <python:tuple>` of :class:`esprima.nodes.Script`
          and :class:`str <python:str>`
        """
        try:
            parsed = esprima.parseScript(as_str, loc = range, range = range)
        except ParseError:
            try:
                parsed = esprima.parseModule(as_str, loc = range, range = range)
            except ParseError:
                if not _break_loop_on_failure:
                    as_str = f"""var randomVariable = {as_str}"""
                    return cls._validate_js_literal(as_str,
                                                    range = range,
                                                    _break_loop_on_failure = True)
                else:
                    raise errors.HighchartsParseError('._validate_js_function() expects '
                                                      'a str containing a valid '
                                                      'JavaScript function. Could not '
                                                      'find a valid function.')

        return parsed, as_str

    @classmethod
    def from_options(cls, options):
        """Create a
        :class:`SharedGanttOptions <highcharts_gantt.global_options.shared_options.SharedGanttOptions>`
        instance from a
        :class:`HighchartsGanttOptions <highcharts_gantt.options.HighchartsGanttOptions>`
        object.

        :param options: A :class:`HighchartsGanttOptions` object to use for the shared
          options instance.
        :type options:
          :class:`HighchartsGanttOptions <highcharts_gantt.options.HighchartsGanttOptions>`
          or coercable

        :returns: A
          :class:`SharedGanttOptions <highcharts_gantt.global_options.shared_options.SharedGanttOptions>`
          instance
        :rtype: :class:`SharedGanttOptions <highcharts_gantt.global_options.shared_options.SharedGanttOptions>`
        """
        if not options:
            return cls()

        options = validate_types(options, types = (HighchartsGanttOptions))
        options_as_dict = options.to_dict()

        instance = cls.from_dict(options_as_dict)

        return instance
