__author__ = 'Falk Ziegler'
__credits__ = ['Falk Ziegler', 'Sebastian Funke']
__maintainer__ = 'Falk Ziegler'
__email__ = 'fz@accurion.com'

__all__ = ['imread']

import numpy as np
from skimage.io import imread as _imread

CHUNK_DATA_KEY = '.ACCURION_RAWDATA'.encode('iso-8859-1')

def imread(file):
    """
    Read an image from a file as an numpy array.
    
    Parameters
    ----------
    file : str
        Path to the image file.
    
    Returns
    -------
    rawdata : array_like
        Image matrix as numpy array.
    """
    rawdata = None
    
    with open(file, 'rb') as fobj:
        fobj.seek(8)                                        # for now we skip the header
        while rawdata is None:
            chunk_length = int.from_bytes(fobj.read(4), byteorder='big')
            chunk_name = fobj.read(4).decode('iso-8859-1')

            if chunk_name == 'IHDR':                        # must appear first
                width = int.from_bytes(fobj.read(4), byteorder='big')
                height = int.from_bytes(fobj.read(4), byteorder='big')
                bit_depth = int.from_bytes(fobj.read(1), byteorder='big')
                color_type = int.from_bytes(fobj.read(1), byteorder='big')
                significant_bits = bit_depth
                fobj.seek(chunk_length - 6, 1)              # jump over the next 3 Bytes and the CRC (4Bytes)

            elif chunk_name == 'tEXt':                      # stores key-value pair separated with a null character (1Byte)
                chunk_data = fobj.read(chunk_length)
                if chunk_data[:len(CHUNK_DATA_KEY)] == CHUNK_DATA_KEY: # the key is present
                    offset = len(CHUNK_DATA_KEY) + 1
                    # now the LabVIEW specific offset
                    offset += 12 + int.from_bytes(chunk_data[offset : offset + 2], byteorder='big')
                    rawdata = np.frombuffer(chunk_data[offset:], '>f4').reshape(height, width).astype(np.float32)
                fobj.seek(4, 1)                             # skip CRC (4Bytes)!

            elif chunk_name == 'sBIT':
                if color_type == 0:
                    significant_bits = int.from_bytes(fobj.read(1), byteorder='big')
                    fobj.seek(4, 1)
                else:
                    raise NotImplementedError('Unsupported image type...')

            elif chunk_name == 'IEND':                      # marks the end of the png stream
                # the key was not found so try to read the image directly,
                # maybe we have to do a right bit shift operation of the pixel values!
                rawdata = _imread(file)
                if 0 < significant_bits < bit_depth:
                    rawdata = np.right_shift(rawdata, bit_depth - significant_bits)

            else:
                fobj.seek(chunk_length + 4, 1)              # skip the complete chunk
                continue
        return np.transpose(rawdata)


def imsave(file):
    """
    Saves an numpy 2d array as an image.
    """
    raise NotImplementedError
