// RTA001 CUDA proposal kernel.  Final scientific scores are recomputed on CPU.
#include <cuda_runtime.h>

#include <cstdint>
#include <cstdlib>

extern "C" {

struct RTA001CudaInfo {
  int device_count;
  int device;
  int major;
  int minor;
  std::uint64_t total_memory;
};

__global__ void assign_kernel(const std::int16_t* vectors,
                              const std::int16_t* medoids,
                              const std::int16_t* weights,
                              int rows,
                              int dimensions,
                              int restarts,
                              int k,
                              std::int32_t* assignments,
                              std::uint64_t* costs) {
  const int row = blockIdx.x * blockDim.x + threadIdx.x;
  const int restart = blockIdx.y;
  if (row >= rows || restart >= restarts) return;
  const std::int16_t* vector = vectors + static_cast<std::size_t>(row) * dimensions;
  std::uint64_t best_cost = UINT64_MAX;
  int best = 0;
  for (int cluster = 0; cluster < k; ++cluster) {
    const std::int16_t* medoid = medoids +
        (static_cast<std::size_t>(restart) * k + cluster) * dimensions;
    std::uint64_t cost = 0;
    for (int d = 0; d < dimensions; ++d) {
      int delta = static_cast<int>(vector[d]) - static_cast<int>(medoid[d]);
      if (delta < 0) delta = -delta;
      cost += static_cast<std::uint64_t>(delta) * static_cast<std::uint16_t>(weights[d]);
    }
    if (cost < best_cost) {
      best_cost = cost;
      best = cluster;
    }
  }
  const std::size_t index = static_cast<std::size_t>(restart) * rows + row;
  assignments[index] = best;
  costs[index] = best_cost;
}

int rta001_cuda_info(RTA001CudaInfo* output) {
  if (output == nullptr) return 1;
  int count = 0;
  if (cudaGetDeviceCount(&count) != cudaSuccess || count < 1) return 2;
  int device = 0;
  if (cudaGetDevice(&device) != cudaSuccess) return 3;
  cudaDeviceProp properties{};
  if (cudaGetDeviceProperties(&properties, device) != cudaSuccess) return 4;
  output->device_count = count;
  output->device = device;
  output->major = properties.major;
  output->minor = properties.minor;
  output->total_memory = properties.totalGlobalMem;
  return 0;
}

int rta001_assign_many(const std::int16_t* host_vectors,
                       const std::int16_t* host_medoids,
                       const std::int16_t* host_weights,
                       int rows,
                       int dimensions,
                       int restarts,
                       int k,
                       std::int32_t* host_assignments,
                       std::uint64_t* host_costs) {
  if (host_vectors == nullptr || host_medoids == nullptr || host_weights == nullptr ||
      host_assignments == nullptr || host_costs == nullptr || rows <= 0 ||
      dimensions <= 0 || restarts <= 0 || k <= 0) return 10;
  std::int16_t *vectors = nullptr, *medoids = nullptr, *weights = nullptr;
  std::int32_t* assignments = nullptr;
  std::uint64_t* costs = nullptr;
  const std::size_t vector_bytes = static_cast<std::size_t>(rows) * dimensions * sizeof(std::int16_t);
  const std::size_t medoid_bytes = static_cast<std::size_t>(restarts) * k * dimensions * sizeof(std::int16_t);
  const std::size_t weight_bytes = static_cast<std::size_t>(dimensions) * sizeof(std::int16_t);
  const std::size_t assignment_bytes = static_cast<std::size_t>(restarts) * rows * sizeof(std::int32_t);
  const std::size_t cost_bytes = static_cast<std::size_t>(restarts) * rows * sizeof(std::uint64_t);
  int rc = 0;
#define CUDA_GUARD(call, value) do { if ((call) != cudaSuccess) { rc = (value); goto cleanup; } } while (0)
  CUDA_GUARD(cudaMalloc(&vectors, vector_bytes), 11);
  CUDA_GUARD(cudaMalloc(&medoids, medoid_bytes), 12);
  CUDA_GUARD(cudaMalloc(&weights, weight_bytes), 13);
  CUDA_GUARD(cudaMalloc(&assignments, assignment_bytes), 14);
  CUDA_GUARD(cudaMalloc(&costs, cost_bytes), 15);
  CUDA_GUARD(cudaMemcpy(vectors, host_vectors, vector_bytes, cudaMemcpyHostToDevice), 16);
  CUDA_GUARD(cudaMemcpy(medoids, host_medoids, medoid_bytes, cudaMemcpyHostToDevice), 17);
  CUDA_GUARD(cudaMemcpy(weights, host_weights, weight_bytes, cudaMemcpyHostToDevice), 18);
  {
    dim3 block(256, 1, 1);
    dim3 grid((rows + 255) / 256, restarts, 1);
    assign_kernel<<<grid, block>>>(vectors, medoids, weights, rows, dimensions, restarts, k,
                                   assignments, costs);
  }
  CUDA_GUARD(cudaGetLastError(), 19);
  CUDA_GUARD(cudaDeviceSynchronize(), 20);
  CUDA_GUARD(cudaMemcpy(host_assignments, assignments, assignment_bytes, cudaMemcpyDeviceToHost), 21);
  CUDA_GUARD(cudaMemcpy(host_costs, costs, cost_bytes, cudaMemcpyDeviceToHost), 22);
cleanup:
  cudaFree(vectors);
  cudaFree(medoids);
  cudaFree(weights);
  cudaFree(assignments);
  cudaFree(costs);
  return rc;
#undef CUDA_GUARD
}

}  // extern "C"
