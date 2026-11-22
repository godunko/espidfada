//
//  Copyright (C) 2026, Vadim Godunko
//
//  SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//

#ifndef ESPIDFADA_CONSTANTS_H
#define ESPIDFADA_CONSTANTS_H

/* Sizes encode value + 1 so even zero cannot become a zero-sized symbol.
 * These objects belong only in a dedicated, unlinked probe translation unit. */

#define ESPIDFADA_SIZEOF(name, type) \
    const unsigned char espidfada_sizeof_##name[sizeof(type) + 1] \
        __attribute__((used)) = {0}
#define ESPIDFADA_ALIGNOF(name, type) \
    const unsigned char espidfada_alignof_##name[_Alignof(type) + 1] \
        __attribute__((used)) = {0}

#endif
