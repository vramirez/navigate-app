import React from 'react'
import PropTypes from 'prop-types'

/**
 * KeywordTags Component
 *
 * Displays keywords or entities as colored badge pills
 * Supports both array of strings or comma-separated string
 */
export default function KeywordTags({
  keywords = null,
  type = 'keyword',
  className = ''
}) {
  // Handle empty or null keywords
  if (!keywords || (Array.isArray(keywords) && keywords.length === 0)) {
    return (
      <p className="text-sm text-gray-400 italic">
        {type === 'entity' ? 'No se detectaron entidades' : 'No hay palabras clave'}
      </p>
    )
  }

  // Parse keywords - handle both array and comma-separated string
  let keywordArray = []
  if (Array.isArray(keywords)) {
    keywordArray = keywords
  } else if (typeof keywords === 'string') {
    // Split by comma and trim whitespace
    keywordArray = keywords.split(',').map(k => k.trim()).filter(k => k.length > 0)
  }

  if (keywordArray.length === 0) {
    return (
      <p className="text-sm text-gray-400 italic">
        {type === 'entity' ? 'No se detectaron entidades' : 'No hay palabras clave'}
      </p>
    )
  }

  // Color schemes for different tag types
  const getTagColors = (index) => {
    const colorSchemes = {
      keyword: [
        'bg-blue-100 text-blue-700 border-blue-300',
        'bg-purple-100 text-purple-700 border-purple-300',
        'bg-indigo-100 text-indigo-700 border-indigo-300',
        'bg-cyan-100 text-cyan-700 border-cyan-300',
        'bg-sky-100 text-sky-700 border-sky-300'
      ],
      entity: [
        'bg-green-100 text-green-700 border-green-300',
        'bg-emerald-100 text-emerald-700 border-emerald-300',
        'bg-teal-100 text-teal-700 border-teal-300',
        'bg-lime-100 text-lime-700 border-lime-300',
        'bg-green-100 text-green-600 border-green-200'
      ]
    }
    const scheme = colorSchemes[type] || colorSchemes.keyword
    return scheme[index % scheme.length]
  }

  return (
    <div className={`flex flex-wrap gap-2 ${className}`}>
      {keywordArray.map((keyword, index) => (
        <span
          key={`${keyword}-${index}`}
          className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border transition-all duration-200 hover:shadow-md ${getTagColors(index)}`}
          title={keyword}
        >
          {keyword}
        </span>
      ))}
    </div>
  )
}

KeywordTags.propTypes = {
  keywords: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.string),
    PropTypes.string
  ]),
  type: PropTypes.oneOf(['keyword', 'entity']),
  className: PropTypes.string
}
