import React from 'react'
import PropTypes from 'prop-types'

/**
 * ScoreIndicator Component
 *
 * Displays a visual indicator for ML scores (0.0 to 1.0 scale)
 * with color-coded progress bar and percentage display
 *
 * Color Scheme:
 * - 0.0-0.3: Red (low)
 * - 0.3-0.6: Yellow (medium)
 * - 0.6-1.0: Green (high)
 */
export default function ScoreIndicator({
  score = null,
  label,
  description = null
}) {
  // Handle null/undefined scores
  if (score === null || score === undefined) {
    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">{label}</span>
          <span className="text-sm text-gray-400">No disponible</span>
        </div>
        {description && (
          <p className="text-xs text-gray-500">{description}</p>
        )}
      </div>
    )
  }

  // Determine color based on score
  const getScoreColor = (score) => {
    if (score >= 0.6) {
      return {
        bg: 'bg-green-500',
        text: 'text-green-700',
        bgLight: 'bg-green-100',
        label: 'Alta'
      }
    } else if (score >= 0.3) {
      return {
        bg: 'bg-yellow-500',
        text: 'text-yellow-700',
        bgLight: 'bg-yellow-100',
        label: 'Media'
      }
    } else {
      return {
        bg: 'bg-red-500',
        text: 'text-red-700',
        bgLight: 'bg-red-100',
        label: 'Baja'
      }
    }
  }

  const colors = getScoreColor(score)
  const percentage = Math.round(score * 100)

  return (
    <div className="space-y-2">
      {/* Label and Score */}
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">{label}</span>
        <div className="flex items-center gap-2">
          <span className={`text-sm font-bold ${colors.text}`}>
            {percentage}%
          </span>
          <span className={`text-xs px-2 py-0.5 rounded-full ${colors.bgLight} ${colors.text}`}>
            {colors.label}
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
        <div
          className={`h-full ${colors.bg} transition-all duration-300 ease-out`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      {/* Description */}
      {description && (
        <p className="text-xs text-gray-500">{description}</p>
      )}
    </div>
  )
}

ScoreIndicator.propTypes = {
  score: PropTypes.number,
  label: PropTypes.string.isRequired,
  description: PropTypes.string
}
