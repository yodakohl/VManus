#include <algorithm>
#include <cstdint>
#include <limits>

extern "C" double gdt001_skeleton_score(
    const int32_t *tokens, const int64_t *offsets, int64_t line_count,
    const int32_t *mapping, const double *starts, const double *transitions,
    const double *terminals) {
  constexpr int X = 28;
  double total = 0.0;
  for (int64_t line = 0; line < line_count; ++line) {
    const int64_t begin = offsets[line], end = offsets[line + 1];
    if (begin == end) continue;
    int previous = mapping[tokens[begin]];
    double current[X], next[X];
    for (int x = 0; x < X; ++x) current[x] = starts[previous * X + x];
    for (int64_t position = begin + 1; position < end; ++position) {
      const int target = mapping[tokens[position]];
      const double *matrix = transitions + (((previous * 21 + target) * X) * X);
      for (int destination = 0; destination < X; ++destination) {
        double best = std::numeric_limits<double>::infinity();
        for (int source = 0; source < X; ++source)
          best = std::min(best, current[source] + matrix[source * X + destination]);
        next[destination] = best;
      }
      std::copy(next, next + X, current);
      previous = target;
    }
    double best = std::numeric_limits<double>::infinity();
    const double *tail = terminals + previous * X;
    for (int source = 0; source < X; ++source)
      best = std::min(best, current[source] + tail[source]);
    total += best;
  }
  return total;
}
