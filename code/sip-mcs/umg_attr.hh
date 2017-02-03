/* vim: set sw=4 sts=4 et foldmethod=syntax : */

#ifndef PARASOLS_GUARD_GRAPH_UMG_ATTR_HH
#define PARASOLS_GUARD_GRAPH_UMG_ATTR_HH 1

#include "graph.hh"
#include <string>

/**
 * Read an undirected multigraph (w attributes) format file into a Graph.
 */
auto read_umg_attr(const std::string & filename) -> Graph;

#endif
