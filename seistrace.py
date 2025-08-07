import os
import subprocess
from ctypes import (
    CDLL,
    POINTER,
    c_bool,
    c_char_p,
    c_double,
    c_longlong,
    c_void_p,
    cast,
    pointer,
)

from numpy.ctypeslib import as_array

res = subprocess.run(["pkg-config", "--libs", "seistrace"], capture_output=True)
lib_path = os.path.join(res.stdout.decode().split()[0][2:], "libseistrace.so")
lib = CDLL(lib_path)


class TraceHeader:
    __seis_trace_header_new = lib.seis_trace_header_new
    __seis_trace_header_new.restype = c_void_p
    __seis_trace_header_ref = lib.seis_trace_header_ref
    __seis_trace_header_ref.argtypes = [POINTER(POINTER(c_void_p))]
    __seis_trace_header_ref.restype = c_void_p
    __seis_trace_header_unref = lib.seis_trace_header_unref
    __seis_trace_header_unref.argtypes = [POINTER(POINTER(c_void_p))]
    __seis_trace_header_set_int = lib.seis_trace_header_set_int
    __seis_trace_header_set_int.argtypes = [c_void_p, c_char_p, c_longlong]
    __seis_trace_header_set_real = lib.seis_trace_header_set_real
    __seis_trace_header_set_real.argtypes = [c_void_p, c_char_p, c_double]
    __seis_trace_header_get = lib.seis_trace_header_get
    __seis_trace_header_get.argtypes = [c_void_p, c_char_p]
    __seis_trace_header_get.restype = POINTER(c_void_p)
    __seis_trace_header_value_is_int = lib.seis_trace_header_value_is_int
    __seis_trace_header_value_is_int.argtypes = [c_void_p]
    __seis_trace_header_value_is_int.restype = c_bool
    __seis_trace_header_value_is_real = lib.seis_trace_header_value_is_real
    __seis_trace_header_value_is_real.argtypes = [c_void_p]
    __seis_trace_header_value_is_real.restype = c_bool
    __seis_trace_header_value_get_int = lib.seis_trace_header_value_get_int
    __seis_trace_header_value_get_int.argtypes = [c_void_p]
    __seis_trace_header_value_get_int.restype = POINTER(c_longlong)
    __seis_trace_header_value_get_real = lib.seis_trace_header_value_get_real
    __seis_trace_header_value_get_real.argtypes = [c_void_p]
    __seis_trace_header_value_get_real.restype = POINTER(c_double)
    __seis_trace_header_exists = lib.seis_trace_header_exists
    __seis_trace_header_exists.argtypes = [c_void_p, c_char_p]
    __seis_trace_header_exists.restype = c_bool
    ptr_own = True

    def __init__(self, ptr=None) -> None:
        self.pointer = pointer
        if ptr:
            self.ptr_own = False
            self.__pimpl = cast(ptr, POINTER(c_void_p))
        else:
            self.__pimpl = cast(self.__seis_trace_header_new(), POINTER(c_void_p))

    def __enter__(self):
        return self

    def __exit__(self, *exec_info):
        self.__del__()

    def __del__(self):
        if self.ptr_own:
            self.__seis_trace_header_unref(self.pointer(self.__pimpl))

    def set(self, hdr_name, val):
        """Cast val whether to inti or to float to write header
        in appropriate format"""
        if isinstance(val, int):
            self.__seis_trace_header_set_int(self.__pimpl, hdr_name.encode(), val)
        elif isinstance(val, float):
            self.__seis_trace_header_set_real(self.__pimpl, hdr_name.encode(), val)
        else:
            raise TypeError("Header value could be only integer" " or floating point")

    def get(self, hdr_name):
        v = self.__seis_trace_header_get(self.__pimpl, hdr_name.encode())
        if not v:
            raise ValueError("No such header")
        if self.__seis_trace_header_value_is_int(v):
            res = self.__seis_trace_header_value_get_int(v)
        else:
            res = self.__seis_trace_header_value_get_real(v)
        return res[0]


# class Samples:
#     def __init__(self, pointer, num):
#         self.ptr = pointer
#         self.num = num
#
#     def __iter__(self):
#         self.counter = 0
#         return self
#
#     def __next__(self):
#         if self.counter < self.num:
#             res = self.ptr[self.counter]
#             self.counter += 1
#             return res
#         else:
#             raise StopIteration


class Trace:
    __seis_trace_new = lib.seis_trace_new
    __seis_trace_new.argtypes = [c_longlong]
    __seis_trace_new.restype = c_void_p
    __seis_trace_new_with_header = lib.seis_trace_new_with_header
    __seis_trace_new_with_header.argtypes = [c_longlong, c_void_p]
    __seis_trace_new_with_header.restype = c_void_p
    __seis_trace_unref = lib.seis_trace_unref
    __seis_trace_unref.argtypes = [POINTER(POINTER(c_void_p))]
    __seis_trace_get_header = lib.seis_trace_get_header
    __seis_trace_get_header.argtypes = [c_void_p]
    __seis_trace_get_header.restype = c_void_p
    __seis_trace_get_samples = lib.seis_trace_get_samples
    __seis_trace_get_samples.argtypes = [c_void_p]
    __seis_trace_get_samples.restype = POINTER(c_double)
    __seis_trace_get_samples_num = lib.seis_trace_get_samples_num
    __seis_trace_get_samples_num.argtypes = [c_void_p]
    __seis_trace_get_samples_num.restype = c_longlong

    def __init__(self, samp_num=None, hdr=None, ptr=None):
        self.pointer = pointer
        if ptr:
            self.__pimpl = cast(ptr, POINTER(c_void_p))
        elif samp_num:
            if hdr:
                self.__pimpl = cast(
                    self.__seis_trace_new_with_header(samp_num, hdr.__pimpl),
                    POINTER(c_void_p),
                )
            else:
                self.__pimpl = cast(self.__seis_trace_new(samp_num), POINTER(c_void_p))
        else:
            raise TypeError("Pointer or samp_num should be specified")

    def __enter__(self):
        return self

    def __exit__(self, *exec_info):
        self.__del__()

    def __del__(self):
        self.__seis_trace_unref(self.pointer(self.__pimpl))

    def header(self):
        return TraceHeader(self.__seis_trace_get_header(self.__pimpl))

    def samples(self):
        num = self.__seis_trace_get_samples_num(self.__pimpl)
        samp = self.__seis_trace_get_samples(self.__pimpl)
        # samp = cast(samp, POINTER(c_double))
        return as_array(samp, (num,))
        #  return Samples(samp, num)
