"""The suite of window functions."""

import numpy as np
from scipy import special, linalg
from scipy.fftpack import fft

__all__ = ['boxcar', 'triang', 'parzen', 'bohman', 'blackman', 'nuttall',
           'blackmanharris', 'flattop', 'bartlett', 'hanning', 'barthann',
           'hamming', 'kaiser', 'gaussian', 'general_gaussian', 'chebwin',
           'slepian', 'hann', 'get_window']


def boxcar(M, sym=True):
    """Return a boxcar or rectangular window.
    
    Included for completeness, this is equivalent to no window at all.

    Parameters
    ----------
    M : int
        Number of points in the output window. If zero or less, an empty
        array is returned.
    sym : bool, optional
        Whether the window is symmetric. (Has no effect for boxcar.)

    Returns
    -------
    w : ndarray
        The window, with the maximum value normalized to 1

    """
    return np.ones(M, float)


def triang(M, sym=True):
    """Return a triangular window.

    Parameters
    ----------
    M : int
        Number of points in the output window. If zero or less, an empty
        array is returned.
    sym : bool, optional
        When True, generates a symmetric window, for use in filter design. 
        When False, generates a periodic window, for use in spectral analysis.

    Returns
    -------
    w : ndarray
        The window, with the maximum value normalized to 1 (though the value 1 
        does not appear if the number of samples is even and sym is True).

    """
    if M < 1:
        return np.array([])
    if M == 1:
        return np.ones(1, 'd')
    odd = M % 2
    if not sym and not odd:
        M = M + 1
    n = np.arange(1, int((M + 1) / 2) + 1)
    if M % 2 == 0:
        w = (2 * n - 1.0) / M
        w = np.r_[w, w[::-1]]
    else:
        w = 2 * n / (M + 1.0)
        w = np.r_[w, w[-2::-1]]

    if not sym and not odd:
        w = w[:-1]
    return w


def parzen(M, sym=True):
    """Return a Parzen window.

    Parameters
    ----------
    M : int
        Number of points in the output window. If zero or less, an empty
        array is returned.
    sym : bool, optional
        When True, generates a symmetric window, for use in filter design. 
        When False, generates a periodic window, for use in spectral analysis.

    Returns
    -------
    w : ndarray
        The window, with the maximum value normalized to 1 (though the value 1 
        does not appear if the number of samples is even and sym is True).

    """
    if M < 1:
        return np.array([])
    if M == 1:
        return np.ones(1, 'd')
    odd = M % 2
    if not sym and not odd:
        M = M + 1
    n = np.arange(-(M - 1) / 2.0, (M - 1) / 2.0 + 0.5, 1.0)
    na = np.extract(n < -(M - 1) / 4.0, n)
    nb = np.extract(abs(n) <= (M - 1) / 4.0, n)
    wa = 2 * (1 - np.abs(na) / (M / 2.0)) ** 3.0
    wb = (1 - 6 * (np.abs(nb) / (M / 2.0)) ** 2.0 +
          6 * (np.abs(nb) / (M / 2.0)) ** 3.0)
    w = np.r_[wa, wb, wa[::-1]]
    if not sym and not odd:
        w = w[:-1]
    return w


def bohman(M, sym=True):
    """Return a Bohman window.

    Parameters
    ----------
    M : int
        Number of points in the output window. If zero or less, an empty
        array is returned.
    sym : bool, optional
        When True, generates a symmetric window, for use in filter design. 
        When False, generates a periodic window, for use in spectral analysis.

    Returns
    -------
    w : ndarray
        The window, with the maximum value normalized to 1 (though the value 1 
        does not appear if the number of samples is even and sym is True).

    """
    if M < 1:
        return np.array([])
    if M == 1:
        return np.ones(1, 'd')
    odd = M % 2
    if not sym and not odd:
        M = M + 1
    fac = np.abs(np.linspace(-1, 1, M)[1:-1])
    w = (1 - fac) * np.cos(np.pi * fac) + 1.0 / np.pi * np.sin(np.pi * fac)
    w = np.r_[0, w, 0]
    if not sym and not odd:
        w = w[:-1]
    return w


def blackman(M, sym=True):
    """Return a Blackman window.

    The Blackman window is a taper formed by using the the first three
    terms of a summation of cosines. It was designed to have close to the
    minimal leakage possible.  It is close to optimal, only slightly worse
    than a Kaiser window.

    Parameters
    ----------
    M : int
        Number of points in the output window. If zero or less, an empty
        array is returned.
    sym : bool, optional
        When True, generates a symmetric window, for use in filter design. 
        When False, generates a periodic window, for use in spectral analysis.
        
    Returns
    -------
    w : ndarray
        The window, with the maximum value normalized to 1 (though the value 1 
        does not appear if the number of samples is even and sym is True).
        
    See Also
    --------
    bartlett, hamming, hann, kaiser

    Notes
    -----
    The Blackman window is defined as

    .. math::  w(n) = 0.42 - 0.5 \\cos(2\\pi n/M) + 0.08 \\cos(4\\pi n/M)

    Most references to the Blackman window come from the signal processing
    literature, where it is used as one of many windowing functions for
    smoothing values.  It is also known as an apodization (which means
    "removing the foot", i.e. smoothing discontinuities at the beginning
    and end of the sampled signal) or tapering function. It is known as a
    "near optimal" tapering function, almost as good (by some measures)
    as the Kaiser window.

    References
    ----------
    .. [1] Blackman, R.B. and Tukey, J.W., (1958) The measurement of power spectra,
           Dover Publications, New York.
    .. [2] Oppenheim, A.V., and R.W. Schafer. Discrete-Time Signal Processing.
           Upper Saddle River, NJ: Prentice-Hall, 1999, pp. 468-471.

    Examples
    --------
    >>> scipy.signal.blackman(12)
    array([-0.        ,  0.03260643,  0.15990363,  0.41439798,  0.73604518,
            0.96704677,  0.96704677,  0.73604518,  0.41439798,  0.15990363,
            0.03260643, -0.        ])

    Plot the window and the frequency response:

    >>> from numpy.fft import fft, fftshift
    >>> window = scipy.signal.blackman(51)
    >>> plt.plot(window)
    [<matplotlib.lines.Line2D object at 0x...>]
    >>> plt.title("Blackman window")
    <matplotlib.text.Text object at 0x...>
    >>> plt.ylabel("Amplitude")
    <matplotlib.text.Text object at 0x...>
    >>> plt.xlabel("Sample")
    <matplotlib.text.Text object at 0x...>
    >>> plt.show()

    >>> plt.figure()
    <matplotlib.figure.Figure object at 0x...>
    >>> A = fft(window, 2048) / 25.5
    >>> mag = np.abs(fftshift(A))
    >>> freq = np.linspace(-0.5, 0.5, len(A))
    >>> response = 20 * np.log10(mag)
    >>> response = np.clip(response, -100, 100)
    >>> plt.plot(freq, response)
    [<matplotlib.lines.Line2D object at 0x...>]
    >>> plt.title("Frequency response of Blackman window")
    <matplotlib.text.Text object at 0x...>
    >>> plt.ylabel("Magnitude [dB]")
    <matplotlib.text.Text object at 0x...>
    >>> plt.xlabel("Normalized frequency [cycles per sample]")
    <matplotlib.text.Text object at 0x...>
    >>> plt.axis('tight')
    (-0.5, 0.5, -100.0, ...)
    >>> plt.show()

    """
    # Docstring adapted from NumPy's blackman function
    if M < 1:
        return np.array([])
    if M == 1:
        return np.ones(1, 'd')
    odd = M % 2
    if not sym and not odd:
        M = M + 1
    n = np.arange(0, M)
    w = (0.42 - 0.5 * np.cos(2.0 * np.pi * n / (M - 1)) +
         0.08 * np.cos(4.0 * np.pi * n / (M - 1)))
    if not sym and not odd:
        w = w[:-1]
    return w


def nuttall(M, sym=True):
    """Return a minimum 4-term Blackman-Harris window according to Nuttall.

    Parameters
    ----------
    M : int
        Number of points in the output window. If zero or less, an empty
        array is returned.
    sym : bool, optional
        When True, generates a symmetric window, for use in filter design. 
        When False, generates a periodic window, for use in spectral analysis.

    Returns
    -------
    w : ndarray
        The window, with the maximum value normalized to 1 (though the value 1 
        does not appear if the number of samples is even and sym is True).

    """
    if M < 1:
        return np.array([])
    if M == 1:
        return np.ones(1, 'd')
    odd = M % 2
    if not sym and not odd:
        M = M + 1
    a = [0.3635819, 0.4891775, 0.1365995, 0.0106411]
    n = np.arange(0, M)
    fac = n * 2 * np.pi / (M - 1.0)
    w = (a[0] - a[1] * np.cos(fac) +
         a[2] * np.cos(2 * fac) - a[3] * np.cos(3 * fac))
    if not sym and not odd:
        w = w[:-1]
    return w


def blackmanharris(M, sym=True):
    """Return a minimum 4-term Blackman-Harris window.

    Parameters
    ----------
    M : int
        Number of points in the output window. If zero or less, an empty
        array is returned.
    sym : bool, optional
        When True, generates a symmetric window, for use in filter design. 
        When False, generates a periodic window, for use in spectral analysis.

    Returns
    -------
    w : ndarray
        The window, with the maximum value normalized to 1 (though the value 1 
        does not appear if the number of samples is even and sym is True).

    """
    if M < 1:
        return np.array([])
    if M == 1:
        return np.ones(1, 'd')
    odd = M % 2
    if not sym and not odd:
        M = M + 1
    a = [0.35875, 0.48829, 0.14128, 0.01168]
    n = np.arange(0, M)
    fac = n * 2 * np.pi / (M - 1.0)
    w = (a[0] - a[1] * np.cos(fac) +
         a[2] * np.cos(2 * fac) - a[3] * np.cos(3 * fac))
    if not sym and not odd:
        w = w[:-1]
    return w


def flattop(M, sym=True):
    """Return a flat top window.

    Parameters
    ----------
    M : int
        Number of points in the output window. If zero or less, an empty
        array is returned.
    sym : bool, optional
        When True, generates a symmetric window, for use in filter design. 
        When False, generates a periodic window, for use in spectral analysis.

    Returns
    -------
    w : ndarray
        The window function

    """
    if M < 1:
        return np.array([])
    if M == 1:
        return np.ones(1, 'd')
    odd = M % 2
    if not sym and not odd:
        M = M + 1
    a = [0.2156, 0.4160, 0.2781, 0.0836, 0.0069]
    n = np.arange(0, M)
    fac = n * 2 * np.pi / (M - 1.0)
    w = (a[0] - a[1] * np.cos(fac) +
         a[2] * np.cos(2 * fac) - a[3] * np.cos(3 * fac) +
         a[4] * np.cos(4 * fac))
    if not sym and not odd:
        w = w[:-1]
    return w


def bartlett(M, sym=True):
    """Return a Bartlett window.

    The Bartlett window is very similar to a triangular window, except
    that the end points are at zero.  It is often used in signal
    processing for tapering a signal, without generating too much
    ripple in the frequency domain.
    
    Parameters
    ----------
    M : int
        Number of points in the output window. If zero or less, an empty
        array is returned.
    sym : bool, optional
        When True, generates a symmetric window, for use in filter design. 
        When False, generates a periodic window, for use in spectral analysis.

    Returns
    -------
    w : ndarray
        The triangular window, with the maximum value normalized to 1 (though the value 1 
        does not appear if the number of samples is even and sym is True), with the first
        and last samples equal to zero.

    See Also
    --------
    blackman, hamming, hann, kaiser

    Notes
    -----
    The Bartlett window is defined as

    .. math:: w(n) = \\frac{2}{M-1} \\left(
              \\frac{M-1}{2} - \\left|n - \\frac{M-1}{2}\\right|
              \\right)

    Most references to the Bartlett window come from the signal
    processing literature, where it is used as one of many windowing
    functions for smoothing values.  Note that convolution with this
    window produces linear interpolation.  It is also known as an
    apodization (which means"removing the foot", i.e. smoothing
    discontinuities at the beginning and end of the sampled signal) or
    tapering function. The fourier transform of the Bartlett is the product
    of two sinc functions.
    Note the excellent discussion in Kanasewich.

    References
    ----------
    .. [1] M.S. Bartlett, "Periodogram Analysis and Continuous Spectra",
           Biometrika 37, 1-16, 1950.
    .. [2] E.R. Kanasewich, "Time Sequence Analysis in Geophysics",
           The University of Alberta Press, 1975, pp. 109-110.
    .. [3] A.V. Oppenheim and R.W. Schafer, "Discrete-Time Signal
           Processing", Prentice-Hall, 1999, pp. 468-471.
    .. [4] Wikipedia, "Window function",
           http://en.wikipedia.org/wiki/Window_function
    .. [5] W.H. Press,  B.P. Flannery, S.A. Teukolsky, and W.T. Vetterling,
           "Numerical Recipes", Cambridge University Press, 1986, page 429.

    Examples
    --------
    >>> scipy.signal.bartlett(12)
    array([ 0.        ,  0.18181818,  0.36363636,  0.54545455,  0.72727273,
            0.90909091,  0.90909091,  0.72727273,  0.54545455,  0.36363636,
            0.18181818,  0.        ])

    Plot the window and its frequency response (requires matplotlib):

    >>> from numpy.fft import fft, fftshift
    >>> window = scipy.signal.bartlett(51)
    >>> plt.plot(window)
    [<matplotlib.lines.Line2D object at 0x...>]
    >>> plt.title("Bartlett window")
    <matplotlib.text.Text object at 0x...>
    >>> plt.ylabel("Amplitude")
    <matplotlib.text.Text object at 0x...>
    >>> plt.xlabel("Sample")
    <matplotlib.text.Text object at 0x...>
    >>> plt.show()

    >>> plt.figure()
    <matplotlib.figure.Figure object at 0x...>
    >>> A = fft(window, 2048) / 25.5
    >>> mag = np.abs(fftshift(A))
    >>> freq = np.linspace(-0.5, 0.5, len(A))
    >>> response = 20 * np.log10(mag)
    >>> response = np.clip(response, -100, 100)
    >>> plt.plot(freq, response)
    [<matplotlib.lines.Line2D object at 0x...>]
    >>> plt.title("Frequency response of Bartlett window")
    <matplotlib.text.Text object at 0x...>
    >>> plt.ylabel("Magnitude [dB]")
    <matplotlib.text.Text object at 0x...>
    >>> plt.xlabel("Normalized frequency [cycles per sample]")
    <matplotlib.text.Text object at 0x...>
    >>> plt.axis('tight')
    (-0.5, 0.5, -100.0, ...)
    >>> plt.show()

    """
    # Docstring adapted from NumPy's bartlett function
    if M < 1:
        return np.array([])
    if M == 1:
        return np.ones(1, 'd')
    odd = M % 2
    if not sym and not odd:
        M = M + 1
    n = np.arange(0, M)
    w = np.where(np.less_equal(n, (M - 1) / 2.0),
                 2.0 * n / (M - 1), 2.0 - 2.0 * n / (M - 1))
    if not sym and not odd:
        w = w[:-1]
    return w


def hann(M, sym=True):
    """Return a Hann window.

    The Hann window is a taper formed by using a raised cosine or sine-squared 
    with ends that touch zero.

    Parameters
    ----------
    M : int
        Number of points in the output window. If zero or less, an empty
        array is returned.
    sym : bool, optional
        When True, generates a symmetric window, for use in filter design. 
        When False, generates a periodic window, for use in spectral analysis.

    Returns
    -------
    w : ndarray
        The window, with the maximum value normalized to 1 (though the value 1 
        does not appear if `M` is even and `sym` is True).

    See Also
    --------
    bartlett, blackman, hamming, kaiser

    Notes
    -----
    The Hann window is defined as

    .. math::  w(n) = 0.5 - 0.5cos\\left(\\frac{2\\pi{n}}{M-1}\\right)
               \\qquad 0 \\leq n \\leq M-1

    The window was named for Julius van Hann, an Austrian meterologist. It is
    also known as the Cosine Bell. It is sometimes erroneously referred to as the 
    "Hanning" window, from the use of "hann" as a verb in the original paper and 
    confusion with the very similar Hamming window.

    Most references to the Hann window come from the signal processing
    literature, where it is used as one of many windowing functions for
    smoothing values.  It is also known as an apodization (which means
    "removing the foot", i.e. smoothing discontinuities at the beginning
    and end of the sampled signal) or tapering function.

    References
    ----------
    .. [1] Blackman, R.B. and Tukey, J.W., (1958) The measurement of power
           spectra, Dover Publications, New York.
    .. [2] E.R. Kanasewich, "Time Sequence Analysis in Geophysics",
           The University of Alberta Press, 1975, pp. 106-108.
    .. [3] Wikipedia, "Window function",
           http://en.wikipedia.org/wiki/Window_function
    .. [4] W.H. Press,  B.P. Flannery, S.A. Teukolsky, and W.T. Vetterling,
           "Numerical Recipes", Cambridge University Press, 1986, page 425.

    Examples
    --------
    >>> scipy.signal.hann(12)
    array([ 0.        ,  0.07937323,  0.29229249,  0.57115742,  0.82743037,
            0.97974649,  0.97974649,  0.82743037,  0.57115742,  0.29229249,
            0.07937323,  0.        ])

    Plot the window and its frequency response:

    >>> from numpy.fft import fft, fftshift
    >>> window = scipy.signal.hann(51)
    >>> plt.plot(window)
    [<matplotlib.lines.Line2D object at 0x...>]
    >>> plt.title("Hann window")
    <matplotlib.text.Text object at 0x...>
    >>> plt.ylabel("Amplitude")
    <matplotlib.text.Text object at 0x...>
    >>> plt.xlabel("Sample")
    <matplotlib.text.Text object at 0x...>
    >>> plt.show()

    >>> plt.figure()
    <matplotlib.figure.Figure object at 0x...>
    >>> A = fft(window, 2048) / 25.5
    >>> mag = np.abs(fftshift(A))
    >>> freq = np.linspace(-0.5, 0.5, len(A))
    >>> response = 20 * np.log10(mag)
    >>> response = np.clip(response, -100, 100)
    >>> plt.plot(freq, response)
    [<matplotlib.lines.Line2D object at 0x...>]
    >>> plt.title("Frequency response of the Hann window")
    <matplotlib.text.Text object at 0x...>
    >>> plt.ylabel("Magnitude [dB]")
    <matplotlib.text.Text object at 0x...>
    >>> plt.xlabel("Normalized frequency [cycles per sample]")
    <matplotlib.text.Text object at 0x...>
    >>> plt.axis('tight')
    (-0.5, 0.5, -100.0, ...)
    >>> plt.show()

    """
    # Docstring adapted from NumPy's hanning function
    if M < 1:
        return np.array([])
    if M == 1:
        return np.ones(1, 'd')
    odd = M % 2
    if not sym and not odd:
        M = M + 1
    n = np.arange(0, M)
    w = 0.5 - 0.5 * np.cos(2.0 * np.pi * n / (M - 1))
    if not sym and not odd:
        w = w[:-1]
    return w

hanning = hann


def barthann(M, sym=True):
    """Return a modified Bartlett-Hann window.

    Parameters
    ----------
    M : int
        Number of points in the output window. If zero or less, an empty
        array is returned.
    sym : bool, optional
        When True, generates a symmetric window, for use in filter design. 
        When False, generates a periodic window, for use in spectral analysis.

    Returns
    -------
    w : ndarray
        The window, with the maximum value normalized to 1 (though the value 1 
        does not appear if the number of samples is even and sym is True).

    """
    if M < 1:
        return np.array([])
    if M == 1:
        return np.ones(1, 'd')
    odd = M % 2
    if not sym and not odd:
        M = M + 1
    n = np.arange(0, M)
    fac = np.abs(n / (M - 1.0) - 0.5)
    w = 0.62 - 0.48 * fac + 0.38 * np.cos(2 * np.pi * fac)
    if not sym and not odd:
        w = w[:-1]
    return w


def hamming(M, sym=True):
    """Return a Hamming window.

    The Hamming window is a taper formed by using a raised cosine with 
    non-zero endpoints, optimized to minimize the nearest side lobe.
    
    Parameters
    ----------
    M : int
        Number of points in the output window. If zero or less, an empty
        array is returned.
    sym : bool, optional
        When True, generates a symmetric window, for use in filter design. 
        When False, generates a periodic window, for use in spectral analysis.

    Returns
    -------
    w : ndarray
        The window, with the maximum value normalized to 1 (though the value 1 
        does not appear if the number of samples is even and sym is True).

    See Also
    --------
    bartlett, blackman, hann, kaiser

    Notes
    -----
    The Hamming window is defined as

    .. math::  w(n) = 0.54 - 0.46cos\\left(\\frac{2\\pi{n}}{M-1}\\right)
               \\qquad 0 \\leq n \\leq M-1

    The Hamming was named for R. W. Hamming, an associate of J. W. Tukey and
    is described in Blackman and Tukey. It was recommended for smoothing the
    truncated autocovariance function in the time domain.
    Most references to the Hamming window come from the signal processing
    literature, where it is used as one of many windowing functions for
    smoothing values.  It is also known as an apodization (which means
    "removing the foot", i.e. smoothing discontinuities at the beginning
    and end of the sampled signal) or tapering function.

    References
    ----------
    .. [1] Blackman, R.B. and Tukey, J.W., (1958) The measurement of power
           spectra, Dover Publications, New York.
    .. [2] E.R. Kanasewich, "Time Sequence Analysis in Geophysics", The
           University of Alberta Press, 1975, pp. 109-110.
    .. [3] Wikipedia, "Window function",
           http://en.wikipedia.org/wiki/Window_function
    .. [4] W.H. Press,  B.P. Flannery, S.A. Teukolsky, and W.T. Vetterling,
           "Numerical Recipes", Cambridge University Press, 1986, page 425.

    Examples
    --------
    >>> scipy.signal.hamming(12)
    array([ 0.08      ,  0.15302337,  0.34890909,  0.60546483,  0.84123594,
            0.98136677,  0.98136677,  0.84123594,  0.60546483,  0.34890909,
            0.15302337,  0.08      ])

    Plot the window and the frequency response:

    >>> from numpy.fft import fft, fftshift
    >>> window = scipy.signal.hamming(51)
    >>> plt.plot(window)
    [<matplotlib.lines.Line2D object at 0x...>]
    >>> plt.title("Hamming window")
    <matplotlib.text.Text object at 0x...>
    >>> plt.ylabel("Amplitude")
    <matplotlib.text.Text object at 0x...>
    >>> plt.xlabel("Sample")
    <matplotlib.text.Text object at 0x...>
    >>> plt.show()

    >>> plt.figure()
    <matplotlib.figure.Figure object at 0x...>
    >>> A = fft(window, 2048) / 25.5
    >>> mag = np.abs(fftshift(A))
    >>> freq = np.linspace(-0.5, 0.5, len(A))
    >>> response = 20 * np.log10(mag)
    >>> response = np.clip(response, -100, 100)
    >>> plt.plot(freq, response)
    [<matplotlib.lines.Line2D object at 0x...>]
    >>> plt.title("Frequency response of Hamming window")
    <matplotlib.text.Text object at 0x...>
    >>> plt.ylabel("Magnitude [dB]")
    <matplotlib.text.Text object at 0x...>
    >>> plt.xlabel("Normalized frequency [cycles per sample]")
    <matplotlib.text.Text object at 0x...>
    >>> plt.axis('tight')
    (-0.5, 0.5, -100.0, ...)
    >>> plt.show()

    """
    # Docstring adapted from NumPy's hamming function
    if M < 1:
        return np.array([])
    if M == 1:
        return np.ones(1, 'd')
    odd = M % 2
    if not sym and not odd:
        M = M + 1
    n = np.arange(0, M)
    w = 0.54 - 0.46 * np.cos(2.0 * np.pi * n / (M - 1))
    if not sym and not odd:
        w = w[:-1]
    return w


def kaiser(M, beta, sym=True):
    """Return a Kaiser window.

    The Kaiser window is a taper formed by using a Bessel function.

    Parameters
    ----------
    M : int
        Number of points in the output window. If zero or less, an empty
        array is returned.
    beta : float
        Shape parameter, determines trade-off between main-lobe width and 
        side lobe level. As beta gets large, the window narrows.
    sym : bool, optional
        When True, generates a symmetric window, for use in filter design. 
        When False, generates a periodic window, for use in spectral analysis.
        
    Returns
    -------
    w : ndarray
        The window, with the maximum value normalized to 1 (though the value 1 
        does not appear if the number of samples is even and sym is True).
    
    See Also
    --------
    bartlett, blackman, hamming, hann

    Notes
    -----
    The Kaiser window is defined as

    .. math::  w(n) = I_0\\left( \\beta \\sqrt{1-\\frac{4n^2}{(M-1)^2}}
               \\right)/I_0(\\beta)

    with

    .. math:: \\quad -\\frac{M-1}{2} \\leq n \\leq \\frac{M-1}{2},

    where :math:`I_0` is the modified zeroth-order Bessel function.

    The Kaiser was named for Jim Kaiser, who discovered a simple approximation
    to the DPSS window based on Bessel functions.
    The Kaiser window is a very good approximation to the Digital Prolate
    Spheroidal Sequence, or Slepian window, which is the transform which
    maximizes the energy in the main lobe of the window relative to total
    energy.

    The Kaiser can approximate many other windows by varying the beta
    parameter.

    ====  =======================
    beta  Window shape
    ====  =======================
    0     Rectangular
    5     Similar to a Hamming
    6     Similar to a Hann
    8.6   Similar to a Blackman
    ====  =======================

    A beta value of 14 is probably a good starting point. Note that as beta
    gets large, the window narrows, and so the number of samples needs to be
    large enough to sample the increasingly narrow spike, otherwise nans will
    get returned.

    Most references to the Kaiser window come from the signal processing
    literature, where it is used as one of many windowing functions for
    smoothing values.  It is also known as an apodization (which means
    "removing the foot", i.e. smoothing discontinuities at the beginning
    and end of the sampled signal) or tapering function.

    References
    ----------
    .. [1] J. F. Kaiser, "Digital Filters" - Ch 7 in "Systems analysis by
           digital computer", Editors: F.F. Kuo and J.F. Kaiser, p 218-285.
           John Wiley and Sons, New York, (1966).
    .. [2] E.R. Kanasewich, "Time Sequence Analysis in Geophysics", The
           University of Alberta Press, 1975, pp. 177-178.
    .. [3] Wikipedia, "Window function",
           http://en.wikipedia.org/wiki/Window_function

    Examples
    --------
    >>> scipy.signal.kaiser(12, 14)
    array([ 0.00000773,  0.00346009,  0.04652002,  0.22973712,  0.59988532,
            0.9456749 ,  0.9456749 ,  0.59988532,  0.22973712,  0.04652002,
            0.00346009,  0.00000773])

    Plot the window and the frequency response:

    >>> from numpy.fft import fft, fftshift
    >>> window = scipy.signal.kaiser(51, 14)
    >>> plt.plot(window)
    [<matplotlib.lines.Line2D object at 0x...>]
    >>> plt.title("Kaiser window")
    <matplotlib.text.Text object at 0x...>
    >>> plt.ylabel("Amplitude")
    <matplotlib.text.Text object at 0x...>
    >>> plt.xlabel("Sample")
    <matplotlib.text.Text object at 0x...>
    >>> plt.show()

    >>> plt.figure()
    <matplotlib.figure.Figure object at 0x...>
    >>> A = fft(window, 2048) / 25.5
    >>> mag = np.abs(fftshift(A))
    >>> freq = np.linspace(-0.5, 0.5, len(A))
    >>> response = 20 * np.log10(mag)
    >>> response = np.clip(response, -100, 100)
    >>> plt.plot(freq, response)
    [<matplotlib.lines.Line2D object at 0x...>]
    >>> plt.title("Frequency response of Kaiser window")
    <matplotlib.text.Text object at 0x...>
    >>> plt.ylabel("Magnitude [dB]")
    <matplotlib.text.Text object at 0x...>
    >>> plt.xlabel("Normalized frequency [cycles per sample]")
    <matplotlib.text.Text object at 0x...>
    >>> plt.axis('tight')
    (-0.5, 0.5, -100.0, ...)
    >>> plt.show()

    """
    # Docstring adapted from NumPy's kaiser function
    if M < 1:
        return np.array([])
    if M == 1:
        return np.ones(1, 'd')
    odd = M % 2
    if not sym and not odd:
        M = M + 1
    n = np.arange(0, M)
    alpha = (M - 1) / 2.0
    w = (special.i0(beta * np.sqrt(1 - ((n - alpha) / alpha) ** 2.0)) /
         special.i0(beta))
    if not sym and not odd:
        w = w[:-1]
    return w


def gaussian(M, std, sym=True):
    """Return a Gaussian window.

    Parameters
    ----------
    M : int
        Number of points in the output window. If zero or less, an empty
        array is returned.
    std : float
        Standard deviation.
    sym : bool, optional
        When True, generates a symmetric window, for use in filter design. 
        When False, generates a periodic window, for use in spectral analysis.

    Returns
    -------
    w : ndarray
        The window, with the maximum value normalized to 1 (though the value 1 
        does not appear if the number of samples is even and sym is True).

    Notes
    -----
    The Gaussian window is defined as

    .. math::  w(n) = e^{ -\\frac{1}{2}\\left(\\frac{n}{\\sigma}\\right)^2 }

    """
    if M < 1:
        return np.array([])
    if M == 1:
        return np.ones(1, 'd')
    odd = M % 2
    if not sym and not odd:
        M = M + 1
    n = np.arange(0, M) - (M - 1.0) / 2.0
    sig2 = 2 * std * std
    w = np.exp(-n ** 2 / sig2)
    if not sym and not odd:
        w = w[:-1]
    return w


def general_gaussian(M, p, sig, sym=True):
    """Return a window with a generalized Gaussian shape.

    The Gaussian shape is defined as ``exp(-0.5*abs(x/sig)**(2*p))``, the
    half-power point is at ``(2*log(2)))**(1/(2*p)) * sig``.

    """
    # FIXME: What are p and sig called in English?  Improve docstring
    if M < 1:
        return np.array([])
    if M == 1:
        return np.ones(1, 'd')
    odd = M % 2
    if not sym and not odd:
        M = M + 1
    n = np.arange(0, M) - (M - 1.0) / 2.0
    w = np.exp(-0.5 * np.abs(n / sig) ** (2 * p))
    if not sym and not odd:
        w = w[:-1]
    return w


# `chebwin` contributed by Kumar Appaiah.

def chebwin(M, at, sym=True):
    """Return a Dolph-Chebyshev window.

    Parameters
    ----------
    M : int
        Number of points in the output window. If zero or less, an empty
        array is returned.
    at : float
        Attenuation (in dB).
    sym : bool, optional
        When True, generates a symmetric window, for use in filter design. 
        When False, generates a periodic window, for use in spectral analysis.

    Returns
    -------
    w : ndarray
        The window function
    
    """
    if M < 1:
        return np.array([])
    if M == 1:
        return np.ones(1, 'd')

    odd = M % 2
    if not sym and not odd:
        M = M + 1

    # compute the parameter beta
    order = M - 1.0
    beta = np.cosh(1.0 / order * np.arccosh(10 ** (np.abs(at) / 20.)))
    k = np.r_[0:M] * 1.0
    x = beta * np.cos(np.pi * k / M)
    # Find the window's DFT coefficients
    # Use analytic definition of Chebyshev polynomial instead of expansion
    # from scipy.special. Using the expansion in scipy.special leads to errors.
    p = np.zeros(x.shape)
    p[x > 1] = np.cosh(order * np.arccosh(x[x > 1]))
    p[x < -1] = (1 - 2 * (order % 2)) * np.cosh(order * np.arccosh(-x[x < -1]))
    p[np.abs(x) <= 1] = np.cos(order * np.arccos(x[np.abs(x) <= 1]))

    # Appropriate IDFT and filling up
    # depending on even/odd M
    if M % 2:
        w = np.real(fft(p))
        n = (M + 1) / 2
        w = w[:n] / w[0]
        w = np.concatenate((w[n - 1:0:-1], w))
    else:
        p = p * np.exp(1.j * np.pi / M * np.r_[0:M])
        w = np.real(fft(p))
        n = M / 2 + 1
        w = w / w[1]
        w = np.concatenate((w[n - 1:0:-1], w[1:n]))
    if not sym and not odd:
        w = w[:-1]
    return w


def slepian(M, width, sym=True):
    """Return the M-point Slepian window.
    
    Used to maximize the energy concentration in the main lobe.  Also called 
    the digital prolate spheroidal sequence (DPSS).

    """
    # FIXME: Improve docstring, explain what "width" does
    
    if (M * width > 27.38):
        raise ValueError("Cannot reliably obtain slepian sequences for"
              " M*width > 27.38.")
    if M < 1:
        return np.array([])
    if M == 1:
        return np.ones(1, 'd')
    odd = M % 2
    if not sym and not odd:
        M = M + 1

    twoF = width / 2.0
    alpha = (M - 1) / 2.0
    m = np.arange(0, M) - alpha
    n = m[:, np.newaxis]
    k = m[np.newaxis, :]
    AF = twoF * special.sinc(twoF * (n - k))
    [lam, vec] = linalg.eig(AF)
    ind = np.argmax(abs(lam), axis=-1)
    w = np.abs(vec[:, ind])
    w = w / max(w)

    if not sym and not odd:
        w = w[:-1]
    return w


def get_window(window, Nx, fftbins=True):
    """
    Return a window of length `Nx` and type `window`.

    Parameters
    ----------
    window : string, float, or tuple
        The type of window to create. See below for more details.
    Nx : int
        The number of samples in the window.
    fftbins : bool, optional
        If True, create a "periodic" window ready to use with ifftshift
        and be multiplied by the result of an fft (SEE ALSO fftfreq).

    Notes
    -----
    Window types:

        boxcar, triang, blackman, hamming, hann, bartlett, flattop, 
        parzen, bohman, blackmanharris, nuttall, barthann,
        kaiser (needs beta), gaussian (needs std),
        general_gaussian (needs power, width),
        slepian (needs width), chebwin (needs attenuation)


    If the window requires no parameters, then `window` can be a string.

    If the window requires parameters, then `window` must be a tuple
    with the first argument the string name of the window, and the next
    arguments the needed parameters.

    If `window` is a floating point number, it is interpreted as the beta
    parameter of the kaiser window.

    Each of the window types listed above is also the name of
    a function that can be called directly to create a window of
    that type.

    Examples
    --------
    >>> get_window('triang', 7)
    array([ 0.25,  0.5 ,  0.75,  1.  ,  0.75,  0.5 ,  0.25])
    >>> get_window(('kaiser', 4.0), 9)
    array([ 0.08848053,  0.32578323,  0.63343178,  0.89640418,  1.        ,
            0.89640418,  0.63343178,  0.32578323,  0.08848053])
    >>> get_window(4.0, 9)
    array([ 0.08848053,  0.32578323,  0.63343178,  0.89640418,  1.        ,
            0.89640418,  0.63343178,  0.32578323,  0.08848053])

    """

    sym = not fftbins
    try:
        beta = float(window)
    except (TypeError, ValueError):
        args = ()
        if isinstance(window, tuple):
            winstr = window[0]
            if len(window) > 1:
                args = window[1:]
        elif isinstance(window, str):
            if window in ['kaiser', 'ksr', 'gaussian', 'gauss', 'gss',
                        'general gaussian', 'general_gaussian',
                        'general gauss', 'general_gauss', 'ggs',
                        'slepian', 'optimal', 'slep', 'dss',
                        'chebwin', 'cheb']:
                raise ValueError("The '" + window + "' window needs one or "
                                    "more parameters  -- pass a tuple.")
            else:
                winstr = window

        if winstr in ['blackman', 'black', 'blk']:
            winfunc = blackman
        elif winstr in ['triangle', 'triang', 'tri']:
            winfunc = triang
        elif winstr in ['hamming', 'hamm', 'ham']:
            winfunc = hamming
        elif winstr in ['bartlett', 'bart', 'brt']:
            winfunc = bartlett
        elif winstr in ['hanning', 'hann', 'han']:
            winfunc = hann
        elif winstr in ['blackmanharris', 'blackharr', 'bkh']:
            winfunc = blackmanharris
        elif winstr in ['parzen', 'parz', 'par']:
            winfunc = parzen
        elif winstr in ['bohman', 'bman', 'bmn']:
            winfunc = bohman
        elif winstr in ['nuttall', 'nutl', 'nut']:
            winfunc = nuttall
        elif winstr in ['barthann', 'brthan', 'bth']:
            winfunc = barthann
        elif winstr in ['flattop', 'flat', 'flt']:
            winfunc = flattop
        elif winstr in ['kaiser', 'ksr']:
            winfunc = kaiser
        elif winstr in ['gaussian', 'gauss', 'gss']:
            winfunc = gaussian
        elif winstr in ['general gaussian', 'general_gaussian',
                        'general gauss', 'general_gauss', 'ggs']:
            winfunc = general_gaussian
        elif winstr in ['boxcar', 'box', 'ones', 'rect', 'rectangular']:
            winfunc = boxcar
        elif winstr in ['slepian', 'slep', 'optimal', 'dpss', 'dss']:
            winfunc = slepian
        elif winstr in ['chebwin', 'cheb']:
            winfunc = chebwin
        else:
            raise ValueError("Unknown window type.")

        params = (Nx,) + args + (sym,)
    else:
        winfunc = kaiser
        params = (Nx, beta, sym)

    return winfunc(*params)
