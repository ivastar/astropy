# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""Testing :mod:`astropy.cosmology.flrw.lambdacdm`."""

##############################################################################
# IMPORTS


# THIRD PARTY
import pytest

# LOCAL
import astropy.units as u
from astropy.cosmology import FlatLambdaCDM, LambdaCDM
from astropy.cosmology.flrw.lambdacdm import ellipkinc, hyp2f1
from astropy.cosmology.tests.helper import get_redshift_methods
from astropy.cosmology.tests.test_core import invalid_zs, valid_zs
from astropy.utils.compat.optional_deps import HAS_SCIPY

from .test_base import FlatFLRWMixinTest, FLRWTest

##############################################################################
# TESTS
##############################################################################


@pytest.mark.skipif(HAS_SCIPY, reason="scipy is installed")
def test_optional_deps_functions():
    """Test stand-in functions when optional dependencies not installed."""
    with pytest.raises(ModuleNotFoundError, match="No module named 'scipy.special'"):
        ellipkinc()

    with pytest.raises(ModuleNotFoundError, match="No module named 'scipy.special'"):
        hyp2f1()


##############################################################################


class TestLambdaCDM(FLRWTest):
    """Test :class:`astropy.cosmology.LambdaCDM`."""

    def setup_class(self):
        """Setup for testing."""
        super().setup_class(self)
        self.cls = LambdaCDM

    # ===============================================================
    # Method & Attribute Tests

    _FLRW_redshift_methods = get_redshift_methods(
        LambdaCDM, include_private=True, include_z2=False
    ) - {"_dS_age"}
    # `_dS_age` is removed because it doesn't strictly rely on the value of `z`,
    # so any input that doesn't trip up ``np.shape`` is "valid"

    @pytest.mark.skipif(not HAS_SCIPY, reason="scipy is not installed")
    @pytest.mark.parametrize("z, exc", invalid_zs)
    @pytest.mark.parametrize("method", _FLRW_redshift_methods)
    def test_redshift_method_bad_input(self, cosmo, method, z, exc):
        """Test all the redshift methods for bad input."""
        super().test_redshift_method_bad_input(cosmo, method, z, exc)

    @pytest.mark.parametrize("z", valid_zs)
    def test_w(self, cosmo, z):
        """Test :meth:`astropy.cosmology.LambdaCDM.w`."""
        super().test_w(cosmo, z)

        w = cosmo.w(z)
        assert u.allclose(w, -1.0)

    def test_repr(self, cosmo_cls, cosmo):
        """Test method ``.__repr__()``."""
        super().test_repr(cosmo_cls, cosmo)

        expected = (
            'LambdaCDM(name="ABCMeta", H0=70.0 km / (Mpc s), Om0=0.27,'
            " Ode0=0.73, Tcmb0=3.0 K, Neff=3.04, m_nu=[0. 0. 0.] eV,"
            " Ob0=0.03)"
        )
        assert repr(cosmo) == expected


# -----------------------------------------------------------------------------


class TestFlatLambdaCDM(FlatFLRWMixinTest, TestLambdaCDM):
    """Test :class:`astropy.cosmology.FlatLambdaCDM`."""

    def setup_class(self):
        """Setup for testing."""
        super().setup_class(self)
        self.cls = FlatLambdaCDM

    @pytest.mark.skipif(not HAS_SCIPY, reason="scipy is not installed")
    @pytest.mark.parametrize("z, exc", invalid_zs)
    @pytest.mark.parametrize("method", TestLambdaCDM._FLRW_redshift_methods - {"Otot"})
    def test_redshift_method_bad_input(self, cosmo, method, z, exc):
        """Test all the redshift methods for bad input."""
        super().test_redshift_method_bad_input(cosmo, method, z, exc)

    # ===============================================================
    # Method & Attribute Tests

    def test_repr(self, cosmo_cls, cosmo):
        """Test method ``.__repr__()``."""
        super().test_repr(cosmo_cls, cosmo)

        expected = (
            'FlatLambdaCDM(name="ABCMeta", H0=70.0 km / (Mpc s),'
            " Om0=0.27, Tcmb0=3.0 K, Neff=3.04, m_nu=[0. 0. 0.] eV,"
            " Ob0=0.03)"
        )
        assert repr(cosmo) == expected


##############################################################################
# Comparison to Other Codes


@pytest.mark.skipif(not HAS_SCIPY, reason="requires scipy.")
def test_flat_z1():
    """Test a flat cosmology at z=1 against several other on-line calculators.

    Test values were taken from the following web cosmology calculators on
    2012-02-11:

    Wright: http://www.astro.ucla.edu/~wright/CosmoCalc.html
            (https://ui.adsabs.harvard.edu/abs/2006PASP..118.1711W)
    Kempner: http://www.kempner.net/cosmic.php
    iCosmos: http://www.icosmos.co.uk/index.html
    """
    cosmo = FlatLambdaCDM(H0=70, Om0=0.27, Tcmb0=0.0)

    # The order of values below is Wright, Kempner, iCosmos'
    assert u.allclose(
        cosmo.comoving_distance(1), [3364.5, 3364.8, 3364.7988] * u.Mpc, rtol=1e-4
    )
    assert u.allclose(
        cosmo.angular_diameter_distance(1),
        [1682.3, 1682.4, 1682.3994] * u.Mpc,
        rtol=1e-4,
    )
    assert u.allclose(
        cosmo.luminosity_distance(1), [6729.2, 6729.6, 6729.5976] * u.Mpc, rtol=1e-4
    )
    assert u.allclose(
        cosmo.lookback_time(1), [7.841, 7.84178, 7.843] * u.Gyr, rtol=1e-3
    )
    assert u.allclose(
        cosmo.lookback_distance(1), [2404.0, 2404.24, 2404.4] * u.Mpc, rtol=1e-3
    )
