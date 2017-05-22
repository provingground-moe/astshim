/*
 * LSST Data Management System
 * Copyright 2017 AURA/LSST.
 *
 * This product includes software developed by the
 * LSST Project (http://www.lsst.org/).
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
#ifndef ASTSHIM_LUTMAP_H
#define ASTSHIM_LUTMAP_H

#include <memory>

#include "astshim/base.h"
#include "astshim/Mapping.h"

namespace ast {

/**
LutMap is a specialised form of @ref Mapping which transforms 1-dimensional coordinates by using
linear interpolation in a lookup table. Each input coordinate value is first scaled to give
the index of an entry in the table by subtracting a starting value (the input coordinate corresponding to
the first table entry) and dividing by an increment (the difference in input coordinate value
between adjacent table entries).

The resulting index will usually contain a fractional part, so the output coordinate value
is then generated by interpolating linearly between the appropriate entries in the table.
If the index lies outside the range of the table, linear extrapolation is used based on
the two nearest entries (i.e. the two entries at the start or end of the table, as appropriate).

If the lookup table entries increase or decrease monotonically, then the inverse transformation
may also be performed.

### Attributes

In addition to those attributes provided by @ref Mapping and @ref Object,
@ref LutMap has the following attributes:

- @ref LutMap_LutEpsilon "LutEpsilon": The relative error of the values in the table.
- @ref LutMap_LutInterp "LutInterp": The interpolation method to use between table entries.

### Notes

- If the entries in the lookup table either increase or decrease monotonically, then the `LutMap`'s
    `TranInverse` attribute will have a value of one, indicating that the inverse transformation
    can be performed. Otherwise, it will have a value of zero, so that any attempt to use
    the inverse transformation will result in an error.
*/
class LutMap : public Mapping {
    friend class Object;

public:
    /**
    Construct an LutMap


    @param[in] lut  The lookup table.
    @param[in] start  The input coordinate value which corresponds to the first lookup table entry.
    @param[in] inc  The lookup table spacing (the increment in input coordinate value between successive
                    lookup table entries). This value may be positive or negative, but must not be zero.
    @param[in] options   Comma-separated list of attribute assignments.
    @param[in] options  Comma-separated list of attribute assignments.
    */
    explicit LutMap(std::vector<double> const &lut, double start, double inc, std::string const &options = "")
            : Mapping(reinterpret_cast<AstMapping *>(
                      astLutMap(lut.size(), lut.data(), start, inc, "%s", options.c_str()))) {}

    virtual ~LutMap() {}

    LutMap(LutMap const &) = delete;
    LutMap(LutMap &&) = default;
    LutMap &operator=(LutMap const &) = delete;
    LutMap &operator=(LutMap &&) = default;

    /// Return a deep copy of this object.
    std::shared_ptr<LutMap> copy() const { return std::static_pointer_cast<LutMap>(copyPolymorphic()); }

    /**
    Get attribute @ref LutMap_LutEpsilon "LutEpsilon": the relative error of the values in the table.
    */
    double getLutEpsilon() const { return getD("LutEpsilon"); }

    /**
    Get attribute @ref LutMap_LutInterp "LutInterp": the interpolation method to use between table entries.
    */
    int getLutInterp() const { return getI("LutInterp"); }

protected:
    virtual std::shared_ptr<Object> copyPolymorphic() const override {
        return copyImpl<LutMap, AstLutMap>();
    }

    /// Construct an LutMap from a raw AST pointer
    explicit LutMap(AstLutMap *rawptr) : Mapping(reinterpret_cast<AstMapping *>(rawptr)) {
        if (!astIsALutMap(getRawPtr())) {
            std::ostringstream os;
            os << "this is a " << getClassName() << ", which is not a LutMap";
            throw std::invalid_argument(os.str());
        }
    }
};

}  // namespace ast

#endif
