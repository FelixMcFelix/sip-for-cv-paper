/* vim: set sw=4 sts=4 et foldmethod=syntax : */

#include "lad_pos.hh"
#include "graph.hh"

#include <fstream>

namespace
{
    auto read_word(std::ifstream &infile) -> unsigned
    {
        unsigned x;
        infile >> x;
        return x;
    }

    auto scan_to_pos(std::ifstream &infile, const std::string &filename) -> void
    {
        char c;
        infile >> c;
        while (c != '@')
        {
            if (c == '\n' || c == EOF)
                throw GraphFileError(filename, "file missing position data");
            infile >> c;
        }
    }
}

auto read_lad_pos(const std::string & filename) -> Graph
{
    Graph result(0);

    std::ifstream infile{ filename };
    if (! infile)
        throw GraphFileError{ filename, "unable to open file" };

    result.resize(read_word(infile));
    if (! infile)
        throw GraphFileError{ filename, "error reading size" };

    for (unsigned r = 0 ; r < result.size() ; ++r) {
        unsigned c_end = read_word(infile);
        if (! infile)
            throw GraphFileError{ filename, "error reading edges count" };

        for (unsigned c = 0 ; c < c_end ; ++c) {
            unsigned e = read_word(infile);

            if (e >= result.size())
                throw GraphFileError{ filename, "edge index out of bounds" };

            result.add_edge(r, e);
        }

        // New stuff
        scan_to_pos(infile, filename);
        unsigned x = read_word(infile),
            y = read_word(infile);
        result.add_pos(r, x, y);
    }

    std::string rest;
    if (infile >> rest)
        throw GraphFileError{ filename, "EOF not reached, next text is \"" + rest + "\"" };
    if (! infile.eof())
        throw GraphFileError{ filename, "EOF not reached" };

    return result;
}

