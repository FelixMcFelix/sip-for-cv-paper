/* vim: set sw=4 sts=4 et foldmethod=syntax : */

#include "lad.hh"
#include "vf.hh"
#include "dimacs.hh"
#include "umg_attr.hh"
#include "umg_attr_lab.hh"
#include "sequential.hh"

#include <boost/program_options.hpp>
#include <boost/filesystem.hpp>

namespace fs = boost::filesystem;

#include <iostream>
#include <exception>
#include <cstdlib>
#include <chrono>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <fstream>
#include <cmath>

namespace po = boost::program_options;

using std::chrono::steady_clock;
using std::chrono::duration_cast;
using std::chrono::milliseconds;

/* Helper: return a function that runs the specified algorithm, dealing
 * with timing information and timeouts. */
template <typename Result_, typename Params_, typename Data_>
auto run_this_wrapped(const std::function<Result_ (const Data_ &, const Params_ &)> & func)
    -> std::function<Result_ (const Data_ &, Params_ &, bool &, int)>
{
    return [func] (const Data_ & data, Params_ & params, bool & aborted, int timeout) -> Result_ {
        /* For a timeout, we use a thread and a timed CV. We also wake the
         * CV up if we're done, so the timeout thread can terminate. */
        std::thread timeout_thread;
        std::mutex timeout_mutex;
        std::condition_variable timeout_cv;
        std::atomic<bool> abort;
        abort.store(false);
        params.abort = &abort;
        if (0 != timeout) {
            timeout_thread = std::thread([&] {
                    auto abort_time = std::chrono::steady_clock::now() + std::chrono::seconds(timeout);
                    {
                        /* Sleep until either we've reached the time limit,
                         * or we've finished all the work. */
                        std::unique_lock<std::mutex> guard(timeout_mutex);
                        while (! abort.load()) {
                            if (std::cv_status::timeout == timeout_cv.wait_until(guard, abort_time)) {
                                /* We've woken up, and it's due to a timeout. */
                                aborted = true;
                                break;
                            }
                        }
                    }
                    abort.store(true);
                    });
        }

        /* Start the clock */
        params.start_time = std::chrono::steady_clock::now();

        try {
            auto result = func(data, params);

            /* Clean up the timeout thread */
            if (timeout_thread.joinable()) {
                {
                    std::unique_lock<std::mutex> guard(timeout_mutex);
                    abort.store(true);
                    timeout_cv.notify_all();
                }
                timeout_thread.join();
            }

            return result;
        }
        catch (...) {
            /* Clean up the timeout thread */
            if (timeout_thread.joinable()) {
                {
                    std::unique_lock<std::mutex> guard(timeout_mutex);
                    abort.store(true);
                    timeout_cv.notify_all();
                }
                timeout_thread.join();
            }

            throw;
        }
    };
}

/* Helper: return a function that runs the specified algorithm, dealing
 * with timing information and timeouts. */
template <typename Result_, typename Params_, typename Data_>
auto run_this(Result_ func(const Data_ &, const Params_ &)) -> std::function<Result_ (const Data_ &, Params_ &, bool &, int)>
{
    return run_this_wrapped(std::function<Result_ (const Data_ &, const Params_ &)>(func));
}

auto main(int argc, char * argv[]) -> int
{
    auto algorithm = sequential_ix_subgraph_isomorphism;

    unsigned use_neighbours;

    try {
        po::options_description display_options{ "Program options" };
        display_options.add_options()
            ("help",                                  "Display help information")
            ("timeout",            po::value<int>(),  "Abort after this many seconds")
            ("neighbours",         po::value<unsigned>(&use_neighbours)->default_value(5),  "Use this many neighbours for classification")
            ("format",             po::value<std::string>(), "Specify graph file format (lad, dimacs, vf, umg_attr or umg_attr_lab)")
            ("d2graphs",                              "Use d2 graphs")
            ("d2cgraphs",                             "Use d2 complement graphs")
            ("degree",                                "Use degree filtering")
            ("nds",                                   "Use NDS filtering")
            ("cnds",                                  "Use Combined NDS filtering")
            ("ilf",                                   "Use ILF filtering")
            ("except",             po::value<int>(),  "Allow this many pattern vertices to be excluded")
            ("high-wildcards",                        "Treat wildcard vertices as having high degree")
            ("induced",                               "Induced")
            ("expensive-stats",                       "Calculate expensive stats")
            ("edge-overlap",                          "Allow edge compatibility for any overlap in umg_attr")
            ("disable-attr-filtering",                "Disable filtering from umg_attr labels")
            ;

        po::options_description all_options{ "All options" };
        all_options.add_options()
            ("pattern-folder", "Specify the pattern folder (LAD format)")
            ("pattern-csv", "Specify the csv file mapping pattern graphs to labels")
            ("target-folder",  "Specify the target folder (LAD format)")
            ("target-csv",  "Specify the csv file mapping target graphs to labels")
            ;

        all_options.add(display_options);

        po::positional_options_description positional_options;
        positional_options
            .add("pattern-folder", 1)
            .add("pattern-csv", 1)
            .add("target-folder", 1)
            .add("target-csv", 1)
            ;

        po::variables_map options_vars;
        po::store(po::command_line_parser(argc, argv)
                .options(all_options)
                .positional(positional_options)
                .run(), options_vars);
        po::notify(options_vars);

        /* --help? Show a message, and exit. */
        if (options_vars.count("help")) {
            std::cout << "Usage: " << argv[0] << " [options] pattern-folder pattern-csv target-folder target-csv" << std::endl;
            std::cout << std::endl;
            std::cout << display_options << std::endl;
            return EXIT_SUCCESS;
        }

        /* No algorithm or no input file specified? Show a message and exit. */
        if (! options_vars.count("pattern-folder") || ! options_vars.count("target-folder") ||
            ! options_vars.count("pattern-csv") || ! options_vars.count("target-csv")) {
            std::cout << "Usage: " << argv[0] << " [options] pattern-folder pattern-csv target-folder target-csv" << std::endl;
            return EXIT_FAILURE;
        }

        /* Figure out what our options should be. */
        Params params;

        params.d2graphs = options_vars.count("d2graphs");
        params.d2cgraphs = options_vars.count("d2cgraphs");
        params.induced = options_vars.count("induced");
        params.degree = options_vars.count("degree");
        params.nds = options_vars.count("nds");
        params.cnds = options_vars.count("cnds");
        params.expensive_stats = options_vars.count("expensive-stats");
        params.high_wildcards = options_vars.count("high-wildcards");
        params.ilf = options_vars.count("ilf");
        params.edge_overlap = options_vars.count("edge-overlap");
        params.disable_attr_filter = options_vars.count("disable-attr-filtering");
        if (options_vars.count("except"))
            params.except = options_vars["except"].as<int>();

        auto read_function = read_lad;

        if (options_vars.count("format")) {
            if (options_vars["format"].as<std::string>() == "lad")
                read_function = read_lad;
            else if (options_vars["format"].as<std::string>() == "dimacs")
                read_function = read_dimacs;
            else if (options_vars["format"].as<std::string>() == "vf")
                read_function = read_vf;
            else if (options_vars["format"].as<std::string>() == "umg_attr")
                read_function = read_umg_attr;
            else if (options_vars["format"].as<std::string>() == "umg_attr_lab")
                read_function = read_umg_attr_lab;
            else {
                std::cerr << "Unknown format " << options_vars["format"].as<std::string>() << std::endl;
                return EXIT_FAILURE;
            }
        }

        /* Read in the graphs */
        // auto graphs = std::make_pair(
        //     read_function(options_vars["pattern-file"].as<std::string>()),
        //     read_function(options_vars["target-file"].as<std::string>()));

        /* Now, run (per-core) to get classification label for input graph */

        // std::vector<std::pair<std::string, Graph > > patterns, targets;

        // Graph, classification
        std::vector<std::tuple<Graph, unsigned > > targets;
        // Graph, classification, name
        std::vector<std::tuple<Graph, unsigned, std::string > > patterns;

        std::ifstream p_csv_file{ options_vars["pattern-csv"].as<std::string>() };
        std::ifstream t_csv_file{ options_vars["target-csv"].as<std::string>() };

        auto p_folder = options_vars["pattern-folder"].as<std::string>();
        auto t_folder = options_vars["target-folder"].as<std::string>();

        std::string line;

        // read in target graphs (training set)
        while (std::getline(t_csv_file, line)) {
            std::stringstream lineStream(line);

            std::string fname;
            std::getline(lineStream, fname, ',');
            std::string name = fname.substr(0, fname.find("."));

            unsigned label;
            lineStream >> label;

            targets.push_back(std::make_tuple(read_function(t_folder + "/" + name), label));
        }

        // read in pattern graphs (test set)
        while (std::getline(p_csv_file, line)) {
            std::stringstream lineStream(line);

            std::string fname;
            std::getline(lineStream, fname, ',');
            std::string name = fname.substr(0, fname.find("."));

            unsigned label;
            lineStream >> label;

            patterns.push_back(std::make_tuple(read_function(p_folder + "/" + name), label, name));
        }

        for (auto & p : patterns) {
            // List of GED, classification
            std::vector<std::pair<unsigned, unsigned> > dists;

            auto graph_p = std::get<0>(p);
            auto class_p = std::get<1>(p);
            auto fname_p = std::get<2>(p);

            for (auto & t : targets) {
                auto graph_t = std::get<0>(t);
                auto class_t = std::get<1>(t);

                auto graphs = std::make_pair(graph_p, graph_t);

                /* Do the actual run. */
                bool aborted = false;
                auto result = run_this(algorithm)(
                        graphs,
                        params,
                        aborted,
                        options_vars.count("timeout") ? options_vars["timeout"].as<int>() : 0);

                /* Stop the clock. */
                auto overall_time = duration_cast<milliseconds>(steady_clock::now() - params.start_time);

                unsigned mcs_size = 0;

                if (!result.stats.empty())
                    for (auto & s : result.stats)
                        if (s.first == "SIZE")
                            mcs_size = stoul(s.second);

                // Compute graph edit distance
                unsigned ged = abs(mcs_size - graph_p.size()) + abs(mcs_size - graph_t.size());

                dists.push_back(std::make_pair(ged, class_t));
            }

            // Sort by increasing distance, take the k-closest elements.
            // Tally up their votes.
            std::sort(dists.begin(), dists.end());

            // Map classifications to vote counts.
            std::map<unsigned, unsigned> tallies;

            auto first_n = dists.begin();
            auto last_n = dists.size() < use_neighbours
                ? dists.end()
                : first_n + use_neighbours;

            for (auto i = first_n; i != last_n; ++i){
                auto label = i->second;

                // Create new if needed
                tallies.insert(std::make_pair(label, 0));

                // Now update.
                tallies[label] += 1;
            }

            // Now sort.
            std::vector<std::pair<unsigned, unsigned> > v_tall(tallies.begin(), tallies.end());

            // Sort into decreasing order on vote count.
            std::sort(v_tall.begin(), v_tall.end(),
                [](std::pair<unsigned, unsigned> & a, std::pair<unsigned, unsigned> & b){
                    return a.second > b.second;
                });

            // Take top class!
            auto ans = v_tall[0].first;
            std::cout << fname_p << " " << class_p << " " << ans << " " << (ans == class_p) << "\n";
        }


        /* Display the results. */
        // std::cout << std::boolalpha << ! result.isomorphism.empty() << " " << result.nodes;

        // if (aborted)
        //     std::cout << " aborted";
        // std::cout << std::endl;

        // for (auto v : result.isomorphism)
        //     std::cout << "(" << v.first << " -> " << v.second << ") ";
        // std::cout << std::endl;

        // std::cout << overall_time.count();
        // if (! result.times.empty()) {
        //     for (auto t : result.times)
        //         std::cout << " " << t.count();
        // }
        // std::cout << std::endl;

        // if (! result.stats.empty()) {
        //     for (auto & s : result.stats) {
        //         std::cout << s.first << "=" << s.second << " ";
        //     }
        //     std::cout << std::endl;
        // }

        // if (! result.isomorphism.empty()) {
        //     for (unsigned i = 0 ; i < graphs.first.size() ; ++i) {
        //         for (unsigned j = 0 ; j < graphs.first.size() ; ++j) {
        //             if (graphs.first.adjacent(i, j)) {
        //                 if (result.isomorphism.find(i)->second != -1 && result.isomorphism.find(j)->second != -1) {
        //                     if (! graphs.second.adjacent(result.isomorphism.find(i)->second, result.isomorphism.find(j)->second)) {
        //                         std::cerr << "Oops! not an isomorphism: " << i << " -- " << j << " but "
        //                            << result.isomorphism.find(i)->second << " -/- " << result.isomorphism.find(j)->second << std::endl;
        //                         return EXIT_FAILURE;
        //                     }
        //                 }
        //             }
        //             else if (params.induced && ! graphs.first.adjacent(i, j)) {
        //                 if (result.isomorphism.find(i)->second != -1 && result.isomorphism.find(j)->second != -1) {
        //                     if (graphs.second.adjacent(result.isomorphism.find(i)->second, result.isomorphism.find(j)->second)) {
        //                         std::cerr << "Oops! not an induced isomorphism: " << i << " -/- " << j << " but "
        //                            << result.isomorphism.find(i)->second << " -- " << result.isomorphism.find(j)->second << std::endl;
        //                         return EXIT_FAILURE;
        //                     }
        //                 }
        //             }
        //         }
        //     }
        // }

        return EXIT_SUCCESS;
    }
    catch (const po::error & e) {
        std::cerr << "Error: " << e.what() << std::endl;
        std::cerr << "Try " << argv[0] << " --help" << std::endl;
        return EXIT_FAILURE;
    }
    catch (const std::exception & e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return EXIT_FAILURE;
    }
}
