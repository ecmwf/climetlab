# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

import ctypes
import ctypes.util
import sys
import os

import numpy as np
from functools import partial

lib = None

try:
    import ecmwflibs

    lib = ecmwflibs.find("eccodes")
except ModuleNotFoundError:
    lib = ctypes.util.find_library("eccodes")


if lib is None:
    for lib in (
        "/opt/ecmwf/eccodes/lib/libeccodes.so",
        "/usr/local/lib/libeccodes.dylib",
    ):
        if os.path.exists(lib):
            break

dll = ctypes.CDLL(lib)
libc = ctypes.CDLL(ctypes.util.find_library("c"))


class FILE(ctypes.Structure):
    pass


FILE_p = ctypes.POINTER(FILE)


####################################################################
class grib_context(ctypes.Structure):
    pass


grib_context_p = ctypes.POINTER(grib_context)

####################################################################


def _string_to_char(x):
    return x.encode()


def _char_to_string(x):
    return x.decode()


def _convert_strings(fn):

    convert = False

    for a in fn.argtypes:
        if a is c_char_p:
            convert = True

    if fn.restype is c_char_p:
        convert = True

    if not convert:
        return fn

    def wrapped(*args):

        new_args = []
        for a, t in zip(args, fn.argtypes):
            if t is c_char_p:
                a = string_to_char(a)
            new_args.append(a)

        r = fn(*new_args)
        if fn.restype is c_char_p:
            r = char_to_string(r)
        return r

    return wrapped


if sys.version_info[0] > 2:
    convert_strings = _convert_strings
    char_to_string = _char_to_string
    string_to_char = _string_to_char
else:

    def convert_strings(x):
        return x

    def char_to_string(x):
        return x

    def string_to_char(x):
        return x


####################################################################
class grib_handle(ctypes.Structure):
    pass


grib_handle_p = ctypes.POINTER(grib_handle)


####################################################################
class grib_keys_iterator(ctypes.Structure):
    pass


grib_keys_iterator_p = ctypes.POINTER(grib_keys_iterator)

####################################################################
c_int = ctypes.c_int
c_int_p = ctypes.POINTER(c_int)

c_long = ctypes.c_long
c_long_p = ctypes.POINTER(c_long)

c_uint = ctypes.c_uint
c_uint_p = ctypes.POINTER(c_uint)

c_ulong = ctypes.c_ulong
c_ulong_p = ctypes.POINTER(c_ulong)

c_double = ctypes.c_double
c_double_p = ctypes.POINTER(c_double)

c_char = ctypes.c_char
c_char_p = ctypes.c_char_p

c_void_p = ctypes.c_void_p

# TODO: check
c_size_t = c_uint
c_size_t_p = c_uint_p


####################################################################
def checked_error_in_last_paramater(fn):
    def wrapped(*args):
        err = c_int(0)
        err_p = ctypes.cast(ctypes.addressof(err), c_int_p)
        params = [a for a in args]
        params.append(err_p)

        result = fn(*params)
        if err.value:
            raise GribError(err)
        return result

    return wrapped


def checked_return_code(fn):
    def wrapped(*args):
        err = fn(*args)
        if err:
            raise GribError(err)

    return wrapped


####################################################################


def return_type(fn, ctype):
    def wrapped(*args):
        result = ctype()
        result_p = ctypes.cast(ctypes.addressof(result), ctypes.POINTER(ctype))
        params = [a for a in args]
        params.append(result_p)
        fn(*params)
        return result.value

    return wrapped


####################################################################


grib_handle_new_from_file = dll.grib_handle_new_from_file
grib_handle_new_from_file.restype = grib_handle_p
grib_handle_new_from_file.argtypes = (grib_context_p, FILE_p, c_int_p)

####################################################################

grib_handle_new_from_message_copy = dll.grib_handle_new_from_message_copy
grib_handle_new_from_message_copy.restype = grib_handle_p
grib_handle_new_from_message_copy.argtypes = (grib_context_p, c_void_p, c_size_t)

####################################################################

grib_handle_delete = dll.grib_handle_delete
grib_handle_delete.restype = None
grib_handle_delete.argtypes = (grib_handle_p,)

####################################################################


grib_keys_iterator_new = dll.grib_keys_iterator_new
grib_keys_iterator_new.restype = grib_keys_iterator_p
grib_keys_iterator_new.argtypes = (grib_handle_p, c_ulong, c_char_p)
grib_keys_iterator_new = convert_strings(grib_keys_iterator_new)

GRIB_KEYS_ITERATOR_ALL_KEYS = 0
####################################################################

grib_keys_iterator_delete = dll.grib_keys_iterator_delete
grib_keys_iterator_delete.restype = None
grib_keys_iterator_delete.argtypes = (grib_keys_iterator_p,)

####################################################################
grib_keys_iterator_next = dll.grib_keys_iterator_next
grib_keys_iterator_next.restype = c_int
grib_keys_iterator_next.argtypes = (grib_keys_iterator_p,)
####################################################################
grib_keys_iterator_get_name = dll.grib_keys_iterator_get_name
grib_keys_iterator_get_name.restype = c_char_p
grib_keys_iterator_get_name.argtypes = (grib_keys_iterator_p,)
grib_keys_iterator_get_name = convert_strings(grib_keys_iterator_get_name)
####################################################################
_grib_keys_iterator_get_string = dll.grib_keys_iterator_get_string
_grib_keys_iterator_get_string.restype = c_int
_grib_keys_iterator_get_string.argtypes = (
    grib_keys_iterator_p,
    c_char_p,
    c_size_t_p,
)

_grib_keys_iterator_get_string = checked_return_code(_grib_keys_iterator_get_string)


def grib_keys_iterator_get_string(iterator):
    size = c_size_t(1024)
    buf = ctypes.create_string_buffer(size.value)
    size_p = ctypes.cast(ctypes.addressof(size), c_size_t_p)
    _grib_keys_iterator_get_string(iterator, buf, size_p)
    return char_to_string(buf.value)


def grib_iterate(handle, namespace):
    i = grib_keys_iterator_new(handle, GRIB_KEYS_ITERATOR_ALL_KEYS, namespace)
    try:
        while grib_keys_iterator_next(i):
            name = grib_keys_iterator_get_name(i)
            value = grib_keys_iterator_get_string(i)
            yield (name, value)
    finally:
        grib_keys_iterator_delete(i)


def grib_get_keys_values(handle, namespace):
    return dict(grib_iterate(handle, namespace))


####################################################################


grib_get_size = dll.grib_get_size
grib_get_size.restype = c_int
grib_get_size.argtypes = (grib_handle_p, c_char_p, c_size_t_p)
grib_get_size = convert_strings(grib_get_size)

grib_get_size = checked_return_code(grib_get_size)
grib_get_size = return_type(grib_get_size, c_size_t)
####################################################################

grib_get_long = dll.grib_get_long
grib_get_long.restype = c_int
grib_get_long.argtypes = (grib_handle_p, c_char_p, c_long_p)
grib_get_long = convert_strings(grib_get_long)

grib_get_long = checked_return_code(grib_get_long)
grib_get_long = return_type(grib_get_long, c_long)

####################################################################

grib_get_double = dll.grib_get_double
grib_get_double.restype = c_int
grib_get_double.argtypes = (grib_handle_p, c_char_p, c_double_p)
grib_get_double = convert_strings(grib_get_double)

grib_get_double = checked_return_code(grib_get_double)
grib_get_double = return_type(grib_get_double, c_double)


####################################################################
_grib_get_string = dll.grib_get_string
_grib_get_string.restype = c_int
_grib_get_string.argtypes = (grib_handle_p, c_char_p, c_char_p, c_size_t_p)
_grib_get_string = checked_return_code(_grib_get_string)


def grib_get_string(handle, name):
    size = c_size_t(1024)
    buf = ctypes.create_string_buffer(size.value)
    size_p = ctypes.cast(ctypes.addressof(size), c_size_t_p)
    _grib_get_string(handle, string_to_char(name), buf, size_p)
    return char_to_string(buf.value)


####################################################################
_grib_get_double_array = dll.grib_get_double_array
_grib_get_double_array.restype = c_int
_grib_get_double_array.argtypes = (grib_handle_p, c_char_p, c_double_p, c_size_t_p)
_grib_get_double_array = convert_strings(_grib_get_double_array)
_grib_get_double_array = checked_return_code(_grib_get_double_array)

####################################################################
_grib_get_long_array = dll.grib_get_long_array
_grib_get_long_array.restype = c_int
_grib_get_long_array.argtypes = (grib_handle_p, c_char_p, c_long_p, c_size_t_p)
_grib_get_long_array = convert_strings(_grib_get_long_array)
_grib_get_long_array = checked_return_code(_grib_get_long_array)


####################################################################


def grib_get_bytes(handle, name):
    raise Exception("Not implemented")


####################################################################
grib_get_native_type = dll.grib_get_native_type
grib_get_native_type.restype = c_int
grib_get_native_type.argtypes = (grib_handle_p, c_char_p, c_int_p)
grib_get_native_type = convert_strings(grib_get_native_type)

grib_get_native_type = checked_return_code(grib_get_native_type)
grib_get_native_type = return_type(grib_get_native_type, c_int)

####################################################################

grib_get_error_message = dll.grib_get_error_message
grib_get_error_message.restype = c_char_p
grib_get_error_message.argtypes = (c_int,)
grib_get_error_message = convert_strings(grib_get_error_message)

####################################################################


####################################################################
_grib_get_gaussian_latitudes = dll.grib_get_gaussian_latitudes
_grib_get_gaussian_latitudes.restype = c_int
_grib_get_gaussian_latitudes.argtypes = (c_int, c_double_p)

_grib_get_gaussian_latitudes = checked_return_code(_grib_get_gaussian_latitudes)


def grib_get_gaussian_latitudes(N):
    array = np.empty((N * 2,), dtype=np.float64)
    array_p = array.ctypes.data_as(c_double_p)
    _grib_get_gaussian_latitudes(N, array_p)
    return array


####################################################################


class GribError(Exception):
    def __init__(self, err):
        super(GribError, self).__init__("%s (%s)" % (grib_get_error_message(err), err))
        self.err = err


grib_handle_new_from_file = partial(grib_handle_new_from_file, None)
grib_handle_new_from_file = checked_error_in_last_paramater(grib_handle_new_from_file)

####################################################################
grib_handle_new_from_message_copy = partial(grib_handle_new_from_message_copy, None)
grib_handle_new_from_message_copy = checked_error_in_last_paramater(
    grib_handle_new_from_message_copy
)

####################################################################
TYPE_GETTERS = (
    None,
    grib_get_long,
    grib_get_double,
    grib_get_string,
    grib_get_bytes,
)


def grib_get(handle, name):
    t = grib_get_native_type(handle, name)
    return TYPE_GETTERS[t](handle, name)


####################################################################
def grib_get_long_array(handle, name):
    size = grib_get_size(handle, name)
    array = np.empty((size,), dtype=np.long)
    array_p = array.ctypes.data_as(c_long_p)

    size = c_size_t(size)
    size_p = ctypes.cast(ctypes.addressof(size), c_size_t_p)

    _grib_get_long_array(handle, name, array_p, size_p)
    return array


####################################################################
def grib_get_double_array(handle, name):
    size = grib_get_size(handle, name)
    array = np.empty((size,), dtype=np.float64)
    array_p = array.ctypes.data_as(c_double_p)

    size = c_size_t(size)
    size_p = ctypes.cast(ctypes.addressof(size), c_size_t_p)

    _grib_get_double_array(handle, name, array_p, size_p)
    return array


####################################################################

fopen = libc.fopen
fopen.argtypes = (c_char_p, c_char_p)
fopen.restype = FILE_p
fopen = convert_strings(fopen)

fclose = libc.fclose
fclose.argtypes = (FILE_p,)
fclose.restype = c_int


ftell = libc.ftell
ftell.argtypes = (FILE_p,)
fclose.restype = c_long

fseek = libc.fseek
fseek.argtypes = (FILE_p, c_long, c_int)
fseek.restype = c_int


class CFile(object):
    def __init__(self, path):
        self.f = fopen(path, "rb")
        if not self.f:
            raise Exception("Cannot open %s" % (path,))

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def close(self):
        if self.f:
            fclose(self.f)
            self.f = None

    def tell(self):
        return ftell(self.f)

    def position(self, position, whence=0):
        return fseek(self.f, position, whence)

    def next(self):
        return grib_handle_new_from_file(self.f)


class CFile2(object):
    def __init__(self, path):
        self.f = open(path, "rb")
        if not self.f:
            raise Exception("Cannot open %s" % (path,))
        self.as_FILE = ctypes.pythonapi.PyFile_AsFile
        self.as_FILE.restype = FILE_p
        self.as_FILE.argtypes = (ctypes.py_object,)

    def tell(self):
        return self.f.tell()

    def next_grib(self):
        return grib_handle_new_from_file(self.as_FILE(self.f))


def grib_file_open(path):
    return CFile(path)


####################################################################
def grib_values(handle, name="values"):
    array = grib_get_double_array(handle, name)

    if grib_get(handle, "bitmapPresent"):
        missingValue = grib_get(handle, "missingValue")
        array[array == missingValue] = np.nan

    return array


def grib_pl_array(handle, name="pl"):
    return grib_get_long_array(handle, name)
