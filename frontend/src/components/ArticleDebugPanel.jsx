import React, { useState } from 'react'
import { ChevronDownIcon, ChevronUpIcon, ClipboardDocumentIcon, CheckIcon } from '@heroicons/react/24/outline'

/**
 * ArticleDebugPanel - Self-contained debug component
 *
 * Displays ALL ML-extracted features for debugging purposes.
 * This component can be safely removed later without affecting other code.
 *
 * To remove:
 * 1. Delete this file
 * 2. Remove import and usage from ArticleDetail.jsx
 */
export default function ArticleDebugPanel({ article }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [copied, setCopied] = useState(false)

  if (!article) return null

  const handleCopyJSON = () => {
    const jsonString = JSON.stringify(article, null, 2)
    navigator.clipboard.writeText(jsonString)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  // Use backend-calculated completeness score
  const completenessScore = article.feature_completeness_score || 0.0
  const completenessPercentage = Math.round(completenessScore * 100)

  // Get color based on completeness percentage
  const getCompletenessColor = (score) => {
    if (score >= 0.8) return 'bg-green-500'
    if (score >= 0.5) return 'bg-yellow-500'
    if (score >= 0.3) return 'bg-orange-500'
    return 'bg-red-500'
  }

  const FieldRow = ({ label, value, type = 'text' }) => {
    let displayValue = value

    // Handle different value types
    if (value === null || value === undefined || value === '') {
      displayValue = <span className="text-gray-400 italic">—</span>
    } else if (type === 'boolean') {
      displayValue = value ? (
        <span className="text-green-600 font-semibold">✓ Sí</span>
      ) : (
        <span className="text-red-600">✗ No</span>
      )
    } else if (type === 'array') {
      if (Array.isArray(value) && value.length > 0) {
        displayValue = (
          <div className="space-y-1">
            <span className="text-xs text-gray-500">({value.length} items)</span>
            <div className="flex flex-wrap gap-1">
              {value.map((item, idx) => (
                <span key={idx} className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs font-mono">
                  {typeof item === 'object' ? JSON.stringify(item) : item}
                </span>
              ))}
            </div>
          </div>
        )
      } else {
        displayValue = <span className="text-gray-400 italic">[]</span>
      }
    } else if (type === 'datetime') {
      displayValue = value ? (
        <span className="font-mono text-xs">{new Date(value).toLocaleString('es-CO')}</span>
      ) : (
        <span className="text-gray-400 italic">—</span>
      )
    } else if (type === 'number') {
      displayValue = <span className="font-mono">{value}</span>
    } else {
      displayValue = <span className="font-mono text-xs">{String(value)}</span>
    }

    return (
      <div className="grid grid-cols-2 gap-2 py-2 border-b border-gray-200">
        <dt className="text-sm font-semibold text-gray-700">{label}</dt>
        <dd className="text-sm text-gray-900">{displayValue}</dd>
      </div>
    )
  }

  const FeatureGroup = ({ title, children }) => (
    <div className="mb-6">
      <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider mb-3 pb-2 border-b-2 border-gray-400">
        {title}
      </h4>
      <dl className="space-y-1">{children}</dl>
    </div>
  )

  return (
    <div className="card border-2 border-dashed border-orange-400 bg-white shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="px-3 py-1 bg-orange-500 text-white text-xs font-bold rounded uppercase">
            DEBUG
          </span>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-2 text-left font-bold text-gray-900 hover:text-orange-600 transition-colors"
          >
            <span className="text-lg">Todas las features extraídas</span>
            {isExpanded ? (
              <ChevronUpIcon className="h-5 w-5" />
            ) : (
              <ChevronDownIcon className="h-5 w-5" />
            )}
          </button>
        </div>

        <button
          onClick={handleCopyJSON}
          className="flex items-center gap-2 px-3 py-1.5 bg-gray-700 text-white text-xs font-medium rounded hover:bg-gray-800 transition-colors"
        >
          {copied ? (
            <>
              <CheckIcon className="h-4 w-4" />
              Copiado!
            </>
          ) : (
            <>
              <ClipboardDocumentIcon className="h-4 w-4" />
              Copiar JSON
            </>
          )}
        </button>
      </div>

      {/* Completeness Progress Bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-semibold text-gray-700">
            Completitud de extracción
          </span>
          <span className="text-sm font-mono text-gray-900">
            {completenessPercentage}% ({completenessScore.toFixed(2)})
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className={`h-3 ${getCompletenessColor(completenessScore)} transition-all duration-300`}
            style={{ width: `${completenessPercentage}%` }}
          />
        </div>
      </div>

      {/* Expandable Content */}
      {isExpanded && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Column 1 */}
          <div>
            {/* Categorization */}
            <FeatureGroup title="Categorización">
              <FieldRow label="category" value={article.category} />
              <FieldRow label="subcategory" value={article.subcategory} />
              <FieldRow label="event_type (legacy)" value={article.event_type} />
              <FieldRow label="event_type_detected" value={article.event_type_detected} />
              <FieldRow label="event_subtype" value={article.event_subtype} />
              <FieldRow label="section" value={article.section} />
              <FieldRow label="crawl_section" value={article.crawl_section} />
            </FeatureGroup>

            {/* Geographic Features */}
            <FeatureGroup title="Geographic Features">
              <FieldRow label="primary_city" value={article.primary_city} />
              <FieldRow label="neighborhood" value={article.neighborhood} />
              <FieldRow label="venue_name" value={article.venue_name} />
              <FieldRow label="venue_address" value={article.venue_address} />
              <FieldRow label="latitude" value={article.latitude} type="number" />
              <FieldRow label="longitude" value={article.longitude} type="number" />
              <FieldRow label="event_country" value={article.event_country} />
              <FieldRow label="event_location (legacy)" value={article.event_location} />
            </FeatureGroup>

            {/* Colombian Relevance */}
            <FeatureGroup title="Colombian Relevance">
              <FieldRow label="colombian_involvement" value={article.colombian_involvement} type="boolean" />
              <FieldRow label="event_country" value={article.event_country} />
              <FieldRow label="source_country" value={article.source_country} />
            </FeatureGroup>

            {/* Keywords & Entities */}
            <FeatureGroup title="Keywords & Entities">
              <FieldRow label="extracted_keywords" value={article.extracted_keywords} type="array" />
              <FieldRow label="entities" value={article.entities} type="array" />
            </FeatureGroup>
          </div>

          {/* Column 2 */}
          <div>
            {/* Temporal Features */}
            <FeatureGroup title="Temporal Features">
              <FieldRow label="event_start_datetime" value={article.event_start_datetime} type="datetime" />
              <FieldRow label="event_end_datetime" value={article.event_end_datetime} type="datetime" />
              <FieldRow label="event_duration_hours" value={article.event_duration_hours} type="number" />
              <FieldRow label="event_date (legacy)" value={article.event_date} type="datetime" />
              <FieldRow label="published_date" value={article.published_date} type="datetime" />
            </FeatureGroup>

            {/* Scale Features */}
            <FeatureGroup title="Scale Features">
              <FieldRow label="expected_attendance" value={article.expected_attendance} type="number" />
              <FieldRow label="event_scale" value={article.event_scale} />
            </FeatureGroup>

            {/* ML Scores */}
            <FeatureGroup title="ML Scores">
              <FieldRow label="business_relevance_score" value={article.business_relevance_score} type="number" />
              <FieldRow label="business_suitability_score" value={article.business_suitability_score} type="number" />
              <FieldRow label="urgency_score" value={article.urgency_score} type="number" />
              <FieldRow label="sentiment_score" value={article.sentiment_score} type="number" />
            </FeatureGroup>

            {/* Processing Metadata */}
            <FeatureGroup title="Processing Metadata">
              <FieldRow label="features_extracted" value={article.features_extracted} type="boolean" />
              <FieldRow label="feature_extraction_date" value={article.feature_extraction_date} type="datetime" />
              <FieldRow label="feature_extraction_confidence" value={article.feature_extraction_confidence} type="number" />
              <FieldRow label="feature_completeness_score" value={article.feature_completeness_score} type="number" />
              <FieldRow label="processing_error" value={article.processing_error} />
            </FeatureGroup>

            {/* Article Metadata */}
            <FeatureGroup title="Article Metadata">
              <FieldRow label="id" value={article.id} type="number" />
              <FieldRow label="source_name" value={article.source_name} />
              <FieldRow label="author" value={article.author} />
              <FieldRow label="created_at" value={article.created_at} type="datetime" />
              <FieldRow label="updated_at" value={article.updated_at} type="datetime" />
            </FeatureGroup>
          </div>
        </div>
      )}

      {/* Collapsed State Hint */}
      {!isExpanded && (
        <p className="text-sm text-gray-500 italic">
          Click para ver todos los campos extraídos por ML (útil para debugging)
        </p>
      )}
    </div>
  )
}
