import React from 'react'
import PropTypes from 'prop-types'

/**
 * RelevanceBadge Component
 *
 * Displays a visual indicator of article relevance score
 *
 * Relevance Levels:
 * - High (0.6-1.0): Green badge - "Alta relevancia"
 * - Medium (0.3-0.6): Yellow badge - "Relevancia media"
 * - Low (0.0-0.3): Gray badge - "Baja relevancia"
 * - Not Processed (-1.0): Red badge - "Sin procesar"
 */
export default function RelevanceBadge({ score }) {
  const getRelevanceInfo = (score) => {
    if (score < 0) {
      return {
        label: 'Sin procesar',
        bgColor: 'bg-red-100',
        textColor: 'text-red-700',
        borderColor: 'border-red-300',
        icon: '⏳'
      }
    } else if (score >= 0.6) {
      return {
        label: 'Alta relevancia',
        bgColor: 'bg-green-100',
        textColor: 'text-green-700',
        borderColor: 'border-green-300',
        icon: '⭐'
      }
    } else if (score >= 0.3) {
      return {
        label: 'Relevancia media',
        bgColor: 'bg-yellow-100',
        textColor: 'text-yellow-700',
        borderColor: 'border-yellow-300',
        icon: '📊'
      }
    } else {
      return {
        label: 'Baja relevancia',
        bgColor: 'bg-gray-100',
        textColor: 'text-gray-600',
        borderColor: 'border-gray-300',
        icon: '📰'
      }
    }
  }

  const info = getRelevanceInfo(score)

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium border ${info.bgColor} ${info.textColor} ${info.borderColor}`}
      title={`Puntuación de relevancia: ${score >= 0 ? score.toFixed(2) : 'No procesado'}`}
    >
      <span>{info.icon}</span>
      <span>{info.label}</span>
    </span>
  )
}

RelevanceBadge.propTypes = {
  score: PropTypes.number.isRequired
}
