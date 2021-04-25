from puzzle import Puzzle
from solver import Solver


def main():
    # test_names = ["5by5",
    #               "10by10",
    #               "15by15",
    #               "20by20",
    #               "25by25",
    #               "30by25",
    #               "50by50"
    #               ]
    # tests = [] * len(test_names)
    # for i in range(len(tests)):
    #     name = test_names[i]
    #     tests[i] = Solver(Puzzle(name,
    #                              "lib\\" + name + "RowClues.txt",
    #                              "lib\\" + name + "ColClues.txt"
    #                              ))
    #     tests[i].priority_solve(update_solve=True)
    p = Puzzle("5by5", "lib\\5by5RowClues.txt", "lib\\5by5ColClues.txt")
    s = Solver(p)
    s.slow_solve()


if __name__ == "__main__":
    main()