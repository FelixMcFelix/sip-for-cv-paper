/* vim: set sw=4 sts=4 et foldmethod=syntax : */

#include <iostream>
#include "graph.hh"
#include <algorithm>
#include <cstdlib>

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

    // std::cout << "checking "
    //     << a << ' '
    //     << b << ' '
    //     << val << ' '
    //     << std::get<0>(sequence_data) << ' '
    //     << edge_list.size() << '\n';

    // std::cout << "List from " << a << " to " << b << '\n';
    // for (auto el : edge_list)
    //     std::cout << "val " << std::get<0>(el) << " count " << std::get<1>(el) << '\n';
    // std::cout << "TOTAL " << std::get<0>(sequence_data) << '\n';

    std::get<1>(sequence_data) = edge_list;
    _sequences[_position(a, b)] = _sequences[_position(b, a)] = sequence_data;
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