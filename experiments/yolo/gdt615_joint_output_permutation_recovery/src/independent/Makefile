CXX ?= g++
CXXFLAGS ?= -O3 -std=c++20 -Wall -Wextra -Wpedantic -pthread

.PHONY: all clean self-test

all: stage0_independent

stage0_independent: stage0_independent.cpp
	$(CXX) $(CXXFLAGS) $< -o $@

self-test: stage0_independent
	./stage0_independent --self-test

clean:
	rm -f stage0_independent
