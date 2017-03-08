/* vim: set sw=4 sts=4 et foldmethod=syntax : */

#include "umg_attr_lab.hh"
#include "graph.hh"

#include <fstream>

namespace
{
    auto read_word(std::ifstream & infile) -> unsigned
    {
        unsigned x;
        infile >> x;
        return x;
    }
}

auto read_umg_attr_lab(const std::string & filename) -> Graph
{
    Graph result(0);

    std::ifstream infile{ filename };
    if (! infile)
        throw GraphFileError{ filename, "unable to open file" };

    unsigned vert_count = read_word(infile);
    result.resize(vert_count);
    if (! infile)
        throw GraphFileError{ filename, "error reading size" };

    unsigned edge_count = read_word(infile);

    for (unsigned i = 0; i < vert_count; i++)
        result.add_label(i, read_word(infile));

    while (edge_count-- > 0) {
        unsigned from = read_word(infile),
                 to   = read_word(infile),
                 val  = read_word(infile);

        if (from >= result.size() || to >= result.size())
            throw GraphFileError{ filename, "edge index out of bounds" };

        result.add_edge(from, to, val);
    }

    std::string rest;
    if (infile >> rest)
        throw GraphFileError{ filename, "EOF not reached, next text is \"" + rest + "\"" };
    if (! infile.eof())
        throw GraphFileError{ filename, "EOF not reached" };

    return result;
}

