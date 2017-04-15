/* vim: set sw=4 sts=4 et foldmethod=syntax : */

#ifndef GUARD_LAD_POS_HH
#define GUARD_LAD_POS_HH 1

#include "graph.hh"

#include <string>

/**
 * Read a LAD format file w/ positional data into a Graph.
 *
 * \throw GraphFileError
 */
auto read_lad_pos(const std::string & filename) -> Graph;

#endif
