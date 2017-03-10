override CXXFLAGS += -O3 -march=native -std=c++14 -I./ -W -Wall -g -ggdb3 -pthread
override LDFLAGS += -pthread

boost_ldlibs := -lboost_regex -lboost_thread -lboost_system -lboost_program_options

TGT_LDLIBS := $(boost_ldlibs)

TARGET := solve_subgraph_isomorphism

SOURCES := \
    sequential.cc \
    graph.cc \
    lad.cc \
    dimacs.cc \
    vf.cc \
    umg_attr.cc \
    umg_attr_lab.cc \
    solve_subgraph_isomorphism.cc