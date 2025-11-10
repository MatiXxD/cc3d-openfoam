#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>

void process(const std::string &input, const std::string &output) {
  std::cout << "start processing file: " << input << std::endl;

  // input
  std::ifstream file(input);
  std::vector<int> data;

  std::string line;
  while (std::getline(file, line)) {
    std::istringstream ss(line);

    int value;
    while (ss >> value) {
      data.push_back(value);
    }
  }

  std::cout << data.size() << " values read from file" << std::endl;
  file.close();

  // output
  std::ofstream outfile(output);
  outfile << "processed data:\n";

  for (const auto &value : data) {
    outfile << 2 * value << ' ';
  }
  outfile << "\n";

  std::cout << "result was written to: " << output << std::endl;
  outfile.close();
}

int main(int argc, char *argv[]) {
  process(argv[1], argv[2]);
}