export const SkeletonLoader: React.FC = () => (
  <div className="animate-pulse">
    <div className="h-8 bg-gray-800 rounded mb-4"></div>
    <div className="h-32 bg-gray-800 rounded"></div>
  </div>
)

export const StatCardSkeleton: React.FC = () => (
  <div className="bg-gray-900 rounded-lg p-6 animate-pulse">
    <div className="h-4 bg-gray-800 rounded w-24 mb-2"></div>
    <div className="h-8 bg-gray-800 rounded w-32"></div>
  </div>
)

export const ChartSkeleton: React.FC = () => (
  <div className="bg-gray-900 rounded-lg p-6 animate-pulse">
    <div className="h-64 bg-gray-800 rounded"></div>
  </div>
)
