import React from 'react'

interface StatCardProps {
  label: string
  value: string | number
  subtext?: string
  color?: 'blue' | 'green' | 'red' | 'yellow' | 'default'
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  subtext,
  color = 'default',
}) => {
  const colorClasses = {
    blue: 'border-blue-500 bg-blue-500/10',
    green: 'border-green-500 bg-green-500/10',
    red: 'border-red-500 bg-red-500/10',
    yellow: 'border-yellow-500 bg-yellow-500/10',
    default: 'border-gray-700',
  }

  const textColorClasses = {
    blue: 'text-blue-400',
    green: 'text-green-400',
    red: 'text-red-400',
    yellow: 'text-yellow-400',
    default: 'text-gray-400',
  }

  return (
    <div
      className={`bg-gray-900 rounded-lg p-6 border ${colorClasses[color]} transition-all hover:border-opacity-100`}
    >
      <p className="text-gray-400 text-sm mb-2">{label}</p>
      <p className={`text-3xl font-bold ${textColorClasses[color]}`}>
        {value}
      </p>
      {subtext && <p className="text-gray-500 text-xs mt-2">{subtext}</p>}
    </div>
  )
}
