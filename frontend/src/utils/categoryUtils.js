/**
 * Category Utilities for News Classification
 *
 * Two-tier system:
 * - Public categories: Broad categories displayed to users (10 total)
 * - Private subcategories: Detailed subcategories for ML classification (40+ total)
 */

// Mapping from private subcategories to public categories
export const subcategoryToCategory = {
  // Eventos
  'conciertos': 'eventos',
  'festivales': 'eventos',
  'deportes': 'eventos',
  'teatro-cultura': 'eventos',
  'ferias': 'eventos',

  // Gastronomía
  'tendencias-gastronomicas': 'gastronomia',
  'bebidas': 'gastronomia',
  'competencias-culinarias': 'gastronomia',
  'apertura-cierre': 'gastronomia',
  'productos-nuevos': 'gastronomia',

  // Infraestructura
  'obras-viales': 'infraestructura',
  'transporte-publico': 'infraestructura',
  'desarrollo-urbano': 'infraestructura',
  'servicios-publicos': 'infraestructura',

  // Clima y Alertas
  'clima-extremo': 'clima-alertas',
  'alertas-emergencia': 'clima-alertas',
  'desastres-naturales': 'clima-alertas',

  // Turismo
  'estadisticas-turismo': 'turismo',
  'feriados-puentes': 'turismo',
  'temporada-alta-baja': 'turismo',
  'turismo-internacional': 'turismo',

  // Economía
  'tendencias-consumo': 'economia',
  'inflacion-precios': 'economia',
  'empleo': 'economia',
  'poder-adquisitivo': 'economia',

  // Regulaciones
  'leyes-nuevas': 'regulaciones',
  'permisos-licencias': 'regulaciones',
  'salud-publica': 'regulaciones',
  'impuestos': 'regulaciones',
  'horarios-restricciones': 'regulaciones',

  // Educación
  'universidades': 'educacion',
  'colegios': 'educacion',
  'inicio-fin-semestre': 'educacion',

  // Comunidad
  'eventos-barriales': 'comunidad',
  'mercados-ferias': 'comunidad',
  'tendencias-sociales': 'comunidad',
  'celebraciones-locales': 'comunidad',

  // Seguridad
  'seguridad-publica': 'seguridad',
  'zonas-riesgo': 'seguridad',
  'operativos-policiales': 'seguridad',
}

// Category color schemes for UI
export const categoryColors = {
  'eventos': {
    bg: 'bg-purple-50',
    text: 'text-purple-700',
    border: 'border-purple-200',
    icon: '🎉'
  },
  'gastronomia': {
    bg: 'bg-orange-50',
    text: 'text-orange-700',
    border: 'border-orange-200',
    icon: '🍽️'
  },
  'infraestructura': {
    bg: 'bg-gray-50',
    text: 'text-gray-700',
    border: 'border-gray-200',
    icon: '🏙️'
  },
  'clima-alertas': {
    bg: 'bg-blue-50',
    text: 'text-blue-700',
    border: 'border-blue-200',
    icon: '⛈️'
  },
  'turismo': {
    bg: 'bg-cyan-50',
    text: 'text-cyan-700',
    border: 'border-cyan-200',
    icon: '✈️'
  },
  'economia': {
    bg: 'bg-green-50',
    text: 'text-green-700',
    border: 'border-green-200',
    icon: '💰'
  },
  'regulaciones': {
    bg: 'bg-amber-50',
    text: 'text-amber-700',
    border: 'border-amber-200',
    icon: '⚖️'
  },
  'educacion': {
    bg: 'bg-indigo-50',
    text: 'text-indigo-700',
    border: 'border-indigo-200',
    icon: '🎓'
  },
  'comunidad': {
    bg: 'bg-pink-50',
    text: 'text-pink-700',
    border: 'border-pink-200',
    icon: '👥'
  },
  'seguridad': {
    bg: 'bg-red-50',
    text: 'text-red-700',
    border: 'border-red-200',
    icon: '🛡️'
  }
}

/**
 * Get public category from subcategory
 * @param {string} subcategory - Private subcategory ID
 * @returns {string} Public category ID
 */
export function getCategoryFromSubcategory(subcategory) {
  return subcategoryToCategory[subcategory] || null
}

/**
 * Get category color scheme
 * @param {string} category - Public category ID
 * @returns {object} Color scheme object with bg, text, border, icon
 */
export function getCategoryColors(category) {
  return categoryColors[category] || categoryColors['comunidad'] // Default fallback
}

/**
 * Get category icon
 * @param {string} category - Public category ID
 * @returns {string} Emoji icon
 */
export function getCategoryIcon(category) {
  return categoryColors[category]?.icon || '📰'
}

/**
 * Format category badge classes
 * @param {string} category - Public category ID
 * @returns {string} Tailwind CSS classes for badge
 */
export function getCategoryBadgeClasses(category) {
  const colors = getCategoryColors(category)
  return `inline-flex items-center gap-1 px-2 py-1 text-xs font-semibold rounded-md ${colors.bg} ${colors.text} ${colors.border} border`
}
