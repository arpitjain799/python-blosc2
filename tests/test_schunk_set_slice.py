########################################################################
#
#       Author:  The Blosc development team - blosc@blosc.org
#
########################################################################

import numpy
import pytest

import blosc2


@pytest.mark.parametrize("contiguous", [True, False])
@pytest.mark.parametrize("urlpath", [None, "b2frame"])
@pytest.mark.parametrize("mode", ["w", "a"])
@pytest.mark.parametrize(
    "cparams, dparams, nchunks, start, stop",
    [
        ({"compcode": blosc2.Codec.LZ4, "clevel": 6, "typesize": 4}, {}, 10, 0, 100),
        ({"typesize": 4}, {"nthreads": 4}, 1, 7, 23),
        ({"splitmode": blosc2.SplitMode.ALWAYS_SPLIT, "nthreads": 5, "typesize": 4}, {"schunk": None}, 5, 21, 200 * 2 * 100),
        ({"compcode": blosc2.Codec.LZ4HC, "typesize": 4}, {}, 7, None, None),
        ({"typesize": 4, "blocksize": 200 * 100}, {}, 7, 3, -12),
        ({"blocksize": 200 * 100, "typesize": 4}, {}, 5, -2456, -234),
    ],
)
def test_schunk_set_slice(contiguous, urlpath, mode, cparams, dparams, nchunks, start, stop):
    storage = {"contiguous": contiguous, "urlpath": urlpath, "cparams": cparams, "dparams": dparams}
    blosc2.remove_urlpath(urlpath)

    data = numpy.arange(200 * 100 * nchunks, dtype="int32")
    schunk = blosc2.SChunk(chunksize=200 * 100 * 4, data=data, mode=mode, **storage)

    val = nchunks * numpy.arange(data[start:stop].size, dtype="int32")
    schunk[start:stop] = val

    out = numpy.empty(val.shape, dtype="int32")
    if start is None and stop is None:
        schunk.get_slice(out=out)
    else:
        schunk.get_slice(start, stop, out)
    assert numpy.array_equal(val, out)

    blosc2.remove_urlpath(urlpath)
