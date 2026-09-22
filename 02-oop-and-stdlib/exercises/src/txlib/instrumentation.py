"""Cross-cutting concerns — TODO.

@timed              decorator logging "<function name> took 0.123 s" at INFO level
                    must preserve __name__ and __doc__ (functools.wraps)
                    must time failing calls too (try/finally)

class Timer:        context manager exposing .elapsed after the block
                    must not swallow exceptions
"""
