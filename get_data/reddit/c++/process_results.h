#include <vector>
#include <string>
#include <unordered_map>

using namespace std;
//TODO configure with fpath, to write directly to file
class ResultProcessor{
private:
    vector<string> FieldsToKeep;
public:
    ResultProcessor()= default;;

    unordered_map<string, string> process_one(unordered_map<string, string>& result_to_process);

    vector<unordered_map<string, string>> process_many(vector<unordered_map<string, string>>& results_to_process);

    void configure(vector<string>& fields_to_keep);
};