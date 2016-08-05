/*
 * LSST Data Management System
 *
 * This product includes software developed by the
 * LSST Project (http://www.lsst.org/).
 * See the COPYRIGHT file
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the LSST License Statement and
 * the GNU General Public License along with this program.  If not,
 * see <https://www.lsstcorp.org/LegalNotices/>.
 */
#include <memory>
#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "astshim/Mapping.h"
#include "astshim/UnitNormMap.h"

namespace py = pybind11;
using namespace pybind11::literals;

namespace ast {

PYBIND11_PLUGIN(unitNormMap) {
    py::module::import("astshim.mapping");

    py::module mod("unitNormMap", "Python wrapper for UnitNormMap");

    py::class_<UnitNormMap, std::shared_ptr<UnitNormMap>, Mapping> cls(mod, "UnitNormMap");

    cls.def(py::init<std::vector<double> const &, std::string const &>(), "centre"_a, "options"_a="");

    cls.def("copy", &UnitNormMap::copy);

    return mod.ptr();
}

}  // ast
