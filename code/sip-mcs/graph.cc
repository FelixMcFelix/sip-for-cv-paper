/* vim: set sw=4 sts=4 et foldmethod=syntax : */

#include "graph.hh"
#include <algorithm>

GraphFileError::GraphFileError(const std::string & filename, const std::string & message) throw () :
    _what("Error reading graph file '" + filename + "': " + message)
{
}

auto GraphFileError::what() const throw () -> const char *
{
    return _what.c_str();
}

Graph::Graph(unsigned size)
{
    if (0 != size)
        resize(size);
}

auto Graph::_position(unsigned a, unsigned b) const -> AdjacencyMatrix::size_type
{
    return (a * _size) + b;
}

auto Graph::resize(unsigned size) -> void
{
    _size = size;
    _adjacency.resize(size * size);
    _sequences.resize(size * size);
}

auto Graph::add_edge(unsigned a, unsigned b) -> void
{
    _adjacency[_position(a, b)] = 1;
    _adjacency[_position(b, a)] = 1;
}

auto Graph::add_edge(unsigned a, unsigned b, unsigned val) -> void
{
    add_edge(a, b);
    _attr_graph &= true;

    auto sequence_data = _sequences[_position(a, b)];
    std::get<0>(sequence_data) += 1;
    auto edge_list = std::get<1>(sequence_data);

    if (edge_list.empty())
        edge_list.push_back(std::pair<std::uint16_t, std::uint16_t>(val, 1));
    else
        for (unsigned i = 0; i < edge_list.size(); ++i) {
            auto curr_val = std::get<0>(edge_list[i]);

            if (val == curr_val) {
                std::get<1>(edge_list[i]) += 1;
            } else if ((i == edge_list.size()-1 && val > curr_val) || (i < edge_list.size()-1 && val > curr_val && val < std::get<0>(edge_list[i+1]))) {
                edge_list.insert(edge_list.begin() + i + 1, std::pair<std::uint16_t, std::uint16_t>(val, 1));
                break;
            } else if (i == 0 && val < curr_val) {
                edge_list.insert(edge_list.begin() + i, std::pair<std::uint16_t, std::uint16_t>(val, 1));
                break;
            }
        }

    std::get<1>(sequence_data) = edge_list;
    _sequences[_position(a, b)] = _sequences[_position(b, a)] = sequence_data;
}

auto Graph::get_edge_seq(unsigned a, unsigned b) const -> const Sequence
{
    return _sequences[_position(a, b)];
}

auto in(const Graph::Sequence & pattern, const Graph::Sequence & target) -> bool
{
    for (
        auto it_p  = pattern.second.begin(),
             end_p = pattern.second.end(),
             it_t  = target.second.begin(),
             end_t = target.second.end();
        it_p != end_p;
        it_p++, it_t++)
    {
        while(it_t != end_t && (*it_p).first != (*it_t).first)
            it_t++;

        if(it_t == end_t || (*it_p).second > (*it_t).second)
            return false;
    }

    return true;
}

auto Graph::get_seq_nhood(unsigned a, Sequence s) const -> const std::vector<unsigned>
{
    std::vector<unsigned> out;

    unsigned i = 0;
    for (auto it = _sequences.begin() + a * _size, end = _sequences.begin() + (a+1) * _size; it != end; it++, i++)
        if (in(s, *it))
            out.push_back(i);

    return out;
}

auto Graph::adjacent(unsigned a, unsigned b) const -> bool
{
    return _adjacency[_position(a, b)];
}

auto Graph::size() const -> unsigned
{
    return _size;
}

auto Graph::degree(unsigned a) const -> unsigned
{
    return std::count_if(
            _adjacency.begin() + a * _size,
            _adjacency.begin() + (a + 1) * _size,
            [] (unsigned x) { return !!x; });
}

auto Graph::is_attr_graph() const -> bool
{
    return _attr_graph;
}