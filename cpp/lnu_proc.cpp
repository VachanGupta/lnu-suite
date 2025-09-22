
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <dirent.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <signal.h>
#include <algorithm>
#include <streambuf>
#include <sstream>

std::string read_file(const std::string& path) {
    std::ifstream ifs(path);
    if (!ifs.is_open()) return "";
    std::string content((std::istreambuf_iterator<char>(ifs)), std::istreambuf_iterator<char>());
    return content;
}

void list_procs() {
    DIR* d = opendir("/proc");
    if (!d) {
        perror("opendir /proc failed. This tool is for Linux only.");
        return;
    }

    struct dirent* entry;
    std::cout << "PID\tUID\tCMD\n";
    
    while ((entry = readdir(d)) != NULL) {
        if (entry->d_type != DT_DIR) continue;
        
        std::string name = entry->d_name;
        if (!std::all_of(name.begin(), name.end(), ::isdigit)) continue;

        std::string status_path = "/proc/" + name + "/status";
        std::string cmdline_path = "/proc/" + name + "/cmdline";

        std::string status = read_file(status_path);
        std::string cmdline = read_file(cmdline_path);
        
        if (cmdline.empty()) {
            cmdline = read_file("/proc/" + name + "/comm");

            if (!cmdline.empty() && cmdline.back() == '\n') {
                cmdline.pop_back();
            }
        }

        std::string uid = "-";
        std::size_t pos = status.find("Uid:");
        if (pos != std::string::npos) {
            std::string line = status.substr(pos, status.find('\n', pos) - pos);
            std::stringstream ss(line);
            std::string tag; 
            ss >> tag >> uid; 
        }
        
        for (char& c : cmdline) {
            if (c == '\0') c = ' ';
        }
        
        std::cout << name << "\t" << uid << "\t" << (!cmdline.empty() ? cmdline : std::string("-")) << "\n";
    }
    
    closedir(d);
}
.
void do_kill(pid_t pid) {
    if (kill(pid, 0) != 0) {
        perror("Process check failed (does the process exist and do you have permission?)");
        return;
    }
    
    std::cout << "Sending SIGTERM to process " << pid << ", waiting 1 second...\n";
    if (kill(pid, SIGTERM) == 0) {
        sleep(1);
        if (kill(pid, 0) == 0) {
            std::cout << "Process is still alive, sending SIGKILL...\n";
            if (kill(pid, SIGKILL) != 0) {
                perror("kill(SIGKILL) failed");
            } else {
                std::cout << "SIGKILL sent.\n";
            }
        } else {
            std::cout << "Process exited gracefully after SIGTERM.\n";
        }
    } else {
        perror("kill(SIGTERM) failed");
    }
}

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: lnu-proc <list|kill> [pid]\n";
        return 1;
    }
    
    std::string cmd = argv[1];
    if (cmd == "list") {
        list_procs();
    } else if (cmd == "kill") {
        if (argc < 3) {
            std::cerr << "Usage: lnu-proc kill <pid>\n";
            return 1;
        }
        try {
            pid_t pid = std::stoi(argv[2]);
            do_kill(pid);
        } catch (const std::invalid_argument& e) {
            std::cerr << "Invalid PID specified.\n";
            return 1;
        } catch (const std::out_of_range& e) {
            std::cerr << "PID is out of range.\n";
            return 1;
        }
    } else {
        std::cerr << "Unknown command: " << cmd << "\n";
        return 1;
    }
    
    return 0;
}
